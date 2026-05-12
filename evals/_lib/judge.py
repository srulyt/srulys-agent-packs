"""LLM-as-judge helper.

Calls the existing ``@eval-judge`` agent (which ships under
``agent-packs/eval-framework/``) via Copilot CLI to score a SUT artifact
against a free-form criteria string. Returns a :class:`Verdict` with a
``passed`` boolean, a numeric ``score`` in ``[0.0, 1.0]``, and the judge's
reasoning + cited evidence.

Tests use it like::

    verdict = judge(
        artifact=arch_md.read_text(),
        criteria="Architecture must describe exactly 2 agents named...",
    )
    assert verdict.passed, verdict.reasoning

Determinism: the judge is single-shot in v1. If a particular test is flaky
because of judge non-determinism, wrap the call in a small loop that
asserts the verdict is consistent across N invocations -- but only do this
where it has been observed to matter, not by default.
"""

from __future__ import annotations

import dataclasses
import json
import os
import re
import tempfile
from pathlib import Path
from typing import Sequence

from . import copilot


# Default acceptance threshold. Override per-call with ``threshold=`` or
# globally with the ``EVAL_JUDGE_THRESHOLD`` env var.
DEFAULT_THRESHOLD = 0.7


@dataclasses.dataclass(frozen=True)
class Verdict:
    """Structured judge response."""

    passed: bool
    score: float
    reasoning: str
    evidence: list[dict]
    raw_response: str
    """The judge's verbatim stdout, persisted for debugging."""

    def __bool__(self) -> bool:
        return self.passed


class JudgeError(RuntimeError):
    """Raised when the judge subprocess fails or returns unparsable output."""


def judge(
    *,
    artifact: str,
    criteria: str,
    threshold: float | None = None,
    golden: Sequence[str] = (),
    log_dir: Path | None = None,
    timeout: float = 180.0,
) -> Verdict:
    """Score ``artifact`` against ``criteria`` using the @eval-judge agent.

    Parameters
    ----------
    artifact:
        The text to evaluate (typically a file produced by the SUT).
    criteria:
        Free-form description of what "good" looks like. Be specific:
        the judge has nothing else to anchor on.
    threshold:
        Score >= threshold => ``passed=True``. Defaults to
        :data:`DEFAULT_THRESHOLD`.
    golden:
        Optional reference texts (e.g. expected outputs) the judge can
        compare against.
    log_dir:
        Where to persist the judge prompt + raw response for debugging.
        Defaults to a fresh temp dir.
    timeout:
        Subprocess wall-clock limit.
    """
    threshold = (
        threshold
        if threshold is not None
        else float(os.environ.get("EVAL_JUDGE_THRESHOLD", DEFAULT_THRESHOLD))
    )
    log_dir = log_dir or Path(tempfile.mkdtemp(prefix="eval-judge-"))
    log_dir.mkdir(parents=True, exist_ok=True)

    prompt = _build_prompt(artifact=artifact, criteria=criteria, golden=list(golden))
    (log_dir / "judge-prompt.md").write_text(prompt, encoding="utf-8")

    # The judge agent ships under agent-packs/eval-framework. To invoke it,
    # we launch copilot from a workspace that has the agent staged. We
    # stage just the judge agent into the log_dir to keep this self-contained.
    workspace = log_dir / "_judge_ws"
    workspace.mkdir(exist_ok=True)
    _stage_judge_agent(workspace)

    result = copilot.run_agent(
        prompt=prompt,
        workspace=workspace,
        agent="eval-judge",
        log_path=log_dir / "judge.log",
        timeout=timeout,
    )

    if not result.ok:
        raise JudgeError(
            f"Judge subprocess exited {result.returncode}. "
            f"See log: {result.log_path}"
        )

    parsed = _extract_json(result.stdout)
    if parsed is None:
        raise JudgeError(
            f"Judge returned no parsable JSON. See log: {result.log_path}\n"
            f"--- stdout ---\n{result.stdout[:2000]}"
        )

    score = float(parsed.get("score", 0.0))
    return Verdict(
        passed=score >= threshold,
        score=score,
        reasoning=str(parsed.get("rationale", "")).strip(),
        evidence=list(parsed.get("evidence", []) or []),
        raw_response=result.stdout,
    )


# ---- prompt construction ------------------------------------------------

_PROMPT_TEMPLATE = """\
You are evaluating a single artifact against criteria. Read carefully and
score strictly. If criteria are unmet, score low. Cite concrete evidence.

Output **exactly one JSON object** on stdout with the schema:
```json
{{
  "score": 0.0,
  "rationale": "short prose explanation",
  "evidence": [{{"path": "artifact", "quote": "..."}}]
}}
```

## Criteria
{criteria}

## Artifact
```
{artifact}
```
{golden_block}
"""


def _build_prompt(*, artifact: str, criteria: str, golden: list[str]) -> str:
    golden_block = ""
    if golden:
        parts = ["\n## Reference (golden)"]
        for i, g in enumerate(golden, 1):
            parts.append(f"\n### Reference {i}\n```\n{g}\n```")
        golden_block = "\n".join(parts)
    return _PROMPT_TEMPLATE.format(
        criteria=criteria.strip(),
        artifact=artifact,
        golden_block=golden_block,
    )


_JSON_RE = re.compile(r"\{.*\}", re.DOTALL)


def _extract_json(text: str) -> dict | None:
    """Find the first balanced JSON object in ``text``."""
    # Try the whole thing first.
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Greedy-then-shrink: try the largest substring that starts with `{`
    # and ends with `}`.
    start = text.find("{")
    end = text.rfind("}")
    while start != -1 and end != -1 and end > start:
        chunk = text[start : end + 1]
        try:
            return json.loads(chunk)
        except json.JSONDecodeError:
            end = text.rfind("}", start, end)
    return None


def _stage_judge_agent(workspace: Path) -> None:
    """Stage the @eval-judge agent + minimal scaffolding into ``workspace``."""
    import shutil

    src = (
        Path(__file__).resolve().parents[2]
        / "agent-packs"
        / "eval-framework"
        / ".github"
        / "agents"
    )
    dest = workspace / ".github" / "agents"
    dest.mkdir(parents=True, exist_ok=True)
    for agent_file in src.glob("*.agent.md"):
        shutil.copy2(agent_file, dest / agent_file.name)

"""LLM-as-judge helper (repo-agnostic).

Scores a single SUT artifact against free-form criteria by invoking the
bundled ``eval-judge`` agent through the configured
:class:`~evalpilot.runners.base.SUTRunner`. Returns a :class:`Verdict` with
a ``passed`` boolean, a numeric ``score`` in ``[0.0, 1.0]``, and the judge's
reasoning + cited evidence.

The judge agent ships as package data
(``evalpilot/_data/agents/eval-judge.agent.md``) and is staged into a
throwaway workspace for each call, so this works in any repository without
older repository-specific layouts.
"""

from __future__ import annotations

import dataclasses
import json
import os
import re
import shutil
import tempfile
from pathlib import Path
from typing import Optional, Sequence

from .config import find_judge_agent_file
from .runners.base import get_runner


DEFAULT_THRESHOLD = 0.7


@dataclasses.dataclass(frozen=True)
class Verdict:
    """Structured judge response."""

    passed: bool
    score: float
    reasoning: str
    evidence: list[dict]
    raw_response: str

    def __bool__(self) -> bool:
        return self.passed


class JudgeError(RuntimeError):
    """Raised when the judge subprocess fails or returns unparsable output."""


def judge(
    *,
    artifact: str,
    criteria: str,
    threshold: Optional[float] = None,
    golden: Sequence[str] = (),
    log_dir: Optional[Path] = None,
    timeout: float = 180.0,
) -> Verdict:
    """Score ``artifact`` against ``criteria`` using the eval-judge agent."""
    threshold = (
        threshold
        if threshold is not None
        else float(
            os.environ.get("EVALPILOT_JUDGE_THRESHOLD")
            or os.environ.get("EVAL_JUDGE_THRESHOLD", DEFAULT_THRESHOLD)
        )
    )
    log_dir = log_dir or Path(tempfile.mkdtemp(prefix="evalpilot-judge-"))
    log_dir.mkdir(parents=True, exist_ok=True)

    prompt = _build_prompt(artifact=artifact, criteria=criteria, golden=list(golden))
    (log_dir / "judge-prompt.md").write_text(prompt, encoding="utf-8")

    workspace = log_dir / "_judge_ws"
    workspace.mkdir(exist_ok=True)
    _stage_judge_agent(workspace)

    runner = get_runner()
    result = runner.run_agent(
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
        criteria=criteria.strip(), artifact=artifact, golden_block=golden_block
    )


def _extract_json(text: str) -> Optional[dict]:
    """Find the first balanced JSON object in ``text``."""
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
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
    """Stage the bundled eval-judge agent into ``workspace/.github/agents``."""
    agent_file = find_judge_agent_file()
    if agent_file is None:
        raise JudgeError(
            "Bundled eval-judge agent not found. Set EVALPILOT_JUDGE_AGENT "
            "to its path or reinstall evalpilot."
        )
    dest = workspace / ".github" / "agents"
    dest.mkdir(parents=True, exist_ok=True)
    shutil.copy2(agent_file, dest / agent_file.name)


__all__ = ["Verdict", "JudgeError", "judge", "DEFAULT_THRESHOLD"]

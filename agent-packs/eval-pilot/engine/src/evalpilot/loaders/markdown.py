"""Parse a Markdown ``*.eval.md`` file into an :class:`~evalpilot.spec.EvalSpec`.

The Markdown surface is the default because most of an eval *is* prose —
prompts and judge criteria read naturally as text — while the few structured
knobs (staging, file assertions, metrics) live in small fenced ``yaml``
blocks. A spec reads top-to-bottom as arrange → act → assert.

File shape::

    ---
    name: my-eval
    target: my-agent
    kind: agent            # agent | skill | none
    tags: [smoke, judge]
    timeout: 900
    ---

    # Human title
    > One-line summary (compact view).

    ## Description
    Multi-paragraph, human-readable explanation of what this eval checks and
    why. Shown in detailed output and used as the authoring intent when a
    user writes the description first and asks an agent to implement the rest.

    ## Setup
    ```yaml
    stage: { agent: my-agent }
    files: [{ copy: "fixtures/**", dest: "." }]
    ```

    ## Act
    ```prompt
    ...the prompt sent to the SUT...
    ```

    ## Assert
    ```yaml
    files: { exists: [out.md], absent: ["**/SECRET"] }
    contains: [{ path: out.md, text: "Status: draft" }]
    judge:   { artifact: out.md, threshold: 0.7, criteria: "..." }
    metrics: [{ name: judge_score, value: $judge.score,
                direction: higher_is_better, baseline: rolling_mean,
                tolerance: 0.1 }]
    ```

Any ``## Assert`` list key maps to an assertion kind; ``asserts:`` is the
generic escape hatch (``{kind: ..., ...}``).
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

import yaml

from ..spec import (
    ActSpec,
    AssertionSpec,
    EvalSpec,
    FileCopy,
    JudgeSpec,
    MetricSpec,
    SetupSpec,
    StageSpec,
)

_FRONTMATTER = re.compile(r"^\ufeff?---\s*\n(.*?)\n---\s*\n", re.DOTALL)
_FENCE = re.compile(r"```([^\n`]*)\n(.*?)```", re.DOTALL)
_HEADING = re.compile(r"^(#{1,6})\s+(.*)$", re.MULTILINE)

# Assert-block list keys that map directly onto an assertion kind.
_LIST_KINDS = {
    "contains", "not_contains", "prose_contains", "stdout_contains",
    "matches", "glob_count", "json_path", "json_empty",
    "section_contains", "section_not_contains", "file_exists", "file_absent",
}


class EvalParseError(ValueError):
    """Raised when a ``*.eval.md`` file cannot be parsed into a spec."""


def load_markdown_eval(path: Path) -> EvalSpec:
    """Load and parse a ``*.eval.md`` file from disk."""
    path = Path(path)
    text = path.read_text(encoding="utf-8")
    spec = parse_markdown_eval(text, spec_path=path)
    spec.base_dir = path.parent
    return spec


def parse_markdown_eval(text: str, *, spec_path: Optional[Path] = None) -> EvalSpec:
    """Parse ``*.eval.md`` source text into an :class:`EvalSpec`."""
    front, body = _split_frontmatter(text)
    title, blockquote, sections = _split_sections(body)

    name = front.get("name") or _slug(title) or "unnamed-eval"
    kind = str(front.get("kind", "none")).lower()
    summary = str(front.get("summary") or blockquote or "").strip()
    desc_section = sections.get("description")
    description = ""
    if desc_section is not None:
        description = desc_section.prose().strip()
    if not description:
        description = str(front.get("description") or "").strip()
    setup = _parse_setup(sections.get("setup"))
    act = _parse_act(sections.get("act"), front)
    assertions, judges, metrics = _parse_assert(sections.get("assert"))

    spec = EvalSpec(
        name=name,
        target=front.get("target"),
        kind=kind,
        tags=_as_list(front.get("tags")),
        timeout=float(front.get("timeout", 600)),
        summary=summary,
        description=description or summary,
        setup=setup,
        act=act,
        assertions=assertions,
        judges=judges,
        metrics=metrics,
        spec_path=str(spec_path) if spec_path else None,
        base_dir=spec_path.parent if spec_path else None,
    )
    return spec


# ---- structural parsing -------------------------------------------------


def _split_frontmatter(text: str) -> tuple[dict, str]:
    m = _FRONTMATTER.match(text)
    if not m:
        return {}, text
    try:
        data = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError as exc:
        raise EvalParseError(f"invalid frontmatter YAML: {exc}") from exc
    if not isinstance(data, dict):
        raise EvalParseError("frontmatter must be a YAML mapping")
    return data, text[m.end():]


class _Section:
    def __init__(self, raw: str) -> None:
        self.raw = raw
        self.blocks: list[tuple[str, str]] = [
            (lang.strip().lower(), content)
            for lang, content in _FENCE.findall(raw)
        ]

    def block(self, lang: str) -> Optional[str]:
        for blang, content in self.blocks:
            if blang == lang:
                return content
        return None

    def prose(self) -> str:
        """Section text with fenced blocks and blockquotes stripped."""
        stripped = _FENCE.sub("", self.raw)
        lines = [ln for ln in stripped.splitlines() if not ln.strip().startswith(">")]
        return "\n".join(lines).strip()


def _split_sections(body: str) -> tuple[str, str, dict[str, _Section]]:
    """Return (title, summary, {section_name_lower: _Section}).

    The second value is the one-line ``> blockquote`` summary that lives under
    the ``# Title`` (above the first ``## Section``).
    """
    title = ""
    summary = ""
    sections: dict[str, _Section] = {}

    # Blank out fenced regions so headings *inside* code don't split sections.
    masked = _mask_fences(body)

    matches = list(_HEADING.finditer(masked))
    first_start = matches[0].start() if matches else len(body)
    preamble = body[:first_start]

    for h in matches:
        level = len(h.group(1))
        heading_text = h.group(2).strip()
        if level == 1 and not title:
            title = heading_text
    if not title:
        m = re.search(r"^#\s+(.*)$", preamble, re.MULTILINE)
        if m:
            title = m.group(1).strip()

    # Collect level-2 sections (## Setup / ## Act / ## Assert ...).
    h2 = [h for h in matches if len(h.group(1)) == 2]
    for i, h in enumerate(h2):
        start = h.end()
        end = h2[i + 1].start() if i + 1 < len(h2) else len(body)
        name = h.group(2).strip().lower()
        sections[name] = _Section(body[start:end])

    # The `> summary` blockquote lives above the first ## section (usually
    # right under the # Title). Scan that whole header region.
    header_end = h2[0].start() if h2 else len(body)
    qm = re.search(r"^>\s?(.*)$", body[:header_end], re.MULTILINE)
    if qm:
        summary = qm.group(1).strip()

    return title, summary, sections


def _mask_fences(text: str) -> str:
    """Blank fenced regions while preserving length + newline positions.

    Heading detection runs on the masked text so ``#`` lines *inside* code
    fences don't split sections; offsets must stay aligned with the original
    body, so each fence is replaced char-for-char (newlines kept, others → space).
    """

    def _blank(m: "re.Match") -> str:
        return "".join("\n" if ch == "\n" else " " for ch in m.group(0))

    return _FENCE.sub(_blank, text)


# ---- section builders ---------------------------------------------------


def _parse_setup(section: Optional[_Section]) -> SetupSpec:
    if section is None:
        return SetupSpec()
    raw = section.block("yaml") or section.block("json")
    data = _yaml(raw) if raw else {}
    if data is None:
        data = {}
    if not isinstance(data, dict):
        raise EvalParseError("## Setup yaml block must be a mapping")
    stage_data = data.get("stage") or {}
    stage = StageSpec(
        agent=stage_data.get("agent"),
        skill=stage_data.get("skill"),
        all=bool(stage_data.get("all", False)),
        include_skills=bool(stage_data.get("include_skills", True)),
    )
    files = []
    for f in data.get("files", []) or []:
        if isinstance(f, str):
            files.append(FileCopy(copy=f))
        elif isinstance(f, dict):
            files.append(FileCopy(copy=str(f["copy"]), dest=str(f.get("dest", "."))))
    return SetupSpec(stage=stage, files=files)


def _parse_act(section: Optional[_Section], front: dict) -> Optional[ActSpec]:
    prompt = None
    agent = front.get("agent")
    skill = front.get("skill")
    timeout = front.get("timeout")
    if section is not None:
        prompt = section.block("prompt")
        if prompt is None:
            # A yaml block may carry {prompt, agent, skill, timeout}.
            raw = section.block("yaml")
            if raw:
                data = _yaml(raw) or {}
                prompt = data.get("prompt")
                agent = data.get("agent", agent)
                skill = data.get("skill", skill)
                timeout = data.get("timeout", timeout)
        if prompt is None:
            prompt = section.prose()
    if not prompt:
        return None
    return ActSpec(
        prompt=prompt.rstrip("\n") + "\n" if not prompt.endswith("\n") else prompt,
        agent=agent,
        skill=skill,
        timeout=float(timeout) if timeout is not None else None,
    )


def _parse_assert(
    section: Optional[_Section],
) -> tuple[list[AssertionSpec], list[JudgeSpec], list[MetricSpec]]:
    assertions: list[AssertionSpec] = []
    judges: list[JudgeSpec] = []
    metrics: list[MetricSpec] = []
    if section is None:
        return assertions, judges, metrics

    raw = section.block("yaml") or section.block("json")
    data = _yaml(raw) if raw else {}
    if data and not isinstance(data, dict):
        raise EvalParseError("## Assert yaml block must be a mapping")
    data = data or {}

    # files: {exists: [...], absent: [...]}
    files = data.get("files") or {}
    if files.get("exists"):
        assertions.append(AssertionSpec(kind="file_exists",
                                        args={"paths": _as_list(files["exists"])}))
    if files.get("absent"):
        assertions.append(AssertionSpec(kind="file_absent",
                                        args={"paths": _as_list(files["absent"])}))

    # direct list kinds
    for kind in _LIST_KINDS:
        for entry in data.get(kind, []) or []:
            assertions.append(_assertion_from_entry(kind, entry))

    # generic escape hatch
    for entry in data.get("asserts", []) or []:
        if not isinstance(entry, dict) or "kind" not in entry:
            raise EvalParseError("each 'asserts' entry needs a 'kind'")
        e = dict(entry)
        kind = e.pop("kind")
        name = e.pop("name", None)
        assertions.append(AssertionSpec(kind=kind, args=e, name=name))

    # judges (single mapping or list)
    judge_block = data.get("judge")
    if judge_block is not None:
        entries = judge_block if isinstance(judge_block, list) else [judge_block]
        for e in entries:
            judges.append(_judge_from_entry(e))
    # standalone ```judge fenced block => criteria only
    jc = section.block("judge")
    if jc:
        judges.append(JudgeSpec(criteria=jc.strip()))

    for e in data.get("metrics", []) or []:
        metrics.append(_metric_from_entry(e))

    return assertions, judges, metrics


def _assertion_from_entry(kind: str, entry) -> AssertionSpec:
    if isinstance(entry, str):
        return AssertionSpec(kind=kind, args={"text": entry})
    if isinstance(entry, dict):
        e = dict(entry)
        name = e.pop("name", None)
        return AssertionSpec(kind=kind, args=e, name=name)
    raise EvalParseError(f"invalid {kind} entry: {entry!r}")


def _judge_from_entry(e: dict) -> JudgeSpec:
    if not isinstance(e, dict) or "criteria" not in e:
        raise EvalParseError("each judge needs 'criteria'")
    return JudgeSpec(
        criteria=str(e["criteria"]),
        artifact=e.get("artifact"),
        threshold=float(e.get("threshold", 0.7)),
        name=str(e.get("name", "judge")),
        golden=_as_list(e.get("golden")),
    )


def _metric_from_entry(e: dict) -> MetricSpec:
    if not isinstance(e, dict) or "name" not in e:
        raise EvalParseError("each metric needs 'name'")
    baseline = e.get("baseline", "last")
    baseline_value = e.get("baseline_value")
    strategy = str(baseline) if isinstance(baseline, str) else "pinned"
    if isinstance(baseline, (int, float)):
        baseline_value = float(baseline)
    return MetricSpec(
        name=str(e["name"]),
        value=e.get("value"),
        direction=str(e.get("direction", "higher_is_better")),
        unit=str(e.get("unit", "")),
        baseline_strategy=strategy,
        baseline=baseline_value,
        window=int(e.get("window", 5)),
        tolerance=float(e.get("tolerance", 0.0)),
        tolerance_pct=float(e.get("tolerance_pct", 0.0)),
        gate=bool(e.get("gate", False)),
    )


# ---- small utilities ----------------------------------------------------


def _yaml(raw: str):
    try:
        return yaml.safe_load(raw)
    except yaml.YAMLError as exc:
        raise EvalParseError(f"invalid YAML block: {exc}") from exc


def _as_list(value) -> list:
    if value is None:
        return []
    if isinstance(value, (list, tuple)):
        return list(value)
    return [value]


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


__all__ = ["load_markdown_eval", "parse_markdown_eval", "EvalParseError"]

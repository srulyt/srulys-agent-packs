"""The :class:`EvalSpec` — the compiled, engine-neutral description of one eval.

Both authoring surfaces (the Markdown ``*.eval.md`` loader and the fluent
Python builder) produce an :class:`EvalSpec`. The :mod:`evalpilot.executor`
consumes it. Nothing here executes anything; this module is pure data plus a
little validation, so a spec can be inspected, printed, or lint-checked
without a live SUT.

Structure mirrors arrange → act → assert:

* :class:`SetupSpec`   — what to stage into the workspace (arrange).
* :class:`ActSpec`     — the prompt to drive the SUT with (act).
* :class:`AssertionSpec` / :class:`JudgeSpec` / :class:`MetricSpec` — checks
  and recorded numbers (assert).
"""

from __future__ import annotations

import dataclasses
from pathlib import Path
from typing import Any, Callable, Optional

AGENT = "agent"
SKILL = "skill"
NONE = "none"


@dataclasses.dataclass
class StageSpec:
    """What agents/skills to copy into the eval workspace."""

    agent: Optional[str] = None
    skill: Optional[str] = None
    all: bool = False
    include_skills: bool = True


@dataclasses.dataclass
class FileCopy:
    """Copy fixture files into the workspace before the SUT runs."""

    copy: str            # source path/glob, relative to the spec's base_dir
    dest: str = "."      # destination subdir inside the workspace


@dataclasses.dataclass
class SetupSpec:
    """Arrange step: staging + fixture files."""

    stage: StageSpec = dataclasses.field(default_factory=StageSpec)
    files: list = dataclasses.field(default_factory=list)  # list[FileCopy]


@dataclasses.dataclass
class ActSpec:
    """Act step: drive the SUT with a prompt."""

    prompt: str
    agent: Optional[str] = None   # explicit agent override
    skill: Optional[str] = None   # run in skill-isolation mode
    timeout: Optional[float] = None


@dataclasses.dataclass
class AssertionSpec:
    """One assertion. ``kind`` selects a registered checker; ``args`` are its
    parameters. ``predicate`` carries a Python callable for ``kind='custom'``.
    """

    kind: str
    args: dict = dataclasses.field(default_factory=dict)
    name: Optional[str] = None
    predicate: Optional[Callable] = None


@dataclasses.dataclass
class JudgeSpec:
    """An LLM-as-judge assertion over an artifact (or stdout)."""

    criteria: str
    artifact: Optional[str] = None      # file glob; None => use stdout
    threshold: float = 0.7
    name: str = "judge"
    golden: list = dataclasses.field(default_factory=list)


@dataclasses.dataclass
class MetricSpec:
    """A numeric metric recorded to JSONL history and (optionally) gated.

    ``value`` may be a number, a callable (builder only), or a ``$``-reference
    string resolved by the executor: ``$judge.score``, ``$judge.<name>.score``,
    ``$duration``, ``$stdout.words``, ``$stdout.chars``, ``$assertions.pass_rate``.
    """

    name: str
    value: Any
    direction: str = "higher_is_better"
    unit: str = ""
    baseline_strategy: str = "last"
    baseline: Optional[float] = None
    window: int = 5
    tolerance: float = 0.0
    tolerance_pct: float = 0.0
    gate: bool = False


@dataclasses.dataclass
class EvalSpec:
    """The full compiled description of one eval."""

    name: str
    target: Optional[str] = None
    kind: str = NONE
    tags: list = dataclasses.field(default_factory=list)
    timeout: float = 600.0
    summary: str = ""
    description: str = ""
    setup: SetupSpec = dataclasses.field(default_factory=SetupSpec)
    act: Optional[ActSpec] = None
    assertions: list = dataclasses.field(default_factory=list)  # AssertionSpec
    judges: list = dataclasses.field(default_factory=list)       # JudgeSpec
    metrics: list = dataclasses.field(default_factory=list)      # MetricSpec
    spec_path: Optional[str] = None
    base_dir: Optional[Path] = None

    def __post_init__(self) -> None:
        if self.kind not in (AGENT, SKILL, NONE):
            raise ValueError(
                f"eval {self.name!r}: kind must be 'agent', 'skill', or 'none', "
                f"got {self.kind!r}"
            )
        # Infer the staged target when the setup doesn't say otherwise.
        if self.target and self.kind == AGENT and not self.setup.stage.agent \
                and not self.setup.stage.all:
            self.setup.stage.agent = self.target
        if self.target and self.kind == SKILL and not self.setup.stage.skill \
                and not self.setup.stage.all:
            self.setup.stage.skill = self.target

    def has_prose(self) -> bool:
        """True when the eval carries human-readable intent (summary/description)."""
        return bool(self.summary.strip() or self.description.strip())

    def is_implemented(self) -> bool:
        """True when the eval has an act prompt and at least one check."""
        act_ok = self.act is not None and bool(self.act.prompt.strip())
        checks_ok = bool(self.assertions or self.judges or self.metrics)
        return act_ok and checks_ok

    def is_stub(self) -> bool:
        """A description-first draft: has prose but isn't implemented yet.

        Enables the "write the description, then ask an agent to implement"
        workflow — such files are reported as stubs by ``evalpilot lint``
        rather than as hard errors.
        """
        return self.has_prose() and not self.is_implemented()

    def validate(self) -> list[str]:
        """Return a list of human-readable problems (empty when the spec is ok)."""
        problems: list[str] = []
        if not self.name:
            problems.append("missing 'name'")
        if self.act is None:
            problems.append("missing an '## Act' prompt")
        elif not self.act.prompt.strip():
            problems.append("act prompt is empty")
        if self.kind == AGENT and not (
            self.setup.stage.agent or self.setup.stage.all
        ):
            problems.append("kind=agent but no agent is staged (set 'target')")
        if self.kind == SKILL and not (
            self.setup.stage.skill or self.setup.stage.all
        ):
            problems.append("kind=skill but no skill is staged (set 'target')")
        if not (self.assertions or self.judges or self.metrics):
            problems.append("no assertions, judges, or metrics — nothing to check")
        for m in self.metrics:
            if not m.name:
                problems.append("a metric is missing 'name'")
        return problems


__all__ = [
    "AGENT",
    "SKILL",
    "NONE",
    "StageSpec",
    "FileCopy",
    "SetupSpec",
    "ActSpec",
    "AssertionSpec",
    "JudgeSpec",
    "MetricSpec",
    "EvalSpec",
]

"""Fluent Python builder for evals — the power-user / escape-hatch surface.

Mirrors the Markdown DSL one-to-one but stays in Python, so authors who need
loops, computed prompts, shared fixtures, or arbitrary predicate assertions
never hit a DSL wall::

    from evalpilot import Eval

    spec = (
        Eval("migration-plan", target="my-agent", kind="agent",
             tags=["smoke", "judge"], timeout=600)
        .describe("Produces an ordered migration plan that names tests.")
        .prompt("Create a migration plan for argparse -> Typer.")
        .expect_file("plan.md")
        .expect_contains("test", path="plan.md")
        .judge("Score 1.0 only if it lists ordered steps and names tests.",
               artifact="plan.md", threshold=0.7)
        .metric("judge_score", "$judge.score", direction="higher_is_better",
                baseline="rolling_mean", tolerance=0.1)
        .check("plan is short", lambda ctx: len(ctx.read("plan.md") or "") < 8000)
        .build()
    )

Every method returns ``self`` for chaining; :meth:`build` returns the
validated :class:`~evalpilot.spec.EvalSpec` the executor consumes.
"""

from __future__ import annotations

from typing import Callable, Optional, Union

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

_UNSET = object()


class Eval:
    """Chainable builder that compiles to an :class:`EvalSpec`."""

    def __init__(
        self,
        name: str,
        *,
        target: Optional[str] = None,
        kind: str = "none",
        tags=(),
        timeout: float = 600.0,
        summary: str = "",
        description: str = "",
    ) -> None:
        self._name = name
        self._target = target
        self._kind = kind
        self._tags = list(tags)
        self._timeout = float(timeout)
        self._summary = summary
        self._description = description
        self._stage = StageSpec()
        self._files: list[FileCopy] = []
        self._act: Optional[ActSpec] = None
        self._assertions: list[AssertionSpec] = []
        self._judges: list[JudgeSpec] = []
        self._metrics: list[MetricSpec] = []

    # ---- metadata / arrange --------------------------------------------

    def summarize(self, text: str) -> "Eval":
        """Set the one-line summary shown in compact listings."""
        self._summary = text
        return self

    def describe(self, text: str) -> "Eval":
        """Set the multi-paragraph human-readable description."""
        self._description = text
        return self

    def tag(self, *tags: str) -> "Eval":
        self._tags.extend(tags)
        return self

    def stage_agent(self, name: str, *, include_skills: bool = True) -> "Eval":
        self._stage.agent = name
        self._stage.include_skills = include_skills
        return self

    def stage_skill(self, name: str) -> "Eval":
        self._stage.skill = name
        return self

    def stage_all(self) -> "Eval":
        self._stage.all = True
        return self

    def copy(self, src: str, dest: str = ".") -> "Eval":
        self._files.append(FileCopy(copy=src, dest=dest))
        return self

    # ---- act ------------------------------------------------------------

    def prompt(
        self,
        text: str,
        *,
        agent: Optional[str] = None,
        skill: Optional[str] = None,
        timeout: Optional[float] = None,
    ) -> "Eval":
        self._act = ActSpec(prompt=text, agent=agent, skill=skill, timeout=timeout)
        return self

    # ---- assert ---------------------------------------------------------

    def expect_file(self, *paths: str) -> "Eval":
        self._assertions.append(
            AssertionSpec(kind="file_exists", args={"paths": list(paths)})
        )
        return self

    def expect_absent(self, *paths: str) -> "Eval":
        self._assertions.append(
            AssertionSpec(kind="file_absent", args={"paths": list(paths)})
        )
        return self

    def expect_contains(
        self, text: Union[str, list], *, path: Optional[str] = None,
        ignore_case: bool = False, name: Optional[str] = None,
    ) -> "Eval":
        return self._text_assert("contains", text, path, name, ignore_case)

    def expect_not_contains(
        self, text: Union[str, list], *, path: Optional[str] = None,
        name: Optional[str] = None,
    ) -> "Eval":
        return self._text_assert("not_contains", text, path, name, False)

    def expect_prose(
        self, text: Union[str, list], *, path: Optional[str] = None,
        name: Optional[str] = None,
    ) -> "Eval":
        return self._text_assert("prose_contains", text, path, name, False)

    def expect_stdout(
        self, text: Union[str, list], *, ignore_case: bool = False,
        name: Optional[str] = None,
    ) -> "Eval":
        return self._text_assert("stdout_contains", text, None, name, ignore_case)

    def expect_matches(
        self, pattern: str, *, path: Optional[str] = None, flags: str = "",
        name: Optional[str] = None,
    ) -> "Eval":
        args = {"pattern": pattern, "flags": flags}
        if path:
            args["path"] = path
        self._assertions.append(AssertionSpec(kind="matches", args=args, name=name))
        return self

    def expect_glob_count(
        self, pattern: str, *, min=None, max=None, equals=None,
        name: Optional[str] = None,
    ) -> "Eval":
        args: dict = {"pattern": pattern}
        if min is not None:
            args["min"] = min
        if max is not None:
            args["max"] = max
        if equals is not None:
            args["equals"] = equals
        self._assertions.append(AssertionSpec(kind="glob_count", args=args, name=name))
        return self

    def expect_json(
        self, path: str, query: str, *, equals=_UNSET, exists=_UNSET,
        name: Optional[str] = None,
    ) -> "Eval":
        args: dict = {"path": path, "query": query}
        if equals is not _UNSET:
            args["equals"] = equals
        if exists is not _UNSET:
            args["exists"] = exists
        self._assertions.append(AssertionSpec(kind="json_path", args=args, name=name))
        return self

    def expect(self, kind: str, *, name: Optional[str] = None, **args) -> "Eval":
        """Generic escape hatch for any registered assertion kind."""
        self._assertions.append(AssertionSpec(kind=kind, args=args, name=name))
        return self

    def check(self, name: str, predicate: Callable) -> "Eval":
        """Register a custom Python predicate ``predicate(ctx) -> bool | (bool, str)``."""
        self._assertions.append(
            AssertionSpec(kind="custom", name=name, predicate=predicate)
        )
        return self

    def judge(
        self,
        criteria: str,
        *,
        artifact: Optional[str] = None,
        threshold: float = 0.7,
        name: str = "judge",
        golden=(),
    ) -> "Eval":
        self._judges.append(
            JudgeSpec(criteria=criteria, artifact=artifact, threshold=threshold,
                      name=name, golden=list(golden))
        )
        return self

    def metric(
        self,
        name: str,
        value,
        *,
        direction: str = "higher_is_better",
        unit: str = "",
        baseline: Union[str, float] = "last",
        baseline_value: Optional[float] = None,
        window: int = 5,
        tolerance: float = 0.0,
        tolerance_pct: float = 0.0,
        gate: bool = False,
    ) -> "Eval":
        if isinstance(baseline, (int, float)):
            strategy, baseline_value = "pinned", float(baseline)
        else:
            strategy = baseline
        self._metrics.append(
            MetricSpec(
                name=name, value=value, direction=direction, unit=unit,
                baseline_strategy=strategy, baseline=baseline_value,
                window=window, tolerance=tolerance, tolerance_pct=tolerance_pct,
                gate=gate,
            )
        )
        return self

    # ---- compile --------------------------------------------------------

    def _text_assert(self, kind, text, path, name, ignore_case) -> "Eval":
        args: dict = {}
        if isinstance(text, (list, tuple)):
            args["all"] = list(text)
        else:
            args["text"] = text
        if path:
            args["path"] = path
        if ignore_case:
            args["ignore_case"] = True
        self._assertions.append(AssertionSpec(kind=kind, args=args, name=name))
        return self

    def build(self) -> EvalSpec:
        spec = EvalSpec(
            name=self._name,
            target=self._target,
            kind=self._kind,
            tags=self._tags,
            timeout=self._timeout,
            summary=self._summary,
            description=self._description or self._summary,
            setup=SetupSpec(stage=self._stage, files=self._files),
            act=self._act,
            assertions=self._assertions,
            judges=self._judges,
            metrics=self._metrics,
        )
        return spec


__all__ = ["Eval"]

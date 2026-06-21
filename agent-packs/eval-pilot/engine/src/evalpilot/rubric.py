"""Binary (pass/fail) rubric results.

A *rubric* is a set of named pass/fail checks evaluated against a SUT's
output. It is the binary counterpart to :mod:`evalpilot.metrics` (numeric,
tracked over time). Checks can come from structural assertions, judge
verdicts, or any boolean condition.

Typical use in a test::

    from evalpilot import rubric, check_judge

    result = rubric(
        ("architecture.md exists", arch.exists()),
        ("declares two agents", agent_count == 2),
        check_judge("on-topic & well-structured", verdict),
    )
    result.assert_passed(log_path=res.log_path)

A rubric can optionally be recorded to the metric store as a 0/1
``pass_rate`` series so binary outcomes are also trendable over time.
"""

from __future__ import annotations

import dataclasses
from pathlib import Path
from typing import Iterable, Optional, Union


@dataclasses.dataclass(frozen=True)
class Check:
    """A single named pass/fail criterion."""

    name: str
    passed: bool
    detail: str = ""


# A check may be supplied as a Check, or a (name, passed[, detail]) tuple.
CheckLike = Union[Check, tuple]


def _coerce(check: CheckLike) -> Check:
    if isinstance(check, Check):
        return check
    if isinstance(check, tuple):
        if len(check) == 2:
            name, passed = check
            return Check(name=str(name), passed=bool(passed))
        if len(check) == 3:
            name, passed, detail = check
            return Check(name=str(name), passed=bool(passed), detail=str(detail))
    raise TypeError(
        f"Each check must be a Check or a (name, passed[, detail]) tuple; "
        f"got {check!r}"
    )


@dataclasses.dataclass(frozen=True)
class RubricResult:
    """Outcome of evaluating a rubric."""

    checks: list[Check]

    @property
    def passed(self) -> bool:
        return all(c.passed for c in self.checks)

    @property
    def failed(self) -> list[Check]:
        return [c for c in self.checks if not c.passed]

    @property
    def pass_rate(self) -> float:
        if not self.checks:
            return 1.0
        return sum(1 for c in self.checks if c.passed) / len(self.checks)

    def __bool__(self) -> bool:
        return self.passed

    def summary(self) -> str:
        lines = [
            f"[{'PASS' if c.passed else 'FAIL'}] {c.name}"
            + (f" — {c.detail}" if c.detail else "")
            for c in self.checks
        ]
        header = (
            f"Rubric: {sum(1 for c in self.checks if c.passed)}/"
            f"{len(self.checks)} checks passed"
        )
        return "\n".join([header, *lines])

    def assert_passed(self, *, log_path: Optional[Union[str, Path]] = None) -> None:
        """Raise ``AssertionError`` if any check failed (for use in pytest)."""
        if self.passed:
            return
        failed = "\n".join(
            f"  - {c.name}" + (f": {c.detail}" if c.detail else "")
            for c in self.failed
        )
        log_hint = f"\n  log: {log_path}" if log_path else ""
        raise AssertionError(
            f"Rubric failed ({len(self.failed)}/{len(self.checks)} checks "
            f"did not pass):\n{failed}{log_hint}"
        )

    def record_pass_rate(self, *, eval_id: str, name: str = "pass_rate",
                         **kwargs):
        """Record this rubric's pass-rate to the metric store (0..1)."""
        from . import metrics

        return metrics.record_metric(
            name=name,
            value=self.pass_rate,
            eval_id=eval_id,
            direction="higher_is_better",
            unit="ratio",
            **kwargs,
        )


def rubric(*checks: CheckLike) -> RubricResult:
    """Build a :class:`RubricResult` from checks.

    Accepts :class:`Check` instances and/or ``(name, passed[, detail])``
    tuples, in any mix.
    """
    return RubricResult(checks=[_coerce(c) for c in checks])


def check_judge(name: str, verdict, *, detail: Optional[str] = None) -> Check:
    """Turn an LLM judge :class:`~evalpilot.judge.Verdict` into a :class:`Check`."""
    reasoning = getattr(verdict, "reasoning", "")
    score = getattr(verdict, "score", None)
    auto_detail = (
        f"score={score:.2f}: {reasoning}" if score is not None else reasoning
    )
    return Check(
        name=name,
        passed=bool(getattr(verdict, "passed", verdict)),
        detail=detail if detail is not None else auto_detail,
    )


__all__ = ["Check", "RubricResult", "rubric", "check_judge"]

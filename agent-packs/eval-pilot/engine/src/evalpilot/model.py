"""Modeled eval results — the single source of truth every renderer reads.

The executor turns each eval into an :class:`EvalResult` and a whole run into
an :class:`EvalRunReport`. These dataclasses are deliberately plain and
JSON-round-trippable (paths are stored as strings), so the terminal, HTML,
and JSON renderers all consume the *same* structured object rather than
re-deriving outcomes from pytest's report-log.

Status vocabulary (one string per eval):

* ``"passed"``  — ran and every assertion/metric gate passed.
* ``"failed"``  — ran but at least one assertion/metric gate failed.
* ``"skipped"`` — deliberately not run (SUT unavailable, ``skip`` tag, …).
* ``"error"``   — the harness itself blew up (bad spec, exception).
"""

from __future__ import annotations

import dataclasses
from typing import Any, Optional

PASSED = "passed"
FAILED = "failed"
SKIPPED = "skipped"
ERROR = "error"

_TERMINAL_OK = {PASSED, SKIPPED}


@dataclasses.dataclass
class AssertionResult:
    """Outcome of one assertion in an eval's ``## Assert`` block."""

    kind: str
    name: str
    passed: bool
    detail: str = ""
    data: dict = dataclasses.field(default_factory=dict)

    @classmethod
    def from_dict(cls, d: dict) -> "AssertionResult":
        return cls(
            kind=d["kind"],
            name=d["name"],
            passed=bool(d["passed"]),
            detail=d.get("detail", ""),
            data=dict(d.get("data", {})),
        )


@dataclasses.dataclass
class JudgeResult:
    """Outcome of one LLM-as-judge assertion."""

    name: str
    passed: bool
    score: float
    threshold: float
    reasoning: str = ""
    evidence: list = dataclasses.field(default_factory=list)
    log_path: Optional[str] = None

    @classmethod
    def from_dict(cls, d: dict) -> "JudgeResult":
        return cls(
            name=d["name"],
            passed=bool(d["passed"]),
            score=float(d["score"]),
            threshold=float(d["threshold"]),
            reasoning=d.get("reasoning", ""),
            evidence=list(d.get("evidence", [])),
            log_path=d.get("log_path"),
        )


@dataclasses.dataclass
class MetricRecord:
    """A metric recorded during this run, plus its regression verdict.

    A JSON-clean projection of :class:`evalpilot.metrics.MetricResult` (whose
    ``history_path`` is a :class:`~pathlib.Path`).
    """

    name: str
    value: float
    unit: str = ""
    direction: str = "higher_is_better"
    baseline: Optional[float] = None
    baseline_strategy: str = "last"
    delta: Optional[float] = None
    pct_delta: Optional[float] = None
    regressed: bool = False
    gated: bool = False
    history_path: Optional[str] = None

    @classmethod
    def from_metric_result(cls, mr, *, gated: bool = False) -> "MetricRecord":
        return cls(
            name=mr.name,
            value=mr.value,
            unit=mr.unit,
            direction=mr.direction,
            baseline=mr.baseline,
            baseline_strategy=mr.baseline_strategy,
            delta=mr.delta,
            pct_delta=mr.pct_delta,
            regressed=mr.regressed,
            gated=gated,
            history_path=str(mr.history_path),
        )

    @classmethod
    def from_dict(cls, d: dict) -> "MetricRecord":
        return cls(
            name=d["name"],
            value=float(d["value"]),
            unit=d.get("unit", ""),
            direction=d.get("direction", "higher_is_better"),
            baseline=d.get("baseline"),
            baseline_strategy=d.get("baseline_strategy", "last"),
            delta=d.get("delta"),
            pct_delta=d.get("pct_delta"),
            regressed=bool(d.get("regressed", False)),
            gated=bool(d.get("gated", False)),
            history_path=d.get("history_path"),
        )


@dataclasses.dataclass
class EvalResult:
    """The modeled outcome of running one eval spec."""

    name: str
    status: str
    target: Optional[str] = None
    kind: str = "none"
    summary: str = ""
    description: str = ""
    tags: list = dataclasses.field(default_factory=list)
    duration_seconds: float = 0.0
    prompt: Optional[str] = None
    assertions: list = dataclasses.field(default_factory=list)  # AssertionResult
    judges: list = dataclasses.field(default_factory=list)      # JudgeResult
    metrics: list = dataclasses.field(default_factory=list)     # MetricRecord
    log_path: Optional[str] = None
    spec_path: Optional[str] = None
    skip_reason: str = ""
    error: Optional[str] = None
    started_at: str = ""

    # ---- derived views --------------------------------------------------

    @property
    def passed(self) -> bool:
        return self.status == PASSED

    @property
    def ok(self) -> bool:
        """True when the eval did not fail/error (passed or skipped)."""
        return self.status in _TERMINAL_OK

    @property
    def check_total(self) -> int:
        return len(self.assertions) + len(self.judges)

    @property
    def check_passed(self) -> int:
        return sum(1 for a in self.assertions if a.passed) + sum(
            1 for j in self.judges if j.passed
        )

    def failed_labels(self) -> list[str]:
        out = [a.name for a in self.assertions if not a.passed]
        out += [j.name for j in self.judges if not j.passed]
        out += [f"metric:{m.name}" for m in self.metrics if m.gated and m.regressed]
        return out

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "EvalResult":
        return cls(
            name=d["name"],
            status=d["status"],
            target=d.get("target"),
            kind=d.get("kind", "none"),
            summary=d.get("summary", ""),
            description=d.get("description", ""),
            tags=list(d.get("tags", [])),
            duration_seconds=float(d.get("duration_seconds", 0.0)),
            prompt=d.get("prompt"),
            assertions=[AssertionResult.from_dict(a) for a in d.get("assertions", [])],
            judges=[JudgeResult.from_dict(j) for j in d.get("judges", [])],
            metrics=[MetricRecord.from_dict(m) for m in d.get("metrics", [])],
            log_path=d.get("log_path"),
            spec_path=d.get("spec_path"),
            skip_reason=d.get("skip_reason", ""),
            error=d.get("error"),
            started_at=d.get("started_at", ""),
        )


@dataclasses.dataclass
class EvalRunReport:
    """The modeled outcome of a whole ``evalpilot run`` invocation."""

    run_id: str
    started_at: str = ""
    finished_at: str = ""
    duration_seconds: float = 0.0
    results: list = dataclasses.field(default_factory=list)  # EvalResult
    git_sha: Optional[str] = None

    # ---- aggregate counts ----------------------------------------------

    @property
    def total(self) -> int:
        return len(self.results)

    def _count(self, status: str) -> int:
        return sum(1 for r in self.results if r.status == status)

    @property
    def passed(self) -> int:
        return self._count(PASSED)

    @property
    def failed(self) -> int:
        return self._count(FAILED)

    @property
    def skipped(self) -> int:
        return self._count(SKIPPED)

    @property
    def errored(self) -> int:
        return self._count(ERROR)

    @property
    def ok(self) -> bool:
        """True when nothing failed or errored (CI-gate friendly)."""
        return self.failed == 0 and self.errored == 0

    @property
    def regressions(self) -> int:
        return sum(
            1 for r in self.results for m in r.metrics if m.gated and m.regressed
        )

    def to_dict(self) -> dict:
        return {
            "run_id": self.run_id,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "duration_seconds": self.duration_seconds,
            "git_sha": self.git_sha,
            "summary": {
                "total": self.total,
                "passed": self.passed,
                "failed": self.failed,
                "skipped": self.skipped,
                "errored": self.errored,
                "regressions": self.regressions,
            },
            "results": [r.to_dict() for r in self.results],
        }

    @classmethod
    def from_dict(cls, d: dict) -> "EvalRunReport":
        return cls(
            run_id=d["run_id"],
            started_at=d.get("started_at", ""),
            finished_at=d.get("finished_at", ""),
            duration_seconds=float(d.get("duration_seconds", 0.0)),
            git_sha=d.get("git_sha"),
            results=[EvalResult.from_dict(r) for r in d.get("results", [])],
        )


__all__ = [
    "PASSED",
    "FAILED",
    "SKIPPED",
    "ERROR",
    "AssertionResult",
    "JudgeResult",
    "MetricRecord",
    "EvalResult",
    "EvalRunReport",
]

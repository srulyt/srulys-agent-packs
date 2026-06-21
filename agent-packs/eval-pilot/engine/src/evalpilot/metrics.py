"""Numeric metric results with JSONL history and trend/regression compare.

This is the half of the result model that the binary rubric cannot express:
a *number* you want to track across runs (latency, token cost, a judge
score, a coverage percentage, an artifact word count, …). Each recorded
value is appended as one JSON line to a **committed** history file:

    <eval_root>/_metrics/<metric-slug>/history.jsonl

Because the history is plain JSONL committed in the target repo, trends are
git-diffable and portable — no database, no external service.

Recording a metric also **compares it to a baseline** and flags
regressions. The baseline is resolved by strategy:

* ``"last"``        — the most recent prior recorded value (default).
* ``"rolling_mean"``— mean of the last ``window`` prior values.
* ``"best"``        — the best prior value given ``direction``.
* ``"pinned"``      — an explicit ``baseline=`` value you pass in.

``direction`` decides what "worse" means:

* ``"higher_is_better"`` — a *drop* beyond tolerance is a regression.
* ``"lower_is_better"``  — a *rise* beyond tolerance is a regression.
* ``"neutral"``          — never flagged; recorded for information only.

Tolerance is ``tolerance`` (absolute) and/or ``tolerance_pct`` (fraction of
the baseline); a value must be worse than the baseline by more than the
allowed slack to count as a regression.
"""

from __future__ import annotations

import dataclasses
import json
import os
import re
import subprocess
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from .config import find_metrics_root


_DIRECTIONS = {"higher_is_better", "lower_is_better", "neutral"}

# Process-wide run id so every metric recorded in one pytest run shares it.
_RUN_ID: Optional[str] = None


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def run_id() -> str:
    """Return a stable id for the current process/run (or ``EVALPILOT_RUN_ID``)."""
    global _RUN_ID
    if _RUN_ID is None:
        _RUN_ID = os.environ.get("EVALPILOT_RUN_ID") or (
            datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S") + "-" + uuid.uuid4().hex[:8]
        )
    return _RUN_ID


def git_sha(repo: Optional[Path] = None) -> Optional[str]:
    """Return the short git SHA of ``repo`` (cwd by default), or None."""
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=str(repo) if repo else None,
            capture_output=True,
            text=True,
            check=False,
        )
        sha = out.stdout.strip()
        return sha or None
    except (FileNotFoundError, OSError):
        return None


def metric_slug(eval_id: str, name: str) -> str:
    """Stable filesystem slug identifying a metric series."""
    raw = f"{eval_id}__{name}" if eval_id else name
    return re.sub(r"[^A-Za-z0-9._-]+", "_", raw).strip("_")


def history_path(eval_id: str, name: str,
                 metrics_root: Optional[Path] = None) -> Path:
    """Return the JSONL history path for a metric series."""
    root = metrics_root or find_metrics_root()
    return root / metric_slug(eval_id, name) / "history.jsonl"


@dataclasses.dataclass(frozen=True)
class MetricResult:
    """Outcome of recording one metric value, with its regression verdict."""

    eval_id: str
    name: str
    value: float
    unit: str
    direction: str
    baseline: Optional[float]
    baseline_strategy: str
    delta: Optional[float]
    pct_delta: Optional[float]
    regressed: bool
    tolerance: float
    tolerance_pct: float
    run_id: str
    git_sha: Optional[str]
    timestamp: str
    history_path: Path

    def as_record(self) -> dict:
        return {
            "ts": self.timestamp,
            "run_id": self.run_id,
            "git_sha": self.git_sha,
            "eval_id": self.eval_id,
            "name": self.name,
            "value": self.value,
            "unit": self.unit,
            "direction": self.direction,
            "baseline": self.baseline,
            "baseline_strategy": self.baseline_strategy,
            "delta": self.delta,
            "pct_delta": self.pct_delta,
            "regressed": self.regressed,
            "tolerance": self.tolerance,
            "tolerance_pct": self.tolerance_pct,
        }

    def assert_no_regression(self, *, log_path=None) -> None:
        """Raise ``AssertionError`` if this metric regressed (for gating tests)."""
        if not self.regressed:
            return
        log_hint = f"\n  log: {log_path}" if log_path else ""
        raise AssertionError(
            f"Metric {self.name!r} regressed: value={self.value} "
            f"baseline={self.baseline} ({self.baseline_strategy}, "
            f"{self.direction}); delta={self.delta} "
            f"tolerance={self.tolerance} tolerance_pct={self.tolerance_pct}."
            f"{log_hint}"
        )

    def summary(self) -> str:
        base = (
            f"{self.baseline} ({self.baseline_strategy})"
            if self.baseline is not None
            else "(no baseline yet)"
        )
        verdict = "REGRESSED" if self.regressed else "ok"
        return (
            f"metric {self.name}={self.value}{self.unit and ' ' + self.unit} "
            f"vs baseline {base} -> {verdict}"
        )


def load_history(eval_id: str, name: str,
                 metrics_root: Optional[Path] = None) -> list[dict]:
    """Return all prior records for a metric series (oldest first)."""
    path = history_path(eval_id, name, metrics_root)
    if not path.exists():
        return []
    records = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return records


def _resolve_baseline(history: list[dict], *, strategy: str, direction: str,
                      window: int, pinned: Optional[float]) -> Optional[float]:
    values = [r["value"] for r in history if isinstance(r.get("value"), (int, float))]
    if strategy == "pinned":
        return pinned
    if not values:
        return None
    if strategy == "last":
        return float(values[-1])
    if strategy == "rolling_mean":
        window_vals = values[-window:] if window > 0 else values
        return sum(window_vals) / len(window_vals)
    if strategy == "best":
        return max(values) if direction == "higher_is_better" else min(values)
    raise ValueError(f"Unknown baseline strategy: {strategy!r}")


def _is_regression(value: float, baseline: Optional[float], *, direction: str,
                   tolerance: float, tolerance_pct: float) -> bool:
    if baseline is None or direction == "neutral":
        return False
    slack = max(tolerance, abs(baseline) * tolerance_pct)
    if direction == "higher_is_better":
        # worse = lower; regression if value < baseline - slack
        return value < baseline - slack
    if direction == "lower_is_better":
        # worse = higher; regression if value > baseline + slack
        return value > baseline + slack
    return False


def record_metric(
    *,
    name: str,
    value: float,
    eval_id: str = "",
    direction: str = "higher_is_better",
    unit: str = "",
    baseline_strategy: str = "last",
    baseline: Optional[float] = None,
    window: int = 5,
    tolerance: float = 0.0,
    tolerance_pct: float = 0.0,
    metrics_root: Optional[Path] = None,
    repo: Optional[Path] = None,
) -> MetricResult:
    """Record ``value`` for a metric series and compute its regression verdict.

    Appends one JSON line to the series' ``history.jsonl`` and returns a
    :class:`MetricResult`. The comparison baseline is computed from the
    *prior* history (this value is excluded), so the very first recording
    has ``baseline=None`` and ``regressed=False``.
    """
    if direction not in _DIRECTIONS:
        raise ValueError(f"direction must be one of {_DIRECTIONS}, got {direction!r}")
    value = float(value)

    history = load_history(eval_id, name, metrics_root)
    resolved_baseline = _resolve_baseline(
        history, strategy=baseline_strategy, direction=direction,
        window=window, pinned=baseline,
    )
    delta = (value - resolved_baseline) if resolved_baseline is not None else None
    pct_delta = (
        (delta / resolved_baseline)
        if (delta is not None and resolved_baseline not in (None, 0))
        else None
    )
    regressed = _is_regression(
        value, resolved_baseline, direction=direction,
        tolerance=tolerance, tolerance_pct=tolerance_pct,
    )

    result = MetricResult(
        eval_id=eval_id,
        name=name,
        value=value,
        unit=unit,
        direction=direction,
        baseline=resolved_baseline,
        baseline_strategy=baseline_strategy,
        delta=delta,
        pct_delta=pct_delta,
        regressed=regressed,
        tolerance=tolerance,
        tolerance_pct=tolerance_pct,
        run_id=run_id(),
        git_sha=git_sha(repo),
        timestamp=_now_iso(),
        history_path=history_path(eval_id, name, metrics_root),
    )

    result.history_path.parent.mkdir(parents=True, exist_ok=True)
    with result.history_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(result.as_record()) + "\n")
    return result


def summarize(eval_id: str, name: str,
              metrics_root: Optional[Path] = None) -> dict:
    """Return a compact trend summary for a metric series."""
    history = load_history(eval_id, name, metrics_root)
    values = [r["value"] for r in history if isinstance(r.get("value"), (int, float))]
    return {
        "eval_id": eval_id,
        "name": name,
        "count": len(history),
        "first": values[0] if values else None,
        "latest": values[-1] if values else None,
        "min": min(values) if values else None,
        "max": max(values) if values else None,
        "mean": (sum(values) / len(values)) if values else None,
        "regressions": sum(1 for r in history if r.get("regressed")),
        "history_path": str(history_path(eval_id, name, metrics_root)),
    }


def iter_series(metrics_root: Optional[Path] = None):
    """Yield ``(slug, history_path)`` for every metric series on disk."""
    root = metrics_root or find_metrics_root()
    if not root.exists():
        return
    for series_dir in sorted(p for p in root.iterdir() if p.is_dir()):
        hp = series_dir / "history.jsonl"
        if hp.exists():
            yield series_dir.name, hp


__all__ = [
    "MetricResult",
    "record_metric",
    "load_history",
    "summarize",
    "history_path",
    "metric_slug",
    "iter_series",
    "run_id",
    "git_sha",
]

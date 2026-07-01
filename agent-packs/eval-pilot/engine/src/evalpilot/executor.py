"""Standalone executor — runs an :class:`EvalSpec` and produces the result model.

This is the engine's heart and the reason evalpilot no longer needs pytest as
its author-facing runner: :func:`run_eval` performs arrange → act → assert for
one spec and returns an :class:`~evalpilot.model.EvalResult`; :func:`run_specs`
fans a batch out (optionally in parallel) into an
:class:`~evalpilot.model.EvalRunReport`. Everything downstream (terminal /
HTML / JSON renderers, the ``--check`` CI gate) reads that model.

Design notes:

* Reuses the existing pytest-independent primitives — :class:`Workspace`,
  the pluggable :class:`SUTRunner`, :func:`evalpilot.judge.judge`, and
  :func:`evalpilot.metrics.record_metric`.
* Each eval gets its own workspace + logs under ``<run_dir>/<slug>/`` so the
  result location is obvious and triage-friendly.
* When the SUT is unavailable or skipped, the eval is reported ``skipped``
  (never a false failure).
"""

from __future__ import annotations

import re
import time
import traceback
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from . import metrics as metrics_mod
from . import model
from .assertions import AssertContext, run_assertion
from .config import find_eval_root
from .judge import JudgeError, judge as judge_call
from .model import (
    AssertionResult,
    EvalResult,
    EvalRunReport,
    JudgeResult,
    MetricRecord,
)
from .runners.base import SUTRunner, get_runner
from .spec import AGENT, SKILL, EvalSpec
from .workspace import Workspace


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _slug(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "-", text).strip("-") or "eval"


# ---- single eval --------------------------------------------------------


def run_eval(
    spec: EvalSpec,
    *,
    work_root: Optional[Path] = None,
    runner: Optional[SUTRunner] = None,
) -> EvalResult:
    """Execute one spec and return its :class:`EvalResult`."""
    started_at = _now_iso()
    t0 = time.monotonic()
    runner = runner or get_runner()
    work_root = Path(work_root or (find_eval_root() / "_runs" / "scratch"))
    slug = _slug(spec.name)
    ws_root = work_root / slug / "ws"
    logs_dir = work_root / slug / "_logs"

    base = _result_shell(spec, started_at)

    problems = spec.validate()
    if problems:
        base.status = model.ERROR
        base.error = "invalid spec: " + "; ".join(problems)
        base.duration_seconds = time.monotonic() - t0
        return base

    if "skip" in spec.tags:
        base.status = model.SKIPPED
        base.skip_reason = "eval tagged 'skip'"
        base.duration_seconds = time.monotonic() - t0
        return base

    if not runner.available():
        base.status = model.SKIPPED
        base.skip_reason = (
            f"SUT runner {runner.name!r} unavailable (set COPILOT_BIN / PATH, "
            f"or use EVALPILOT_RUNNER=mock)"
        )
        base.duration_seconds = time.monotonic() - t0
        return base

    try:
        ws = Workspace(root=ws_root, logs_dir=logs_dir, runner=runner)
        _arrange(spec, ws)
        result = _act(spec, ws)
        base.log_path = str(result.log_path)

        if not result.usable:
            base.status = model.SKIPPED
            base.skip_reason = result.unavailable_reason()
            base.duration_seconds = time.monotonic() - t0
            return base

        if not result.ok:
            base.status = model.FAILED
            base.error = (
                f"SUT exited {result.returncode}; see {result.log_path}"
            )
            # Still evaluate assertions to give a full picture.
        ctx = AssertContext(root=ws.root, stdout=result.stdout, stderr=result.stderr)
        base.assertions = [run_assertion(a, ctx) for a in spec.assertions]
        base.judges = _run_judges(spec, ctx, logs_dir)
        base.metrics = _record_metrics(spec, base, result)
        base.status = _final_status(base, result)
    except Exception as exc:  # noqa: BLE001 - surface harness errors as ERROR
        base.status = model.ERROR
        base.error = f"{type(exc).__name__}: {exc}\n{traceback.format_exc()}"

    base.duration_seconds = time.monotonic() - t0
    return base


def run_specs(
    specs: list[EvalSpec],
    *,
    work_root: Optional[Path] = None,
    parallel: int = 1,
    runner: Optional[SUTRunner] = None,
) -> EvalRunReport:
    """Execute a batch of specs into an :class:`EvalRunReport`."""
    run_id = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%S")
    work_root = Path(work_root or (find_eval_root() / "_runs" / run_id))
    started_at = _now_iso()
    t0 = time.monotonic()

    def _one(s: EvalSpec) -> EvalResult:
        return run_eval(s, work_root=work_root, runner=runner)

    if parallel and parallel > 1 and len(specs) > 1:
        with ThreadPoolExecutor(max_workers=parallel) as pool:
            results = list(pool.map(_one, specs))
    else:
        results = [_one(s) for s in specs]

    return EvalRunReport(
        run_id=run_id,
        started_at=started_at,
        finished_at=_now_iso(),
        duration_seconds=time.monotonic() - t0,
        results=results,
        git_sha=metrics_mod.git_sha(),
    )


# ---- phases -------------------------------------------------------------


def _result_shell(spec: EvalSpec, started_at: str) -> EvalResult:
    return EvalResult(
        name=spec.name,
        status=model.PASSED,
        target=spec.target,
        kind=spec.kind,
        summary=spec.summary,
        description=spec.description,
        tags=list(spec.tags),
        prompt=spec.act.prompt if spec.act else None,
        spec_path=spec.spec_path,
        started_at=started_at,
    )


def _arrange(spec: EvalSpec, ws: Workspace) -> None:
    stage = spec.setup.stage
    if stage.all:
        ws.stage_all()
    if stage.agent:
        ws.stage_agent(stage.agent, include_skills=stage.include_skills)
    if stage.skill:
        ws.stage_skill(stage.skill)
    base_dir = spec.base_dir
    for fc in spec.setup.files:
        _copy_fixture(base_dir, fc.copy, fc.dest, ws)


def _copy_fixture(base_dir: Optional[Path], pattern: str, dest: str,
                  ws: Workspace) -> None:
    if base_dir is None:
        src = Path(pattern)
        if src.exists():
            ws.stage_files(src, dest)
        return
    matches = sorted(base_dir.glob(pattern))
    if not matches and (base_dir / pattern).exists():
        matches = [base_dir / pattern]
    for m in matches:
        ws.stage_files(m, dest)


def _act(spec: EvalSpec, ws: Workspace):
    act = spec.act
    assert act is not None
    timeout = act.timeout if act.timeout is not None else spec.timeout
    skill = act.skill or (spec.target if spec.kind == SKILL else None)
    if skill:
        return ws.run_skill(skill=skill, prompt=act.prompt, timeout=timeout)
    agent = act.agent or (spec.target if spec.kind == AGENT else None)
    return ws.run_agent(prompt=act.prompt, agent=agent, timeout=timeout)


def _run_judges(spec: EvalSpec, ctx: AssertContext, logs_dir: Path) -> list[JudgeResult]:
    out: list[JudgeResult] = []
    for i, js in enumerate(spec.judges):
        artifact = ctx.read(js.artifact) if js.artifact else ctx.stdout
        if artifact is None:
            out.append(JudgeResult(
                name=js.name, passed=False, score=0.0, threshold=js.threshold,
                reasoning=f"judge artifact not found: {js.artifact}",
            ))
            continue
        try:
            verdict = judge_call(
                artifact=artifact, criteria=js.criteria, threshold=js.threshold,
                golden=js.golden, log_dir=logs_dir / f"judge-{i}-{_slug(js.name)}",
            )
            out.append(JudgeResult(
                name=js.name, passed=verdict.passed, score=verdict.score,
                threshold=js.threshold, reasoning=verdict.reasoning,
                evidence=list(verdict.evidence),
            ))
        except JudgeError as exc:
            out.append(JudgeResult(
                name=js.name, passed=False, score=0.0, threshold=js.threshold,
                reasoning=f"judge error: {exc}",
            ))
    return out


def _record_metrics(spec: EvalSpec, base: EvalResult, result) -> list[MetricRecord]:
    out: list[MetricRecord] = []
    for ms in spec.metrics:
        try:
            value = _resolve_value(ms.value, base, result)
        except (KeyError, ValueError, TypeError) as exc:
            # Record nothing but keep a visible failed marker via assertion.
            base.assertions.append(AssertionResult(
                kind="metric", name=f"metric:{ms.name}", passed=False,
                detail=f"could not resolve value {ms.value!r}: {exc}",
            ))
            continue
        mr = metrics_mod.record_metric(
            name=ms.name, value=value, eval_id=_slug(spec.name),
            direction=ms.direction, unit=ms.unit,
            baseline_strategy=ms.baseline_strategy, baseline=ms.baseline,
            window=ms.window, tolerance=ms.tolerance, tolerance_pct=ms.tolerance_pct,
        )
        out.append(MetricRecord.from_metric_result(mr, gated=ms.gate))
    return out


def _resolve_value(value, base: EvalResult, result) -> float:
    if callable(value):
        return float(value(_MetricContext(base, result)))
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str) and value.startswith("$"):
        return _resolve_ref(value, base, result)
    return float(value)


def _resolve_ref(ref: str, base: EvalResult, result) -> float:
    parts = ref[1:].split(".")
    head = parts[0]
    if head == "judge":
        if len(parts) == 2 and parts[1] == "score":
            return _first_judge_score(base)
        if len(parts) == 3 and parts[2] == "score":
            return _named_judge_score(base, parts[1])
        raise ValueError(f"bad judge ref {ref!r}")
    if head == "duration":
        return float(result.duration_seconds)
    if head == "stdout":
        metric = parts[1] if len(parts) > 1 else "chars"
        text = result.stdout
        return float({
            "words": len(text.split()),
            "chars": len(text),
            "lines": len(text.splitlines()),
        }[metric])
    if head in ("assertions", "checks"):
        total = base.check_total if head == "checks" else len(base.assertions)
        passed = base.check_passed if head == "checks" else sum(
            1 for a in base.assertions if a.passed)
        return (passed / total) if total else 1.0
    raise ValueError(f"unknown metric ref {ref!r}")


def _first_judge_score(base: EvalResult) -> float:
    if not base.judges:
        raise ValueError("$judge.score used but no judge ran")
    return float(base.judges[0].score)


def _named_judge_score(base: EvalResult, name: str) -> float:
    for j in base.judges:
        if j.name == name:
            return float(j.score)
    raise ValueError(f"no judge named {name!r}")


class _MetricContext:
    """Passed to callable metric values in the Python builder."""

    def __init__(self, base: EvalResult, result) -> None:
        self.judges = {j.name: j.score for j in base.judges}
        self.duration = result.duration_seconds
        self.stdout = result.stdout
        self.result = result
        self.assertions = base.assertions


def _final_status(base: EvalResult, result) -> str:
    if not result.ok:
        return model.FAILED
    if any(not a.passed for a in base.assertions):
        return model.FAILED
    if any(not j.passed for j in base.judges):
        return model.FAILED
    if any(m.gated and m.regressed for m in base.metrics):
        return model.FAILED
    return model.PASSED


__all__ = ["run_eval", "run_specs"]

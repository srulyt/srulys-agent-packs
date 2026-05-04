"""Aggregator for ``run-pack`` / ``run-case`` — autonomous execution.

This module wraps the existing ``plan`` → ``drive``/SUT → ``capture-local``
→ ``judge-plan`` → ``run-judge`` → ``score`` pipeline into a single
non-interactive entry point. ``run.py`` dispatches its CLI subparsers
into the public functions defined here.

Design notes:

* All stdout from the CLI subcommands is the pack-summary JSON object
  (and nothing else). Progress text goes to stderr so the
  ``@factory-eval-runner`` agent can parse stdout as JSON.

* Exit codes are 0 (pass) / 1 (one or more cases failed) /
  2 (harness error: missing copilot bin, malformed spec, judge crash,
  budget exceeded).

* The pack-summary is ALWAYS written to ``--out`` even on harness
  errors so the runner can read partial results.

* ``run-pack`` mints a fresh per-case run-id of shape
  ``<n>-<short-hex>`` (F10.4) so re-runs don't collide on the
  ``fixtures/<case>/<session>.json`` filename.
"""

from __future__ import annotations

import datetime as dt
import json
import os
import re
import secrets
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

import yaml

from . import (
    loaders,
    local_extractor,
    models,
    paths_layout,
    report,
    store,
    workspace,
)
from .assertions import ASSERTIONS
from .assertions.base import AssertionContext
from .judge import (
    CopilotBinNotFound,
    JudgeManifest,
    apply_double_invoke,
    build_manifest,
    load_responses,
    run_manifest,
)
from .judge.subprocess_runner import (
    CopilotBinNotFound as JudgeCopilotBinNotFound,
)
from .sut_runner import (
    CopilotBinNotFound as SUTCopilotBinNotFound,
    run_sut_once,
)


@dataclass
class CaseOutcome:
    case_id: str
    run_id: str
    status: str  # pass | fail | error
    verdict: models.CaseVerdict | None = None
    harness_error: str | None = None
    judge_calls: int = 0
    failures: list[dict[str, Any]] = field(default_factory=list)
    fixture_path: str | None = None
    results_path: str | None = None
    report_path: str | None = None


@dataclass
class PackRunOptions:
    pack: str
    evals_root: str
    out_path: str
    cases_subset: list[str] | None = None
    max_judge_calls: int | None = None
    max_wall_clock_seconds: int | None = None
    copilot_bin: str = "copilot"
    judge_seed: str | None = None
    fail_fast: bool = False
    sut_timeout_seconds: float = 1800.0
    judge_timeout_seconds: float = 600.0
    # When set, run-case reuses this fixture and skips SUT execution.
    fixture_path: str | None = None
    # When True, do not invoke the SUT — only run judge+score against
    # the fixture identified by capture-local-style auto-discovery.
    # Reserved for future use.
    skip_sut: bool = False


# --------------------------------------------------------------------- ids


_SHORT_HEX = re.compile(r"^[0-9a-f]+$")


def mint_run_id(seq: int) -> str:
    """``<seq>-<6-hex>`` — unique per attempt, sortable, short."""
    return f"{seq}-{secrets.token_hex(3)}"


def _now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


# --------------------------------------------------------------------- discovery


def discover_cases(
    *,
    evals_root: str,
    pack: str,
    subset: list[str] | None = None,
) -> list[Path]:
    """Return ``case.yaml`` paths under ``evals/packs/<pack>/cases/``.

    Honours ``subset`` (list of case ids) when provided.
    """
    base = paths_layout.cases_dir(evals_root, pack)
    if not base.exists():
        return []
    out: list[Path] = []
    for case_path in sorted(base.iterdir()):
        if not case_path.is_dir():
            continue
        case_yaml = case_path / "case.yaml"
        if not case_yaml.exists():
            continue
        if subset is not None and case_path.name not in subset:
            continue
        out.append(case_yaml)
    return out


# --------------------------------------------------------------------- failures


def _fixable_paths_for_agent(spec: models.PackSpec, agent: str | None) -> list[str]:
    """Translate an assertion's `agent` into write-scope-allow regexes.

    The engineer's fix mode uses these to know which file is allowed
    to be edited to address a failure.
    """
    if not agent:
        return []
    a = spec.agent(agent)
    if a is None:
        return []
    return list(a.write_scope_allow)


def _extract_failures(
    *,
    verdict: models.CaseVerdict,
    spec: models.PackSpec,
    case_id: str,
    spec_path: str,
    case_path: str,
    fixture_path: str | None,
) -> list[dict[str, Any]]:
    """Build the F2 ``failures[]`` list from a verdict."""
    failures: list[dict[str, Any]] = []
    repro_base = (
        f"python -m eval_engine.harness.run replay --spec {spec_path} "
        f"--case {case_path} --run-id {verdict.run_id}"
    )
    if fixture_path:
        repro_base += f" --fixture {fixture_path}"
    for a in verdict.assertions:
        if a.status not in ("fail", "error"):
            continue
        if a.severity not in ("warn", "blocker"):
            continue
        failures.append({
            "kind": "assertion",
            "id": a.assertion_id,
            "severity": a.severity,
            "agent": a.agent,
            "message": a.message,
            "evidence_excerpt": _excerpt_from_evidence(a.evidence),
            "fixable_in": _fixable_paths_for_agent(spec, a.agent),
            "repro_command": repro_base,
        })
    for rv in verdict.rubric_scores.values():
        if rv.status not in ("fail", "error"):
            continue
        failures.append({
            "kind": "rubric",
            "id": rv.rubric_id,
            "apply_to": rv.apply_to,
            "severity": rv.severity,
            "score": rv.score,
            "threshold": rv.threshold,
            "feedback": rv.rationale[:400] if rv.rationale else "",
            "message": rv.message,
            "fixable_in": [],  # rubric failures are content failures; engineer infers target
            "repro_command": repro_base,
        })
    return failures


def _excerpt_from_evidence(evidence: list[dict[str, Any]]) -> str:
    """Pick a representative <=400 char excerpt from an assertion's evidence."""
    for e in evidence or []:
        for k in ("excerpt", "snippet", "message", "value"):
            v = e.get(k)
            if isinstance(v, str) and v.strip():
                return v[:400]
    return ""


# --------------------------------------------------------------------- run-case


def run_one_case(
    *,
    spec: models.PackSpec,
    spec_path: str,
    case_path: str,
    case: models.CaseSpec,
    run_id: str,
    options: PackRunOptions,
    repo_root: str,
    log_progress=lambda *a, **k: None,
    judge_calls_remaining: int | None = None,
) -> CaseOutcome:
    """Run a single case end-to-end. See module docstring for flow."""
    eval_root = options.evals_root
    ws_root = str(paths_layout.workspace_dir(
        eval_root, spec.pack, workspace._safe_segment(case.id), run_id,
    ))
    golden_dir = str(paths_layout.golden_staging_dir(eval_root, run_id))

    # Path 1: replay mode — fixture supplied, skip stage + SUT + capture.
    if options.fixture_path:
        try:
            fixture = loaders.load_fixture(options.fixture_path)
        except Exception as exc:
            return CaseOutcome(
                case_id=case.id, run_id=run_id, status="error",
                harness_error=f"fixture load failed: {exc}",
            )
        fixture_path = str(Path(options.fixture_path).resolve())
        # We still need a workspace for assertions / judge artifact resolution.
        if not Path(ws_root).exists():
            try:
                workspace.allocate(
                    eval_root=eval_root, pack=spec.pack,
                    case_id=case.id, run_id=run_id,
                )
            except Exception as exc:
                return CaseOutcome(
                    case_id=case.id, run_id=run_id, status="error",
                    harness_error=f"workspace alloc failed: {exc}",
                )
    else:
        # Stage workspace.
        try:
            ws_root_p, golden_p = workspace.allocate(
                eval_root=eval_root, pack=spec.pack,
                case_id=case.id, run_id=run_id,
            )
            workspace.stage(
                case=case,
                workspace_root=ws_root_p,
                golden_staging_dir=golden_p,
                repo_cache_dir=str(paths_layout.repo_cache_dir(eval_root)),
            )
            ws_root = ws_root_p
            golden_dir = golden_p
        except Exception as exc:
            return CaseOutcome(
                case_id=case.id, run_id=run_id, status="error",
                harness_error=f"workspace stage failed: {exc}",
            )

        # Render the initial prompt.
        prompt_path = Path(case.case_dir) / case.prompt_file
        rendered_prompt = workspace.render_template(
            prompt_path.read_text(encoding="utf-8"),
            {**case.prompt_template_vars,
             "workspace_root": ws_root, "run_id": run_id, "case_dir": case.case_dir},
        )

        # Run SUT — prompt-only path. Cases with scripted_user are NOT
        # supported by run-pack directly; the operator should drive them
        # via the dedicated `drive` subcommand and replay via --fixture.
        if case.scripted_user:
            return CaseOutcome(
                case_id=case.id, run_id=run_id, status="error",
                harness_error=(
                    f"case {case.id} declares scripted_user; run-pack "
                    "supports prompt-only cases. Use `drive` + replay "
                    "for scripted cases."
                ),
            )

        log_progress(f"[{case.id}] running SUT (timeout={options.sut_timeout_seconds}s)")
        try:
            sut_res = run_sut_once(
                prompt=rendered_prompt,
                workspace_root=ws_root,
                pack=spec.pack,
                run_id=run_id,
                copilot_bin=options.copilot_bin,
                timeout_seconds=options.sut_timeout_seconds,
            )
        except SUTCopilotBinNotFound as exc:
            return CaseOutcome(
                case_id=case.id, run_id=run_id, status="error",
                harness_error=f"copilot-bin-not-found: {exc}",
            )
        if sut_res.timed_out:
            return CaseOutcome(
                case_id=case.id, run_id=run_id, status="error",
                harness_error=(
                    f"SUT exceeded sut_timeout_seconds="
                    f"{options.sut_timeout_seconds}; stderr_tail="
                    f"{sut_res.stderr_tail}"
                ),
            )
        if sut_res.exit_code != 0:
            log_progress(
                f"[{case.id}] SUT exited {sut_res.exit_code}; "
                "continuing to capture+score (the run may still be evaluable)"
            )

        # Capture fixture.
        try:
            session = local_extractor.find_session_by_name(run_id)
            if session is None:
                return CaseOutcome(
                    case_id=case.id, run_id=run_id, status="error",
                    harness_error=(
                        f"could not locate Copilot CLI session for run_id={run_id}"
                    ),
                )
            log_path = local_extractor.find_log_for_session(session)
            if log_path is None:
                return CaseOutcome(
                    case_id=case.id, run_id=run_id, status="error",
                    harness_error=f"no process log for session {session.id}",
                )
            cap = local_extractor.build_fixture(
                log_path=log_path,
                pack=spec.pack,
                case_id=case.id,
                workspace_root=ws_root,
                run_id=run_id,
            )
            fx_dest = (
                paths_layout.fixtures_dir(eval_root, spec.pack)
                / case.id
                / f"{run_id}.json"
            )
            local_extractor.write_fixture(cap.fixture, fx_dest)
            fixture_path = str(fx_dest)
            fixture = loaders.load_fixture(fixture_path)
        except Exception as exc:
            return CaseOutcome(
                case_id=case.id, run_id=run_id, status="error",
                harness_error=f"capture-local failed: {exc}",
            )

    # Build judge manifest.
    rubrics_dir = Path(__file__).resolve().parent.parent / "rubrics"
    rubrics: dict[str, models.Rubric] = {}
    for ref in spec.rubrics:
        for ext in (".md", ".yaml"):
            candidate = rubrics_dir / f"{ref.id}{ext}"
            if candidate.exists():
                rubrics[ref.id] = loaders.load_rubric(candidate)
                break
    response_dir = str(paths_layout.judge_responses_dir(eval_root, run_id))
    manifest = build_manifest(
        spec=spec, case=case, fixture=fixture, rubrics=rubrics,
        workspace_root=ws_root, golden_staging_dir=golden_dir,
        response_dir=response_dir, judge_model=spec.models.get("judge"),
        strict_pass=spec.loop_convergence.is_strict,
    )
    # Persist manifest for debuggability.
    try:
        manifest_path = paths_layout.judge_manifest_path(eval_root, run_id)
        manifest.write(str(manifest_path))
    except Exception:
        pass  # debug-only

    # Budget pre-check.
    expected_calls = len(manifest.requests)
    if (
        judge_calls_remaining is not None
        and expected_calls > judge_calls_remaining
    ):
        return CaseOutcome(
            case_id=case.id, run_id=run_id, status="error",
            harness_error=(
                f"budget-exceeded: case requires {expected_calls} judge "
                f"calls but only {judge_calls_remaining} remain in this loop"
            ),
            fixture_path=fixture_path,
        )

    # Run judge.
    log_progress(
        f"[{case.id}] running judge ({expected_calls} requests, "
        f"strict_pass={spec.loop_convergence.is_strict})"
    )
    try:
        run_results = run_manifest(
            manifest,
            copilot_bin=options.copilot_bin,
            timeout_seconds=options.judge_timeout_seconds,
            judge_seed=options.judge_seed,
        )
    except JudgeCopilotBinNotFound as exc:
        return CaseOutcome(
            case_id=case.id, run_id=run_id, status="error",
            harness_error=f"copilot-bin-not-found (judge): {exc}",
            fixture_path=fixture_path, judge_calls=0,
        )
    judge_calls = len(run_results)

    # Score.
    responses = load_responses(manifest)
    rubric_verdicts = apply_double_invoke(
        responses, manifest,
        strict_pass=spec.loop_convergence.is_strict,
    )

    ctx = AssertionContext(
        spec=spec, case=case, fixture=fixture,
        workspace_root=ws_root, golden_staging_dir=golden_dir,
    )
    assertion_results: list[models.AssertionVerdict] = []
    for a in ASSERTIONS:
        assertion_results.extend(a.run(ctx))

    spec_hash = loaders.file_hash(spec_path)
    prompt_p = Path(case.case_dir) / case.prompt_file
    prompt_hash = loaders.file_hash(prompt_p) if prompt_p.exists() else None
    rubric_hashes: dict[str, str] = {}
    for ref in spec.rubrics:
        for ext in (".md", ".yaml"):
            r_path = rubrics_dir / f"{ref.id}{ext}"
            if r_path.exists():
                rubric_hashes[ref.id] = loaders.file_hash(r_path)

    verdict = report.aggregate(
        pack=spec.pack, case_id=case.id, run_id=run_id,
        session_id=fixture.session_id, repo_root=repo_root, fixture=fixture,
        spec=spec, assertions=assertion_results,
        rubric_verdicts=rubric_verdicts,
        judge_model=spec.models.get("judge"),
        prompt_hash=prompt_hash, spec_hash=spec_hash,
        rubric_hashes=rubric_hashes, run_kind="local",
    )

    # Persist as JSONL line + markdown report (matches existing `score` flow).
    results_dir = str(paths_layout.results_local_dir(eval_root, spec.pack))
    try:
        jsonl_path = store.append(verdict, results_dir=results_dir)
    except Exception as exc:
        log_progress(f"[{case.id}] WARNING: failed to append results JSONL: {exc}")
        jsonl_path = None
    try:
        md_path = report.write_report(
            verdict,
            reports_root=str(paths_layout.reports_dir(eval_root, spec.pack)),
        )
    except Exception:
        md_path = None

    failures = _extract_failures(
        verdict=verdict, spec=spec, case_id=case.id,
        spec_path=spec_path, case_path=case_path, fixture_path=fixture_path,
    )

    # Apply strict-pass at the case level: a verdict.status of "pass"
    # alone is not enough — under strict-pass, any warn rubric failure
    # means the case did not pass.
    case_status = verdict.status
    if case_status == "pass" and spec.loop_convergence.is_strict:
        warn_failed = any(
            rv.severity == "warn" and rv.status in ("fail", "error")
            for rv in verdict.rubric_scores.values()
        )
        if warn_failed:
            case_status = "fail"

    return CaseOutcome(
        case_id=case.id, run_id=run_id, status=case_status, verdict=verdict,
        judge_calls=judge_calls, failures=failures,
        fixture_path=fixture_path, results_path=jsonl_path, report_path=md_path,
    )


# --------------------------------------------------------------------- run-pack


def _summary(outcomes: Iterable[CaseOutcome]) -> dict[str, int]:
    s = {"cases_total": 0, "cases_passed": 0, "cases_failed": 0, "cases_errored": 0}
    for o in outcomes:
        s["cases_total"] += 1
        if o.status == "pass":
            s["cases_passed"] += 1
        elif o.status == "error":
            s["cases_errored"] += 1
        else:
            s["cases_failed"] += 1
    return s


def _build_pack_summary(
    *,
    spec: models.PackSpec | None,
    options: PackRunOptions,
    outcomes: list[CaseOutcome],
    started_at: str,
    completed_at: str,
    harness_error: str | None,
    exit_code: int,
    judge_calls_used: int,
    wall_clock_seconds: float,
) -> dict[str, Any]:
    cases_json: list[dict[str, Any]] = []
    for o in outcomes:
        case_record: dict[str, Any] = {
            "case_id": o.case_id,
            "status": o.status,
            "run_id": o.run_id,
            "results_path": o.results_path,
            "report_path": o.report_path,
            "fixture_path": o.fixture_path,
            "judge_calls": o.judge_calls,
            "failures": o.failures,
        }
        if o.harness_error:
            case_record["harness_error"] = o.harness_error
        cases_json.append(case_record)

    spec_models = dict(spec.models) if spec is not None else {}
    summary = {
        "schema_version": "1.0",
        "pack": options.pack,
        "evals_root": options.evals_root,
        "started_at": started_at,
        "completed_at": completed_at,
        "wall_clock_seconds": round(wall_clock_seconds, 3),
        "harness_error": harness_error,
        "exit_code": exit_code,
        "summary": _summary(outcomes),
        "cases": cases_json,
        "models": {
            "resolved": spec_models,
            "sut": spec_models.get(options.pack),
            "judge": spec_models.get("judge"),
        },
        "judge_calls_used": judge_calls_used,
        "resolved_budgets": (
            {
                "max_judge_calls_per_loop": options.max_judge_calls,
                "max_wall_clock_seconds_per_loop": options.max_wall_clock_seconds,
                "max_total_wall_clock_seconds": (
                    spec.budgets.max_total_wall_clock_seconds if spec else None
                ),
                "bail_action": (
                    spec.budgets.bail_action if spec else "surface-partial"
                ),
            }
        ),
        "resolved_convergence": (
            {
                "required_status": (
                    spec.loop_convergence.required_status if spec else "pass"
                ),
                "warn_promotes_to_blocker": (
                    spec.loop_convergence.warn_promotes_to_blocker
                    if spec else False
                ),
                "allow_failing_cases": (
                    spec.loop_convergence.allow_failing_cases if spec else []
                ),
            }
        ),
    }
    return summary


def _resolve_options(options: PackRunOptions, spec: models.PackSpec) -> None:
    """Pin lower-of-flag-and-spec for budget guards (mutates in place)."""
    spec_caps = {
        "max_judge_calls": spec.budgets.max_judge_calls_per_loop,
        "max_wall_clock_seconds": spec.budgets.max_wall_clock_seconds_per_loop,
    }
    for attr, spec_v in spec_caps.items():
        flag_v = getattr(options, attr)
        chosen: int | None
        if flag_v is None and spec_v is None:
            chosen = None
        elif flag_v is None:
            chosen = spec_v
        elif spec_v is None:
            chosen = flag_v
        else:
            chosen = min(flag_v, spec_v)
        setattr(options, attr, chosen)


def _write_summary(out_path: str, summary: dict[str, Any]) -> None:
    p = Path(out_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")


def run_pack(options: PackRunOptions, *, repo_root: str) -> int:
    """Execute the pack and return the process exit code (0/1/2)."""

    started_at = _now_iso()
    t0 = time.monotonic()
    outcomes: list[CaseOutcome] = []
    harness_error: str | None = None
    exit_code = 0
    judge_calls_used = 0
    spec: models.PackSpec | None = None

    def progress(msg: str) -> None:
        sys.stderr.write(msg + "\n")
        sys.stderr.flush()

    def finalise(code: int, err: str | None) -> int:
        completed_at = _now_iso()
        wc = time.monotonic() - t0
        summary = _build_pack_summary(
            spec=spec, options=options, outcomes=outcomes,
            started_at=started_at, completed_at=completed_at,
            harness_error=err, exit_code=code,
            judge_calls_used=judge_calls_used, wall_clock_seconds=wc,
        )
        try:
            _write_summary(options.out_path, summary)
        except Exception as exc:
            progress(f"warning: could not write summary to {options.out_path}: {exc}")
        sys.stdout.write(json.dumps(summary, indent=2, ensure_ascii=False))
        sys.stdout.write("\n")
        sys.stdout.flush()
        return code

    # Load spec.
    spec_path = str(paths_layout.spec_path(options.evals_root, options.pack))
    if not Path(spec_path).exists():
        return finalise(2, f"spec-not-found: {spec_path}")
    try:
        spec = loaders.load_spec(spec_path)
    except Exception as exc:
        return finalise(2, f"spec-invalid: {exc}")

    _resolve_options(options, spec)

    # Discover cases.
    case_yamls = discover_cases(
        evals_root=options.evals_root, pack=options.pack,
        subset=options.cases_subset,
    )
    if not case_yamls:
        if options.cases_subset:
            return finalise(2, f"no cases match subset {options.cases_subset!r}")
        return finalise(2, f"no cases found under evals/packs/{options.pack}/cases/")

    # Run loop.
    for i, case_yaml in enumerate(case_yamls, start=1):
        try:
            case = loaders.load_case(case_yaml)
        except Exception as exc:
            outcomes.append(CaseOutcome(
                case_id=case_yaml.parent.name, run_id="-",
                status="error",
                harness_error=f"case-invalid ({case_yaml}): {exc}",
            ))
            harness_error = "case-invalid"
            if options.fail_fast:
                exit_code = 2
                break
            continue

        # Wall-clock budget check before starting the case.
        elapsed = time.monotonic() - t0
        if (
            options.max_wall_clock_seconds is not None
            and elapsed >= options.max_wall_clock_seconds
        ):
            outcomes.append(CaseOutcome(
                case_id=case.id, run_id="-",
                status="error",
                harness_error=(
                    f"budget-exceeded: wall-clock {elapsed:.0f}s >= "
                    f"max_wall_clock_seconds_per_loop="
                    f"{options.max_wall_clock_seconds}"
                ),
            ))
            harness_error = "budget-exceeded"
            break

        run_id = mint_run_id(i)
        progress(f"[{i}/{len(case_yamls)}] {case.id} (run-id={run_id})")
        judge_remaining: int | None
        if options.max_judge_calls is None:
            judge_remaining = None
        else:
            judge_remaining = max(0, options.max_judge_calls - judge_calls_used)
        outcome = run_one_case(
            spec=spec, spec_path=spec_path, case_path=str(case_yaml),
            case=case, run_id=run_id, options=options,
            repo_root=repo_root, log_progress=progress,
            judge_calls_remaining=judge_remaining,
        )
        outcomes.append(outcome)
        judge_calls_used += outcome.judge_calls

        if outcome.status == "error":
            # Sticky harness_error on the pack summary if any case errored.
            if outcome.harness_error and harness_error is None:
                harness_error = outcome.harness_error
            if options.fail_fast:
                break
        elif outcome.status == "fail" and options.fail_fast:
            break

    # Decide exit code.
    if harness_error is not None:
        # If at least one case errored, exit 2.
        exit_code = 2
    else:
        # Apply allow_failing_cases at this stage.
        if any(
            o.status not in ("pass",)
            and not spec.loop_convergence.is_case_allowed_to_fail(o.case_id)
            for o in outcomes
        ):
            exit_code = 1
        else:
            exit_code = 0

    return finalise(exit_code, harness_error)


# --------------------------------------------------------------------- run-case


def run_case_cli(
    *,
    spec_path: str,
    case_path: str,
    options: PackRunOptions,
    repo_root: str,
    run_id: str | None = None,
) -> int:
    """One-shot run of a single case. Used by the ``run-case`` subcommand."""
    started_at = _now_iso()
    t0 = time.monotonic()
    spec: models.PackSpec | None = None
    outcomes: list[CaseOutcome] = []
    harness_error: str | None = None

    def progress(msg: str) -> None:
        sys.stderr.write(msg + "\n")
        sys.stderr.flush()

    def finalise(code: int, err: str | None) -> int:
        completed_at = _now_iso()
        wc = time.monotonic() - t0
        summary = _build_pack_summary(
            spec=spec, options=options, outcomes=outcomes,
            started_at=started_at, completed_at=completed_at,
            harness_error=err, exit_code=code,
            judge_calls_used=sum(o.judge_calls for o in outcomes),
            wall_clock_seconds=wc,
        )
        try:
            _write_summary(options.out_path, summary)
        except Exception as exc:
            progress(f"warning: could not write summary to {options.out_path}: {exc}")
        sys.stdout.write(json.dumps(summary, indent=2, ensure_ascii=False))
        sys.stdout.write("\n")
        sys.stdout.flush()
        return code

    if not Path(spec_path).exists():
        return finalise(2, f"spec-not-found: {spec_path}")
    try:
        spec = loaders.load_spec(spec_path)
    except Exception as exc:
        return finalise(2, f"spec-invalid: {exc}")
    _resolve_options(options, spec)

    try:
        case = loaders.load_case(case_path)
    except Exception as exc:
        return finalise(2, f"case-invalid ({case_path}): {exc}")

    rid = run_id or mint_run_id(1)
    outcome = run_one_case(
        spec=spec, spec_path=spec_path, case_path=case_path,
        case=case, run_id=rid, options=options,
        repo_root=repo_root, log_progress=progress,
        judge_calls_remaining=options.max_judge_calls,
    )
    outcomes.append(outcome)
    if outcome.status == "error":
        return finalise(2, outcome.harness_error)
    if outcome.status == "fail":
        if spec.loop_convergence.is_case_allowed_to_fail(outcome.case_id):
            return finalise(0, None)
        return finalise(1, None)
    return finalise(0, None)

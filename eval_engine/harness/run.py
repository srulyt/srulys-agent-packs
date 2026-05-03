"""Harness CLI entry point.

Subcommands:

    plan        Stage a workspace and emit operator instructions
    judge-plan  Build a judge manifest from a captured fixture
    score       Apply assertions + judge responses, write report + JSONL
    replay      Re-run scoring over an existing fixture (no workspace)
    promote     Re-record a results-local entry into the committed results dir
    resume      Resume an in-progress workspace (read its _runstate.json)
    cleanup     Delete workspaces marked complete
    abandon     Mark a workspace as abandoned

The harness deliberately does not try to drive the Copilot CLI itself —
it splits one full evaluation into stages the operator drives.
"""

from __future__ import annotations

import argparse
import dataclasses
import datetime as dt
import json
import os
import sys
from pathlib import Path

from . import loaders, models, paths_layout, report, store, workspace
from .assertions import ASSERTIONS
from .assertions.base import AssertionContext
from .judge import build_manifest, load_responses, apply_double_invoke, JudgeManifest


def _engine_root() -> str:
    """Self-locating: the eval_engine directory containing this file."""
    return str(Path(__file__).resolve().parent.parent)


def _evals_root(args: argparse.Namespace | None = None) -> str:
    """Per-repo evals/ directory.

    Resolution order:
      1. ``--evals-root`` CLI flag (if provided on this command)
      2. ``EVALS_ROOT`` environment variable
      3. ``<repo-root>/evals`` (sibling of eval_engine/)
    """
    if args is not None and getattr(args, "evals_root", None):
        return str(Path(args.evals_root).resolve())
    env = os.environ.get("EVALS_ROOT")
    if env:
        return str(Path(env).resolve())
    return str(Path(__file__).resolve().parents[2] / "evals")


# Backwards-compat alias used by some helpers below.
def _eval_root(args: argparse.Namespace | None = None) -> str:
    return _evals_root(args)


def _repo_root() -> str:
    return str(Path(__file__).resolve().parents[2])


def _new_run_id() -> str:
    ts = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")
    return f"{ts}-{os.urandom(3).hex()}"


# ---------- plan ---------------------------------------------------------


def cmd_plan(args: argparse.Namespace) -> int:
    eval_root = _eval_root(args)
    spec = loaders.load_spec(args.spec)
    case = loaders.load_case(args.case)
    if case.pack != spec.pack:
        print(
            f"warning: case.pack ({case.pack}) != spec.pack ({spec.pack})",
            file=sys.stderr,
        )
    run_id = args.run_id or _new_run_id()
    ws_root, golden = workspace.allocate(
        eval_root=eval_root, pack=spec.pack, case_id=case.id, run_id=run_id,
    )
    repo_cache = str(paths_layout.repo_cache_dir(eval_root))
    workspace.stage(
        case=case,
        workspace_root=ws_root,
        golden_staging_dir=golden,
        repo_cache_dir=repo_cache,
    )
    rs = workspace.RunState(
        run_id=run_id, pack=spec.pack, case_id=case.id,
        spec_path=str(args.spec), case_path=str(args.case),
        workspace_root=ws_root, golden_staging_dir=golden,
        started_at=dt.datetime.now(dt.timezone.utc).isoformat(),
        stage="staged", keep_workspace=bool(args.keep_workspace),
    )
    rs.write()
    prompt_path = Path(case.case_dir) / case.prompt_file
    rendered_prompt = workspace.render_template(
        prompt_path.read_text(encoding="utf-8"),
        {**case.prompt_template_vars,
         "workspace_root": ws_root, "run_id": run_id, "case_dir": case.case_dir},
    )
    instructions_file = Path(ws_root) / "_runstate.prompt.md"
    instructions_file.write_text(rendered_prompt, encoding="utf-8")
    print(f"workspace: {ws_root}")
    print(f"golden staging: {golden}")
    print()
    print("=" * 72)
    print("Operator steps:")
    print(f"  1. cd {ws_root}")
    print(
        "  2. open Copilot CLI in this directory and paste the contents "
        f"of:\n     {instructions_file}"
    )
    print("  3. capture the session id (timestamp+suffix shown by the CLI)")
    print(
        "  4. extract the fixture from the local CLI process log:\n"
        f"     python -m eval_engine.harness.run capture-local "
        f"--pack {spec.pack} --case {case.id} --run-id {run_id}"
    )
    print(
        "     (Add --log <path> if auto-discovery in ~/.copilot/logs/ "
        "fails.)"
    )
    print(
        "     For cases that declare scripted_user replies, drive the SUT "
        "hands-off via:\n"
        f"     python -m eval_engine.harness.run drive "
        f"--spec {args.spec} --case {args.case} --run-id {run_id}"
    )
    print(
        "  5. then run: python -m eval_engine.harness.run judge-plan "
        f"--run-id {run_id} --spec {args.spec} --case {args.case} "
        "--fixture <path-to-fixture>"
    )
    print("=" * 72)
    return 0


# ---------- judge-plan ---------------------------------------------------


def cmd_judge_plan(args: argparse.Namespace) -> int:
    eval_root = _eval_root(args)
    spec = loaders.load_spec(args.spec)
    case = loaders.load_case(args.case)
    fixture = loaders.load_fixture(args.fixture)
    rubrics: dict[str, models.Rubric] = {}
    rubrics_dir = Path(_engine_root()) / "rubrics"
    for ref in spec.rubrics:
        for ext in (".md", ".yaml"):
            candidate = rubrics_dir / f"{ref.id}{ext}"
            if candidate.exists():
                rubrics[ref.id] = loaders.load_rubric(candidate)
                break
    ws_root = str(paths_layout.workspace_dir(
        eval_root, spec.pack, workspace._safe_segment(case.id), args.run_id))
    rs_path = Path(ws_root) / "_runstate.json"
    if rs_path.exists():
        rs = workspace.RunState.read(ws_root)
        golden = rs.golden_staging_dir
    else:
        golden = str(paths_layout.golden_staging_dir(eval_root, args.run_id))
    response_dir = str(paths_layout.judge_responses_dir(eval_root, args.run_id))
    manifest = build_manifest(
        spec=spec, case=case, fixture=fixture, rubrics=rubrics,
        workspace_root=ws_root, golden_staging_dir=golden,
        response_dir=response_dir, judge_model=spec.models.get("judge"),
    )
    manifest_path = paths_layout.judge_manifest_path(eval_root, args.run_id)
    manifest.write(str(manifest_path))
    print(f"judge manifest: {manifest_path}")
    print(f"response dir:   {response_dir}")
    print()
    print("=" * 72)
    print("For each request below, invoke @eval-judge in your CLI and save its "
          "JSON response to the listed path:")
    for req in manifest.requests:
        print(f"  - {req.request_id}: {req.response_file}")
    print()
    print("Then run:")
    print(
        f"  python -m eval_engine.harness.run score --run-id {args.run_id} "
        f"--spec {args.spec} --case {args.case} --fixture {args.fixture} "
        f"--manifest {manifest_path}"
    )
    print("=" * 72)
    return 0


# ---------- score --------------------------------------------------------


def cmd_score(args: argparse.Namespace) -> int:
    eval_root = _eval_root(args)
    repo_root = _repo_root()
    spec = loaders.load_spec(args.spec)
    case = loaders.load_case(args.case)
    fixture = loaders.load_fixture(args.fixture)

    # Run all registered assertions.
    ws_root = str(paths_layout.workspace_dir(
        eval_root, spec.pack, workspace._safe_segment(case.id), args.run_id))
    golden = str(paths_layout.golden_staging_dir(eval_root, args.run_id))
    ctx = AssertionContext(
        spec=spec, case=case, fixture=fixture,
        workspace_root=ws_root, golden_staging_dir=golden,
    )
    assertion_results: list[models.AssertionVerdict] = []
    for a in ASSERTIONS:
        assertion_results.extend(a.run(ctx))

    # Resolve judge responses (if a manifest was supplied).
    rubric_verdicts: list[models.RubricVerdict] = []
    if args.manifest:
        manifest = JudgeManifest.read(args.manifest)
        responses = load_responses(manifest)
        rubric_verdicts = apply_double_invoke(responses, manifest)

    spec_hash = loaders.file_hash(args.spec)
    prompt_path = Path(case.case_dir) / case.prompt_file
    prompt_hash = loaders.file_hash(prompt_path) if prompt_path.exists() else None
    rubric_hashes: dict[str, str] = {}
    rubrics_dir = Path(_engine_root()) / "rubrics"
    for ref in spec.rubrics:
        for ext in (".md", ".yaml"):
            r_path = rubrics_dir / f"{ref.id}{ext}"
            if r_path.exists():
                rubric_hashes[ref.id] = loaders.file_hash(r_path)

    verdict = report.aggregate(
        pack=spec.pack, case_id=case.id, run_id=args.run_id,
        session_id=fixture.session_id, repo_root=repo_root, fixture=fixture,
        spec=spec, assertions=assertion_results, rubric_verdicts=rubric_verdicts,
        judge_model=spec.models.get("judge"),
        prompt_hash=prompt_hash, spec_hash=spec_hash,
        rubric_hashes=rubric_hashes, run_kind="local",
        repeat_group_id=args.repeat_group_id, repeat_index=args.repeat_index,
    )

    # Persist.
    results_dir = str(
        paths_layout.results_dir(eval_root, spec.pack)
        if args.record else paths_layout.results_local_dir(eval_root, spec.pack)
    )
    if args.record:
        if not store.is_working_tree_clean(repo_root) and not args.allow_dirty:
            print("refusing to --record: working tree dirty (use --allow-dirty to override)",
                  file=sys.stderr)
            return 2
    jsonl_path = store.append(verdict, results_dir=results_dir)
    reports_root = str(paths_layout.reports_dir(eval_root, spec.pack))
    md_path = report.write_report(verdict, reports_root=reports_root)

    # Update runstate.
    if Path(ws_root, "_runstate.json").exists():
        rs = workspace.RunState.read(ws_root)
        rs.stage = "complete"
        rs.write()

    print(f"status:   {verdict.status}")
    print(f"jsonl:    {jsonl_path}")
    print(f"report:   {md_path}")
    return 0 if verdict.status == "pass" else 1


# ---------- replay -------------------------------------------------------


def cmd_replay(args: argparse.Namespace) -> int:
    """Re-run scoring against an already-captured fixture, no workspace."""
    args.record = False
    args.allow_dirty = False
    args.repeat_group_id = None
    args.repeat_index = None
    args.manifest = args.manifest if hasattr(args, "manifest") else None
    return cmd_score(args)


# ---------- promote ------------------------------------------------------


def cmd_promote(args: argparse.Namespace) -> int:
    eval_root = _eval_root(args)
    repo_root = _repo_root()
    src = paths_layout.results_local_dir(eval_root, args.pack) / "runs.jsonl"
    if not src.exists():
        print(f"no local results for pack {args.pack}", file=sys.stderr)
        return 2
    target_runs: list[dict] = []
    for rec in store.iter_records(src):
        if rec.get("run_id") == args.run_id:
            target_runs.append(rec)
    if not target_runs:
        print(f"run_id {args.run_id} not found in {src}", file=sys.stderr)
        return 2
    written = store.promote(
        target_runs[-1],
        repo_root=repo_root,
        results_dir=str(paths_layout.results_dir(eval_root, args.pack)),
        allow_dirty=args.allow_dirty,
    )
    print(f"promoted to: {written}")
    return 0


# ---------- resume / cleanup / abandon -----------------------------------


def cmd_resume(args: argparse.Namespace) -> int:
    eval_root = _eval_root(args)
    states = workspace.list_workspaces(eval_root)
    if not states:
        print("no active workspaces")
        return 0
    print(f"{'stage':<18} {'pack':<24} {'case':<28} run_id")
    for rs in sorted(states, key=lambda r: r.started_at):
        print(f"{rs.stage:<18} {rs.pack:<24} {rs.case_id:<28} {rs.run_id}")
    return 0


def cmd_cleanup(args: argparse.Namespace) -> int:
    eval_root = _eval_root(args)
    affected = workspace.cleanup_orphans(eval_root, dry_run=not args.apply)
    for p in affected:
        print(("would delete" if not args.apply else "deleted") + f": {p}")
    return 0


def cmd_abandon(args: argparse.Namespace) -> int:
    workspace.abandon(args.workspace)
    print(f"marked abandoned: {args.workspace}")
    return 0


# ---------- capture-local ------------------------------------------------


def cmd_capture_local(args: argparse.Namespace) -> int:
    """Build a fixture from a local Copilot CLI process log.

    Pairs with a SUT run launched non-interactively, e.g.::

        copilot -p $prompt --agent <pack> --allow-all-tools `
                --allow-all-paths --no-ask-user --name <run-id>

    The local CLI does not expose ``session_store_sql``, so this command
    reconstructs the fixture by parsing ``~/.copilot/logs/process-*.log``.
    """
    from . import local_extractor

    eval_root = _eval_root(args)

    # Resolve workspace path: explicit override, or
    # <evals-root>/packs/<pack>/workspaces/<case>/<run-id>/.
    if args.workspace:
        workspace_path = Path(args.workspace).resolve()
    else:
        workspace_path = (
            paths_layout.workspaces_dir(eval_root, args.pack)
            / args.case
            / args.run_id
        )
    if not workspace_path.exists():
        print(
            f"warning: workspace path does not exist: {workspace_path}",
            file=sys.stderr,
        )

    # Resolve the log file.
    if args.log:
        log_path = Path(args.log).resolve()
    else:
        # Find the session id by looking up --name in the local DB, then
        # find the log that contains that session id.
        session = local_extractor.find_session_by_name(args.run_id)
        if session is None:
            print(
                f"could not find a Copilot CLI session whose cwd or summary "
                f"contains {args.run_id!r}; pass --log <path> explicitly.",
                file=sys.stderr,
            )
            return 2
        log_path = local_extractor.find_log_for_session(session)
        if log_path is None:
            print(
                f"found session {session.id} but no matching process log "
                f"in {local_extractor.DEFAULT_LOG_DIR}",
                file=sys.stderr,
            )
            return 2
        print(f"resolved session: {session.id}")
    print(f"reading log: {log_path}")

    res = local_extractor.build_fixture(
        log_path=log_path,
        pack=args.pack,
        case_id=args.case,
        workspace_root=str(workspace_path),
        run_id=args.run_id,
    )
    for w in res.warnings:
        print(f"warning: {w}", file=sys.stderr)

    # Resolve destination.
    fx = res.fixture
    if args.out:
        dest = Path(args.out).resolve()
    else:
        dest = (
            paths_layout.fixtures_dir(eval_root, args.pack)
            / args.case
            / f"{fx['session_id']}.json"
        )
    local_extractor.write_fixture(fx, dest)
    print(f"wrote fixture: {dest}")
    print(
        f"  invocations={len(fx['invocations'])} "
        f"tool_calls={len(fx['tool_calls'])} "
        f"file_accesses={len(fx['file_accesses'])}"
    )
    return 0


# ---------- drive --------------------------------------------------------


def cmd_drive(args: argparse.Namespace) -> int:
    """Drive a SUT Copilot CLI run hands-off using the case's scripted_user schedule.

    This is the production entry point for the scripted-user driver.
    The case under test must declare a non-empty ``scripted_user:``
    list; the driver feeds those replies to the SUT at each
    ``awaiting-*`` park. After the SUT exits cleanly, the operator
    runs ``capture-local`` to lift the fixture out of the local CLI
    process log.
    """
    from . import scripted_user as _scripted_user

    eval_root = _eval_root(args)
    spec = loaders.load_spec(args.spec)
    case = loaders.load_case(args.case)
    if not case.scripted_user:
        print(
            f"error: case {case.id} has no scripted_user schedule; "
            "drive requires at least one entry.",
            file=sys.stderr,
        )
        return 2

    if args.workspace:
        workspace_path = Path(args.workspace).resolve()
    else:
        workspace_path = (
            paths_layout.workspaces_dir(eval_root, spec.pack)
            / case.id
            / args.run_id
        )
    if not workspace_path.exists():
        print(
            f"error: workspace path does not exist: {workspace_path}\n"
            "Run `python -m eval_engine.harness.run plan` first.",
            file=sys.stderr,
        )
        return 2

    prompt_path = Path(args.prompt_file) if args.prompt_file else (
        workspace_path / "_runstate.prompt.md"
    )
    if not prompt_path.exists():
        print(f"error: prompt file not found: {prompt_path}", file=sys.stderr)
        return 2
    initial_prompt = prompt_path.read_text(encoding="utf-8")

    result, rc = _scripted_user.run_with_subprocess(
        case=case,
        workspace_root=workspace_path,
        initial_prompt=initial_prompt,
        copilot_bin=args.copilot_bin,
        pack=spec.pack,
        run_id=args.run_id,
        state_glob=args.state_glob,
        poll_interval=args.poll_interval,
        deadline_seconds=args.deadline,
        submit_sequence=args.submit_sequence,
        use_pty=args.use_pty,
    )
    print(f"driver status: {result.status}")
    print(f"served replies: {len(result.served)}")
    for s in result.served:
        print(f"  - {s.on_phase}: {s.reply_preview!r}")
    if result.unserved:
        print(f"unserved (still queued): {len(result.unserved)}")
        for u in result.unserved:
            print(f"  - {u.on_phase}")
    if result.message:
        print(f"note: {result.message}")
    print(f"final phase: {result.final_phase}")
    print(f"copilot exit: {rc}")
    return 0 if result.status in {"terminal", "exhausted"} and rc == 0 else 1





def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="eval_engine.harness.run")

    # Common args available on every subcommand.
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument(
        "--evals-root", default=None,
        help="Override the per-repo evals/ directory (default: <repo>/evals "
             "or $EVALS_ROOT)",
    )

    sub = p.add_subparsers(dest="command", required=True)

    pl = sub.add_parser("plan", parents=[common],
                        help="Stage workspace and emit operator instructions")
    pl.add_argument("--spec", required=True)
    pl.add_argument("--case", required=True)
    pl.add_argument("--run-id", default=None)
    pl.add_argument("--keep-workspace", action="store_true")
    pl.set_defaults(func=cmd_plan)

    jp = sub.add_parser("judge-plan", parents=[common], help="Build a judge manifest from a fixture")
    jp.add_argument("--run-id", required=True)
    jp.add_argument("--spec", required=True)
    jp.add_argument("--case", required=True)
    jp.add_argument("--fixture", required=True)
    jp.set_defaults(func=cmd_judge_plan)

    sc = sub.add_parser("score", parents=[common], help="Apply assertions + judge responses, persist verdict")
    sc.add_argument("--run-id", required=True)
    sc.add_argument("--spec", required=True)
    sc.add_argument("--case", required=True)
    sc.add_argument("--fixture", required=True)
    sc.add_argument("--manifest", default=None)
    sc.add_argument("--record", action="store_true",
                    help="Promote to committed evals/packs/<pack>/results/ instead of results-local/")
    sc.add_argument("--allow-dirty", action="store_true")
    sc.add_argument("--repeat-group-id", default=None)
    sc.add_argument("--repeat-index", type=int, default=None)
    sc.set_defaults(func=cmd_score)

    rp = sub.add_parser("replay", parents=[common], help="Re-score an existing fixture without staging a workspace")
    rp.add_argument("--run-id", required=True)
    rp.add_argument("--spec", required=True)
    rp.add_argument("--case", required=True)
    rp.add_argument("--fixture", required=True)
    rp.add_argument("--manifest", default=None)
    rp.set_defaults(func=cmd_replay)

    pr = sub.add_parser("promote", parents=[common])
    pr.add_argument("--pack", required=True)
    pr.add_argument("--run-id", required=True)
    pr.add_argument("--allow-dirty", action="store_true")
    pr.set_defaults(func=cmd_promote)

    sub.add_parser("resume", parents=[common]).set_defaults(func=cmd_resume)

    cl = sub.add_parser("cleanup", parents=[common])
    cl.add_argument("--apply", action="store_true")
    cl.set_defaults(func=cmd_cleanup)

    ab = sub.add_parser("abandon", parents=[common])
    ab.add_argument("--workspace", required=True)
    ab.set_defaults(func=cmd_abandon)

    cp = sub.add_parser(
        "capture-local", parents=[common],
        help="Build a fixture from a local Copilot CLI process log",
    )
    cp.add_argument("--pack", required=True, help="Pack id (e.g. copilot-factory)")
    cp.add_argument("--case", required=True, help="Case id (matching the cases/<id>/ folder)")
    cp.add_argument("--run-id", required=True, help="Run id (matches `copilot --name`)")
    cp.add_argument("--log", default=None,
                    help="Process log path (default: auto-discovered from ~/.copilot/logs/)")
    cp.add_argument("--workspace", default=None,
                    help="Workspace path (default: evals/packs/<pack>/workspaces/<case>/<run-id>/)")
    cp.add_argument("--out", default=None,
                    help="Output fixture path (default: evals/packs/<pack>/fixtures/<case>/<session_id>.json)")
    cp.set_defaults(func=cmd_capture_local)

    dr = sub.add_parser(
        "drive", parents=[common],
        help="Drive a SUT Copilot CLI run hands-off using a case's scripted_user schedule",
    )
    dr.add_argument("--spec", required=True)
    dr.add_argument("--case", required=True)
    dr.add_argument("--run-id", required=True, help="Run id (matches `copilot --name`)")
    dr.add_argument("--workspace", default=None,
                    help="Workspace path (default: <evals>/packs/<pack>/workspaces/<case>/<run-id>/)")
    dr.add_argument("--prompt-file", default=None,
                    help="Initial prompt path (default: <workspace>/_runstate.prompt.md)")
    dr.add_argument("--copilot-bin", default="copilot",
                    help="Copilot CLI executable (default: copilot)")
    dr.add_argument("--state-glob", default=".spec-author/sessions/*/state.json",
                    help="Glob pattern for the SUT's state.json under the workspace")
    dr.add_argument("--poll-interval", type=float, default=0.5,
                    help="Seconds between state polls (default: 0.5)")
    dr.add_argument("--deadline", type=float, default=600.0,
                    help="Hard upper bound on the run in seconds (default: 600)")
    dr.add_argument("--submit-sequence", default="\n",
                    help=(
                        "Wire-protocol terminator written after each scripted "
                        "reply to trigger the SUT's submit gesture. Defaults "
                        "to a single newline; set to '\\n\\n' (or another "
                        "sequence) once diagnostics establish the actual "
                        "Copilot CLI gesture."
                    ))
    dr.add_argument("--use-pty", action="store_true",
                    help=(
                        "Allocate a real PTY for the SUT instead of piping "
                        "stdin (Unix only; raises NotImplementedError on "
                        "Windows). Use when isatty()-gated interactive REPL "
                        "behaviour is suspected."
                    ))
    dr.set_defaults(func=cmd_drive)

    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())

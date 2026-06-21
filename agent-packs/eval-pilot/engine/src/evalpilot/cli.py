"""``evalpilot`` command-line interface.

Subcommands:

* ``evalpilot init``     — scaffold an ``evals/`` tree into the current repo.
* ``evalpilot run``      — run evals via pytest with a friendly summary.
* ``evalpilot metrics``  — show metric trends; ``--check`` fails on regressions.
* ``evalpilot discover`` — list the agents and skills evalpilot can see here.

The engine itself ships the pytest fixtures/markers as a plugin, so ``run``
is a thin wrapper around ``pytest`` plus report-log parsing.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional

from . import discovery, metrics
from .config import find_eval_root, find_metrics_root, find_repo_root, bundled_data_dir


# ---- init ---------------------------------------------------------------


def _cmd_init(args) -> int:
    repo_root = find_repo_root()
    eval_root = find_eval_root(repo_root)
    templates = bundled_data_dir() / "templates"

    eval_root.mkdir(parents=True, exist_ok=True)
    created: list[Path] = []

    def _copy(src: Path, dst: Path) -> None:
        if dst.exists() and not args.force:
            return
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        created.append(dst)

    for src in templates.rglob("*"):
        if src.is_dir():
            continue
        rel = src.relative_to(templates)
        _copy(src, eval_root / rel)

    print(f"evalpilot init -> {eval_root}")
    if created:
        for c in created:
            print(f"  created {c.relative_to(repo_root)}")
    else:
        print("  (nothing to create; pass --force to overwrite)")
    print("\nNext steps:")
    print("  1. pip install -e <plugin>/engine    # if not already installed")
    print(f"  2. evalpilot run {eval_root.name}")
    print("  3. Ask Copilot: 'create an eval for <agent/skill>' (eval-author skill)")
    return 0


# ---- discover -----------------------------------------------------------


def _cmd_discover(args) -> int:
    repo_root = find_repo_root()
    agents = discovery.discover_agents(repo_root)
    skills = discovery.discover_skills(repo_root)
    if args.json:
        print(json.dumps({
            "repo_root": str(repo_root),
            "agents": [{"name": a.name, "path": str(a.path)} for a in agents],
            "skills": [{"name": s.name, "path": str(s.path)} for s in skills],
        }, indent=2))
        return 0
    print(f"repo root: {repo_root}")
    print(f"\nagents ({len(agents)}):")
    for a in agents:
        print(f"  - {a.name:30} {a.path.relative_to(repo_root)}")
    print(f"\nskills ({len(skills)}):")
    for s in skills:
        print(f"  - {s.name:30} {s.path.relative_to(repo_root)}")
    return 0


# ---- run ----------------------------------------------------------------


def _cmd_run(args) -> int:
    eval_root = find_eval_root()
    target = args.target or str(eval_root)
    report_log = eval_root / "_runs" / "latest-report.jsonl"
    report_log.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        sys.executable, "-m", "pytest", target,
        f"--report-log={report_log}", "-v", "--tb=short",
    ]
    if args.k:
        cmd += ["-k", args.k]
    if args.parallel and args.parallel > 1:
        cmd += ["-n", str(args.parallel)]
    if args.markers:
        cmd += ["-m", args.markers]
    cmd += args.pytest_args

    print(f"$ {' '.join(cmd)}\n", flush=True)
    proc = subprocess.run(cmd)
    _summarize_report(report_log)
    return proc.returncode


def _summarize_report(report_log: Path) -> None:
    if not report_log.exists():
        return
    records: dict[str, dict] = {}
    for line in report_log.read_text(encoding="utf-8").splitlines():
        try:
            evt = json.loads(line)
        except json.JSONDecodeError:
            continue
        if evt.get("$report_type") != "TestReport" or not evt.get("nodeid"):
            continue
        rec = records.setdefault(evt["nodeid"], {"outcome": "passed"})
        if evt.get("outcome") != "passed" and rec["outcome"] == "passed":
            rec["outcome"] = evt.get("outcome", "passed")
    passed = sum(1 for r in records.values() if r["outcome"] == "passed")
    failed = sum(1 for r in records.values() if r["outcome"] == "failed")
    skipped = sum(1 for r in records.values() if r["outcome"] == "skipped")
    print(f"\n{'='*60}\nResults: {passed} passed, {failed} failed, {skipped} skipped")
    print(f"Report: {report_log}\n{'='*60}")


# ---- metrics ------------------------------------------------------------


def _cmd_metrics(args) -> int:
    metrics_root = find_metrics_root()
    series = list(metrics.iter_series(metrics_root))
    if args.slug:
        series = [(slug, hp) for slug, hp in series if args.slug in slug]
    if not series:
        print(f"No metric history under {metrics_root}")
        return 0

    any_regression = False
    for slug, hp in series:
        history = []
        for line in hp.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line:
                try:
                    history.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
        if not history:
            continue
        latest = history[-1]
        values = [r["value"] for r in history if isinstance(r.get("value"), (int, float))]
        regressions = sum(1 for r in history if r.get("regressed"))
        any_regression = any_regression or bool(latest.get("regressed"))
        flag = "  <-- REGRESSED" if latest.get("regressed") else ""
        print(f"\n{slug}{flag}")
        print(f"  runs={len(history)} latest={latest.get('value')} "
              f"baseline={latest.get('baseline')} "
              f"min={min(values) if values else None} "
              f"max={max(values) if values else None} "
              f"regressions={regressions}")
        if args.verbose:
            for r in history[-args.tail:]:
                print(f"    {r.get('ts')} {r.get('value')} "
                      f"(Δ{r.get('delta')}) {'REGRESSED' if r.get('regressed') else ''}")

    if args.check and any_regression:
        print("\nRegressions detected in latest run.")
        return 1
    return 0


# ---- argument parsing ---------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="evalpilot", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="command", required=True)

    pi = sub.add_parser("init", help="scaffold an evals/ tree into this repo")
    pi.add_argument("--force", action="store_true", help="overwrite existing files")
    pi.set_defaults(func=_cmd_init)

    pd = sub.add_parser("discover", help="list discoverable agents and skills")
    pd.add_argument("--json", action="store_true")
    pd.set_defaults(func=_cmd_discover)

    pr = sub.add_parser("run", help="run evals via pytest with a summary")
    pr.add_argument("target", nargs="?", help="path or nodeid (default: eval root)")
    pr.add_argument("-k", help="pytest -k expression")
    pr.add_argument("-m", "--markers", help="pytest -m marker expression")
    pr.add_argument("--parallel", type=int, default=0, help="xdist workers")
    pr.add_argument("pytest_args", nargs="*", help="extra args passed to pytest")
    pr.set_defaults(func=_cmd_run)

    pm = sub.add_parser("metrics", help="show metric trends")
    pm.add_argument("slug", nargs="?", help="filter series by substring")
    pm.add_argument("--check", action="store_true",
                    help="exit non-zero if the latest run regressed")
    pm.add_argument("-v", "--verbose", action="store_true")
    pm.add_argument("--tail", type=int, default=5, help="rows to show with -v")
    pm.set_defaults(func=_cmd_metrics)

    return p


def main(argv: Optional[list[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())

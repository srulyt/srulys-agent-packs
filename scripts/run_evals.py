#!/usr/bin/env python
"""Run evals for a given agent pack (or skill) and pretty-print results.

Examples
--------

    # Run every eval for an agent pack (parallelised across all CPUs):
    python scripts/run_evals.py story-telling-agent

    # Run only the named tests within a pack (substring match on the
    # node id; `-k`-style):
    python scripts/run_evals.py story-telling-agent critical_gaps buy_in_deck

    # Run a skill-only eval suite:
    python scripts/run_evals.py agent-builder

    # See what would run without executing:
    python scripts/run_evals.py spec-author --list

    # Disable parallelism (easier to read live output during debugging):
    python scripts/run_evals.py copilot-factory --parallel 1

    # Run *every* eval (no pack arg):
    python scripts/run_evals.py --all

After the run, a summary prints:

* Pass / fail counts and total duration.
* For each failure: the assertion message, the test file:line, the path
  to the captured ``agent.log`` (cmdline, stdin prompt, stdout, stderr,
  exit code), and the path to the surviving workspace dir so you can
  cd in and inspect what the agent actually wrote.

A persistent JSONL report is also written under
``evals/_runs/<timestamp>/report.jsonl`` so a follow-up agent or CI can
parse the structured results without rerunning anything.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
EVALS_DIR = REPO_ROOT / "evals"
RUNS_DIR = EVALS_DIR / "_runs"


# ---- pack/skill resolution -------------------------------------------------


def resolve_pack_dir(name: str) -> Path:
    """Return the eval directory for a pack or skill ``name``.

    Looks first under ``evals/packs/<name>`` then ``evals/skills/<name>``.
    Raises ``SystemExit`` with a helpful message if neither exists.
    """
    candidates = [
        EVALS_DIR / "packs" / name,
        EVALS_DIR / "skills" / name,
    ]
    for c in candidates:
        if c.is_dir():
            return c

    available = sorted(
        [p.name for p in (EVALS_DIR / "packs").iterdir() if p.is_dir()]
        + [p.name for p in (EVALS_DIR / "skills").iterdir() if p.is_dir()]
    )
    sys.exit(
        f"error: no eval directory for '{name}'.\n"
        f"available: {', '.join(available)}\n"
        f"          (or pass --all to run every eval in the repo)"
    )


def collect_node_ids(target: Path) -> list[str]:
    """Use pytest --collect-only to enumerate node ids under ``target``."""
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            str(target),
            "--collect-only",
            "-q",
            "--no-header",
        ],
        cwd=str(EVALS_DIR),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if proc.returncode not in (0, 5):
        # 5 = "no tests collected" which is fine to surface ourselves.
        sys.stderr.write(proc.stdout)
        sys.stderr.write(proc.stderr)
        sys.exit(proc.returncode)
    ids: list[str] = []
    for line in proc.stdout.splitlines():
        line = line.strip()
        if "::" in line and not line.startswith(("=", "-", "_")):
            ids.append(line)
    return ids


def filter_tests(ids: list[str], selectors: list[str]) -> list[str]:
    """Keep only the node ids that match any selector substring.

    Selectors use plain case-insensitive substring match against the node
    id. ``buy_in_deck`` matches both ``test_buy_in_deck_happy_path`` and
    ``test_buy_in_deck_qa_loop``.
    """
    if not selectors:
        return ids
    needles = [s.lower() for s in selectors]
    out = [i for i in ids if any(n in i.lower() for n in needles)]
    if not out:
        sys.exit(
            f"error: no tests matched selectors {selectors}.\n"
            f"available in this pack:\n  - "
            + "\n  - ".join(i.split("::", 1)[1] for i in ids)
        )
    return out


# ---- pytest invocation -----------------------------------------------------


def make_run_dir() -> Path:
    ts = _dt.datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
    d = RUNS_DIR / ts
    d.mkdir(parents=True, exist_ok=True)
    return d


def run_pytest(
    targets: list[str],
    *,
    run_dir: Path,
    parallel: int,
    extra_args: list[str],
) -> int:
    report_log = run_dir / "report.jsonl"
    console_log = run_dir / "console.log"
    cmd: list[str] = [
        sys.executable,
        "-m",
        "pytest",
        *targets,
        f"--report-log={report_log}",
        "-v",
        "--tb=short",
        "-rN",  # don't show the short summary; we render our own
    ]
    if parallel > 1:
        cmd += ["-n", str(parallel)]
    cmd += extra_args

    print(f"$ {' '.join(cmd)}", flush=True)
    print(f"  cwd:     {EVALS_DIR}", flush=True)
    print(f"  run dir: {run_dir}", flush=True)
    print()

    # Tee stdout to the console log file while still streaming to the user.
    with console_log.open("w", encoding="utf-8") as f:
        proc = subprocess.Popen(
            cmd,
            cwd=str(EVALS_DIR),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        assert proc.stdout is not None
        for line in proc.stdout:
            sys.stdout.write(line)
            f.write(line)
        proc.wait()
    return proc.returncode


# ---- report parsing & summary ----------------------------------------------


_ASSERT_RE = re.compile(r"^E\s+(.*)$")
_LOG_RE = re.compile(r"(?:see |log:|log_path[=:]\s*)([A-Za-z]:\\[^\s'\"]+\.log)")


def parse_report(report_log: Path) -> list[dict]:
    """Parse pytest --report-log JSONL into a list of test records."""
    records: dict[str, dict] = {}
    if not report_log.exists():
        return []
    for line in report_log.read_text(encoding="utf-8").splitlines():
        try:
            evt = json.loads(line)
        except json.JSONDecodeError:
            continue
        if evt.get("$report_type") != "TestReport":
            continue
        nodeid = evt.get("nodeid")
        if not nodeid:
            continue
        rec = records.setdefault(
            nodeid,
            {
                "nodeid": nodeid,
                "outcome": "passed",
                "duration": 0.0,
                "longrepr": "",
                "phase_failed": None,
            },
        )
        rec["duration"] += float(evt.get("duration", 0.0) or 0.0)
        outcome = evt.get("outcome", "passed")
        if outcome != "passed" and rec["outcome"] == "passed":
            rec["outcome"] = outcome
            rec["phase_failed"] = evt.get("when")
            longrepr = evt.get("longrepr") or ""
            if isinstance(longrepr, dict):
                longrepr = longrepr.get("reprcrash", {}).get("message", "") or json.dumps(longrepr)
            rec["longrepr"] = str(longrepr)
    return list(records.values())


def extract_assertion(longrepr: str) -> str:
    """Pull the most informative assertion line out of a pytest longrepr."""
    msgs = []
    for line in longrepr.splitlines():
        m = _ASSERT_RE.match(line)
        if m and m.group(1).strip():
            msgs.append(m.group(1).strip())
    if msgs:
        # Prefer the AssertionError line over context lines.
        for m in msgs:
            if m.startswith("AssertionError") or "assert " in m:
                return m
        return msgs[0]
    # Fallback: the first non-empty line of the longrepr.
    for line in longrepr.splitlines():
        s = line.strip()
        if s:
            return s
    return "(no assertion captured)"


def extract_log_path(longrepr: str) -> str | None:
    m = _LOG_RE.search(longrepr)
    if m:
        return m.group(1)
    return None


def workspace_for(log_path: str | None) -> str | None:
    if not log_path:
        return None
    # agent.log lives at <workspace_parent>/_logs/agent.log; the staged
    # workspace is the sibling `ws/` directory.
    p = Path(log_path)
    if p.parent.name == "_logs":
        ws = p.parent.parent / "ws"
        if ws.exists():
            return str(ws)
    return None


def render_summary(records: list[dict]) -> int:
    """Print a friendly summary; return 0 if all passed, 1 otherwise."""
    if not records:
        print("\nNo test results recorded.")
        return 1

    passed = [r for r in records if r["outcome"] == "passed"]
    failed = [r for r in records if r["outcome"] == "failed"]
    skipped = [r for r in records if r["outcome"] == "skipped"]
    errored = [r for r in records if r["outcome"] not in ("passed", "failed", "skipped")]
    total_dur = sum(r["duration"] for r in records)

    print()
    print("=" * 78)
    print(
        f"Results: {len(passed)} passed, {len(failed)} failed, "
        f"{len(skipped)} skipped, {len(errored)} other "
        f"  ({_human_dur(total_dur)} total)"
    )
    print("=" * 78)

    for r in failed + errored:
        nodeid = r["nodeid"]
        short = nodeid.split("::", 1)[-1]
        print()
        print(f"FAIL  {short}")
        print(f"      node:       {nodeid}")
        print(f"      duration:   {_human_dur(r['duration'])}")
        if r.get("phase_failed") and r["phase_failed"] != "call":
            print(f"      phase:      {r['phase_failed']}  (failed before/after the test body)")

        assertion = extract_assertion(r["longrepr"])
        # Wrap the assertion to ~75 cols for readability.
        for i, chunk in enumerate(_wrap(assertion, 75 - len("      assertion: "))):
            label = "      assertion: " if i == 0 else "                 "
            print(label + chunk)

        log_path = extract_log_path(r["longrepr"])
        if log_path:
            print(f"      agent log:  {log_path}")
            ws = workspace_for(log_path)
            if ws:
                print(f"      workspace:  {ws}")
        else:
            print("      (no agent.log path found in failure repr; check console.log)")

        print(f"      hint:       inspect agent.log for the agent's stdin prompt,")
        print(f"                  full stdout, and stderr — that usually explains")
        print(f"                  what the agent did or refused to do.")

    if not failed and not errored:
        print()
        print("All tests passed. 🎉")
        return 0

    print()
    print("Re-run a single failure with:")
    print(f'  python -m pytest "{(failed + errored)[0]["nodeid"]}" -v --tb=long')
    return 1


def _human_dur(seconds: float) -> str:
    if seconds < 1:
        return f"{seconds * 1000:.0f}ms"
    if seconds < 60:
        return f"{seconds:.1f}s"
    m, s = divmod(int(seconds), 60)
    if m < 60:
        return f"{m}m{s:02d}s"
    h, m = divmod(m, 60)
    return f"{h}h{m:02d}m{s:02d}s"


def _wrap(text: str, width: int) -> list[str]:
    if width < 20:
        width = 20
    out: list[str] = []
    for paragraph in text.splitlines() or [""]:
        if not paragraph:
            out.append("")
            continue
        line = ""
        for word in paragraph.split(" "):
            if line and len(line) + 1 + len(word) > width:
                out.append(line)
                line = word
            else:
                line = (line + " " + word) if line else word
        if line:
            out.append(line)
    return out


# ---- CLI -------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run agent-pack evals with friendly output.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "pack",
        nargs="?",
        help="Agent pack or skill name (e.g. story-telling-agent, agent-builder).",
    )
    parser.add_argument(
        "selectors",
        nargs="*",
        help="Optional substrings to filter which tests run within the pack.",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run every eval in the repo (ignores `pack` and `selectors`).",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List the tests that would run, without executing them.",
    )
    parser.add_argument(
        "--parallel",
        type=int,
        default=int(os.environ.get("EVAL_PARALLEL", os.cpu_count() or 4)),
        help="Number of parallel pytest-xdist workers (default: number of CPUs).",
    )
    parser.add_argument(
        "--keep-going",
        action="store_true",
        help="Don't stop after the first failure (default already keeps going).",
    )
    parser.add_argument(
        "--",
        dest="dashdash",
        nargs=argparse.REMAINDER,
        help="Pass remaining args verbatim to pytest.",
    )

    args = parser.parse_args(argv)
    extra: list[str] = list(args.dashdash or [])

    if args.all:
        targets = ["."]
        node_ids = None
    else:
        if not args.pack:
            parser.error("either pack name or --all is required")
        pack_dir = resolve_pack_dir(args.pack)
        node_ids = collect_node_ids(pack_dir)
        node_ids = filter_tests(node_ids, args.selectors)
        targets = node_ids

    if args.list:
        if node_ids is None:
            # --all + --list: just collect everything.
            node_ids = collect_node_ids(EVALS_DIR)
        print(f"{len(node_ids)} test(s) match:")
        for n in node_ids:
            print(f"  - {n}")
        return 0

    print(f"Running {len(targets)} target(s):")
    for t in targets:
        print(f"  - {t}")
    print()

    run_dir = make_run_dir()
    rc = run_pytest(
        targets,
        run_dir=run_dir,
        parallel=max(1, args.parallel),
        extra_args=extra,
    )
    records = parse_report(run_dir / "report.jsonl")
    summary_rc = render_summary(records)
    print()
    print(f"Full console log: {run_dir / 'console.log'}")
    print(f"Structured JSONL: {run_dir / 'report.jsonl'}")

    # Use the summary's verdict so a green "all passed" returns 0 even if
    # pytest itself returned non-zero for an unrelated reason.
    return summary_rc if records else rc


if __name__ == "__main__":
    raise SystemExit(main())

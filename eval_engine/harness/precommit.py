"""Pre-commit hook: warn when a single commit adds large numbers of result
or fixture lines.

Run as: ``python -m eval_engine.harness.precommit`` (intended to be invoked from
a git pre-commit script).

Returns exit code 1 (with an explanatory message) if either:
  * more than ``--max-result-lines`` (default 5) net lines are added to
    any ``evals/packs/<pack>/results/runs.jsonl`` file in the commit, OR
  * more than ``--max-fixture-files`` (default 3) fixture files are
    being committed.

Override with ``EVAL_PRECOMMIT_FORCE=1`` if you really mean it.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys


def _git(cmd: list[str]) -> str:
    return subprocess.check_output(["git"] + cmd, text=True)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-result-lines", type=int, default=5)
    ap.add_argument("--max-fixture-files", type=int, default=3)
    args = ap.parse_args(argv)

    if os.environ.get("EVAL_PRECOMMIT_FORCE") == "1":
        return 0

    diff = _git(["diff", "--cached", "--numstat"])
    result_lines = 0
    fixture_files = 0
    for line in diff.splitlines():
        parts = line.split("\t")
        if len(parts) != 3:
            continue
        added, _, path = parts
        # Pack-centric layout: evals/packs/<pack>/results/runs.jsonl
        if (path.startswith("evals/packs/") and "/results/" in path
                and path.endswith("runs.jsonl")):
            try:
                result_lines += int(added)
            except ValueError:
                pass
        if path.startswith("evals/packs/") and "/fixtures/" in path:
            fixture_files += 1

    if result_lines > args.max_result_lines:
        print(
            f"eval pre-commit: {result_lines} lines added to evals/packs/*/results/ "
            f"in this commit (limit {args.max_result_lines}). "
            "Set EVAL_PRECOMMIT_FORCE=1 to override.",
            file=sys.stderr,
        )
        return 1
    if fixture_files > args.max_fixture_files:
        print(
            f"eval pre-commit: {fixture_files} fixture files staged "
            f"(limit {args.max_fixture_files}). Set EVAL_PRECOMMIT_FORCE=1 to override.",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

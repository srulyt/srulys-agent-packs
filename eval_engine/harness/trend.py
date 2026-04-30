"""Trend reporter: read JSONL run records, render metric/rubric series.

Examples::

    python -m eval_engine.harness.trend --pack copilot-factory --last 20
    python -m eval_engine.harness.trend --pack copilot-factory --metric total_tokens
    python -m eval_engine.harness.trend --pack copilot-factory --rubric coherence
    python -m eval_engine.harness.trend --pack copilot-factory --aggregate-repeats

Reads from BOTH ``evals/packs/<pack>/results/runs.jsonl`` (committed, source of
truth) and ``evals/packs/<pack>/results-local/runs.jsonl`` (local). The
``--source`` flag restricts to one or the other.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from collections import defaultdict
from pathlib import Path
from typing import Iterable

from . import paths_layout, store


def _evals_root(args: argparse.Namespace | None = None) -> Path:
    """Per-repo evals/ directory.

    Resolution: ``--evals-root`` flag → ``$EVALS_ROOT`` → ``<repo>/evals``.
    """
    import os
    if args is not None and getattr(args, "evals_root", None):
        return Path(args.evals_root).resolve()
    env = os.environ.get("EVALS_ROOT")
    if env:
        return Path(env).resolve()
    return Path(__file__).resolve().parents[2] / "evals"


def _records(pack: str, source: str, args: argparse.Namespace | None = None) -> list[dict]:
    out: list[dict] = []
    eval_root = _evals_root(args)
    if source in ("all", "promoted"):
        out.extend(store.iter_pack_records(
            results_dir=paths_layout.results_dir(eval_root, pack)))
    if source in ("all", "local"):
        out.extend(store.iter_pack_records(
            results_dir=paths_layout.results_local_dir(eval_root, pack)))
    out.sort(key=lambda r: r.get("timestamp") or "")
    return out


def _aggregate_repeats(records: list[dict]) -> list[dict]:
    """Collapse runs sharing a repeat_group_id into one summary record.

    Pass policy: aggregated record's status = 'pass' iff *all* members pass.
    Numeric metrics are averaged.
    """
    by_group: dict[str, list[dict]] = defaultdict(list)
    singletons: list[dict] = []
    for r in records:
        gid = r.get("repeat_group_id")
        if gid:
            by_group[gid].append(r)
        else:
            singletons.append(r)
    out = list(singletons)
    for gid, group in by_group.items():
        statuses = {r.get("status") for r in group}
        agg_status = "pass" if statuses == {"pass"} else "fail"
        agg = dict(group[-1])  # base on the latest member
        agg["repeat_group_id"] = gid
        agg["status"] = agg_status
        # Average rubric scores.
        scores: dict[str, list[float]] = defaultdict(list)
        for r in group:
            for key, rv in (r.get("rubric_scores") or {}).items():
                if isinstance(rv, dict) and rv.get("score") is not None:
                    scores[key].append(float(rv["score"]))
        if scores:
            agg["rubric_scores"] = {
                k: {"score": statistics.mean(v), "n": len(v)}
                for k, v in scores.items()
            }
        out.append(agg)
    out.sort(key=lambda r: r.get("timestamp") or "")
    return out


def render_table(rows: Iterable[dict], columns: list[str]) -> str:
    rows = list(rows)
    widths = {c: max(len(c), max((len(str(r.get(c, ""))) for r in rows), default=0))
              for c in columns}
    sep = " | ".join("-" * widths[c] for c in columns)
    header = " | ".join(c.ljust(widths[c]) for c in columns)
    body = "\n".join(
        " | ".join(str(r.get(c, "")).ljust(widths[c]) for c in columns) for r in rows
    )
    return f"{header}\n{sep}\n{body}\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="eval_engine.harness.trend")
    ap.add_argument("--pack", required=True)
    ap.add_argument("--evals-root", default=None,
                    help="Override the per-repo evals/ directory")
    ap.add_argument("--last", type=int, default=20)
    ap.add_argument("--metric", default=None,
                    help="Show a metric series (key inside metrics{})")
    ap.add_argument("--rubric", default=None,
                    help="Show a rubric series (rubric_id, all apply_to)")
    ap.add_argument("--source", choices=["all", "promoted", "local"], default="all")
    ap.add_argument("--aggregate-repeats", action="store_true")
    ap.add_argument("--format", choices=["markdown", "json"], default="markdown")
    args = ap.parse_args(argv)

    records = _records(args.pack, args.source, args)
    if args.aggregate_repeats:
        records = _aggregate_repeats(records)
    records = records[-args.last:]

    if args.format == "json":
        json.dump(records, sys.stdout, indent=2, default=str)
        sys.stdout.write("\n")
        return 0

    if args.metric:
        rows = [
            {
                "timestamp": r.get("timestamp"),
                "case_id": r.get("case_id"),
                "git_sha": (r.get("git_sha") or "")[:8],
                "status": r.get("status"),
                args.metric: (r.get("metrics") or {}).get(args.metric),
            }
            for r in records
        ]
        print(render_table(rows, ["timestamp", "case_id", "git_sha", "status", args.metric]))
        return 0

    if args.rubric:
        rows = []
        for r in records:
            for key, rv in (r.get("rubric_scores") or {}).items():
                if not isinstance(rv, dict):
                    continue
                if not key.startswith(args.rubric + ":") and rv.get("rubric_id") != args.rubric:
                    continue
                rows.append({
                    "timestamp": r.get("timestamp"),
                    "case_id": r.get("case_id"),
                    "apply_to": rv.get("apply_to") or key.split(":", 1)[1],
                    "score": rv.get("score"),
                    "status": rv.get("status"),
                })
        print(render_table(rows, ["timestamp", "case_id", "apply_to", "score", "status"]))
        return 0

    rows = [
        {
            "timestamp": r.get("timestamp"),
            "case_id": r.get("case_id"),
            "status": r.get("status"),
            "blocker_failures": (r.get("metrics") or {}).get("blocker_failures"),
            "subagent_invocations": (r.get("metrics") or {}).get("subagent_invocations"),
            "git_sha": (r.get("git_sha") or "")[:8],
        }
        for r in records
    ]
    print(render_table(
        rows, ["timestamp", "case_id", "status", "blocker_failures",
               "subagent_invocations", "git_sha"],
    ))
    return 0


if __name__ == "__main__":
    sys.exit(main())

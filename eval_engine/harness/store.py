"""Append-only JSONL persistence + derived SQLite index.

The canonical history of every case run is the JSONL file at
``evals/packs/<pack>/results/runs.jsonl`` (committed to git) or, for
unpromoted runs, ``evals/packs/<pack>/results-local/runs.jsonl``
(gitignored). One JSON object per line, schema documented in
``eval_engine/docs/03-rubric-and-results-schema.md``.

This module exposes:

* :func:`append` — atomically append a :class:`models.CaseVerdict` line.
* :func:`iter_records` — stream parsed records from a JSONL file.
* :func:`iter_pack_records` — convenience wrapper for a single pack's
  results directory.
* :func:`promote` — copy a record from results-local to results, marking
  ``run_kind`` and asserting the working tree is clean unless overridden.
* :func:`rebuild_index` — populate ``evals/data/eval.db`` (gitignored) for
  ad-hoc queries; the DB is *derived*, never authoritative.

Path layout is the caller's concern. Callers should derive the
``results_dir`` they pass in from :mod:`eval_engine.harness.paths_layout`.
"""

from __future__ import annotations

import dataclasses
import json
import os
import sqlite3
import subprocess
from pathlib import Path
from typing import Iterable, Iterator

from . import models, paths_layout


def _record_to_dict(rec: models.CaseVerdict) -> dict:
    d = dataclasses.asdict(rec)
    return d


def append(record: models.CaseVerdict, *, results_dir: str | os.PathLike[str]) -> str:
    """Append ``record`` to ``<results_dir>/runs.jsonl``.

    ``results_dir`` should be pack-scoped (use
    :func:`paths_layout.results_dir` or :func:`paths_layout.results_local_dir`).
    """
    target_dir = Path(results_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / "runs.jsonl"
    line = json.dumps(_record_to_dict(record), separators=(",", ":"), sort_keys=True)
    with open(target, "a", encoding="utf-8", newline="\n") as fh:
        fh.write(line + "\n")
    return str(target)


def iter_records(path: str | os.PathLike[str]) -> Iterator[dict]:
    """Yield each record in a JSONL file, skipping blank lines."""
    with open(path, "r", encoding="utf-8") as fh:
        for n, line in enumerate(fh, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{n}: malformed JSONL line: {exc}") from exc


def iter_pack_records(*, results_dir: str | os.PathLike[str]) -> Iterator[dict]:
    """Yield records from ``<results_dir>/runs.jsonl`` (or empty if missing)."""
    target = Path(results_dir) / "runs.jsonl"
    if not target.exists():
        return iter([])
    return iter_records(target)


def is_working_tree_clean(repo_root: str | os.PathLike[str]) -> bool:
    try:
        out = subprocess.check_output(
            ["git", "status", "--porcelain"], cwd=str(repo_root), text=True
        )
    except (OSError, subprocess.CalledProcessError):
        return False
    return out.strip() == ""


def promote(
    record_dict: dict,
    *,
    repo_root: str | os.PathLike[str],
    results_dir: str | os.PathLike[str],
    allow_dirty: bool = False,
) -> str:
    """Re-emit a previously-recorded local run as a promoted record.

    The caller already loaded the dict from results-local. We stamp
    ``run_kind='promoted'`` and append it to ``<results_dir>/runs.jsonl``.
    Refuses to write if the tree is dirty unless ``allow_dirty=True``.
    """
    if not allow_dirty and not is_working_tree_clean(repo_root):
        raise RuntimeError(
            "refusing to promote run: git working tree is dirty; "
            "commit/stash changes or pass allow_dirty=True"
        )
    record_dict = dict(record_dict)
    record_dict["run_kind"] = "promoted"
    if not record_dict.get("pack"):
        raise ValueError("record missing 'pack'")
    target_dir = Path(results_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / "runs.jsonl"
    with open(target, "a", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(record_dict, separators=(",", ":"), sort_keys=True) + "\n")
    return str(target)


# ---------- Derived SQLite ----------------------------------------------

_SCHEMA = """
CREATE TABLE IF NOT EXISTS runs (
    run_id TEXT PRIMARY KEY,
    pack TEXT NOT NULL,
    case_id TEXT NOT NULL,
    session_id TEXT,
    git_sha TEXT,
    timestamp TEXT,
    status TEXT,
    run_kind TEXT,
    repeat_group_id TEXT,
    repeat_index INTEGER,
    prompt_hash TEXT,
    spec_hash TEXT,
    judge_model TEXT,
    json TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS runs_pack_case_ts ON runs(pack, case_id, timestamp);
CREATE INDEX IF NOT EXISTS runs_status ON runs(status);
CREATE TABLE IF NOT EXISTS rubric_scores (
    run_id TEXT NOT NULL,
    rubric_id TEXT NOT NULL,
    apply_to TEXT,
    severity TEXT,
    score REAL,
    threshold REAL,
    status TEXT,
    PRIMARY KEY (run_id, rubric_id, apply_to)
);
CREATE TABLE IF NOT EXISTS assertion_results (
    run_id TEXT NOT NULL,
    assertion_id TEXT NOT NULL,
    layer TEXT,
    severity TEXT,
    status TEXT,
    agent TEXT
);
CREATE INDEX IF NOT EXISTS assertion_results_run ON assertion_results(run_id);
"""


def rebuild_index(
    *,
    evals_root: str | os.PathLike[str],
    db_path: str | os.PathLike[str],
    include_local: bool = False,
) -> int:
    """Drop and rebuild the SQLite index from JSONL. Returns rows ingested.

    Walks every ``packs/<pack>/results/runs.jsonl`` under ``evals_root`` (and
    optionally ``packs/<pack>/results-local/runs.jsonl`` when
    ``include_local=True``).
    """
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    if Path(db_path).exists():
        Path(db_path).unlink()
    conn = sqlite3.connect(db_path)
    try:
        conn.executescript(_SCHEMA)
        n = 0
        for pack in paths_layout.iter_pack_names(evals_root):
            jsonls = [paths_layout.results_dir(evals_root, pack) / "runs.jsonl"]
            if include_local:
                jsonls.append(paths_layout.results_local_dir(evals_root, pack) / "runs.jsonl")
            for jsonl in jsonls:
                if not jsonl.exists():
                    continue
                for rec in iter_records(jsonl):
                    _insert_record(conn, rec)
                    n += 1
        conn.commit()
        return n
    finally:
        conn.close()


def _insert_record(conn: sqlite3.Connection, rec: dict) -> None:
    conn.execute(
        "INSERT OR REPLACE INTO runs(run_id, pack, case_id, session_id, git_sha, "
        "timestamp, status, run_kind, repeat_group_id, repeat_index, prompt_hash, "
        "spec_hash, judge_model, json) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (
            rec.get("run_id"),
            rec.get("pack"),
            rec.get("case_id"),
            rec.get("session_id"),
            rec.get("git_sha"),
            rec.get("timestamp"),
            rec.get("status"),
            rec.get("run_kind"),
            rec.get("repeat_group_id"),
            rec.get("repeat_index"),
            rec.get("prompt_hash"),
            rec.get("spec_hash"),
            rec.get("judge_model"),
            json.dumps(rec, sort_keys=True),
        ),
    )
    for rid, rv in (rec.get("rubric_scores") or {}).items():
        conn.execute(
            "INSERT OR REPLACE INTO rubric_scores VALUES (?,?,?,?,?,?,?)",
            (
                rec["run_id"],
                rid,
                rv.get("apply_to"),
                rv.get("severity"),
                rv.get("score"),
                rv.get("threshold"),
                rv.get("status"),
            ),
        )
    for av in rec.get("assertions") or []:
        conn.execute(
            "INSERT INTO assertion_results VALUES (?,?,?,?,?,?)",
            (
                rec["run_id"],
                av.get("assertion_id"),
                av.get("layer"),
                av.get("severity"),
                av.get("status"),
                av.get("agent"),
            ),
        )

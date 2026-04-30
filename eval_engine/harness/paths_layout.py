"""Single source of truth for the on-disk layout of an ``evals/`` directory.

Every other harness module routes its layout-derived paths through these
helpers so that a future restructure only has to touch this file.

Current layout (pack-centric)::

    evals/
    ├── packs/
    │   └── <pack>/
    │       ├── spec.yaml
    │       ├── cases/<case-id>/{case.yaml, prompt.md, inputs/, golden/, hooks/}
    │       ├── fixtures/<case-id>/<session>.json
    │       ├── results/runs.jsonl
    │       ├── results-local/runs.jsonl
    │       ├── reports/<run-id>.md
    │       └── workspaces/<case-id>/<run-id>/
    └── data/                 (cross-pack scratch)
        ├── judge-manifests/<run-id>.json
        ├── judge-responses/<run-id>/
        ├── golden-staging/<run-id>/
        └── repo-cache/<sha>/

All functions accept ``evals_root`` as a ``str`` or ``Path`` and return
``pathlib.Path``. Callers should ``str(...)`` the result if they need a
string.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterator


def evals_root(root: str | Path) -> Path:
    return Path(root)


# ---------------------------------------------------------------------------
# Cross-pack scratch
# ---------------------------------------------------------------------------


def data_dir(root: str | Path) -> Path:
    """Cross-pack scratch (judge-manifests, repo-cache, golden-staging)."""
    return Path(root) / "data"


def judge_manifest_path(root: str | Path, run_id: str) -> Path:
    return data_dir(root) / "judge-manifests" / f"{run_id}.json"


def judge_responses_dir(root: str | Path, run_id: str) -> Path:
    return data_dir(root) / "judge-responses" / run_id


def golden_staging_dir(root: str | Path, run_id: str) -> Path:
    return data_dir(root) / "golden-staging" / run_id


def repo_cache_dir(root: str | Path) -> Path:
    return data_dir(root) / "repo-cache"


# ---------------------------------------------------------------------------
# Per-pack subtree
# ---------------------------------------------------------------------------


def packs_root(root: str | Path) -> Path:
    return Path(root) / "packs"


def pack_dir(root: str | Path, pack: str) -> Path:
    return packs_root(root) / pack


def spec_path(root: str | Path, pack: str) -> Path:
    return pack_dir(root, pack) / "spec.yaml"


def cases_dir(root: str | Path, pack: str) -> Path:
    return pack_dir(root, pack) / "cases"


def case_dir(root: str | Path, pack: str, case_id: str) -> Path:
    return cases_dir(root, pack) / case_id


def fixtures_dir(root: str | Path, pack: str) -> Path:
    return pack_dir(root, pack) / "fixtures"


def case_fixtures_dir(root: str | Path, pack: str, case_id: str) -> Path:
    return fixtures_dir(root, pack) / case_id


def results_dir(root: str | Path, pack: str) -> Path:
    """Committed results dir; contains ``runs.jsonl``."""
    return pack_dir(root, pack) / "results"


def results_local_dir(root: str | Path, pack: str) -> Path:
    """Local (gitignored) results dir; contains ``runs.jsonl``."""
    return pack_dir(root, pack) / "results-local"


def runs_jsonl(results_dir_: Path) -> Path:
    """Given any results-style dir, return its runs.jsonl path."""
    return results_dir_ / "runs.jsonl"


def reports_dir(root: str | Path, pack: str) -> Path:
    return pack_dir(root, pack) / "reports"


def workspaces_dir(root: str | Path, pack: str) -> Path:
    return pack_dir(root, pack) / "workspaces"


def workspace_dir(root: str | Path, pack: str, case_id: str, run_id: str) -> Path:
    return workspaces_dir(root, pack) / case_id / run_id


# ---------------------------------------------------------------------------
# Discovery (used by resume / cleanup commands)
# ---------------------------------------------------------------------------


def iter_pack_names(root: str | Path) -> Iterator[str]:
    """Yield each pack name with a directory under ``packs/``."""
    base = packs_root(root)
    if not base.exists():
        return
    for p in sorted(base.iterdir()):
        if p.is_dir():
            yield p.name


def iter_workspace_dirs(root: str | Path) -> Iterator[tuple[str, str, str, Path]]:
    """Yield ``(pack, case_id, run_id, path)`` for every existing workspace.

    Walks ``packs/*/workspaces/*/*/`` only — does not descend further.
    """
    for pack in iter_pack_names(root):
        ws_root = workspaces_dir(root, pack)
        if not ws_root.exists():
            continue
        for case_path in sorted(ws_root.iterdir()):
            if not case_path.is_dir():
                continue
            for run_path in sorted(case_path.iterdir()):
                if run_path.is_dir():
                    yield (pack, case_path.name, run_path.name, run_path)

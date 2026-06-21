"""Repo-agnostic configuration and path resolution for evalpilot.

The engine must work inside *any* repository, not just the monorepo it was
extracted from. Nothing here hardcodes ``agent-packs/`` or a fixed
``parents[N]`` repo-root depth. Everything is resolved at runtime from:

* the git repository root (walk up for a ``.git`` marker), or an explicit
  override, falling back to the current working directory; and
* a handful of ``EVALPILOT_*`` environment variables.

Resolution order for every knob is: explicit argument > environment
variable > computed default.
"""

from __future__ import annotations

import dataclasses
import os
from pathlib import Path
from typing import Optional


def _truthy(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in {"1", "true", "yes", "on"}


def find_repo_root(start: Optional[Path] = None) -> Path:
    """Return the repository root for ``start`` (default: cwd).

    Honours ``EVALPILOT_REPO_ROOT`` first. Otherwise walks upward looking
    for a ``.git`` directory/file; if none is found, returns ``start``
    resolved (so the engine still works in a non-git scratch dir).
    """
    override = os.environ.get("EVALPILOT_REPO_ROOT")
    if override:
        return Path(override).expanduser().resolve()

    start = (start or Path.cwd()).resolve()
    for candidate in (start, *start.parents):
        if (candidate / ".git").exists():
            return candidate
    return start


def find_eval_root(repo_root: Optional[Path] = None) -> Path:
    """Return the directory that holds eval tests + metric history.

    Defaults to ``<repo_root>/evals``. Override with
    ``EVALPILOT_EVAL_ROOT`` (absolute, or relative to the repo root).
    """
    repo_root = repo_root or find_repo_root()
    override = os.environ.get("EVALPILOT_EVAL_ROOT")
    if override:
        p = Path(override).expanduser()
        return p if p.is_absolute() else (repo_root / p).resolve()
    return (repo_root / "evals").resolve()


def find_metrics_root(eval_root: Optional[Path] = None) -> Path:
    """Return the directory that holds committed JSONL metric history.

    Defaults to ``<eval_root>/_metrics``. Override with
    ``EVALPILOT_METRICS_ROOT``.
    """
    eval_root = eval_root or find_eval_root()
    override = os.environ.get("EVALPILOT_METRICS_ROOT")
    if override:
        p = Path(override).expanduser()
        return p if p.is_absolute() else (eval_root / p).resolve()
    return (eval_root / "_metrics").resolve()


def bundled_data_dir() -> Path:
    """Return the package's bundled ``_data`` directory (agents, templates)."""
    return (Path(__file__).resolve().parent / "_data").resolve()


def find_judge_agent_file() -> Optional[Path]:
    """Locate the ``eval-judge.agent.md`` the judge helper stages.

    Order:

    1. ``EVALPILOT_JUDGE_AGENT`` (explicit path).
    2. The bundled package-data copy (always present when installed).
    3. The plugin-root ``agents/`` dir, resolved relative to this package
       when running from a source checkout
       (``<plugin>/engine/src/evalpilot`` -> ``<plugin>/agents``).
    """
    override = os.environ.get("EVALPILOT_JUDGE_AGENT")
    if override:
        p = Path(override).expanduser()
        if p.is_file():
            return p

    bundled = bundled_data_dir() / "agents" / "eval-judge.agent.md"
    if bundled.is_file():
        return bundled

    # Source-checkout fallback: package lives at <plugin>/engine/src/evalpilot.
    here = Path(__file__).resolve()
    for parent in here.parents:
        candidate = parent / "agents" / "eval-judge.agent.md"
        if candidate.is_file():
            return candidate
    return None


@dataclasses.dataclass(frozen=True)
class Config:
    """Resolved paths + behavioural flags for a single eval run."""

    repo_root: Path
    eval_root: Path
    metrics_root: Path
    judge_threshold: float
    skip_sut: bool

    @classmethod
    def resolve(
        cls,
        *,
        repo_root: Optional[Path] = None,
        eval_root: Optional[Path] = None,
    ) -> "Config":
        rr = find_repo_root(repo_root) if repo_root is None else repo_root.resolve()
        er = find_eval_root(rr) if eval_root is None else eval_root.resolve()
        return cls(
            repo_root=rr,
            eval_root=er,
            metrics_root=find_metrics_root(er),
            judge_threshold=float(os.environ.get("EVALPILOT_JUDGE_THRESHOLD", "0.7")),
            skip_sut=_truthy("EVALPILOT_SKIP_SUT") or _truthy("EVALS_SKIP_SUT"),
        )


__all__ = [
    "Config",
    "find_repo_root",
    "find_eval_root",
    "find_metrics_root",
    "find_judge_agent_file",
    "bundled_data_dir",
]

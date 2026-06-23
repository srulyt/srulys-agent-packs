"""Use evalpilot fixtures for the copilot-factory suite."""

from __future__ import annotations

from pathlib import Path

import pytest

from evalpilot.pytest_plugin import judge  # noqa: F401
from evalpilot.workspace import Workspace

REPO_ROOT = Path(__file__).resolve().parents[3]
PACK_GITHUB = REPO_ROOT / "agent-packs" / "copilot-factory" / ".github"


@pytest.fixture
def agent_pack(tmp_path: Path):
    """Stage copilot-factory from its source pack to avoid repo-level duplicates."""
    def _factory(agent: str, *, include_skills: bool = True) -> Workspace:
        if agent != "copilot-factory":
            raise LookupError(f"copilot-factory evals expected agent 'copilot-factory', got {agent!r}")
        ws = Workspace(root=tmp_path / "ws", logs_dir=tmp_path / "_logs")
        ws.stage_files(PACK_GITHUB, dest_subdir=".github")
        return ws

    return _factory

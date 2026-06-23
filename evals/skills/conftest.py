"""Use evalpilot fixtures for skill eval suites."""

from __future__ import annotations

from pathlib import Path

import pytest

from evalpilot.pytest_plugin import judge  # noqa: F401
from evalpilot import discovery
from evalpilot.workspace import Workspace

REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def skill(tmp_path: Path):
    """Stage one skill, preferring the repo-level installed copy if duplicated."""
    def _factory(name: str) -> Workspace:
        ws = Workspace(root=tmp_path / "ws", logs_dir=tmp_path / "_logs")
        repo_level = REPO_ROOT / ".github" / "skills" / name
        if repo_level.exists():
            ws.stage_files(repo_level, dest_subdir=str(Path(".github") / "skills" / name))
            return ws
        info = discovery.find_skill(name, REPO_ROOT)
        ws.stage_files(info.path, dest_subdir=str(Path(".github") / "skills" / name))
        return ws

    return _factory

"""Pytest fixtures for the evals framework.

Public fixtures:

* ``workspace`` -- a per-test :class:`Workspace` rooted under pytest's
  ``tmp_path``. No staging is done by default; tests call ``stage_pack``,
  ``stage_skill`` etc. as needed.
* ``copilot_pack(pack_name)`` -- factory fixture: returns a workspace
  with the named pack staged. Most pack evals use this directly.
* ``copilot_skill(skill_name)`` -- factory fixture: returns a workspace
  with just the named skill staged.
* ``judge`` -- the LLM-as-judge helper, exposed as a callable fixture
  so tests don't need to import from ``_lib``.

Add ``-p no:cacheprovider`` is set in pyproject.toml so workspaces don't
pile up across runs; pytest still keeps the most recent few under
``$TMPDIR/pytest-of-<user>/`` for inspection of failures.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

# Make `_lib` importable as `from _lib import copilot, judge, workspace as ws_mod`.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from _lib import copilot as copilot_mod  # noqa: E402
from _lib import judge as judge_mod  # noqa: E402
from _lib.workspace import Workspace  # noqa: E402


# ---- skip markers when copilot CLI is unavailable -----------------------


def pytest_collection_modifyitems(config, items):
    """Skip tests that need the copilot binary if it's not installed.

    Tests opt in by using the ``workspace``, ``copilot_pack``,
    ``copilot_skill``, or ``judge`` fixtures (detected by name).
    """
    try:
        copilot_mod.find_copilot_bin()
        return  # binary present; nothing to skip
    except copilot_mod.CopilotNotInstalled:
        pass

    skip = pytest.mark.skip(reason="`copilot` CLI not on PATH (set COPILOT_BIN)")
    needs_copilot = {"workspace", "copilot_pack", "copilot_skill", "judge"}
    for item in items:
        if needs_copilot.intersection(getattr(item, "fixturenames", ())):
            item.add_marker(skip)


# ---- core fixtures ------------------------------------------------------


@pytest.fixture
def workspace(tmp_path: Path) -> Workspace:
    """Bare workspace. Tests stage what they need."""
    return Workspace(root=tmp_path / "ws", logs_dir=tmp_path / "_logs")


@pytest.fixture
def copilot_pack(tmp_path: Path):
    """Factory: ``ws = copilot_pack("copilot-factory")``."""

    def _factory(pack: str, *, include_skills: bool = True) -> Workspace:
        ws = Workspace(root=tmp_path / "ws", logs_dir=tmp_path / "_logs")
        ws.stage_pack(pack, include_skills=include_skills)
        return ws

    return _factory


@pytest.fixture
def copilot_skill(tmp_path: Path):
    """Factory: ``ws = copilot_skill("excalidraw")``."""

    def _factory(skill: str) -> Workspace:
        ws = Workspace(root=tmp_path / "ws", logs_dir=tmp_path / "_logs")
        ws.stage_skill(skill)
        return ws

    return _factory


@pytest.fixture
def judge(tmp_path: Path):
    """Callable LLM-as-judge fixture; logs land under the test's tmp_path."""

    def _judge(*, artifact: str, criteria: str, **kwargs) -> judge_mod.Verdict:
        log_dir = kwargs.pop("log_dir", tmp_path / "_judge")
        return judge_mod.judge(
            artifact=artifact,
            criteria=criteria,
            log_dir=log_dir,
            **kwargs,
        )

    return _judge

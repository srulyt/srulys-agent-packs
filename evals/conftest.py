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


# ---- per-test report-log flush (H2) -------------------------------------
#
# `pytest-reportlog` writes one JSON line per pytest report, but does not
# flush after each write. When the runner is killed at a wall-clock cap
# (or via H1 per-test timeout that escalates), all completed-test failure
# detail is lost because the kernel buffer is never drained.
#
# We register an after-write `pytest_runtest_logreport` hook (tryfirst is
# False; the reportlog plugin's own hook runs first and writes the line)
# that calls `flush()` + `os.fsync()` on the reportlog file handle so
# every report is durable on disk before the next test starts.
#
# Best-effort: if a future `pytest-reportlog` release renames `_file`,
# we silently degrade to no-flush rather than crashing the suite. The
# regression guard in `evals/static/test_reportlog_flush.py` will fail
# loudly when that happens.

_REPORTLOG_PLUGIN_NAME = "reportlog-plugin"


def pytest_configure(config):
    """Cache the reportlog plugin on the config for fast access in the hook."""
    plugin = config.pluginmanager.get_plugin(_REPORTLOG_PLUGIN_NAME)
    config._evals_reportlog = plugin  # may be None if --report-log not passed


def pytest_runtest_logreport(report):
    """Flush+fsync the report-log after every TestReport write (H2)."""
    import os as _os

    config = getattr(report, "config", None)
    # In recent pytest, the config isn't attached to the report; pull it
    # from the active session via the plugin manager fallback.
    plugin = None
    if config is not None:
        plugin = getattr(config, "_evals_reportlog", None)
    if plugin is None:
        # Last-ditch: walk the global pytest session to find the plugin.
        try:
            import _pytest.config as _pc  # noqa: WPS433
            cfg = _pc.get_config() if hasattr(_pc, "get_config") else None
            if cfg is not None:
                plugin = cfg.pluginmanager.get_plugin(_REPORTLOG_PLUGIN_NAME)
        except Exception:
            plugin = None
    if plugin is None:
        return
    f = getattr(plugin, "_file", None)
    if f is None:
        return
    try:
        f.flush()
        _os.fsync(f.fileno())
    except (OSError, ValueError, AttributeError):
        # File closed, non-fsyncable handle, or plugin internals changed.
        # Don't take down the test suite for a logging best-effort.
        pass


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

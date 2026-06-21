"""evalpilot pytest plugin.

Installed via the ``pytest11`` entry-point in ``pyproject.toml`` so that any
repo with ``evalpilot`` on its path gets these fixtures and markers without
writing a ``conftest.py``:

Fixtures
--------
* ``evalpilot_config`` — resolved :class:`~evalpilot.config.Config` (session).
* ``sut``              — the active :class:`~evalpilot.runners.base.SUTRunner`.
* ``workspace``        — a bare per-test :class:`~evalpilot.workspace.Workspace`.
* ``agent_pack(name)`` — factory: workspace with an agent (+ plugin skills) staged.
* ``skill(name)``      — factory: workspace with one skill staged.
* ``judge``            — LLM-as-judge callable (logs under the test tmp_path).
* ``metric``           — record a numeric metric bound to this test's id.

Markers: ``pack``, ``skill``, ``judge``, ``slow``, ``tooling``, ``metric``.

Tests that use any SUT-driving fixture are auto-skipped when the configured
runner's backend is unavailable (e.g. the ``copilot`` binary is not on PATH).
"""

from __future__ import annotations

import os
import re
from pathlib import Path

import pytest

from . import judge as judge_mod
from . import metrics as metrics_mod
from .config import Config
from .runners.base import get_runner
from .workspace import Workspace


_MARKERS = [
    "pack: exercises a full agent pack/plugin",
    "skill: exercises a single skill in isolation",
    "judge: invokes the LLM-as-judge (slower, costs tokens)",
    "slow: takes > 60s; deselect with -m 'not slow'",
    "tooling: fast, no-LLM tooling smoke evals",
    "metric: records a numeric metric tracked over time",
]

_SUT_FIXTURES = {"workspace", "agent_pack", "skill", "judge", "sut"}


def pytest_configure(config):
    for line in _MARKERS:
        config.addinivalue_line("markers", line)
    # Cache the reportlog plugin for the durability hook (see below).
    config._evalpilot_reportlog = config.pluginmanager.get_plugin("reportlog-plugin")


def pytest_collection_modifyitems(config, items):
    """Skip SUT-driving tests when the runner backend is unavailable."""
    try:
        runner = get_runner()
        if runner.available():
            return
        reason = f"SUT runner {runner.name!r} unavailable (set COPILOT_BIN / PATH)"
    except Exception as exc:  # pragma: no cover - defensive
        reason = f"SUT runner could not be resolved: {exc}"

    skip = pytest.mark.skip(reason=reason)
    for item in items:
        if _SUT_FIXTURES.intersection(getattr(item, "fixturenames", ())):
            item.add_marker(skip)


def pytest_runtest_logreport(report):
    """Flush+fsync the report-log after every write so a killed run keeps detail."""
    config = getattr(report, "config", None)
    plugin = getattr(config, "_evalpilot_reportlog", None) if config else None
    if plugin is None:
        try:
            import _pytest.config as _pc  # noqa: WPS433

            cfg = _pc.get_config() if hasattr(_pc, "get_config") else None
            if cfg is not None:
                plugin = cfg.pluginmanager.get_plugin("reportlog-plugin")
        except Exception:
            plugin = None
    if plugin is None:
        return
    f = getattr(plugin, "_file", None)
    if f is None:
        return
    try:
        f.flush()
        os.fsync(f.fileno())
    except (OSError, ValueError, AttributeError):
        pass


# ---- fixtures -----------------------------------------------------------


@pytest.fixture(scope="session")
def evalpilot_config() -> Config:
    return Config.resolve()


@pytest.fixture
def sut():
    """The active SUT runner."""
    return get_runner()


@pytest.fixture
def workspace(tmp_path: Path) -> Workspace:
    """A bare per-test workspace. Tests stage what they need."""
    return Workspace(root=tmp_path / "ws", logs_dir=tmp_path / "_logs")


@pytest.fixture
def agent_pack(tmp_path: Path):
    """Factory: ``ws = agent_pack("my-orchestrator")`` stages that agent."""

    def _factory(agent: str, *, include_skills: bool = True) -> Workspace:
        ws = Workspace(root=tmp_path / "ws", logs_dir=tmp_path / "_logs")
        ws.stage_agent(agent, include_skills=include_skills)
        return ws

    return _factory


@pytest.fixture
def skill(tmp_path: Path):
    """Factory: ``ws = skill("my-skill")`` stages that one skill."""

    def _factory(name: str) -> Workspace:
        ws = Workspace(root=tmp_path / "ws", logs_dir=tmp_path / "_logs")
        ws.stage_skill(name)
        return ws

    return _factory


@pytest.fixture
def judge(tmp_path: Path):
    """Callable LLM-as-judge; logs land under the test's tmp_path."""

    def _judge(*, artifact: str, criteria: str, **kwargs):
        log_dir = kwargs.pop("log_dir", tmp_path / "_judge")
        return judge_mod.judge(
            artifact=artifact, criteria=criteria, log_dir=log_dir, **kwargs
        )

    return _judge


def _eval_id_from_node(nodeid: str) -> str:
    """Derive a stable, filesystem-friendly metric eval_id from a test nodeid."""
    # e.g. "packs/foo/test_smoke.py::test_latency" -> "packs.foo.test_smoke.test_latency"
    cleaned = nodeid.replace("::", ".").replace("/", ".").replace("\\", ".")
    cleaned = re.sub(r"\.py\b", "", cleaned)
    return re.sub(r"[^A-Za-z0-9._-]+", "_", cleaned).strip("_.")


@pytest.fixture
def metric(request):
    """Record a numeric metric bound to this test's id.

    Usage::

        result = metric("latency_ms", elapsed, direction="lower_is_better",
                        tolerance_pct=0.2)
        result.assert_no_regression()      # optional gate
    """
    eval_id = _eval_id_from_node(request.node.nodeid)

    def _record(name: str, value: float, **kwargs):
        return metrics_mod.record_metric(
            name=name, value=value, eval_id=eval_id, **kwargs
        )

    return _record

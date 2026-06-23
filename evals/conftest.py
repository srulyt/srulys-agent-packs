"""Shared pytest hooks for eval suites."""

from __future__ import annotations

import os

_REPORTLOG_PLUGIN_NAME = "reportlog-plugin"


def pytest_configure(config):
    """Cache the reportlog plugin on the config for fast access in the hook."""
    plugin = config.pluginmanager.get_plugin(_REPORTLOG_PLUGIN_NAME)
    config._evals_reportlog = plugin  # may be None if --report-log not passed


def pytest_runtest_logreport(report):
    """Flush+fsync the report-log after every TestReport write."""
    config = getattr(report, "config", None)
    plugin = getattr(config, "_evals_reportlog", None) if config is not None else None
    if plugin is None:
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
        os.fsync(f.fileno())
    except (OSError, ValueError, AttributeError):
        pass

"""Shared helpers for the pytest-based evals framework.

Public surface:

* ``copilot.run_agent`` / ``copilot.run_skill`` -- subprocess wrappers around
  the Copilot CLI.
* ``workspace.Workspace`` -- per-test isolated working directory with helpers
  to stage pack/skill files and inspect produced artifacts.
* ``judge.judge`` -- LLM-as-judge helper (re-exported from ``evalpilot.judge``)
  that stages and calls the bundled ``eval-judge`` agent.

Tests should import via the ``conftest.py`` fixtures rather than touching
this package directly when possible.
"""

"""Fixtures for the context-pack-builder eval suite.

Stages the plugin's agents and skills into the workspace's ``.github/``
tree (``.github/agents`` + ``.github/skills``) so the Copilot CLI
auto-loads them when the workspace is its cwd. The CLI only discovers
workspace-local agents under ``.github/agents`` (registering each under
its bare filename id, e.g. ``cpb-orchestrator``); a root-level
``agents/`` directory is a *plugin-install* layout that the CLI does
NOT auto-load from cwd, which is why ``--agent cpb-orchestrator`` failed
to resolve before. This mirrors the copilot-factory / spec-author
precedent (stage into ``.github``, invoke by bare id).
"""

from __future__ import annotations

from pathlib import Path

import pytest

from evalpilot.pytest_plugin import judge  # noqa: F401
from evalpilot.workspace import Workspace

REPO_ROOT = Path(__file__).resolve().parents[3]
PACK_ROOT = REPO_ROOT / "agent-packs" / "context-pack-builder"


@pytest.fixture
def agent_pack(tmp_path: Path):
    """Stage context-pack-builder from its source pack into an isolated ws."""

    def _factory(agent: str, *, include_skills: bool = True) -> Workspace:
        if agent != "context-pack-builder":
            raise LookupError(
                "context-pack-builder evals expected agent "
                f"'context-pack-builder', got {agent!r}"
            )
        ws = Workspace(root=tmp_path / "ws", logs_dir=tmp_path / "_logs")
        # Stage into the .github/ tree so the Copilot CLI auto-loads the
        # agents/skills from cwd and registers them by bare id (matching the
        # `--agent cpb-orchestrator` invocation the behavioural tests use).
        ws.stage_files(PACK_ROOT / "agents", dest_subdir=".github/agents")
        if include_skills:
            ws.stage_files(PACK_ROOT / "skills", dest_subdir=".github/skills")
        # Keep plugin.json at the workspace root for parity with a real
        # plugin checkout (harmless; the SUT generates context-packs/ output
        # regardless of its location).
        ws.stage_files(PACK_ROOT / "plugin.json", dest_subdir=".")
        return ws

    return _factory

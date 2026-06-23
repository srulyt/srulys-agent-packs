"""Use evalpilot fixtures for the product-knowledge-brain suite."""

from __future__ import annotations

import pytest

from evalpilot.pytest_plugin import agent_pack, judge, workspace  # noqa: F401


@pytest.fixture
def product_knowledge_brain(workspace):
    """Stage the skills-only Product Knowledge Brain plugin."""
    for skill in (
        "knowledge-brain",
        "knowledge-consolidation",
        "knowledge-organization",
        "knowledge-indexing",
    ):
        workspace.stage_skill(skill)
    return workspace

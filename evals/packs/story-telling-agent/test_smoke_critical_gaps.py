"""Gaps-detection path: a thin brief with no audience, no decision, no
facts must produce ``status: needs-clarification`` and a populated
``gaps.md`` -- NOT a fabricated proposal and certainly NOT a built
deck.

Ported from legacy ``cases/smoke-critical-gaps/``.
"""
from __future__ import annotations

import json

import pytest

PROMPT = """\
@story-orchestrator

Make me a presentation about our product.

That's all I have for you. Go.
"""


@pytest.mark.pack
@pytest.mark.slow
def test_thin_brief_surfaces_gaps_and_blocks_build(copilot_pack):
    ws = copilot_pack("story-telling-agent")
    result = ws.run_agent(prompt=PROMPT, agent="story-orchestrator", timeout=600)
    assert result.ok, f"story-orchestrator failed; see {result.log_path}"

    states = ws.glob(".story-telling-stm/runs/*/state.json")
    assert states, f"state.json missing; see {result.log_path}"
    state = json.loads(states[0].read_text(encoding="utf-8"))
    assert state.get("user_approved") is not True, (
        f"thin brief must NOT set user_approved=True; "
        f"got state={state}; see {result.log_path}"
    )
    phase = state.get("phase") or state.get("current_phase")
    assert phase in (None, "proposal", "intake", "feedback"), (
        f"phase must remain pre-build; got {phase!r}; see {result.log_path}"
    )

    gaps = ws.glob(".story-telling-stm/runs/*/agents/story-strategist/gaps.md")
    assert gaps, f"gaps.md missing; see {result.log_path}"
    gaps_text = gaps[0].read_text(encoding="utf-8")
    assert gaps_text.strip(), f"gaps.md is empty; see {result.log_path}"

    pptx = ws.glob(".story-telling-stm/runs/*/agents/deck-builder/output.pptx")
    assert not pptx, (
        f"deck must NOT be built when proposal needs clarification; "
        f"found {pptx}; see {result.log_path}"
    )

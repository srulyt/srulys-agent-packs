"""Proposal feedback loop: the user rejects the first proposal with
specific feedback, the strategist revises, then the user approves.
``proposal_iteration`` must reach >=2 and Stop-B (no build before
APPROVED) must be honoured.

Ported from legacy ``cases/smoke-revision-then-approve/``.
"""
from __future__ import annotations

import json

import pytest

PROMPT = """\
@story-orchestrator

Build me a 10-minute deck for our weekly engineering all-hands.

**Audience**: ~80 engineers, mixed seniority.

**Decision needed**: none -- informational. Goal is to share Q1
reliability results and set expectations for Q2.

**Context**:
- Q1 incident count down 32% YoY.
- p95 latency improved from 850ms -> 420ms.
- One major outage in March (12 min); root cause was config rollout.
- Q2 focus: shift-left testing, on-call rotation overhaul.

**Tone**: candid, peer-to-peer. No marketing language.

---

When you show me the proposal, I will respond with feedback the FIRST
time. Specifically: I will ask you to (a) replace the opening with the
March outage timeline rather than the YoY metric, and (b) drop the
comparison slide in favor of a metric spotlight. After your revised
proposal, I will reply ``APPROVED``.

When the deck is built and QA-passed, return the path to the .pptx
file.
"""


@pytest.mark.pack
@pytest.mark.slow
def test_proposal_revision_then_approve(agent_pack):
    ws = agent_pack("story-orchestrator")
    result = ws.run_agent(prompt=PROMPT, agent="story-orchestrator", timeout=1200)
    if not result.usable:
        pytest.skip(result.unavailable_reason())
    assert result.ok, f"story-orchestrator failed; see {result.log_path}"

    states = ws.glob(".story-telling-stm/runs/*/state.json")
    assert states, f"state.json missing; see {result.log_path}"
    state = json.loads(states[0].read_text(encoding="utf-8"))
    iter_count = (
        state.get("proposal_iteration")
        or state.get("proposal_iterations")
        or 0
    )
    assert int(iter_count) >= 2, (
        f"proposal_iteration must reach >=2 after one revision; "
        f"got {iter_count}; see {result.log_path}"
    )
    assert state.get("user_approved") is True, (
        f"user_approved must be True at end; got state={state}; "
        f"see {result.log_path}"
    )

    proposals = ws.glob(
        ".story-telling-stm/runs/*/agents/story-strategist/proposal.md"
    )
    assert proposals, f"proposal.md missing; see {result.log_path}"

    pptx = ws.glob(".story-telling-stm/runs/*/agents/deck-builder/output.pptx")
    assert pptx and pptx[0].stat().st_size > 0, (
        f"output.pptx must exist and be non-empty after APPROVED; "
        f"see {result.log_path}"
    )

"""QA revise-loop: deck-builder produces an intentionally problematic
first draft; deck-critic flags >=2 issues with ``verdict: revise``;
deck-builder retries with the top-fixes; deck-critic re-runs and
passes. Verifies ``qa_iteration`` increments and the bounded retry
cap (cap=2).

Ported from legacy ``cases/smoke-visual-qa-loop/``.
"""
from __future__ import annotations

import json

import pytest

PROMPT = """\
@story-orchestrator

Build me a deck for a quarterly product review.

**Audience**: head of product, head of design, head of engineering.

**Decision needed**: align on Q2 priorities.

**Facts**:
- Q1 shipped 3 features (advanced search, dashboard v2, API rate
  limiting).
- One feature missed Q1 (mobile redesign, slipped to Q2).
- Q2 candidates: mobile redesign, internationalization, audit logs.
- Capacity = 2 features in Q2.

**Tone**: candid; this is a working session, not a victory lap.

When you propose, I will respond ``APPROVED`` immediately.

Important instruction for deck-builder: in your FIRST draft,
intentionally overload slides 3 and 4 with bullet text (>50 words per
slide) and put two metrics on slide 5 with no source citation. This
will exercise the deck-critic's revision loop. After deck-critic's
first revise verdict, fix the top issues it identifies and let it
re-run.

Return the final .pptx path once QA verdicts pass.
"""


@pytest.mark.pack
@pytest.mark.slow
def test_qa_revise_loop(copilot_pack):
    ws = copilot_pack("story-telling-agent")
    result = ws.run_agent(prompt=PROMPT, agent="story-orchestrator", timeout=1500)
    assert result.ok, f"story-orchestrator failed; see {result.log_path}"

    pptx = ws.glob(".story-telling-stm/runs/*/agents/deck-builder/output.pptx")
    assert pptx and pptx[0].stat().st_size > 0, (
        f"output.pptx missing or empty; see {result.log_path}"
    )

    qa_reports = ws.glob(
        ".story-telling-stm/runs/*/agents/deck-critic/qa-report.json"
    )
    assert qa_reports, f"qa-report.json missing; see {result.log_path}"

    states = ws.glob(".story-telling-stm/runs/*/state.json")
    assert states, f"state.json missing; see {result.log_path}"
    state = json.loads(states[0].read_text(encoding="utf-8"))
    qa_iter = state.get("qa_iteration") or state.get("qa_iterations") or 0
    assert 1 <= int(qa_iter) <= 2, (
        f"qa_iteration must be 1 or 2 (cap=2); got {qa_iter}; "
        f"see {result.log_path}"
    )

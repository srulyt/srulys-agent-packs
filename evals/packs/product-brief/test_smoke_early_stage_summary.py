"""Smoke evals for the ``product-brief`` agent pack.

Ported from ``evals/packs/product-brief/cases/smoke-early-stage-summary/``.
"""

from __future__ import annotations

import pytest


CONCEPT_NOTE = """\
# Quick Note: thinking about a 'Pinned Insights' feature

Idea: let users star data points in dashboards and have those starred
items collected on a weekly digest email. Not sure if this is worth
building -- traffic to the digest is what would tell us. Pinning would
need to be cross-device but I don't yet know how to handle conflicts.
"""

PROMPT = """\
@brief-orchestrator

I have a rough idea I want to put on paper for my own thinking. The
note is in `inputs/concept-note.md` -- it's just a few paragraphs
describing a hypothesis about a feature I might propose later.

Audience: just me, for now. No decision being asked. Please produce a
short brief that synthesizes what I have. If material is thin, that's
fine -- keep the brief short.
"""


@pytest.mark.pack
@pytest.mark.slow
@pytest.mark.judge
def test_early_stage_summary(agent_pack, judge):
    """Early-stage brief from thin source material; strategy-modeler skipped."""
    ws = agent_pack("brief-orchestrator")

    # Stage the concept note inside the workspace where the prompt expects it.
    inputs = ws.root / "inputs"
    inputs.mkdir(exist_ok=True)
    (inputs / "concept-note.md").write_text(CONCEPT_NOTE, encoding="utf-8")

    result = ws.run_agent(
        prompt=PROMPT,
        agent="brief-orchestrator",
        timeout=600,
    )
    if not result.usable:
        pytest.skip(result.unavailable_reason())
    assert result.ok, f"see {result.log_path}"

    briefs = ws.glob(".product-brief-agent-stm/runs/*/agents/brief-orchestrator/product-brief.md")
    assert len(briefs) == 1, f"expected exactly 1 product-brief.md, got {len(briefs)}"

    maturity_files = ws.glob(".product-brief-agent-stm/runs/*/agents/brief-orchestrator/maturity-assessment.md")
    assert maturity_files, "expected a maturity-assessment.md"

    verdict = judge(
        artifact=briefs[0].read_text(encoding="utf-8"),
        criteria=(
            "The brief MUST:\n"
            "1. Be focused with no padding or filler -- length should match "
            "   the thin source material, but do not penalize thoroughness "
            "   where clarity requires it (no fixed word cap).\n"
            "2. Reference the 'Pinned Insights' / starred-items concept "
            "   from the user's note.\n"
            "3. End with a Summary-style closing section (NOT a 'Decision' or 'Recommendation' ask), "
            "   because the user said 'no decision being asked'.\n"
            "4. Be free of writer-scaffolding / meta-commentary: no content-labels "
            "   or announcing captions (e.g. 'What the customer gets:'), no design "
            "   self-commentary ('...is deliberately simple', 'and that is the point'), "
            "   no significance meta-commentary ('this matters because...', 'the value "
            "   of this is...'), and no emphasis-only 'X, not Y' contrast where the "
            "   positive claim already stands. Judge the CLASS (writer-narration that "
            "   serves the author, not the reader), not these exact phrases -- penalize "
            "   unseen variants that fit the class; do not reward a brief that merely "
            "   avoided the listed phrases while keeping the pattern.\n"
            "Score 1.0 if all four. 0.5 if 2-3. 0 otherwise."
        ),
        threshold=0.7,
    )
    assert verdict.passed, verdict.reasoning

"""Smoke evals for the ``story-telling-agent`` pack.

Ported from ``evals/packs/story-telling-agent/cases/smoke-buy-in-deck/``.
"""

from __future__ import annotations

import pytest


PROMPT = """\
@story-orchestrator

We need a buy-in deck to take to **VP Engineering and Director of
Product** on Friday. The ask: **approve $200K Phase-1 budget** for the
platform team's reliability initiative.

Existing context: we ran a 6-week pilot, p95 latency dropped 38%, two
key on-call rotations stabilized. Phase-1 funds dedicated SRE headcount
and one quarter of capacity to extend the pattern across services.

Build the deck end-to-end (intake -> research -> proposal -> approval
gate -> build -> qa). Approve at the Stop-B gate when prompted -- this
is a non-interactive run, so do not pause for additional input.
"""


@pytest.mark.pack
@pytest.mark.slow
@pytest.mark.judge
def test_buy_in_deck_happy_path(agent_pack, judge):
    """Story orchestrator runs the full happy-path flow and produces a deck."""
    ws = agent_pack("story-orchestrator")

    result = ws.run_agent(
        prompt=PROMPT,
        agent="story-orchestrator",
        timeout=1200,
    )
    if not result.usable:
        pytest.skip(result.unavailable_reason())
    assert result.ok, f"see {result.log_path}"

    # The pack writes everything under .story-telling-stm/runs/<run-id>/.
    run_dirs = ws.glob(".story-telling-stm/runs/*")
    assert run_dirs, "expected a run directory under .story-telling-stm/runs/"

    artifacts = ws.glob(".story-telling-stm/runs/*/**/*.md")
    assert len(artifacts) >= 3, (
        f"expected >=3 markdown artifacts in the run, got {len(artifacts)}"
    )

    # Pick the deck-shaped artifact for the judge (longest .md is a fair proxy).
    deck = max(artifacts, key=lambda p: p.stat().st_size)
    verdict = judge(
        artifact=deck.read_text(encoding="utf-8"),
        criteria=(
            "The deck MUST:\n"
            "1. Address VP Engineering and Director of Product as the audience.\n"
            "2. Make a clear ask for $200K Phase-1 budget.\n"
            "3. Include evidence from the pilot (latency drop, on-call stabilisation).\n"
            "4. Be structured (sections / slide-like progression), not a single prose blob.\n"
            "Score 1.0 if all four. 0.6 if 3/4. 0 otherwise."
        ),
        threshold=0.7,
    )
    assert verdict.passed, verdict.reasoning

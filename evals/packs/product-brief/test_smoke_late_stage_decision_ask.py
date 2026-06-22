"""Smoke: late-stage Decision Ask brief (FY26 onboarding funding).

Exercises the full happy-path evidence-analyst -> strategy-modeler ->
brief-composer flow and verifies the closing section is rendered as a
Decision Ask. Ported from legacy
``cases/smoke-late-stage-decision-ask/``.
"""
from __future__ import annotations

from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures" / "smoke_late_stage_decision_ask"

PROMPT = """\
@brief-orchestrator

We need to build a decision-grade brief asking leadership to approve
funding for a new in-product onboarding flow next planning cycle.

Source material is in ``inputs/``. It includes:

- A draft funding ask (``funding-ask.md``)
- Customer research summary (``customer-research.md``)
- Two competing implementation options with cost ranges (``options.md``)
- Success metrics proposal (``metrics.md``)

Audience: VP Product + CFO. The decision required is **approve / reject
funding for FY26 onboarding redesign**. Please produce a full
late-stage decision brief.
"""


@pytest.mark.pack
@pytest.mark.slow
@pytest.mark.judge
def test_late_stage_decision_ask(agent_pack, judge):
    ws = agent_pack("brief-orchestrator")
    ws.stage_files(FIXTURES, dest_subdir="inputs")

    result = ws.run_agent(prompt=PROMPT, agent="brief-orchestrator", timeout=600)
    if not result.usable:
        pytest.skip(result.unavailable_reason())
    assert result.ok, f"brief-orchestrator failed; see {result.log_path}"

    final = ws.glob(
        ".product-brief-agent-stm/runs/*/agents/brief-orchestrator/product-brief.md"
    )
    assert final, f"final product-brief.md missing; see {result.log_path}"

    for required in (
        ".product-brief-agent-stm/runs/*/agents/brief-orchestrator/handoff-report.md",
        ".product-brief-agent-stm/runs/*/agents/evidence-analyst/evidence-log.md",
        ".product-brief-agent-stm/runs/*/agents/strategy-modeler/decision-model.md",
        ".product-brief-agent-stm/runs/*/agents/brief-composer/product-brief.draft.md",
    ):
        assert ws.glob(required), (
            f"missing required artifact pattern {required!r}; see {result.log_path}"
        )

    verdict = judge(
        artifact=final[0].read_text(encoding="utf-8"),
        criteria=(
            "Score 1.0 if the brief is structured as a late-stage Decision Ask: "
            "names the explicit decision (approve/reject FY26 onboarding "
            "funding), names the decision audience (VP Product + CFO), presents "
            "at least two implementation options with cost trade-offs sourced "
            "from the input materials, ends with a clear recommendation or "
            "decision-required call-out, AND is free of writer-scaffolding / "
            "meta-commentary (no content-labels or announcing captions like "
            "'What the customer gets:', no design self-commentary like "
            "'...is deliberately simple' / 'and that is the point', no significance "
            "meta-commentary like 'this matters because...' / 'the value of this is...', "
            "and no emphasis-only 'X, not Y' contrast where the positive claim already "
            "stands). Judge the writer-scaffolding CLASS (author-serving narration), not "
            "these exact phrases -- penalize unseen variants that fit the class and do "
            "not reward a brief that merely avoided the listed phrases. Score 0.5 if the "
            "brief covers the evidence and options but omits an explicit Decision Ask "
            "closing or carries noticeable writer-scaffolding. "
            "Score 0.0 if it reads as an exploratory summary with no decision "
            "framing."
        ),
        threshold=0.7,
    )
    assert verdict.passed, (
        f"decision-ask judge failed: {verdict.reasoning}; see {result.log_path}"
    )

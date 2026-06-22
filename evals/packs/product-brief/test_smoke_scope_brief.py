"""Smoke: scope-brief (Data Products MVP scope description).

Exercises the new Brief Type axis. The source describes the in/out-of-scope
boundary of an MVP and asks for NO decision, approval, or funding. The
orchestrator should classify the brief as a ``scope-brief``, expand Problem
Scope and Solution Scope, and omit a Call to Action / standalone Open
Questions section rather than manufacturing a decision ask.
"""
from __future__ import annotations

from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures" / "smoke_scope_brief"

PROMPT = """\
@brief-orchestrator

I want a brief that describes the scope of our Data Products MVP so partner
teams understand what is in and out of scope. Source material is in
``inputs/``:

- A scope overview (``scope-overview.md``)
- The per-surface in/out-of-scope boundaries (``surfaces.md``)

Audience: partner engineering teams. This is NOT a decision brief -- the
team has already committed to building the MVP. No approval, funding, or
go/no-go is being requested. Please describe the scope; do not invent a
decision to ask for.
"""


@pytest.mark.pack
@pytest.mark.slow
@pytest.mark.judge
def test_scope_brief(agent_pack, judge):
    ws = agent_pack("brief-orchestrator")
    # Stage only the genuine source docs into inputs/. The fixture
    # directory also contains a README.md that describes the fixture for
    # test-harness maintainers; staging it would feed harness commentary
    # into the SUT inputs, so it is deliberately excluded.
    ws.stage_files(FIXTURES / "scope-overview.md", dest_subdir="inputs")
    ws.stage_files(FIXTURES / "surfaces.md", dest_subdir="inputs")

    result = ws.run_agent(prompt=PROMPT, agent="brief-orchestrator", timeout=600)
    if not result.usable:
        pytest.skip(result.unavailable_reason())
    assert result.ok, f"brief-orchestrator failed; see {result.log_path}"

    final = ws.glob(
        ".product-brief-agent-stm/runs/*/agents/brief-orchestrator/product-brief.md"
    )
    assert len(final) == 1, (
        f"expected exactly 1 product-brief.md, got {len(final)}; see {result.log_path}"
    )

    maturity_files = ws.glob(
        ".product-brief-agent-stm/runs/*/agents/brief-orchestrator/maturity-assessment.md"
    )
    assert maturity_files, f"expected a maturity-assessment.md; see {result.log_path}"
    assessment = maturity_files[0].read_text(encoding="utf-8").lower()
    assert "scope-brief" in assessment, (
        "maturity-assessment.md must record the brief as 'scope-brief'; "
        f"see {result.log_path}"
    )

    verdict = judge(
        artifact=final[0].read_text(encoding="utf-8"),
        criteria=(
            "Score 1.0 ONLY if the brief (a) is structured as a scope "
            "description with distinct Problem Scope and Solution Scope "
            "sections that carry explicit in-scope vs out-of-scope content "
            "(surface by surface for the solution), (b) contains NO "
            "decision/approval/funding/go-no-go ask and NO standalone Open "
            "Questions section, and (c) does not invent a Call to Action. "
            "Score 0.5 if the scope sections are present but an unsolicited "
            "decision ask or a standalone Open Questions section was added. "
            "Score 0.0 if it reads as a generic decision brief that asks the "
            "reader to decide."
        ),
        threshold=0.7,
    )
    assert verdict.passed, (
        f"scope-brief judge failed: {verdict.reasoning}; see {result.log_path}"
    )

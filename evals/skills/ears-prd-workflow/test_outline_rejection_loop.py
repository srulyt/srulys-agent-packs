"""Skill-in-isolation eval: ears-prd-workflow outline-rejection loop.

S1 (`ears-prd-workflow`) OWNS the outline-approval loop, so this test
lives under the workflow skill's eval directory (carry-concern C2).

Drives the flow to step 3, rejects the proposed outline with specific
feedback, and verifies the workflow loops back to steps 1-2 (re-grilling
only the slice the feedback touches), re-presents a revised outline with
`revisions_used` incremented, and does NOT draft the PRD after the
rejection.
"""

from __future__ import annotations

import pytest


PROMPT = """\
You are running the EARS PRD workflow for a "team analytics dashboard"
feature. Proceed to step 3 and present a short outline (section names +
one-line intent) and emit the `prd-outline` block with status proposed.

I am now reviewing your proposed outline and I REJECT it with this
feedback: "The outline is missing anything about access control / who
can view which team's data, and it doesn't cover data retention. Revise
it before drafting."

Respond to this rejection. Do not write the full PRD yet.
"""


@pytest.mark.skill
@pytest.mark.slow
@pytest.mark.judge
def test_outline_rejection_loop(skill, judge):
    """Rejecting the outline loops back to steps 1-2 and re-presents."""
    ws = skill("ears-prd-workflow")

    result = ws.run_skill(
        skill="ears-prd-workflow",
        prompt=PROMPT,
        timeout=300,
        log_name="ears-prd-workflow-rejection-loop",
    )
    if not result.usable:
        pytest.skip(result.unavailable_reason())
    assert result.ok, (
        f"copilot exited {result.returncode}; see {result.log_path}"
    )

    output = result.stdout
    # Structural check: a re-presented outline block must appear.
    assert "prd-outline" in output, (
        f"Expected a re-presented prd-outline block; see {result.log_path}"
    )

    verdict = judge(
        artifact=output,
        criteria=(
            "The response handles an outline rejection during step 3 of "
            "the EARS PRD workflow. It MUST:\n"
            "1. NOT produce a full drafted PRD (no Functional Requirements "
            "   with FR-/AC- IDs) after the rejection — drafting is "
            "   gated on approval.\n"
            "2. Capture the user's feedback (access control / who can view "
            "   which team's data, AND data retention).\n"
            "3. Re-run only the relevant slice of steps 1-2 — e.g. ask "
            "   targeted follow-up question(s) about access control and "
            "   retention rather than re-interrogating everything.\n"
            "4. Re-present a revised `prd-outline` block whose revised "
            "   outline now reflects the feedback (adds access-control and "
            "   retention sections/intents) with status proposed and "
            "   `revisions_used` incremented (>= 1).\n"
            "Score 1.0 only if all four are met. Score 0.5 if 2-3 met. "
            "Score 0.0 otherwise."
        ),
        threshold=0.7,
    )
    assert verdict.passed, (
        f"Judge rejected (score={verdict.score:.2f}): {verdict.reasoning}"
    )

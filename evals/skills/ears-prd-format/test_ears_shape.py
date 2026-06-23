"""Skill-in-isolation eval: ears-prd-format EARS validity.

Gives the format skill a short list of raw requirements and asks it to
format them as EARS Functional Requirements with nested acceptance
criteria, then judges EARS shape.
"""

from __future__ import annotations

import pytest


PROMPT = """\
Format the following raw requirements for an "Orders" service as EARS
Functional Requirements with nested Given/When/Then acceptance criteria.
Use FR-NN and AC-<FR>.<n> IDs. Output the formatted requirements as
markdown.

Raw requirements:
1. The service keeps an audit log of every order state change.
2. When a customer cancels an order, refund the payment.
3. If the payment provider times out, mark the order pending and retry.
4. While the store is in maintenance mode, reject new orders.
"""


@pytest.mark.skill
@pytest.mark.slow
@pytest.mark.judge
def test_ears_shape(skill, judge):
    """Formatted FRs are valid EARS with one shall each and testable ACs."""
    ws = skill("ears-prd-format")

    result = ws.run_skill(
        skill="ears-prd-format",
        prompt=PROMPT,
        timeout=300,
        log_name="ears-prd-format-shape",
    )
    if not result.usable:
        pytest.skip(result.unavailable_reason())
    assert result.ok, (
        f"copilot exited {result.returncode}; see {result.log_path}"
    )

    output = result.stdout
    # Structural checks before the judge.
    assert "FR-" in output, (
        f"Expected FR- IDs in the output; see {result.log_path}"
    )
    assert "AC-" in output, (
        f"Expected AC- IDs in the output; see {result.log_path}"
    )
    assert "shall" in output.lower(), (
        f"Expected EARS 'shall' statements; see {result.log_path}"
    )

    verdict = judge(
        artifact=output,
        criteria=(
            "The response formats raw requirements as EARS Functional "
            "Requirements. Every FR MUST:\n"
            "1. Match one of the 6 EARS patterns (ubiquitous, "
            "   event-driven, state-driven, optional-feature, unwanted, "
            "   complex).\n"
            "2. Contain EXACTLY ONE `shall`.\n"
            "3. Name a system/component as the subject (never 'we' or "
            "   'the user').\n"
            "4. Express WHAT, not HOW (no implementation choices).\n"
            "5. Have at least one nested, testable Given/When/Then "
            "   acceptance criterion with concrete inputs and an "
            "   observable result.\n"
            "Score 1.0 only if ALL listed FRs satisfy all five rules. "
            "Score 0.5 if most do with minor violations. Score 0.0 if "
            "multiple FRs are malformed (e.g. multiple shalls, 'we shall', "
            "or how-not-what)."
        ),
        threshold=0.7,
    )
    assert verdict.passed, (
        f"Judge rejected (score={verdict.score:.2f}): {verdict.reasoning}"
    )

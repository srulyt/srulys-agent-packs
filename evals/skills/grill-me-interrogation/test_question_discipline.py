"""Skill-in-isolation eval: grill-me-interrogation question discipline.

Gives the skill an under-specified feature brief containing at least one
enumerable-answer gap (auth model) and at least one open-ended gap
(latency budget), and asks it to "grill me" to close gaps. Judges
question discipline: one gap per question, P0/P1/P2 tags, multiple-choice
where applicable (with an escape) vs. freeform, and no invented answers.

The judge does NOT assert any maximum question count — the skill removes
the legacy cap deliberately.
"""

from __future__ import annotations

import pytest


PROMPT = """\
Here is an under-specified feature brief: "We want to add a 'share
report' feature so users can share a generated report with people
outside their organization. It should be reasonably fast."

Grill me to close the requirement gaps before any PRD is drafted. Ask
your gap-closing questions now. (Note: the brief deliberately leaves the
authentication/sharing-access model unspecified, and leaves the
performance target as a vague 'reasonably fast'.) Do not draft a PRD;
just produce your interrogation questions.
"""


@pytest.mark.skill
@pytest.mark.slow
@pytest.mark.judge
def test_question_discipline(copilot_skill, judge):
    """Grill-me questions are well-formed, tagged, and MC-vs-freeform correct."""
    ws = copilot_skill("grill-me-interrogation")

    result = ws.run_skill(
        skill="grill-me-interrogation",
        prompt=PROMPT,
        timeout=300,
        log_name="grill-me-question-discipline",
    )
    assert result.ok, (
        f"copilot exited {result.returncode}; see {result.log_path}"
    )

    output = result.stdout
    # Structural check: priority tags should be present.
    assert any(tag in output for tag in ("P0", "P1", "P2")), (
        f"Expected P0/P1/P2 priority tags on questions; see {result.log_path}"
    )

    verdict = judge(
        artifact=output,
        criteria=(
            "The response is a grill-me interrogation question set. It "
            "MUST satisfy ALL of:\n"
            "(a) Each question targets exactly ONE gap — no compound "
            "    questions bundling two decisions.\n"
            "(b) Every question is tagged with a P0/P1/P2 priority, with "
            "    blockers (P0) flagged first.\n"
            "(c) The enumerable gap (the auth / sharing-access model) is "
            "    posed as MULTIPLE-CHOICE with 2-6 sensible, "
            "    mutually-distinct options PLUS an escape such as 'Not "
            "    sure / decide later' (or an explicit freeform/'specify "
            "    your own' affordance). It is acceptable for this to be "
            "    expressed via an ask_user-style call or inline option "
            "    list.\n"
            "(d) The open-ended gap (the latency / performance budget) is "
            "    posed as a FREEFORM question, NOT as fabricated buckets "
            "    like fast/medium/slow.\n"
            "(e) No answers are invented to fill the spec — the skill asks "
            "    rather than assuming.\n"
            "Do NOT penalise the response for asking 'too many' questions; "
            "there is no maximum question count. Score 1.0 only if all "
            "five (a-e) hold. Score 0.5 if 3-4 hold. Score 0.0 otherwise."
        ),
        threshold=0.7,
    )
    assert verdict.passed, (
        f"Judge rejected (score={verdict.score:.2f}): {verdict.reasoning}"
    )

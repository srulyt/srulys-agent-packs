"""Skill-in-isolation eval: ears-prd-workflow happy path (full 4-step flow).

Stages only the ``ears-prd-workflow`` skill and asks the default agent to
produce an EARS PRD for a small, well-specified feature so it can run all
four steps with minimal interrogation and write the document.
"""

from __future__ import annotations

import pytest


PROMPT = """\
Write an EARS-style PRD for a small, well-specified feature: a
"password reset via email" capability for an existing web app's Auth
service. Assume registered users have a verified email on file; the
reset link should be single-use and expire after 15 minutes.

Run the full workflow. Keep interrogation minimal since the feature is
well specified, propose a short outline, and (treating this approval as
granted) format the final PRD. Write it to `password-reset-prd.md` and
emit the `prd-outline` and `prd-summary` blocks in your final response.
"""


@pytest.mark.skill
@pytest.mark.slow
@pytest.mark.judge
def test_smoke_happy_path(copilot_skill, judge):
    """The workflow skill runs all 4 steps and produces a valid EARS PRD."""
    ws = copilot_skill("ears-prd-workflow")

    result = ws.run_skill(
        skill="ears-prd-workflow",
        prompt=PROMPT,
        timeout=300,
        log_name="ears-prd-workflow-smoke",
    )
    assert result.ok, (
        f"copilot exited {result.returncode}; see {result.log_path}"
    )

    output = result.stdout
    # Structural checks before the judge.
    assert "prd-summary" in output, (
        f"Expected a prd-summary block in the output; see {result.log_path}"
    )
    assert "Functional Requirements" in output, (
        f"Expected a Functional Requirements section; see {result.log_path}"
    )

    verdict = judge(
        artifact=output,
        criteria=(
            "The response completes a 4-step EARS PRD workflow. It MUST:\n"
            "1. Contain a PRD with the mandatory sections (Document "
            "   Information, Problem Statement, Goals & Success Metrics, "
            "   Users & Personas, Solution Summary, Functional "
            "   Requirements, Risks & Mitigations, Open Questions, Out of "
            "   Scope).\n"
            "2. Have at least 3 Functional Requirements, each a SINGLE "
            "   valid EARS `shall` statement that names a system (not "
            "   'we'/'the user') and expresses what-not-how.\n"
            "3. Give each FR at least one nested Given/When/Then "
            "   acceptance criterion.\n"
            "4. Include an Open Questions section.\n"
            "5. Emit a `prd-summary` fenced block.\n"
            "6. Contain NO fabricated citations or invented data.\n"
            "Score 1.0 only if all six are met. Score 0.5 if 4-5 met. "
            "Score 0.0 otherwise."
        ),
        threshold=0.7,
    )
    assert verdict.passed, (
        f"Judge rejected (score={verdict.score:.2f}): {verdict.reasoning}"
    )

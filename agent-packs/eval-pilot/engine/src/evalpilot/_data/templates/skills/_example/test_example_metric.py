"""Example **skill** eval — copy and adapt for your own skill.

Shows a skill-in-isolation run plus a metric that is *gated* (a regression
fails the test). Delete the ``_example`` directory once you have real evals.
"""

from __future__ import annotations

import pytest

from evalpilot import rubric

SKILL_NAME = "REPLACE-WITH-YOUR-SKILL-NAME"

PROMPT = "Replace with a small task that exercises the skill."


@pytest.mark.skill
@pytest.mark.slow
@pytest.mark.metric
def test_example_skill(skill, metric):
    ws = skill(SKILL_NAME)

    result = ws.run_skill(skill=SKILL_NAME, prompt=PROMPT, timeout=300)
    if not result.usable:
        pytest.skip(result.unavailable_reason())
    assert result.ok, f"skill exited {result.returncode}; see {result.log_path}"

    rubric(
        ("produced non-empty output", bool(result.stdout.strip())),
    ).assert_passed(log_path=result.log_path)

    # Track response length over time; flag a >25% drift as a regression.
    m = metric(
        "response_words", len(result.stdout.split()),
        direction="lower_is_better", tolerance_pct=0.25,
    )
    m.assert_no_regression(log_path=result.log_path)

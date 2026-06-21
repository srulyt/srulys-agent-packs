"""Example **agent pack** eval — copy and adapt for your own agent.

Demonstrates the dual result model:

* a binary **rubric** (structural asserts + an optional LLM judge), and
* a numeric **metric** recorded to JSONL history for trend tracking.

Replace ``AGENT_NAME`` / ``PROMPT`` / the assertions with your own. Delete
the ``_example`` directory once you have real evals.
"""

from __future__ import annotations

import pytest

from evalpilot import rubric, check_judge

AGENT_NAME = "REPLACE-WITH-YOUR-AGENT-NAME"

PROMPT = """\
Replace this with a prompt that exercises a real scenario for your agent.
Do NOT include the expected answer in the prompt — the point of the judge
is that the agent had to figure it out.
"""


@pytest.mark.pack
@pytest.mark.slow
@pytest.mark.judge
@pytest.mark.metric
def test_example_pack(agent_pack, judge, metric):
    ws = agent_pack(AGENT_NAME)

    result = ws.run_agent(prompt=PROMPT, agent=AGENT_NAME, timeout=600)
    if not result.usable:
        pytest.skip(result.unavailable_reason())
    assert result.ok, f"agent exited {result.returncode}; see {result.log_path}"

    # --- structural artifacts ---
    artifacts = ws.glob("**/*.md")

    # --- optional LLM judge ---
    verdict = judge(
        artifact=artifacts[0].read_text(encoding="utf-8") if artifacts else result.stdout,
        criteria=(
            "Describe concretely what a good result looks like. Be strict: "
            "score 1.0 only if ALL criteria are met, 0.5 for partial."
        ),
        threshold=0.7,
    )

    # --- binary rubric ---
    rubric(
        ("produced at least one artifact", bool(artifacts)),
        check_judge("artifact is on-topic and well-formed", verdict),
    ).assert_passed(log_path=result.log_path)

    # --- numeric metric tracked over time ---
    metric(
        "judge_score", verdict.score,
        direction="higher_is_better", unit="score",
        baseline_strategy="rolling_mean", tolerance=0.1,
    )

---
name: eval-author
description: "Entry workflow for creating evalpilot evals for Copilot agents and skills. Bootstraps evals/, discovers targets, writes pytest rubric and metric tests, and hands off to eval-runner. Trigger keywords: create evals, author evals, test my agent, test my skill, evalpilot, rubric, metric, regression."
argument-hint: "<agent or skill name / scenario>"
user-invocable: true
---

# Eval Author (entry skill)

Use this skill when the user asks to create evals for a Copilot agent, agent pack, or skill. You are authoring pytest tests for the host repository; the Python engine lives in the `evalpilot` package and must already be installed or installed from this plugin's `engine/` directory. Do **not** modify the engine.

## Workflow

1. **Bootstrap the repo**
   - Ensure `evalpilot` is importable. If not, install from the plugin engine:
     - development checkout: `pip install -e <plugin>/engine`
     - installed plugin copy: `pip install <plugin>/engine`
   - If `evals/` does not exist, run `evalpilot init`. It scaffolds sample tests under `evals/packs/_example/` and `evals/skills/_example/`.
2. **Discover targets**
   - Run `evalpilot discover` (or `evalpilot discover --json` if you need machine-readable output).
   - Choose `evals/packs/<agent>/test_*.py` for an agent/pack, or `evals/skills/<skill>/test_*.py` for a skill.
3. **Author both result types**
   - A binary **rubric** with structural checks plus, when useful, `judge(...)` and `check_judge(...)`.
   - At least one numeric **metric** via the `metric` fixture for trend tracking.
4. **Hand off to execution**
   - Load/use `eval-runner`, or run `evalpilot run <target>` directly.
   - For metric trend interpretation, load/use `eval-metrics` or run `evalpilot metrics`.

## Authoring Rules

- Never put the expected answer in the SUT prompt; make the agent solve the task.
- Keep judge criteria strict and concrete. Say what earns 1.0 and what partial credit means.
- Always include `result.log_path` in failure messages: `assert result.ok, f"... {result.log_path}"`, `rubric(...).assert_passed(log_path=result.log_path)`, and `m.assert_no_regression(log_path=result.log_path)`.
- If `result.usable` is false, skip with `pytest.skip(result.unavailable_reason())` so timeouts or `EVALPILOT_SKIP_SUT` are reported clearly.
- Add markers: `@pytest.mark.pack` or `@pytest.mark.skill`, plus `slow`, `judge`, and/or `metric` as appropriate.
- Prefer stable artifacts and structural assertions before asking the judge.
- Record metrics that are meaningful over time: score, latency, word count, artifact count, coverage ratio, token/cost proxy.

## Worked Example: Agent Rubric + Judge Score Metric

```python
from __future__ import annotations

import pytest

from evalpilot import check_judge, rubric

AGENT_NAME = "my-agent"
PROMPT = "Create a concise migration plan for moving a Python CLI from argparse to Typer."


@pytest.mark.pack
@pytest.mark.slow
@pytest.mark.judge
@pytest.mark.metric
def test_agent_migration_plan(agent_pack, judge, metric):
    ws = agent_pack(AGENT_NAME)

    result = ws.run_agent(prompt=PROMPT, agent=AGENT_NAME, timeout=600)
    if not result.usable:
        pytest.skip(result.unavailable_reason())
    assert result.ok, f"agent exited {result.returncode}; see {result.log_path}"

    artifact = result.stdout
    verdict = judge(
        artifact=artifact,
        criteria=(
            "Score 1.0 only if the response includes ordered migration steps, "
            "calls out compatibility risks, and names tests to run. Score 0.5 "
            "for partial coverage. Score 0.0 if it is generic or off-topic."
        ),
        threshold=0.7,
    )

    r = rubric(
        ("produced non-empty output", bool(artifact.strip())),
        ("mentions tests", "test" in artifact.lower()),
        check_judge("plan is specific and complete", verdict),
    )
    r.assert_passed(log_path=result.log_path)

    metric(
        "judge_score", verdict.score,
        direction="higher_is_better", unit="score",
        baseline_strategy="rolling_mean", tolerance=0.1,
    )
```

## Worked Example: Skill Metric Gate

```python
from __future__ import annotations

import pytest

from evalpilot import rubric

SKILL_NAME = "my-skill"
PROMPT = "Summarize the repo's release checklist in five bullets."


@pytest.mark.skill
@pytest.mark.slow
@pytest.mark.metric
def test_skill_response_size(skill, metric):
    ws = skill(SKILL_NAME)

    result = ws.run_skill(skill=SKILL_NAME, prompt=PROMPT, timeout=300)
    if not result.usable:
        pytest.skip(result.unavailable_reason())
    assert result.ok, f"skill exited {result.returncode}; see {result.log_path}"

    words = len(result.stdout.split())
    rubric(
        ("produced output", bool(result.stdout.strip())),
        ("kept response concise", words <= 160, f"words={words}"),
    ).assert_passed(log_path=result.log_path)

    m = metric(
        "response_words", words,
        direction="lower_is_better",
        baseline_strategy="last",
        tolerance_pct=0.25,
    )
    m.assert_no_regression(log_path=result.log_path)
```

## References

- [Fixtures, markers, and environment](references/fixtures-markers-env.md)
- [Metric baselines and tolerances](references/metric-baselines.md)

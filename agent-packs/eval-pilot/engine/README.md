# evalpilot

Portable, repo-agnostic eval engine for GitHub Copilot agents and skills.
Ships inside the **eval-pilot** Copilot plugin and is also a standalone,
pip-installable Python package.

It gives you two kinds of result:

- **Rubric** — binary pass/fail checks (structural asserts + LLM-as-judge).
- **Metric** — numeric values appended to committed **JSONL history** and
  compared against a baseline so regressions surface over time.

## Install

```bash
pip install -e .          # from this engine/ directory
# or, from the installed plugin:
pip install ~/.copilot/installed-plugins/eval-pilot/engine
```

## Quick start

```bash
cd your-repo
evalpilot discover         # what agents/skills can it see?
evalpilot init             # scaffold evals/ (sample rubric + metric tests)
evalpilot run              # run the suite (pytest under the hood)
evalpilot metrics          # show numeric trends
evalpilot metrics --check  # exit non-zero on regression (CI gate)
```

## Authoring an eval

```python
from evalpilot import rubric, check_judge

def test_my_agent(agent_pack, judge, metric):
    ws = agent_pack("my-agent")
    res = ws.run_agent(prompt="...", agent="my-agent", timeout=600)
    assert res.ok, res.log_path

    artifact = ws.find_one("**/output.md").read_text()
    verdict = judge(artifact=artifact, criteria="...strict criteria...")

    rubric(
        ("output exists", bool(artifact)),
        check_judge("on-topic", verdict),
    ).assert_passed(log_path=res.log_path)

    metric("judge_score", verdict.score, direction="higher_is_better",
           baseline_strategy="rolling_mean", tolerance=0.1)
```

## Fixtures (auto-registered pytest plugin)

| Fixture | Purpose |
|---|---|
| `workspace` | bare isolated workspace |
| `agent_pack(name)` | workspace with an agent (+ plugin skills) staged |
| `skill(name)` | workspace with one skill staged |
| `judge` | LLM-as-judge callable |
| `metric` | record a numeric metric bound to the test id |
| `sut` | the active SUT runner |

## Configuration (environment)

| Variable | Effect |
|---|---|
| `EVALPILOT_REPO_ROOT` | override the detected repo root |
| `EVALPILOT_EVAL_ROOT` | override the `evals/` location |
| `EVALPILOT_METRICS_ROOT` | override the metric history location |
| `EVALPILOT_RUNNER` | select the SUT runner (default `copilot`) |
| `EVALPILOT_JUDGE_THRESHOLD` | default judge pass threshold (0.7) |
| `EVALPILOT_SKIP_SUT` | don't launch the SUT (deterministic skips) |
| `EVALPILOT_SUT_TIMEOUT` | clamp every SUT subprocess timeout |
| `COPILOT_BIN` | path to the `copilot` binary |

## Pluggable SUT runners

The Copilot CLI runner is built in. Add another runtime by subclassing
`evalpilot.runners.base.SUTRunner`, decorating it with `@register_runner`,
and selecting it via `EVALPILOT_RUNNER`.

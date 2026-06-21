# Fixtures, Markers, and Environment

## Pytest Fixtures

| Fixture | Purpose |
|---|---|
| `evalpilot_config` | Session-scoped resolved `Config`. |
| `sut` | The active `SUTRunner`. |
| `workspace` | Bare isolated `Workspace`; tests stage what they need. |
| `agent_pack(name)` | Factory returning a workspace with the named agent staged. Pass `include_skills=False` to stage only the agent. |
| `skill(name)` | Factory returning a workspace with the named skill staged. |
| `judge` | LLM-as-judge callable: `judge(artifact=..., criteria=..., threshold=..., golden=..., timeout=...)`. |
| `metric` | Records a metric bound to the pytest node id: `metric(name, value, **kwargs)`. |

## Workspace and RunResult API

Common workspace methods:

- `ws.run_agent(prompt=..., agent=..., timeout=600, log_name="agent")`
- `ws.run_skill(skill=..., prompt=..., timeout=300, log_name="skill")`
- `ws.glob("**/*.md")`
- `ws.find_one("**/artifact.md")`
- `ws.read("relative/path.txt")`

`RunResult` fields: `returncode`, `stdout`, `stderr`, `duration_seconds`, `log_path`, `timed_out`, `skipped`, `extra`; properties: `ok`, `usable`; method: `unavailable_reason()`.

## Markers

| Marker | Meaning |
|---|---|
| `pack` | Exercises a full agent pack/plugin. |
| `skill` | Exercises a single skill in isolation. |
| `judge` | Invokes LLM-as-judge; slower and token-consuming. |
| `slow` | Takes >60s; deselect with `-m "not slow"`. |
| `tooling` | Fast, no-LLM tooling smoke eval. |
| `metric` | Records a numeric metric tracked over time. |

## Environment Variables

| Variable | Effect |
|---|---|
| `EVALPILOT_REPO_ROOT` | Override detected repository root. |
| `EVALPILOT_EVAL_ROOT` | Override `evals/` location. |
| `EVALPILOT_METRICS_ROOT` | Override metric history location. |
| `EVALPILOT_RUNNER` | Select SUT runner; default is `copilot`. |
| `EVALPILOT_JUDGE_THRESHOLD` | Default judge pass threshold; default is `0.7`. |
| `EVALPILOT_SKIP_SUT` | Do not launch the SUT; live SUT tests produce skipped results. |
| `EVALPILOT_SUT_TIMEOUT` | Clamp every SUT subprocess timeout. |
| `COPILOT_BIN` | Path to the `copilot` binary. |

The engine also accepts legacy aliases `EVALS_SKIP_SUT`, `EVALS_SUT_TIMEOUT`, and `EVAL_JUDGE_THRESHOLD` in the runner/judge paths.

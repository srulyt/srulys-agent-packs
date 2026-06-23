# Eval Authoring (eval-pilot pytest plugin)

This is the cross-cutting reference for authoring evals against the
**eval-pilot** pytest plugin. Read it once; then copy the eval-pilot
examples or the `evals/packs/product-brief/` migrated pack pattern and
fill in the blanks.

## Mental model

An eval is a pytest test. It:

1. **Creates** an eval-pilot workspace through a fixture such as
   `agent_pack("<entry-agent>")` or `skill("<skill-name>")`.
2. **Stages** any scenario-specific input files into that workspace.
3. **Runs** the system-under-test through eval-pilot's SUT runner
   (`ws.run_agent(...)` or `ws.run_skill(...)`).
4. **Skips clearly** when the SUT is unavailable:
   `if not result.usable: pytest.skip(result.unavailable_reason())`.
5. **Asserts** on artifacts the SUT produced (file existence, counts,
   content), always citing `result.log_path` for triage.
6. **Optionally** calls the eval-pilot `judge(...)` fixture for
   LLM-as-judge semantic scoring, and records metrics when appropriate.

Eval-pilot lives at `agent-packs/eval-pilot/`; install its bundled
engine (`pip install -e agent-packs/eval-pilot/engine`) before running
`evalpilot` commands or pytest tests that use its fixtures.

## Required directory shape per generated pack

```
evals/packs/<pack>/
├── README.md                          # what these evals cover + run command
├── conftest.py                        # re-exports eval-pilot fixtures
└── test_smoke_<happy-path>.py         # at least one smoke eval per pack
```

Pack-local `conftest.py` pattern:

```python
from __future__ import annotations

from evalpilot.pytest_plugin import agent_pack, judge  # noqa: F401
```

For skill evals (no pack required):

```
evals/skills/<skill>/
├── conftest.py                        # re-exports skill/judge/metric as needed
└── test_<scenario>.py
```

Skill-local `conftest.py` pattern:

```python
from __future__ import annotations

from evalpilot.pytest_plugin import judge, metric, skill  # noqa: F401
```

## Pack eval template

Base new tests on eval-pilot's examples (`evalpilot init` scaffolds
`evals/packs/_example/`) or the migrated `evals/packs/product-brief/`
suite. Skeleton:

```python
from __future__ import annotations

import pytest

from evalpilot import check_judge, rubric

AGENT_NAME = "<entry-agent>"
PROMPT = """\
... user prompt that exercises the scenario ...
"""


@pytest.mark.pack
@pytest.mark.slow
@pytest.mark.judge
def test_<scenario>(agent_pack, judge):
    ws = agent_pack(AGENT_NAME)

    result = ws.run_agent(prompt=PROMPT, agent=AGENT_NAME, timeout=600)
    if not result.usable:
        pytest.skip(result.unavailable_reason())
    assert result.ok, f"agent exited {result.returncode}; see {result.log_path}"

    # 1) Structural assertions
    artifacts = ws.glob("<glob-pattern>")
    assert artifacts, f"expected at least one artifact; see {result.log_path}"

    # 2) Optional LLM judge
    verdict = judge(
        artifact=artifacts[0].read_text(encoding="utf-8"),
        criteria="<concrete description of what 'good' looks like>",
        threshold=0.7,
    )

    rubric(
        ("produced expected artifact", bool(artifacts)),
        check_judge("artifact satisfies scenario", verdict),
    ).assert_passed(log_path=result.log_path)
```

## Skill eval template

Base new tests on eval-pilot's examples (`evalpilot init` scaffolds
`evals/skills/_example/`). Skeleton:

```python
from __future__ import annotations

import pytest

from evalpilot import rubric

SKILL_NAME = "<skill-name>"
PROMPT = """\
... small task that exercises the skill ...
"""


@pytest.mark.skill
@pytest.mark.slow
def test_<scenario>(skill):
    ws = skill(SKILL_NAME)
    result = ws.run_skill(skill=SKILL_NAME, prompt=PROMPT, timeout=300)
    if not result.usable:
        pytest.skip(result.unavailable_reason())
    assert result.ok, f"skill exited {result.returncode}; see {result.log_path}"

    rubric(
        ("produced output", bool(result.stdout.strip())),
    ).assert_passed(log_path=result.log_path)
```

## Fixtures available (provided by eval-pilot)

| Fixture | Returns | Use for |
|---|---|---|
| `workspace` | bare `Workspace` | custom staging |
| `agent_pack(name)` | `Workspace` with the named agent and supporting skills staged | pack evals |
| `skill(name)` | `Workspace` with one skill staged | skill evals |
| `judge` | `judge(artifact=, criteria=, threshold=)` callable | LLM-as-judge |
| `metric` | metric recorder bound to the current pytest nodeid | numeric trend tracking |

`Workspace` exposes `run_agent`, `run_skill`, `glob`, `find_one`,
`read`, and `stage_files`. Logs are written under the test workspace's
configured `_logs/` directory and the path is on `result.log_path`.

## Markers

| Marker | Meaning |
|---|---|
| `pack` | exercises a full agent pack/plugin |
| `skill` | exercises a single skill in isolation |
| `judge` | invokes the LLM-as-judge (slower, costs LLM tokens) |
| `slow` | takes > 60s; deselect with `-m "not slow"` |
| `tooling` | fast, no-LLM tooling smoke evals |
| `metric` | records a numeric metric tracked over time |

Always tag pack/skill evals with `pack`/`skill`. Tag with `judge` if
the test calls the `judge` fixture. Tag with `slow` if it shells out
to Copilot (almost always true for `pack` and `skill` evals). Tag with
`metric` if it records metric history.

## Hard rules (do not violate)

- One eval per `test_<scenario>` function. Don't bundle multiple
  scenarios in one test -- make them separate tests so failures isolate.
- Always include `result.log_path` in failure messages. Operators
  inspect it to debug.
- Always skip unusable SUT results with
  `pytest.skip(result.unavailable_reason())` so `EVALPILOT_SKIP_SUT`,
  missing `copilot`, or timeouts are reported clearly.
- Never put expected-answer text in the user prompt. The whole point
  of judging is that the SUT had to figure it out.
- Be **strict** in `criteria`. A loose criteria string = a useless
  judge call. Score 1.0 only when ALL criteria are met; explicit
  partial-credit anchors at 0.5/0.6 are recommended.
- Always quote YAML `description` fields in any agent files you
  generate alongside the eval (the agent-builder rule).

## Running locally

```powershell
pip install -e agent-packs/eval-pilot/engine

evalpilot run evals/                         # everything
evalpilot run evals/packs/<pack>/            # one pack
evalpilot run evals/skills/<skill>/          # one skill
evalpilot run evals/ -k <substring>          # by name
evalpilot run evals/ -m "not slow"           # marker expression
evalpilot run evals/ --parallel 4            # xdist workers

# Direct pytest also works because eval-pilot registers a pytest plugin:
pytest evals/packs/<pack>/ -v
```

Useful environment knobs:

- `COPILOT_BIN` points eval-pilot at a specific `copilot` binary.
- `EVALPILOT_SUT_TIMEOUT` clamps SUT subprocess timeouts.
- `EVALPILOT_SKIP_SUT=1` prevents launching the SUT; behavioural tests
  should skip through `result.usable` / `result.unavailable_reason()`.
- `EVALPILOT_RUNNER` selects a registered SUT runner; default is `copilot`.

## Running for the factory fix-loop

The factory should run the target through eval-pilot:

```powershell
evalpilot run evals/packs/<pack>
```

`evalpilot run` wraps pytest, writes `evals/_runs/latest-report.jsonl`,
prints a pass/fail/skip summary, and returns pytest's exit code (`0`
for pass, `1` for test failure, other pytest exit codes for collection
or harness errors). If the factory needs a custom report-log path, it
may invoke pytest directly with the eval-pilot plugin installed:

```powershell
pytest evals/packs/<pack>/ --report-log=<out>.jsonl -v --tb=short
```

## Hard checklist for the Factory Engineer

- [ ] `evals/packs/<pack>/conftest.py` re-exports the eval-pilot
      fixtures the tests use (at minimum `agent_pack` and `judge` for
      judged pack evals).
- [ ] `evals/packs/<pack>/test_smoke_<happy-path>.py` exists.
- [ ] At least one structural `assert` (artifact exists, count matches).
- [ ] Every SUT run checks `result.usable` and skips with
      `pytest.skip(result.unavailable_reason())` when unavailable.
- [ ] At least one `judge(...)` call unless the eval is purely
      structural and that is appropriate for the scenario.
- [ ] Every assertion that can fail mentions `result.log_path` so
      operators can find the log.
- [ ] Markers applied: `@pytest.mark.pack` (or `skill`), plus `slow`,
      `judge`, and/or `metric` if applicable.
- [ ] Eval files appear under `files_created` and `evals_created.tests`
      in the build manifest.
- [ ] `pytest --collect-only evals/packs/<pack>/` succeeds.

## Source of truth

When this pack is deployed standalone, this reference is authoritative
for factory-generated eval shape. In the `srulyt/srulys-agent-packs`
monorepo, the runtime source of truth is the eval-pilot plugin under
`agent-packs/eval-pilot/`: its `README.md`, `skills/eval-author/SKILL.md`,
`skills/eval-runner/SKILL.md`, and engine fixtures in
`engine/src/evalpilot/pytest_plugin.py`.

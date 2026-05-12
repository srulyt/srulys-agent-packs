# Eval Authoring (pytest framework)

This is the cross-cutting reference for authoring evals against the
**pytest-based eval framework** that lives in `evals/`. Read it once;
then copy a template and fill in the blanks.

## Mental model

An eval is a pytest test. It:

1. **Stages** a workspace (a tmpdir with the pack or skill copied in).
2. **Runs** the system-under-test by shelling out to `copilot -p ...`.
3. **Asserts** on artifacts the SUT produced (file existence, counts,
   content).
4. **Optionally** calls a tiny `judge(...)` helper for LLM-as-judge
   semantic scoring.

That's it. Each `test_*.py` is self-contained and readable
top-to-bottom.

## Required directory shape per generated pack

```
evals/packs/<pack>/
├── README.md                          # what these evals cover
└── test_smoke_<happy-path>.py         # at least one smoke eval per pack
```

For skill evals (no pack required):

```
evals/skills/<skill>/
└── test_<scenario>.py
```

## Pack eval template

Copy from `evals/_templates/test_pack_eval.py.template`. Skeleton:

```python
import pytest

PROMPT = """\
... user prompt that exercises the scenario ...
"""

@pytest.mark.pack
@pytest.mark.slow
@pytest.mark.judge
def test_<scenario>(copilot_pack, judge):
    ws = copilot_pack("<pack-name>")

    result = ws.run_agent(
        prompt=PROMPT,
        agent="<orchestrator-name>",
        timeout=900,
    )
    assert result.ok, f"see {result.log_path}"

    # 1) Structural assertions
    artifacts = ws.glob("<glob-pattern>")
    assert artifacts, "expected at least one artifact"

    # 2) Optional LLM judge
    verdict = judge(
        artifact=artifacts[0].read_text(encoding="utf-8"),
        criteria="<concrete description of what 'good' looks like>",
        threshold=0.7,
    )
    assert verdict.passed, verdict.reasoning
```

## Skill eval template

Copy from `evals/_templates/test_skill_eval.py.template`. Skeleton:

```python
import pytest

PROMPT = """\
... small task that exercises the skill ...
"""

@pytest.mark.skill
@pytest.mark.slow
@pytest.mark.judge
def test_<scenario>(copilot_skill, judge):
    ws = copilot_skill("<skill-name>")
    result = ws.run_skill(skill="<skill-name>", prompt=PROMPT, timeout=300)
    assert result.ok, f"see {result.log_path}"

    verdict = judge(
        artifact=result.stdout,
        criteria="<what correct skill output looks like>",
        threshold=0.7,
    )
    assert verdict.passed, verdict.reasoning
```

## Fixtures available (provided by `evals/conftest.py`)

| Fixture | Returns | Use for |
|---|---|---|
| `workspace` | bare `Workspace` | custom staging |
| `copilot_pack(name)` | `Workspace` with the pack staged | pack evals |
| `copilot_skill(name)` | `Workspace` with one skill staged | skill evals |
| `judge` | `judge(artifact=, criteria=, threshold=)` callable | LLM-as-judge |

`Workspace` exposes `run_agent`, `run_skill`, `glob`, `find_one`,
`read`, `stage_files`. Logs land under `<workspace>/_logs/<name>.log`
and the path is on `result.log_path`.

## Markers

| Marker | Meaning |
|---|---|
| `pack` | exercises a full agent pack |
| `skill` | exercises a single skill in isolation |
| `judge` | invokes the LLM-as-judge (slower, costs LLM tokens) |
| `slow` | takes > 60s; CI runs them, locals can `pytest -m "not slow"` |

Always tag pack/skill evals with `pack`/`skill`. Tag with `judge` if
the test calls the `judge` fixture. Tag with `slow` if it shells out
to `copilot` (almost always true for `pack` and `skill` evals).

## Hard rules (do not violate)

- One eval per `test_<scenario>` function. Don't bundle multiple
  scenarios in one test -- make them separate tests so failures isolate.
- Always include `result.log_path` in failure messages. Operators
  inspect it to debug.
- Never put expected-answer text in the user prompt. The whole point
  of judging is that the SUT had to figure it out.
- Be **strict** in `criteria`. A loose criteria string = a useless
  judge call. Score 1.0 only when ALL criteria are met; explicit
  partial-credit anchors at 0.5/0.6 are recommended.
- Always quote YAML `description` fields in any agent files you
  generate alongside the eval (the agent-builder rule).

## Running locally

```powershell
pip install -r evals/requirements.txt

pytest evals/                                 # everything
pytest evals/packs/<pack>/                    # one pack
pytest evals/skills/<skill>/                  # one skill
pytest evals/ -k <substring>                  # by name
pytest evals/ -m "not slow"                   # skip LLM-driven
pytest evals/ -n auto                         # parallel
```

## Running for the factory fix-loop

The factory invokes pytest with `--report-log` so it can parse the
verdict programmatically:

```powershell
pytest evals/packs/<pack>/ --report-log=<out>.jsonl -v
```

Exit codes: `0` = pass, `1` = at least one test failed, `>1` =
collection or harness error. `<out>.jsonl` contains one JSON line per
event (collection, test start, test result) with full `longrepr`
failure traces.

## Hard checklist for the Factory Engineer

- [ ] `evals/packs/<pack>/test_smoke_<happy-path>.py` exists.
- [ ] At least one structural `assert` (artifact exists, count matches).
- [ ] At least one `judge(...)` call (unless the eval is purely
      structural and that is appropriate for the scenario).
- [ ] Every assertion that can fail mentions `result.log_path` so
      operators can find the log.
- [ ] Markers applied: `@pytest.mark.pack` (or `skill`), plus `slow`
      and `judge` if applicable.
- [ ] Eval file appears under `files_created` and `evals_created.tests`
      in the build manifest.
- [ ] `pytest --collect-only evals/packs/<pack>/` succeeds.

## Source of truth

When this pack is deployed standalone, this reference is authoritative.
When it ships inside the `srulyt/srulys-agent-packs` monorepo, the
in-repo `evals/README.md` is the runtime source of truth (it documents
environment variables, fixture internals, and CI integration).

# `evals/` — pytest-based eval framework

> **Portable version:** the engine behind this harness is packaged as the
> **`eval-pilot`** Copilot plugin (`agent-packs/eval-pilot/`) so any repo with
> agents/skills can install it (`pip install` the bundled `evalpilot` engine)
> and ask Copilot to *create and run evals* — both binary **rubric** pass/fail
> checks and numeric **metric** results tracked over time in committed JSONL
> history. This in-repo `evals/` **dogfoods** that package: `_lib/judge.py` and
> `_lib/asserts.py` now re-export from `evalpilot`, so there is a single source
> of truth. See `agent-packs/eval-pilot/README.md`.

An eval is a pytest test. To run all evals:

```powershell
pip install -r evals/requirements.txt
pytest evals/                                 # everything
pytest evals/packs/copilot-factory/           # one pack
pytest evals/skills/agent-builder/            # one skill
pytest evals/ -k issue_triage                 # by name
pytest evals/ -m "not slow"                   # fast ones only
pytest evals/ -n auto                         # parallel
```

For a friendlier wrapper that takes a pack name + optional test
selectors, persists each run under `evals/_runs/<timestamp>/`, and
prints a focused failure summary (assertion + agent.log path +
workspace path), use `eval.cmd` from the repo root:

```powershell
.\eval.cmd story-telling-agent                       # all evals in the pack
.\eval.cmd story-telling-agent critical_gaps         # one named eval
.\eval.cmd story-telling-agent buy_in_deck qa_loop   # multiple selectors
.\eval.cmd agent-builder                             # works for skills too
.\eval.cmd spec-author --list                        # show what would run
.\eval.cmd copilot-factory --parallel 1              # serial (easier to read)
.\eval.cmd --all                                     # the whole suite
```

Failures show pytest's standard output: assertion message, captured
stdout/stderr, and the path to the per-run log file.

> Migrating from the old YAML harness? See
> [`MIGRATION_NOTES.md`](MIGRATION_NOTES.md) for what changed and which
> legacy cases were intentionally not ported.

## Layout

```
evals/
├── pyproject.toml         # pytest config (testpaths, markers, norecursedirs)
├── requirements.txt       # pytest, pytest-xdist, pytest-html, pytest-reportlog
├── conftest.py            # shared fixtures: workspace, copilot_pack, copilot_skill, judge
├── _lib/                  # subprocess wrappers, judge helper
├── _templates/            # copy these to author a new eval
├── packs/<pack>/test_*.py # one file per pack eval
├── skills/<skill>/test_*.py # one file per skill-in-isolation eval
└── static/                # static linters (pack contract, _lib smoke tests)
```

## Anatomy of an eval

```python
# evals/packs/copilot-factory/test_smoke_issue_triage.py
import pytest

@pytest.mark.pack
@pytest.mark.slow
@pytest.mark.judge
def test_creates_two_agent_triage_pack(copilot_pack, judge):
    ws = copilot_pack("copilot-factory")          # stages pack into tmpdir

    result = ws.run_agent(                         # shells out to `copilot -p ...`
        prompt="Design and build a 2-agent issue triage pack...",
        agent="copilot-factory",
        timeout=900,
    )
    assert result.ok, f"see {result.log_path}"     # log preserved on failure

    arch = ws.find_one(".copilot-factory/sessions/*/artifacts/architecture.md")

    verdict = judge(                               # LLM-as-judge
        artifact=arch.read_text(),
        criteria="Architecture must describe exactly 2 agents named...",
        threshold=0.7,
    )
    assert verdict.passed, verdict.reasoning
```

A maintainer reads this top-to-bottom and understands the eval in
~30 seconds.

## Authoring a new eval

1. Copy a template into the right directory:
   - Pack eval: `evals/_templates/test_pack_eval.py.template` →
     `evals/packs/<pack>/test_<scenario>.py`
   - Skill eval: `evals/_templates/test_skill_eval.py.template` →
     `evals/skills/<skill>/test_<scenario>.py`
2. Edit the placeholders (prompt, agent name, structural assertions,
   judge criteria).
3. Run it: `pytest evals/packs/<pack>/test_<scenario>.py -v`.
4. Iterate: tighten the criteria, add structural assertions, mark
   `@pytest.mark.slow` if the test takes > 60s.

## Fixtures provided by `conftest.py`

| Fixture | Returns | Use for |
|---|---|---|
| `workspace` | bare `Workspace` | custom staging |
| `copilot_pack(name)` | `Workspace` with the pack staged | pack evals |
| `copilot_skill(name)` | `Workspace` with one skill staged | skill evals |
| `judge` | `judge(artifact=, criteria=, threshold=)` callable | LLM-as-judge |

The `judge` fixture re-exports `evalpilot.judge`, which stages the
bundled `eval-judge` agent (shipped as `evalpilot` package data) and
invokes it via Copilot CLI. Logs and the raw judge response are
persisted under the test's pytest tmp_path for debugging. (The legacy
standalone judge under `agent-packs/eval-framework/` is superseded by
this bundled agent.)

## Logs and failure analysis

- Each `run_agent` / `run_skill` call writes a combined stdout+stderr
  log to `<workspace>/_logs/<name>.log` and returns its path on
  `result.log_path`. Tests should include this path in assertion
  messages.
- pytest preserves the last few `tmp_path` directories per test under
  `$TMPDIR/pytest-of-<user>/`, so failed workspaces stay inspectable.
- The `eval.cmd` wrapper additionally writes the full pytest console
  output to `evals/_runs/<timestamp>/console.log` and a structured
  per-test JSONL to `evals/_runs/<timestamp>/report.jsonl` so a
  follow-up agent or CI step can parse results without rerunning
  anything.
- For ad-hoc CI runs, `pytest --report-log=evals.jsonl` produces the
  same structured output as the wrapper.

## Static pack-contract linter

`scripts/lint_pack.py` validates each agent pack's `.agent.md` and
`SKILL.md` files (front-matter shape, required keys, soft size caps).
It's wired into pytest as `evals/static/test_pack_contract.py` so it
runs alongside the rest of the suite. Run standalone with:

```powershell
python -m scripts.lint_pack --all
python -m scripts.lint_pack copilot-factory
python -m scripts.lint_pack copilot-factory --strict   # warnings = errors
```

## Markers

| Marker | Meaning |
|---|---|
| `pack` | exercises a full agent pack |
| `skill` | exercises a single skill in isolation |
| `judge` | invokes the LLM-as-judge (slower, costs LLM tokens) |
| `slow` | takes > 60s; use `pytest -m "not slow"` to skip |

## Environment

| Variable | Effect |
|---|---|
| `COPILOT_BIN` | Override the path to the `copilot` binary |
| `EVAL_JUDGE_THRESHOLD` | Default judge pass threshold (default `0.7`) |
| `EVAL_GLOBAL_TIMEOUT_SEC` | Wall-clock safety backstop for `eval.cmd` runs (default `14400` = 4h; set `0` to disable). Per-test timeouts in `pyproject.toml` are the primary safety net. |
| `TMPDIR` | Where pytest puts per-test workspaces |

If `copilot` is not on `PATH` (and `COPILOT_BIN` is unset), evals that
need it are auto-skipped; static tests still run.

## Timeouts and failure isolation

The harness uses three layers of timeout, in order of preference:

1. **Per-test pytest-timeout** (the primary safety net): configured in
   `evals/pyproject.toml` (`timeout = 1500`, `timeout_method = "thread"`).
   A single hung Copilot subprocess kills only that test, not the whole
   run. Override per test with `@pytest.mark.timeout(seconds)`.
2. **Per-subprocess `run_agent` / `run_skill` timeout**: each call passes
   `timeout=<seconds>` to the Copilot CLI subprocess; the harness kills
   the whole process tree on timeout via `psutil`.
3. **Global wall-clock backstop in `eval.cmd`**: `--global-timeout`
   (env: `EVAL_GLOBAL_TIMEOUT_SEC`, default 4h). Only fires if a test
   escapes pytest-timeout — set to `0` to disable.

### Windows runtime crashes

Known fatal Windows exit codes (`STATUS_ACCESS_VIOLATION`,
`STATUS_STACK_OVERFLOW`, `STATUS_STACK_BUFFER_OVERRUN`) are surfaced
via `CopilotResult.crash` and the `CopilotProcessCrash` exception
class. When a test fails on `assert result.ok`, check `result.crash`
first — a non-None value means the CLI itself crashed and the agent
prompt is NOT at fault.

### Missing fixture diagnostics

`Workspace.find_one` raises `FixtureMissingError` (an `AssertionError`
subclass) when zero matches are found, with a list of the closest
existing paths in the workspace to help spot a typo or a missing
fixture file.

### Whitespace-tolerant prose assertions

`evals/_lib/asserts.py` provides `assert_prose_contains` /
`assert_prose_not_contains` which normalise whitespace before
comparing. Use them for free-form prose (bait sentences, persona
descriptions); keep plain `assert ... in text` for structural
literals (headings, `Status:` fields, `FR-NN`, `[Deprecated]`).

# evalpilot

A generic, easy-to-use eval framework for GitHub Copilot agents and skills.
Ships inside the **eval-pilot** Copilot plugin and is also a standalone,
pip-installable Python package.

You describe an eval once — as a Markdown `*.eval.md` file or a fluent Python
builder — and evalpilot runs it, produces a **modeled result**, and renders that
result to the terminal, a self-contained HTML report, and canonical JSON. It
gives you two kinds of signal:

- **Assertions + judge** — binary pass/fail (structural checks + LLM-as-judge).
- **Metrics** — numeric values appended to committed **JSONL history** and
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
evalpilot discover                                   # what can it see?
evalpilot init                                       # scaffold evals/
evalpilot new my-eval --target my-agent --kind agent # create a spec
evalpilot lint                                       # validate (no SUT)
evalpilot run                                        # execute + render
evalpilot show --format html --open                  # open the report
evalpilot metrics --check                            # regression gate (CI)
```

`EVALPILOT_RUNNER=mock` runs the entire pipeline offline (no `copilot`, no
tokens) — the engine's own tests and the `new`→`run` demo use it.

## Authoring an eval — Markdown DSL

```markdown
---
name: my-agent-migration-plan
target: my-agent
kind: agent
tags: [smoke, judge]
timeout: 600
---

# Produces a concrete migration plan
> One-line summary (compact view).

## Description
Optional multi-paragraph, human-readable explanation of the scenario and the
expected outcome. A file with only a title + summary + `## Description` (no
`## Act`/`## Assert`) is a valid *stub* — `evalpilot lint` reports it as
`[stub]` rather than an error, so you can write intent first and implement the
executable sections (or have an agent implement them) later.

## Act
```prompt
Create a concise migration plan for moving a Python CLI from argparse to Typer.
```

## Assert
```yaml
files:
  exists: ["**/*.md"]
contains:
  - { text: "test", ignore_case: true }
judge:
  threshold: 0.7
  criteria: |
    Ordered steps + compatibility risks + named tests earns 1.0; 0.5 partial.
metrics:
  - { name: judge_score, value: $judge.score, direction: higher_is_better,
      baseline: rolling_mean, tolerance: 0.1 }
```
```

## Authoring an eval — Python builder

```python
from evalpilot import Eval

eval = (
    Eval("my-agent-migration-plan", target="my-agent", kind="agent",
         tags=["smoke", "judge"], timeout=600)
    .describe("Produces a concrete migration plan.")
    .prompt("Create a concise migration plan for argparse -> Typer.")
    .expect_file("**/*.md")
    .judge("Ordered steps + risks + named tests earns 1.0.", threshold=0.7)
    .metric("judge_score", "$judge.score",
            direction="higher_is_better", baseline="rolling_mean", tolerance=0.1)
    .build()
)
```

## The modeled result

Every run produces an `EvalRunReport` (`evals/_runs/<run-id>/report.json`) made
of `EvalResult`s, each holding assertion results, judge verdicts, metric
records, timings, and log paths. The terminal, HTML, and JSON renderers are pure
projections of this one object, so the JSON is the source of truth and
`evalpilot show` re-renders any past run without re-executing it.

## Extending the assertion vocabulary

Built-ins: `file_exists`, `file_absent`, `glob_count`, `contains`,
`not_contains`, `prose_contains`, `stdout_contains`, `matches`, `json_path`,
`json_empty`, `section_contains`, `section_not_contains`, `custom`. Register
new kinds with the `@assertion` decorator:

```python
from evalpilot.assertions import assertion, AssertContext
from evalpilot.model import AssertionResult

@assertion("has_two_headings")
def _(ctx: AssertContext, args: dict):
    n = ctx.stdout.count("\n# ")
    return AssertionResult(kind="has_two_headings", name="has_two_headings",
                           passed=n >= 2, detail=f"found {n} headings")
```

The Python builder's `.check(name, predicate)` is a per-eval escape hatch, so no
eval is ever blocked by the DSL.

## Configuration (environment)

| Variable | Effect |
|---|---|
| `EVALPILOT_REPO_ROOT` | override the detected repo root |
| `EVALPILOT_EVAL_ROOT` | override the `evals/` location |
| `EVALPILOT_METRICS_ROOT` | override the metric history location |
| `EVALPILOT_RUNNER` | select the SUT runner (`copilot` default, `mock`) |
| `EVALPILOT_JUDGE_THRESHOLD` | default judge pass threshold (0.7) |
| `EVALPILOT_SKIP_SUT` | don't launch the SUT (deterministic skips) |
| `EVALPILOT_SUT_TIMEOUT` | clamp every SUT subprocess timeout |
| `COPILOT_BIN` | path to the `copilot` binary |

## Pluggable SUT runners

The Copilot CLI runner is built in, plus a deterministic `mock` runner. Add
another runtime by subclassing `evalpilot.runners.base.SUTRunner`, decorating it
with `@register_runner`, and selecting it via `EVALPILOT_RUNNER`.

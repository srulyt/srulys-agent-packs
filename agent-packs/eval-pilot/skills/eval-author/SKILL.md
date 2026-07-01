---
name: eval-author
description: "Entry workflow for creating evalpilot evals for Copilot agents and skills. Bootstraps evals/, discovers targets, scaffolds a Markdown *.eval.md (or Python builder) spec, and hands off to eval-runner. Trigger keywords: create evals, author evals, test my agent, test my skill, evalpilot, eval.md, rubric, metric, regression."
argument-hint: "<agent or skill name / scenario>"
user-invocable: true
---

# Eval Author (entry skill)

Use this skill when the user asks to create evals for a Copilot agent, agent
pack, or skill. Modern evalpilot evals are **single self-contained files** that
read top-to-bottom, so a reader understands the eval at a glance and an author
needs only a few steps to create one. The Python engine lives in the
`evalpilot` package and must already be installed (see the plugin README). Do
**not** modify the engine.

## The two authoring surfaces

Every eval compiles to one `EvalSpec`, from either surface:

1. **Markdown DSL — `*.eval.md`** (preferred; prompts/criteria read naturally).
2. **Python builder — `*.eval.py`** (power-user escape hatch: compute prompts,
   share fixtures, register `check(...)` predicates).

Both are discovered by `evalpilot run` / `evalpilot lint`.

## Workflow (how many steps to create an eval?)

1. **Ensure `evalpilot` is importable** and, if `evals/` does not exist, run
   `evalpilot init` (scaffolds `evals/examples/` + `_metrics/`).
2. **Discover the target**: `evalpilot discover` → pick the agent or skill name.
3. **Scaffold**: `evalpilot new <name> --target <target> --kind agent|skill`
   (add `--python` for a builder file). This writes a ready-to-edit spec.
4. **Fill in three things**: the `## Act` prompt, the `## Assert` structural
   checks, and the `judge:` criteria. Keep at least one `metric` for trends.
5. **Validate without the SUT**: `evalpilot lint <file>` (parses + validates).
6. **Hand off**: load/use `eval-runner`, or run `evalpilot run <file>`. For
   trends, load/use `eval-metrics` or run `evalpilot metrics`.

## Description-first authoring (write intent, then implement)

A `.eval.md` needs only a **title, `> summary`, and `## Description`** to be a
valid *stub* — the executable `## Setup` / `## Act` / `## Assert` can come
later. This supports a natural workflow: a human writes what the eval should
check in plain English, then an agent implements the rest.

1. **Scaffold a stub from a description**:
   `evalpilot new <name> --target <target> --kind agent --describe "In plain
   English, describe the scenario, the action, and what a correct result is."`
   This writes a prose-only `## Description` file with no Act/Assert yet.
2. **Lint** it: `evalpilot lint <file>` reports it as `[stub]`
   ("described, awaiting implementation") — **not** an error, and it does not
   fail the lint run. (Use `evalpilot lint --strict` to fail on stubs in CI.)
3. **Implement**: from the `## Description`, fill in `## Act` (the prompt) and
   `## Assert` (structural checks + `judge:` criteria + a `metric`). Once an
   act prompt and at least one check exist, lint flips from `[stub]` to `[ ok ]`.
4. **Run**: `evalpilot run <file>`.

## The `*.eval.md` shape

```markdown
---
name: my-agent-migration-plan
target: my-agent            # agent or skill name
kind: agent                 # agent | skill
tags: [smoke, slow, judge]
timeout: 600
---

# Produces a concrete migration plan
> One-line summary shown in compact listings.

## Description                # optional but recommended
Multi-paragraph, human-readable explanation of the scenario: the starting
context, what the agent is asked to do, and what a correct result looks like.
Lets a reader grasp the eval at a glance — and lets an author write the intent
first and have an agent implement the sections below.

## Setup                    # optional
```yaml
# stage: { agent: my-agent }          # inferred from target+kind
# files: [{ copy: "fixtures/**", dest: "." }]
```

## Act
```prompt
Create a concise migration plan for moving a Python CLI from argparse to Typer.
```

## Assert
```yaml
files:
  exists: ["**/*.md"]
contains:
  - { text: "test", ignore_case: true }   # against stdout by default
judge:
  # artifact: path/to/output.md           # omit to judge stdout
  threshold: 0.7
  criteria: |
    Score 1.0 only if the response includes ordered migration steps, calls out
    compatibility risks, and names tests to run. 0.5 partial; 0.0 off-topic.
metrics:
  - { name: judge_score, value: $judge.score, direction: higher_is_better,
      baseline: rolling_mean, tolerance: 0.1 }
```
```

## The Python builder (equivalent)

```python
from evalpilot import Eval

eval = (
    Eval("my-agent-migration-plan", target="my-agent", kind="agent",
         tags=["smoke", "judge"], timeout=600)
    .describe("Produces a concrete migration plan.")
    .prompt("Create a concise migration plan for argparse -> Typer.")
    .expect_file("**/*.md")
    .expect_stdout("test", ignore_case=True)
    .judge("Ordered steps + risks + tests named earns 1.0.", threshold=0.7)
    .metric("judge_score", "$judge.score",
            direction="higher_is_better", baseline="rolling_mean", tolerance=0.1)
    .build()
)
```

## Assertion vocabulary (`## Assert`)

| Key | Meaning |
|---|---|
| `files.exists` / `files.absent` | glob paths that must / must not exist |
| `glob_count` | a glob must match an expected count |
| `contains` / `not_contains` | substring in stdout (or a file via `path:`) |
| `prose_contains` | whitespace-normalised substring match |
| `stdout_contains` | substring in stdout specifically |
| `matches` | regex match |
| `json_path` | value at a JSON path equals/exists |
| `json_empty` | value at a JSON path is missing, null, or empty |
| `section_contains` / `section_not_contains` | substring scoped to a `## Heading` body |
| `judge` | one or a list of LLM-as-judge verdicts (`threshold`, `criteria`) |
| `asserts` | generic escape hatch: `[{ kind, ...args }]` |

New assertion kinds register via the `@assertion` decorator in
`evalpilot.assertions`, so the DSL can express **any** eval; the Python
builder's `.check(name, predicate)` is a per-eval escape hatch.

## Metric value references

Metric `value:` may be a literal number or a `$`-reference resolved at run time:
`$judge.score`, `$judge.<name>.score`, `$duration`, `$stdout.words|chars|lines`,
`$assertions.pass_rate`, `$checks.pass_rate`. `baseline:` accepts a strategy
name (`rolling_mean`, `last`, `best`) or a number (pinned).

## Authoring rules

- Never put the expected answer in the prompt; make the agent solve the task.
- Keep judge criteria strict and concrete: say what earns 1.0 and partial credit.
- Prefer stable structural assertions before asking the judge.
- Record metrics meaningful over time: judge score, latency, word/artifact count.
- Run `evalpilot lint` before handing off — it catches spec errors with no SUT.

## References

- [Assertion & metric reference](references/metric-baselines.md)
- [Staging, runners, and environment](references/fixtures-markers-env.md)

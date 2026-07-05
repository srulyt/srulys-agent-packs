# evalpilot

A generic, easy-to-use eval framework for GitHub Copilot agents and skills —
the TypeScript/npm `evalpilot` engine.

You describe an eval once — as a Markdown `*.eval.md` file or a fluent
TypeScript `*.eval.ts` builder — and evalpilot runs it, produces a **modeled
result**, and renders that result to the terminal, a self-contained HTML
report, and canonical JSON. It gives you two kinds of signal:

- **Assertions + judge** — binary pass/fail (structural checks + LLM-as-judge).
- **Metrics** — numeric values appended to committed **JSONL history** and
  compared against a baseline so regressions surface over time.

The JSON report schema is the canonical evalpilot report format used by the CLI.

> For a full explanation of the engine's mechanics — discovery, spec
> compilation, staging, the arrange/act/assert pipeline, runners, telemetry,
> the judge, metrics/baselines, and status decisions — see
> [`../docs/how-it-works.md`](../docs/how-it-works.md).

## Install

```bash
npm install --save-dev evalpilot
# or run without installing:
npx evalpilot --help
```

Requires Node.js >= 18.

## Quick start

```bash
cd your-repo
npx evalpilot discover                                  # what can it see?
npx evalpilot init                                      # scaffold evals/
npx evalpilot new my-eval --target my-agent --kind agent # create a spec
npx evalpilot lint                                      # validate (no SUT)
npx evalpilot run                                       # execute + render
npx evalpilot show --format html --open                 # open the report
npx evalpilot metrics --check                           # regression gate (CI)
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
Optional multi-paragraph, human-readable explanation. A file with only a
title + summary + `## Description` (no `## Act`/`## Assert`) is a valid *stub* —
`evalpilot lint` reports it as `[stub]` rather than an error.

## Act
```prompt
Ask the agent to do a real task. Do NOT include the expected answer.
```

## Assert
```yaml
files:
  exists: ["**/*.md"]
contains:
  - { text: "migration", ignore_case: true }
tools:
  called:     ["view"]
  not_called: ["str_replace_editor"]
files_accessed:
  not_read:    ["**/secrets.*"]
  not_written: ["agent-packs/**/*.agent.md"]
tokens:
  max_total: 2000000
  models:    ["claude-*"]
judge:
  threshold: 0.7
  criteria: |
    Score 1.0 only if ALL criteria are met; 0.5 partial; 0.0 off-topic.
metrics:
  - { name: judge_score, value: $judge.score, direction: higher_is_better,
      baseline: rolling_mean, tolerance: 0.1 }
```
```

The `tools`, `files_accessed`, and `tokens` families assert over run telemetry
(tool calls, file-access-by-tool, token/model usage) captured from Copilot's
OpenTelemetry file exporter. They **skip** (never fail) when telemetry is
unavailable — e.g. the `mock` runner or `EVALPILOT_TELEMETRY=off`. Builder
equivalents: `.expectToolCalled`, `.expectToolNotCalled`, `.expectFileRead`,
`.expectFileNotRead`, `.expectFileWritten`, `.expectFileNotWritten`,
`.expectTokenBudget`. Metric refs `$tokens.total|input|output` and
`$tools.count(<name>)` feed these signals into the trend history.

## Authoring an eval — TypeScript builder

Same capabilities as Markdown, but expressed in code so you can compute prompts
or share setup. Export the built spec as the module default (or any export):

```ts
// my-agent.eval.ts
import { Eval } from "evalpilot";

export default new Eval("my-agent-migration-plan", {
  target: "my-agent",
  kind: "agent",
  tags: ["smoke", "judge"],
  timeout: 600,
})
  .describe("A good result: the agent produces a concrete migration plan.")
  .prompt("Ask the agent to do a real task. Do NOT include the expected answer.")
  .expectFile("**/*.md")
  .expectContains("migration", { ignoreCase: true })
  .judge("Score 1.0 only if ALL criteria are met; 0.5 partial; 0.0 off-topic.", {
    threshold: 0.7,
  })
  .metric("judge_score", "$judge.score", {
    direction: "higher_is_better",
    baseline: "rolling_mean",
    tolerance: 0.1,
  })
  .build();
```

`*.eval.ts` files are loaded at runtime via [`jiti`](https://github.com/unjs/jiti)
— no separate compile step is required.

## Programmatic API

```ts
import { runSpecs, collectSpecs, renderTerminal, writeJson } from "evalpilot";

const specs = await collectSpecs("evals");
const report = await runSpecs(specs, { parallel: 4 });
writeJson(report, "evals/_runs/latest/report.json");
console.log(renderTerminal(report));
```

## Structural evals

A structural eval is a `*.eval.ts` spec with `kind: "none"` and no `.prompt(...)`.
It runs offline and checks repository files directly:

```ts
import { Eval } from "evalpilot";

export default new Eval("readme-present", { kind: "none", tags: ["structural"] })
  .check("README exists", (ctx) =>
    ctx.read("README.md") ? true : [false, "missing README.md"]
  )
  .build();
```

In `.check()`, `ctx.root` is the repo root, `ctx.read(rel)` returns text or
`null`, and `ctx.glob(pat)` returns sorted absolute paths.

## License

MIT

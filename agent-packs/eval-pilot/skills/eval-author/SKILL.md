---
name: eval-author
description: "Entry workflow for creating evalpilot evals for Copilot agents and skills. Bootstraps evals/, discovers targets, scaffolds Markdown *.eval.md or TypeScript *.eval.ts specs, and hands off to eval-runner. Trigger keywords: create evals, author evals, test my agent, test my skill, evalpilot, eval.md, eval.ts, rubric, metric, regression."
argument-hint: "<agent or skill name / scenario>"
user-invocable: true
---

# Eval Author (entry skill)

Use this skill when the user asks to create evals for a Copilot agent, agent
pack, or skill. Modern evalpilot evals are **single self-contained files** that
read top-to-bottom. There is exactly one engine: the TypeScript `evalpilot`
CLI, published on npm as the [`evalpilot`](https://www.npmjs.com/package/evalpilot)
package.

## Prerequisite: make the `evalpilot` CLI available

The user should **not** need to install evalpilot manually — do it for them
before running any command below.

1. **Detect** first (fast, no network if already present):
   `npx --no-install evalpilot --version`.
2. **If that fails, install it** as a project dev dependency — the best
   practice for a project tool, because it pins the version in the consumer's
   `package.json` + lockfile for reproducible/CI runs:
   - If there is no `package.json` in the project, create one: `npm init -y`.
   - Install: `npm install --save-dev evalpilot`.
3. **Invoke** every `evalpilot <cmd>` via the package runner: `npx evalpilot
   <cmd>`. `npx` runs the project-local install when present, so the pinned
   version is used. (A global install, `npm i -g evalpilot`, also works if the
   user prefers a bare `evalpilot`.)

For brevity the examples below are written as `evalpilot ...`; run them as
`npx evalpilot ...` unless evalpilot is installed globally.

> Note: if `npm install` reports `ENOVERSIONS` / "No versions available" right
> after a fresh publish, the machine has a `min-release-age` npm policy blocking
> just-published versions; add `--min-release-age=0` or wait out the window.

## The authoring surfaces

Every eval compiles to one `EvalSpec`, from either surface:

1. **Markdown DSL — `*.eval.md`** (preferred for prompts and judge criteria).
2. **TypeScript builder — `*.eval.ts`** (for computed prompts, shared setup,
   custom `.check()` predicates, and structural repository checks).

A third idiom, **structural evals**, uses the TypeScript builder with
`kind: "none"` and no `.prompt(...)`. Structural evals run offline, do not
launch Copilot, and assert directly on repo files.

## Workflow

1. If `evals/` does not exist, run `evalpilot init`.
2. Discover the target: `evalpilot discover`.
3. Scaffold: `evalpilot new <name> --target <target> --kind agent|skill`.
   Use `*.eval.ts` manually when you need the fluent builder or structural checks.
4. Fill in the `## Act` prompt, `## Assert` checks, judge criteria, and metrics.
5. Validate without the SUT: `evalpilot lint <file>`.
6. Hand off to `eval-runner`, or run `evalpilot run <file>`. For trends, run
   `evalpilot metrics`.

## Description-first authoring

A `.eval.md` needs only a **title, `> summary`, and `## Description`** to be a
valid stub. `evalpilot lint <file>` reports it as `[stub]` until `## Act` and at
least one check are added.

## The `*.eval.md` shape

```markdown
---
name: my-agent-migration-plan
target: my-agent
kind: agent
tags: [smoke, slow, judge]
timeout: 600
---

# Produces a concrete migration plan
> One-line summary shown in compact listings.

## Description
Multi-paragraph explanation of the scenario.

## Setup
```yaml
# stage: { agent: my-agent }
# files: [{ copy: "fixtures/**", dest: "." }]
```

## Act
```prompt
Create a concise migration plan for moving a CLI from one parser to another.
```

## Assert
```yaml
files:
  exists: ["**/*.md"]
contains:
  - { text: "test", ignore_case: true }
tools:
  called:     ["view"]                       # each tool must be used >= 1
  not_called: ["str_replace_editor"]         # tool must never be used
  count:      { name: "view", max: 5 }        # min/max/equals per tool
  args_contain: { name: "view", text: "README", ignore_case: true }
files_accessed:
  read:        ["**/*.md"]                    # a matching file must be read
  not_read:    ["**/secrets.*"]               # no matching file may be read
  written:     ["**/architecture.md"]         # a matching file must be written
  not_written: ["agent-packs/**/*.agent.md"]  # no matching file may be written
tokens:
  max_total: 2000000                          # run must stay under budget
  max_input: 1500000
  models:    ["claude-*"]                     # only these models may be used
judge:
  threshold: 0.7
  criteria: |
    Score 1.0 only if the response includes ordered migration steps, calls out
    compatibility risks, and names tests to run. 0.5 partial; 0.0 off-topic.
metrics:
  - { name: judge_score, value: $judge.score, direction: higher_is_better,
      baseline: rolling_mean, tolerance: 0.1 }
```
```

## The `*.eval.ts` builder

```ts
import { Eval } from "evalpilot";

export default new Eval("my-agent-migration-plan", {
  target: "my-agent",
  kind: "agent",
  tags: ["smoke", "judge"],
  timeout: 600,
})
  .describe("Produces a concrete migration plan.")
  .prompt("Create a concise migration plan for parser migration.")
  .expectFile("**/*.md")
  .expectContains("test", { ignoreCase: true })
  .judge("Ordered steps + risks + tests named earns 1.0.", { threshold: 0.7 })
  .metric("judge_score", "$judge.score", {
    direction: "higher_is_better",
    baseline: "rolling_mean",
    tolerance: 0.1,
  })
  .build();
```

## Structural `*.eval.ts` checks

```ts
import { Eval } from "evalpilot";

export default new Eval("plugin-shape", {
  target: "my-agent",
  kind: "none",
  tags: ["structural", "tooling"],
})
  .check("README exists", (ctx) =>
    ctx.read("agent-packs/my-agent/README.md") ? true : [false, "missing README"]
  )
  .check("has agents", (ctx) => ctx.glob("agent-packs/my-agent/.github/agents/*.agent.md").length > 0)
  .build();
```

For structural checks, `ctx.root` is the repo root, `ctx.read(rel)` returns
`text | null`, and `ctx.glob(pat)` returns sorted absolute paths.

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
| `tools.called` / `tools.not_called` | a tool must / must never appear in the run |
| `tools.count` | per-tool call count (`min`/`max`/`equals`) |
| `tools.args_contain` | a tool call's arguments must contain text |
| `files_accessed.read` / `files_accessed.not_read` | a file matching the glob must / must never be read |
| `files_accessed.written` / `files_accessed.not_written` | a file matching the glob must / must never be written |
| `tokens.max_total` / `max_input` / `max_output` | run must stay under a token budget |
| `tokens.models` | only the listed model globs may be used |
| `judge` | one or a list of LLM-as-judge verdicts (`threshold`, `criteria`) |
| `asserts` | generic escape hatch: `[{ kind, ...args }]` |

For code-only assertions, use the TypeScript builder's `.check(name, ctx => true
| [false, "msg"])`.

Telemetry-based assertions (`tools`, `files_accessed`, `tokens`) rely on the
Copilot OpenTelemetry file exporter, which the copilot runner enables
automatically. When telemetry is unavailable (e.g. `--runner mock`, offline CI,
or `EVALPILOT_TELEMETRY=off`), these assertions **skip** — they never fail an
eval or count against its pass-rate. Builder equivalents:
`.expectToolCalled(name, { min, max, argsContain })`,
`.expectToolNotCalled(name)`, `.expectFileRead(glob)`,
`.expectFileNotRead(glob)`, `.expectFileWritten(glob)`,
`.expectFileNotWritten(glob)`, and
`.expectTokenBudget({ maxTotal, maxInput, maxOutput, models })`. Inside
`.check()`, use `ctx.telemetryAvailable`, `ctx.toolCalls(name)`,
`ctx.filesRead()`, `ctx.filesWritten()`, `ctx.modelsUsed()`, `ctx.tools`, and
`ctx.tokens`.

## Metric value references

Metric `value:` may be a literal number or a `$`-reference resolved at run time:
`$judge.score`, `$judge.<name>.score`, `$duration`, `$stdout.words|chars|lines`,
`$assertions.pass_rate`, `$checks.pass_rate`, `$tokens.total|input|output`, and
`$tools.count` / `$tools.count(<name>)`. `baseline:` accepts a strategy
name (`rolling_mean`, `last`, `best`) or a number (pinned).

## Authoring rules

- Never put the expected answer in the prompt; make the agent solve the task.
- Keep judge criteria strict and concrete.
- Prefer stable structural assertions before asking the judge.
- Use structural evals for packaging and repository conformance checks.
- Record metrics meaningful over time: judge score, latency, word/artifact count.
- Run `evalpilot lint` before handing off.

## References

- [Assertion & metric reference](references/metric-baselines.md)
- [Staging, tags, runners, and environment](references/fixtures-markers-env.md)

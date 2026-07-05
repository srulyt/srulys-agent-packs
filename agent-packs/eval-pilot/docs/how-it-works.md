# How evalpilot works — mechanics guide

This is the deep-dive companion to the [package README](../README.md) and the
[engine README](../engine-ts/README.md). It explains what happens under the hood
at every stage, so you can reason about *why* an eval was staged, skipped,
failed, or scored the way it was — and configure the engine with confidence.

If you just want to author and run evals, start with the `eval-author` and
`eval-runner` skills. Read this when you need the model behind them.

## Contents

1. [The pipeline at a glance](#1-the-pipeline-at-a-glance)
2. [Repo root and eval root resolution](#2-repo-root-and-eval-root-resolution)
3. [Discovery — how targets are found](#3-discovery--how-targets-are-found)
4. [Spec collection and compilation](#4-spec-collection-and-compilation)
5. [The EvalSpec model](#5-the-evalspec-model)
6. [Staging — building the isolated workspace](#6-staging--building-the-isolated-workspace)
7. [Execution — arrange, act, assert](#7-execution--arrange-act-assert)
8. [Runners and the SUT](#8-runners-and-the-sut)
9. [Assertions](#9-assertions)
10. [Telemetry](#10-telemetry)
11. [The LLM judge](#11-the-llm-judge)
12. [Metrics, baselines, and regressions](#12-metrics-baselines-and-regressions)
13. [The result model and reporting](#13-the-result-model-and-reporting)
14. [Status decision reference](#14-status-decision-reference)
15. [Environment variables](#15-environment-variables)
16. [CLI reference](#16-cli-reference)
17. [Repo wrappers](#17-repo-wrappers)

---

## 1. The pipeline at a glance

A single `evalpilot run` flows through these stages:

```
resolve roots            find repo root (.git) and eval root (evals/)
   │
collect specs            walk eval root for *.eval.md / *.eval.ts, compile to EvalSpec
   │
for each spec:
   ├─ validate           lint the compiled spec; invalid → ERROR
   ├─ tag filter/skip    -t filter and the 'skip' tag remove or short-circuit specs
   ├─ structural?        kind:none + no prompt → assert on repo files, no SUT
   ├─ arrange            create isolated workspace, stage agent/skill + fixtures
   ├─ act                launch the SUT (copilot/mock) with the prompt over stdin
   └─ assert             run assertions + judges + metrics against the run
   │
aggregate + render       write report.json, report.html, update latest.txt
```

Every stage produces or consumes one canonical data structure — the
`EvalSpec` (input) and the `EvalRunReport` (output). The terminal, HTML, and JSON
renderers are all pure projections of that report, so what you see is always the
same underlying model.

Source map: `discovery.ts`, `collect.ts`, `spec.ts`, `workspace.ts`,
`executor.ts`, `runners/*`, `assertions.ts`, `judge.ts`, `metrics.ts`,
`model.ts`, `render/*`, `cli.ts`.

---

## 2. Repo root and eval root resolution

Everything is anchored to two directories, resolved once per run
(`config.ts`).

**Repo root** (`findRepoRoot`):

1. If `EVALPILOT_REPO_ROOT` is set, use it (expanded/absolute).
2. Otherwise walk **up** from the current working directory until a directory
   containing `.git` is found.
3. If none is found, fall back to the starting directory.

**Eval root** (`findEvalRoot`) — where specs, runs, and metric history live:

- `EVALPILOT_EVAL_ROOT` if set (absolute, or relative to the repo root).
- Otherwise `<repo_root>/evals`.

**Metrics root** (`findMetricsRoot`):

- `EVALPILOT_METRICS_ROOT` if set (absolute, or relative to the eval root).
- Otherwise `<eval_root>/_metrics`.

Because discovery walks the repo root and specs live under the eval root, you can
relocate either independently for monorepos or CI sandboxes without touching
spec files.

---

## 3. Discovery — how targets are found

A spec never contains a path to an agent or skill — only a **name** (the
frontmatter `target`, or an explicit `stage:` name). Discovery (`discovery.ts`)
turns that name into a concrete file by scanning the repo tree. This is why
evalpilot works in an arbitrary repository with no configuration.

### What is scanned

Starting at the repo root, evalpilot walks the whole tree looking for
directories literally named **`agents`** or **`skills`**, pruning noise
directories so a run never rediscovers its own output or dependencies:

```
.git  .hg  .svn  node_modules  __pycache__  .venv  venv
.pytest_cache  .mypy_cache  dist  build  .tox  _runs  _logs  _metrics
```

### Supported layouts

It understands every layout the Copilot CLI itself loads from, so both
repo-level and plugin-packaged content are found:

| Kind | Recognized as | Locations |
|---|---|---|
| Agent | `<name>.agent.md` inside an `agents/` dir | `.github/agents/`, `<plugin>/agents/` |
| Skill | `<name>/SKILL.md` inside a `skills/` dir | `.github/skills/<name>/`, `<plugin>/skills/<name>/` |

- An **agent's name** is the filename stem (`eval-judge.agent.md` → `eval-judge`).
- A **skill's name** is the `SKILL.md` parent directory name.

### Plugin awareness

For every hit, evalpilot records a `plugin_root` by walking **up** from the
`agents/`/`skills/` directory to the nearest ancestor containing a `plugin.json`.
This matters for staging: when an agent that belongs to a plugin is staged, its
sibling `skills/` and `instructions/` directories are staged alongside it (see
§6).

### Name resolution and ambiguity

`findAgent(name)` / `findSkill(name)` filter all discovered items by name:

- **1 match** → used.
- **0 matches** → error listing every available name.
- **2+ matches** → error: *"'<name>' is ambiguous across N locations"*.

The practical rule: **agent and skill names must be unique across the whole
repo.** If you vendor two copies of a skill, discovery will refuse to guess.

### Inspecting discovery

```bash
evalpilot discover            # human-readable list of agents + skills
evalpilot discover --json     # machine-readable (name, path, plugin_root)
```

Run this first whenever a target fails to resolve — it shows exactly what the
engine can see from the current repo root.

---

## 4. Spec collection and compilation

`collectSpecs(target)` (`collect.ts`) accepts a file or a directory:

- A **file** is loaded directly.
- A **directory** is walked recursively (pruning `_runs`, `_metrics`,
  `_templates`, `.git`, `node_modules`, `.venv`, etc.), collecting every spec
  file, then sorted by path for deterministic ordering.

Recognized spec file extensions: `*.eval.md`, `*.eval.ts`, `*.eval.js`,
`*.eval.mjs`.

### Markdown specs

`*.eval.md` files are parsed by the Markdown loader (`loaders/markdown.ts`):
YAML frontmatter plus `## Setup` / `## Act` / `## Assert` (and an optional
`## Description`) sections. Each file compiles to exactly one `EvalSpec`.

### TypeScript specs

`*.eval.ts` / `.js` / `.mjs` files are imported at runtime via
[`jiti`](https://github.com/unjs/jiti) — no separate build step. Every exported
value that is a built `EvalSpec` **or** a fluent `Eval(...)` builder (default or
named export) is collected, so one file may contribute several specs.

A key detail: when your spec does `import { Eval } from "evalpilot"`, the
collector **aliases** `evalpilot` to the *running engine's own entry*
(`ownEntry()`), whether that's an npm install in the consumer repo or an in-repo
development build. This guarantees your spec builds against the exact engine that
will execute it.

---

## 5. The EvalSpec model

Both surfaces compile to one normalized `EvalSpec` (`spec.ts`). The important
fields:

| Field | Meaning |
|---|---|
| `name` | Unique id for the eval (also the metric/slug prefix). |
| `target` | Agent or skill **name** under test (resolved by discovery). |
| `kind` | `agent`, `skill`, or `none`. |
| `tags` | Free-form labels used for selection and behavior (`skip`, `smoke`, `structural`, …). |
| `timeout` | Default SUT timeout in seconds (per-`Act` override possible). |
| `setup.stage` | What to stage: `{ agent, skill, all, include_skills }`. |
| `setup.files` | Fixture copies into the workspace. |
| `act` | The prompt (+ optional per-act `agent`/`skill`/`timeout`). Absent for structural. |
| `assertions`, `judges`, `metrics` | The checks. |

### Kind and staging inference

If you omit `## Setup`, the stage is **inferred** from `target` + `kind`
during normalization (`makeEvalSpec`):

- `kind: agent` + `target: X` → stage agent `X`.
- `kind: skill` + `target: X` → stage skill `X`.
- `kind: none` → stage nothing.

An explicit `## Setup` `stage:` always wins over inference.

### Validation and stubs

`validateSpec` runs before execution. Common problems that produce an **ERROR**
status:

- `kind: agent` but no agent staged (missing `target`).
- `kind: skill` but no skill staged.
- A prompt-bearing eval with no assertions, judges, or metrics
  (*"nothing to check"*).

A file with only a title, `> summary`, and `## Description` (no `## Act`) is a
valid **stub** — `evalpilot lint` reports it as `[stub]` rather than an error, so
you can author description-first and fill in checks later. `lint --strict` treats
stubs as failures for CI.

---

## 6. Staging — building the isolated workspace

Every behavioral eval runs in its own throwaway directory
(`_runs/<run-id>/<slug>/ws`), never against your working tree. The `Workspace`
class (`workspace.ts`) builds it:

1. Create the workspace and logs directories.
2. `git init -q` the workspace (best-effort) so agents that expect a repo behave
   normally; failures are harmless.
3. **Stage** per `setup.stage`:
   - `stageAgent(name)` copies the agent's `agents/` dir into
     `.github/agents/`. Unless `include_skills: false`, it also copies the
     agent's plugin sibling `skills/` and `instructions/` dirs (resolved via the
     `plugin_root`, or a `.github` parent) so the agent's own skills come along.
   - `stageSkill(name)` copies exactly one skill into `.github/skills/<name>/`
     (no agents).
   - `stageAll()` copies **every** discovered agent and skill — used by
     `stage: { all: true }`.
4. **Copy fixtures** from `setup.files`. Each `{ copy, dest }` is glob-expanded
   relative to the spec's own directory (`base_dir`) and copied into the
   workspace, so fixtures live next to the spec that needs them.

The staged workspace is exactly what the SUT sees — nothing more. That isolation
is what makes a **baseline** run possible: a `kind: none` spec *with* a prompt
stages nothing, so the raw harness runs against an empty repo and you can compare
its output against a staged agent/skill run.

---

## 7. Execution — arrange, act, assert

`runEval` (`executor.ts`) drives one spec; `runSpecs` fans a batch out with
bounded concurrency (`--parallel N`, order preserved). For a single spec:

1. **Validate** → ERROR on problems.
2. **`skip` tag** → SKIPPED immediately.
3. **Structural?** (`kind: none` + no prompt) → build an `AssertContext` rooted
   at the repo, evaluate assertions/judges/metrics against repo files, no
   workspace, no runner. (Judges and metrics are allowed but rare here.)
4. **Runner available?** If not (e.g. no `copilot` binary and not `mock`) →
   SKIPPED with a reason.
5. **Arrange** the workspace (§6).
6. **Act** — run the SUT:
   - If the spec (or `Act`) names a **skill**, the prompt is wrapped as
     *"Use the `<skill>` skill to handle the following request. Do not invoke any
     other skill."* and run as a plain agent invocation.
   - Otherwise run as an **agent**: pass `--agent <name>` when a target agent is
     set, else run the bare harness with no agent.
7. **Assert** — build an `AssertContext` over the run's stdout/stderr/telemetry
   and workspace root, then evaluate every assertion, judge, and metric.
8. Compute the final **status** (§14).

If the SUT is *unusable* (e.g. `EVALPILOT_SKIP_SUT` produced a skip result) the
eval is SKIPPED. If the SUT ran but exited non-zero, the eval is marked FAILED
**but assertions still run** so you get a full picture rather than a bare "it
crashed."

---

## 8. Runners and the SUT

The "system under test" is driven by a pluggable **runner**, selected with
`--runner` or `EVALPILOT_RUNNER` (`runners/*`).

### `copilot` (default)

Launches the real Copilot CLI (`runners/copilot.ts`) with hardening learned the
hard way:

- The binary is located via `COPILOT_BIN`, else `copilot` on `PATH` (honoring
  `PATHEXT` on Windows). Absent → the runner reports *unavailable* and the eval
  SKIPs (it does not fail).
- The prompt is fed over **stdin**, never `-p` — the Windows `copilot.CMD` shim
  truncates `-p` at the first newline.
- `--allow-all --no-ask-user` is the only flag combo that reliably grants
  write/shell permissions non-interactively.
- The child runs in its own process group; on timeout the whole tree is killed
  (`tree-kill`) and the run is marked timed-out (exit 124).
- Known fatal Windows exit codes (access violation, stack overflow/buffer
  overrun) are surfaced as a **crash** in the result, so a runtime crash is not
  mistaken for a prompt defect.
- A full transcript (command, cwd, exit, duration, prompt, stdout, stderr) is
  written to the eval's log path for triage.

### `mock`

Deterministic and offline (`runners/mock.ts`). Use
`EVALPILOT_RUNNER=mock` or `--runner mock` to exercise staging, assertions,
judge wiring, metrics, and rendering **without** a `copilot` binary or tokens.
The engine's own tests and the `new`→`run` demo use it.

### Timeouts and skipping

- `EVALPILOT_SUT_TIMEOUT` clamps every SUT subprocess timeout (min of requested
  and cap).
- `EVALPILOT_SKIP_SUT=1` never launches the SUT; behavioral evals produce a SKIP
  result (exit 125) with the prompt still logged.

---

## 9. Assertions

Assertions are small functions registered under a `kind` string
(`assertions.ts`). Register custom ones with
`registerAssertion(kind, fn, help)`; the builder's `.check(name, predicate)` is a
per-eval escape hatch. The full vocabulary usable from `## Assert`:

| Key | Meaning |
|---|---|
| `files.exists` / `files.absent` | glob paths that must / must not exist |
| `glob_count` | a glob must match a count (`min`/`max`/`equals`) |
| `contains` / `not_contains` | substring in stdout (or a file via `path:`) |
| `prose_contains` | substring match after whitespace normalization |
| `stdout_contains` | substring in stdout specifically |
| `matches` | regex match (`pattern`, optional `path`, `flags`) |
| `json_path` | value at a dotted JSON query equals / exists |
| `json_empty` | JSON value is missing, null, `[]`, `{}`, or `""` |
| `section_contains` / `section_not_contains` | match scoped to a `## Heading` body |
| `tools.called` / `tools.not_called` | a tool must / must never appear in the run |
| `tools.count` | per-tool call count (`min`/`max`/`equals`) |
| `tools.args_contain` | a tool call's arguments must contain text |
| `files_accessed.read` / `not_read` | a file matching the glob must / must never be read |
| `files_accessed.written` / `not_written` | a file matching the glob must / must never be written |
| `tokens.max_total` / `max_input` / `max_output` | run must stay under a token budget |
| `tokens.models` | only the listed model globs may be used |
| `judge` | one or a list of LLM-as-judge verdicts |
| `asserts` | generic escape hatch: `[{ kind, ...args }]` for any registered kind |

**Prose vs structural matching:** `prose_contains` collapses all whitespace runs
to single spaces before comparing (`asserts.ts`), so line-wrapping doesn't break
a match. Use it for prose; use `contains`/`matches` when exact formatting
matters.

The `tools`, `files_accessed`, and `tokens` families read **run telemetry**
(§10). When telemetry is unavailable they **skip** — neutral, never failing, and
excluded from the pass-rate — rather than producing false negatives.

Builder equivalents: `.expectFile`, `.expectContains`, `.expectToolCalled`,
`.expectToolNotCalled`, `.expectFileRead/NotRead`,
`.expectFileWritten/NotWritten`, `.expectTokenBudget`, and inside `.check()`:
`ctx.telemetryAvailable`, `ctx.toolCalls(name)`, `ctx.filesRead()`,
`ctx.filesWritten()`, `ctx.modelsUsed()`, `ctx.tools`, `ctx.tokens`.

---

## 10. Telemetry

The `copilot` runner enables Copilot's OpenTelemetry **file** exporter for each
run (`COPILOT_OTEL_FILE_EXPORTER_PATH` + genai content capture), then parses the
emitted JSONL into a normalized telemetry model attached to the run result
(`telemetry/*`). This powers:

- the `tools`, `files_accessed`, `tokens` assertion families, and
- the `$tokens.*` and `$tools.count` metric references.

It is entirely offline — no collector, no network. Captured telemetry stays in
the run's log directory (`<log>.otel.jsonl`) and is **never** written into the
committed report.

Telemetry is unavailable under the `mock` runner, when `EVALPILOT_TELEMETRY=off`
(or `0`/`false`/`none`/`no`), or on a copilot build without the exporter — in
which case telemetry-based assertions **skip**.

---

## 11. The LLM judge

For subjective quality, a `judge` block scores a single artifact against
free-form criteria (`judge.ts`). Mechanics:

1. The judged artifact is either the file at `artifact:` (relative to the
   workspace) or, if omitted, the SUT's **stdout**. A missing artifact fails the
   judge with a clear reason.
2. evalpilot stages the bundled **`eval-judge`** agent into a fresh temp
   workspace and runs it through the same runner as the SUT.
3. The judge is prompted to emit **exactly one JSON object**:
   `{ "score": 0.0, "rationale": "...", "evidence": [{ "path", "quote" }] }`.
   Optional `golden` references are appended to the prompt.
4. evalpilot extracts the first balanced JSON object from stdout (tolerant of
   surrounding text), reads `score` (0–1), and marks the judge **passed** when
   `score >= threshold`.

The threshold precedence is: explicit `threshold:` on the block →
`EVALPILOT_JUDGE_THRESHOLD` → default **0.7**. The judge agent file can be
overridden with `EVALPILOT_JUDGE_AGENT`; otherwise the bundled copy is used.

Because the judge is itself an agent run, it needs a working runner. Under
`--runner mock` judge behavior is deterministic/offline like everything else.

---

## 12. Metrics, baselines, and regressions

Metrics turn a run into a **number tracked over time** (`metrics.ts`). Declared
under `metrics:` as `[{ name, value, direction, baseline, ... }]`.

### Value references

`value` is a literal number or a `$`-reference resolved at run time
(`executor.ts` `resolveRef`):

- `$judge.score` / `$judge.<name>.score`
- `$duration` (wall-clock seconds)
- `$stdout.words` / `$stdout.chars` / `$stdout.lines`
- `$assertions.pass_rate` / `$checks.pass_rate`
- `$tokens.total` / `$tokens.input` / `$tokens.output`
- `$tools.count` / `$tools.count(<name>)`

(The TS builder additionally accepts a function `ctx => number`.)

### History

Each recorded value appends one JSON line to a **committed** history file:

```
<eval_root>/_metrics/<slug>/history.jsonl
```

The slug is `<eval_id>__<metric_name>`, sanitized. Each row carries the value,
resolved baseline, strategy, delta, pct_delta, regression verdict, tolerances,
and provenance (`ts`, `run_id`, `git_sha`). Commit these files with your evals
for portable, git-diffable baselines.

### Baseline strategies

`baseline:` is a strategy name or a pinned number:

| Strategy | Baseline is | Use for |
|---|---|---|
| `last` | the previous committed value (default) | deterministic metrics |
| `rolling_mean` | mean of the last `window` values (default 5) | noisy/LLM metrics |
| `best` | max (higher-is-better) or min (lower-is-better) so far | protecting a best value |
| a number | pinned | fixed thresholds |

### Regression logic

Given `direction`:

- `higher_is_better` → regression when `value < baseline - slack`.
- `lower_is_better` → regression when `value > baseline + slack`.
- `neutral` → never regresses (informational only).

`slack = max(tolerance, |baseline| * tolerance_pct)` — the larger of the absolute
and percentage allowances. The **first** recorded value has no prior baseline and
cannot regress.

### Gating

- `gate: true` makes a regression **fail the eval** (contributes to FAILED).
- Otherwise the metric is informational and surfaces only in
  `evalpilot metrics --check`, which exits non-zero if the latest run regressed.

Guidance: for LLM-derived metrics prefer `rolling_mean` + absolute slack
(`tolerance: 0.05`–`0.1`); for latency/cost/word-count prefer `lower_is_better`
with `last` or `best` and a percentage tolerance.

---

## 13. The result model and reporting

Every run compiles to one `EvalRunReport` (`model.ts`) holding per-eval
`EvalResult`s. Each `EvalResult` has a `status`, the assertion/judge/metric
results, timings, the prompt, and the SUT `log_path`. Aggregate helpers count
passed/failed/skipped/errored; `checkTotal`/`checkPassed` count non-skipped
assertions plus judges.

Outputs (`--format terminal,html,json,all`):

```
<eval-root>/_runs/<run-id>/report.json    canonical modeled result (source of truth)
<eval-root>/_runs/<run-id>/report.html    self-contained report (drill-down + sparkline trends)
<eval-root>/_runs/latest.txt              pointer to the newest report.json
```

`evalpilot show [run] [--format html] [--open]` re-renders any run from its JSON
without re-executing. `_runs/` is generated output and is not committed;
`_metrics/` history **is** committed.

---

## 14. Status decision reference

The final per-eval status is computed deterministically:

| Status | When |
|---|---|
| **ERROR** | Spec failed validation, or an exception was thrown while running/asserting. |
| **SKIPPED** | Tagged `skip`; or the runner is unavailable; or the SUT was skipped/unusable (`EVALPILOT_SKIP_SUT`, exit 125). |
| **FAILED** | SUT exited non-zero; **or** any non-skipped assertion failed; **or** any judge failed; **or** any **gated** metric regressed. |
| **PASSED** | None of the above — all checks passed (skipped telemetry assertions don't count against it). |

Exit code of `evalpilot run`: **0** if every eval passed or was skipped, **1**
otherwise. `--no-gate` forces exit 0 regardless (useful for reporting-only runs).

---

## 15. Environment variables

| Variable | Effect |
|---|---|
| `EVALPILOT_REPO_ROOT` | Override the detected repository root. |
| `EVALPILOT_EVAL_ROOT` | Override the `evals/` location. |
| `EVALPILOT_METRICS_ROOT` | Override the metric history location. |
| `EVALPILOT_RUNNER` | Select the SUT runner (`copilot` default, `mock`). |
| `EVALPILOT_SKIP_SUT` | Never launch the SUT; behavioral evals produce SKIP. |
| `EVALPILOT_SUT_TIMEOUT` | Clamp every SUT subprocess timeout (seconds). |
| `EVALPILOT_JUDGE_THRESHOLD` | Default judge pass threshold (default `0.7`). |
| `EVALPILOT_JUDGE_AGENT` | Path to a custom `eval-judge` agent file. |
| `EVALPILOT_TELEMETRY` | Telemetry capture on by default; `off`/`0`/`false`/`none`/`no` disables it (telemetry asserts then skip). |
| `EVALPILOT_RUN_ID` | Pin the run id shared by all metrics in a run. |
| `COPILOT_BIN` | Path to a specific `copilot` binary. |

(`EVALS_SKIP_SUT` and `EVALS_SUT_TIMEOUT` are accepted as legacy aliases.)

---

## 16. CLI reference

```bash
evalpilot new <name> [--target T] [--kind agent|skill|none] [--ts] [--describe TEXT] [--dir D] [--force]
evalpilot run [target] [-t tags] [--parallel N] [--format terminal|html|json|all] [--runner R] [--open] [--no-gate]
evalpilot show [run] [--format terminal|html] [--open]
evalpilot lint [target] [--strict]
evalpilot init [--force]
evalpilot discover [--json]
evalpilot metrics [slug] [--check] [-v] [--tail N]
```

- **`new`** scaffolds a Markdown spec (or `--ts` builder); `--describe` emits a
  prose-only stub for an agent to fill in.
- **`run`** discovers + executes; `target` is a file or directory path.
- **`lint`** validates specs without launching the SUT; `--strict` fails on
  stubs.
- **`discover`** lists resolvable agents and skills (see §3).
- **`metrics --check`** is the CI regression gate.

### Tag selection

Tags replace runner-specific selection syntax. A comma list; a leading `-` or
`~` excludes:

```bash
evalpilot run -t structural       # only 'structural'
evalpilot run -t "smoke,-slow"    # include 'smoke', exclude 'slow'
```

Common conventions: `pack`, `skill`, `smoke`, `slow`, `judge`, `structural`,
`tooling`. The `skip` tag short-circuits an eval to SKIPPED.

---

## 17. Repo wrappers

From this monorepo, thin wrappers resolve a pack/skill **name** to its eval
directory and forward to the engine:

```bash
node scripts/run-evals.mjs <name>          # run a pack/skill by name
node scripts/run-evals.mjs --all           # everything
node scripts/run-evals.mjs <name> --mock   # offline runner
node scripts/run-evals.mjs <name> --list   # list without running
node scripts/run-evals.mjs <name> -- -t "smoke,-slow"   # pass-through flags
```

On Windows, `eval.cmd <name>` offers the same workflow. Repo npm scripts:
`npm run eval`, `eval:all`, `eval:mock`, `lint:evals`, `lint:packs`,
`engine:build`, `engine:test`.

---

## See also

- [`../README.md`](../README.md) — package overview and installation.
- [`../engine-ts/README.md`](../engine-ts/README.md) — authoring surfaces and the
  programmatic API.
- [`../skills/eval-author/references/metric-baselines.md`](../skills/eval-author/references/metric-baselines.md)
  — assertion & metric reference tables.
- [`../skills/eval-author/references/fixtures-markers-env.md`](../skills/eval-author/references/fixtures-markers-env.md)
  — staging, tags, runners, and environment.

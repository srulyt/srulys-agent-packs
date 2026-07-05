# Staging, Tags, Runners, and Environment

> For the end-to-end mechanics behind these knobs, see the
> [mechanics guide](../../../docs/how-it-works.md).

## Staging (`## Setup` in `.eval.md`)

Each behavioral eval runs in an isolated workspace. Staging controls what is
placed there before the `## Act` prompt runs.

```yaml
stage: { agent: my-agent }          # stage an agent (+ its plugin skills)
# stage: { agent: my-agent, include_skills: false }   # agent only
# stage: { skill: my-skill }        # stage a single skill in isolation
# stage: { all: true }              # stage every discoverable agent + skill
files:                              # optional seed files copied into the workspace
  - { copy: "fixtures/**", dest: "." }
  - { copy: "fixtures/input.md", dest: "docs/input.md" }
```

If you omit `## Setup`, the stage is **inferred** from the frontmatter
`target` + `kind` (`kind: agent` → stage that agent; `kind: skill` → stage that
skill; `kind: none` → stage nothing).

## Arrangement in `.eval.ts`

The TypeScript builder uses methods instead of shared runtime fixtures:

- `.copy(from, dest)` seeds files into the eval workspace.
- `stageAgent(...)` and `stageSkill(...)` arrange agent or skill content when a
  builder spec needs explicit staging.
- `.check(name, ctx => true | [false, "msg"])` adds custom assertions. In
  structural evals (`kind: "none"` and no `.prompt(...)`), checks run directly
  against the repository with `ctx.root`, `ctx.read(rel)`, and `ctx.glob(pat)`.

## Value references (for metrics)

Metric `value:` may be a literal number or a `$`-reference resolved at run time:
`$judge.score`, `$judge.<name>.score`, `$duration`,
`$stdout.words|chars|lines`, `$assertions.pass_rate`, `$checks.pass_rate`,
`$tokens.total|input|output`, and `$tools.count` / `$tools.count(<name>)`.

## Tags

Tags are arbitrary labels in spec frontmatter (`tags: [...]`) or the builder's
`tags` array. They drive selection at run time:

```bash
evalpilot run -t structural       # only 'structural'
evalpilot run -t "smoke,-slow"    # include 'smoke', exclude 'slow'
```

Common conventions: `pack`, `skill`, `smoke`, `slow`, `judge`, `structural`,
`tooling`.

## Runners

The SUT is driven by a pluggable runner selected with `EVALPILOT_RUNNER` or
`--runner`:

- `copilot` (default) — launches the real Copilot CLI.
- `mock` — deterministic and offline; use `EVALPILOT_RUNNER=mock` or
  `evalpilot run --runner mock` to exercise staging, assertions, judge, metrics,
  and rendering without a `copilot` binary or tokens.

Structural evals do not use a SUT runner.

## Environment variables

| Variable | Effect |
|---|---|
| `EVALPILOT_REPO_ROOT` | Override detected repository root. |
| `EVALPILOT_EVAL_ROOT` | Override `evals/` location. |
| `EVALPILOT_METRICS_ROOT` | Override metric history location. |
| `EVALPILOT_RUNNER` | Select SUT runner; default is `copilot`; use `mock` for offline runs. |
| `EVALPILOT_JUDGE_THRESHOLD` | Default judge pass threshold; default is `0.7`. |
| `EVALPILOT_SKIP_SUT` | Do not launch the SUT; live evals produce `SKIP` results. |
| `EVALPILOT_SUT_TIMEOUT` | Clamp every SUT subprocess timeout. |
| `EVALPILOT_TELEMETRY` | Telemetry capture for `tools`/`files_accessed`/`tokens` asserts; default on, set `off`/`0`/`false`/`none`/`no` to disable (those asserts then skip). |
| `COPILOT_BIN` | Path to the `copilot` binary. |

## Telemetry-based assertions

The `copilot` runner enables Copilot's OpenTelemetry file exporter per run
(`COPILOT_OTEL_FILE_EXPORTER_PATH` + genai content capture), then parses the
emitted JSONL into a normalized telemetry model on the run result. This powers
the `tools`, `files_accessed`, and `tokens` assertion families and the
`$tokens.*` / `$tools.count` metric refs — all offline, no collector or network.

When telemetry is unavailable (the `mock` runner, `EVALPILOT_TELEMETRY=off`, or
a copilot build without the exporter), those assertions **skip** rather than
fail: they are neutral and excluded from the pass-rate. Captured telemetry stays
in the run's log directory (`<log>.otel.jsonl`) and is never written into the
committed report.

# Staging, Tags, Runners, and Environment

## Staging (the `## Setup` section)

Each eval runs in an isolated workspace. Staging controls what is placed there
before the `## Act` prompt runs.

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

## Value references (for metrics)

Metric `value:` may be a literal number or a `$`-reference resolved at run time:
`$judge.score`, `$judge.<name>.score`, `$duration`,
`$stdout.words|chars|lines`, `$assertions.pass_rate`, `$checks.pass_rate`.

## Tags

Tags replace the old pytest markers. They are arbitrary labels in the
frontmatter `tags: [...]` list and drive selection at run time:

```bash
evalpilot run -t smoke            # only 'smoke'
evalpilot run -t "smoke,-slow"    # include 'smoke', exclude 'slow'
```

Common conventions: `smoke`, `slow`, `judge`, `metric`, `skill`, `pack`.

## Runners

The SUT is driven by a pluggable runner selected with `EVALPILOT_RUNNER` or
`--runner`:

- `copilot` (default) — launches the real Copilot CLI.
- `mock` — deterministic, offline; runs staging, assertions, judge, metrics,
  and rendering with no `copilot` binary and no tokens. Script it with
  `EVALPILOT_MOCK_STDOUT`, `EVALPILOT_MOCK_FILES` (JSON), and
  `EVALPILOT_MOCK_JUDGE_SCORE`.

Add a runner by subclassing `evalpilot.runners.base.SUTRunner`, decorating it
with `@register_runner`, and selecting it via `EVALPILOT_RUNNER`.

## Environment variables

| Variable | Effect |
|---|---|
| `EVALPILOT_REPO_ROOT` | Override detected repository root. |
| `EVALPILOT_EVAL_ROOT` | Override `evals/` location. |
| `EVALPILOT_METRICS_ROOT` | Override metric history location. |
| `EVALPILOT_RUNNER` | Select SUT runner; default is `copilot`. |
| `EVALPILOT_JUDGE_THRESHOLD` | Default judge pass threshold; default is `0.7`. |
| `EVALPILOT_SKIP_SUT` | Do not launch the SUT; live evals produce `SKIP` results. |
| `EVALPILOT_SUT_TIMEOUT` | Clamp every SUT subprocess timeout. |
| `COPILOT_BIN` | Path to the `copilot` binary. |

The engine also accepts legacy aliases `EVALS_SKIP_SUT`, `EVALS_SUT_TIMEOUT`,
and `EVAL_JUDGE_THRESHOLD` in the runner/judge paths.

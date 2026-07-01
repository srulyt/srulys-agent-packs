# Eval Authoring (evalpilot TypeScript engine)

This is the cross-cutting reference for authoring evals against **Eval Pilot**,
the TypeScript `@evalpilot/cli` engine. Read it once; then copy templates from
`evals/_templates/` and fill in the blanks.

## Mental model

An eval is a single self-contained spec file. It:

1. Declares `name`, `target`, `kind`, tags, and timeout.
2. Stages any needed agent/skill/files.
3. Runs the system-under-test through `evalpilot run` unless it is structural.
4. Asserts on output and generated artifacts.
5. Optionally calls the bundled LLM judge and records metrics.

Eval-pilot lives at `agent-packs/eval-pilot/`. The engine is
`@evalpilot/cli` from `agent-packs/eval-pilot/engine-ts/`.

## Required directory shape per generated pack

```
evals/packs/<pack>/
├── README.md
├── <scenario>.eval.md          # behavioral pack eval
└── <scenario>.eval.ts          # optional builder or structural eval
```

For skill evals:

```
evals/skills/<skill>/
└── <scenario>.eval.md
```

## Markdown pack eval template

```markdown
---
name: <pack>-smoke-<scenario>
target: <entry-agent>
kind: agent
tags: [pack, smoke, judge]
timeout: 900
---

# <Human-readable scenario title>
> One sentence summary.

## Act
```prompt
... user prompt that exercises the scenario ...
```

## Assert
```yaml
files:
  exists: ["<expected-artifact-glob>"]
contains:
  - { text: "<stable keyword>", ignore_case: true }
judge:
  threshold: 0.7
  criteria: |
    Score 1.0 only when ALL required qualities are present. Give 0.5 for
    partial work and 0.0 for off-topic or missing artifacts.
metrics:
  - { name: judge_score, value: $judge.score, direction: higher_is_better,
      baseline: rolling_mean, tolerance: 0.1 }
```
```

## Skill eval template

Use `kind: skill` and the skill name as `target`:

```markdown
---
name: <skill>-smoke-<scenario>
target: <skill-name>
kind: skill
tags: [skill, smoke]
timeout: 300
---

# <Scenario>
> The skill produces useful output for a representative request.

## Act
```prompt
... small task that exercises the skill ...
```

## Assert
```yaml
contains:
  - { text: "<stable keyword>", ignore_case: true }
```
```

## Structural eval template

Use structural evals for packaging conformance and repository checks. They use
`kind: "none"` and no `.prompt(...)`, so they run offline.

```ts
import { Eval } from "@evalpilot/cli";

export default new Eval("<pack>-plugin-shape", {
  target: "<pack>",
  kind: "none",
  tags: ["pack", "structural", "tooling"],
})
  .check("README exists", (ctx) =>
    ctx.read("agent-packs/<pack>/README.md") ? true : [false, "missing README"]
  )
  .check("has agent files", (ctx) =>
    ctx.glob("agent-packs/<pack>/.github/agents/*.agent.md").length > 0
      ? true
      : [false, "missing agent files"]
  )
  .build();
```

In `.check()`, `ctx.root` is the repo root, `ctx.read(rel)` returns text or
`null`, and `ctx.glob(pat)` returns sorted absolute paths.

## Tags

Use tags, not runner-specific markers:

| Tag | Meaning |
|---|---|
| `pack` | exercises a full agent pack/plugin |
| `skill` | exercises a single skill in isolation |
| `smoke` | representative confidence scenario |
| `slow` | long-running behavioral eval |
| `judge` | invokes the LLM-as-judge |
| `structural` | offline repository/file conformance check |
| `tooling` | engine or repository tooling check |

Filter with `evalpilot run -t "smoke,-slow"`.

## Hard rules

- One scenario per eval spec. Do not bundle unrelated scenarios.
- Never put expected-answer text in the user prompt.
- Be strict in judge criteria: state what earns 1.0 and what earns partial credit.
- Always include at least one stable structural assertion.
- Use structural `*.eval.ts` for pack-shape checks.
- Always quote YAML `description` fields in agent files generated alongside evals.

## Running locally

```powershell
evalpilot run evals/                         # everything
evalpilot run evals/packs/<pack>/            # one pack path
evalpilot run evals/skills/<skill>/          # one skill path
evalpilot run evals/ -t "smoke,-slow"        # tag expression
evalpilot run evals/ --parallel 4            # concurrent workers
evalpilot run evals/ --runner mock           # offline runner
node scripts/run-evals.mjs <pack>            # repo convenience
node scripts/run-evals.mjs <pack> --mock
```

Useful environment knobs:

- `COPILOT_BIN` points eval-pilot at a specific `copilot` binary.
- `EVALPILOT_SUT_TIMEOUT` clamps SUT subprocess timeouts.
- `EVALPILOT_SKIP_SUT=1` prevents launching the SUT; live evals skip.
- `EVALPILOT_RUNNER=mock` selects the offline runner.

## Running for the factory fix-loop

The factory should run the target through eval-pilot:

```powershell
evalpilot run evals/packs/<pack>
```

For offline structural or smoke checks:

```powershell
evalpilot run evals/packs/<pack> --runner mock
```

The engine writes `evals/_runs/<run-id>/report.json` and returns `0` when the
run gates pass, `1` when any eval fails.

## Hard checklist for the Factory Engineer

- [ ] `evals/packs/<pack>/<scenario>.eval.md` or `.eval.ts` exists.
- [ ] Behavioral specs include `target`, `kind`, tags, action prompt, and checks.
- [ ] Structural specs use `kind: "none"`, no `.prompt(...)`, and `.check(...)`.
- [ ] At least one stable structural assertion exists.
- [ ] Judge criteria are concrete and strict when judge is used.
- [ ] Eval files appear under `files_created` and `evals_created.tests` in the
      build manifest.
- [ ] `evalpilot lint evals/packs/<pack>/` succeeds.

## Source of truth

When this pack is deployed standalone, this reference is authoritative for
factory-generated eval shape. In the monorepo, the runtime source of truth is
the eval-pilot plugin under `agent-packs/eval-pilot/`: its `README.md`,
`skills/eval-author/SKILL.md`, `skills/eval-runner/SKILL.md`, and
`engine-ts/README.md`.

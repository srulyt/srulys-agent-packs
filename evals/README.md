# `evals/` — evalpilot TypeScript eval harness

This directory dogfoods **Eval Pilot**, the TypeScript `evalpilot` engine
from `agent-packs/eval-pilot/engine-ts/`. Eval specs are single, readable files
that produce binary rubric signal, LLM-as-judge results, and numeric metric
history over time.

To run evals from the repo root:

```powershell
npm run engine:build
npm run eval
npm run eval:all
npm run eval:mock
node scripts/run-evals.mjs --all
node scripts/run-evals.mjs copilot-factory
node scripts/run-evals.mjs eval-author --mock -- -t structural
.\eval.cmd copilot-factory
.\eval.cmd --all
.\eval.cmd eval-author --list
```

You can also invoke the engine directly. `target` is a file or directory path:

```powershell
evalpilot run evals/
evalpilot run evals/packs/copilot-factory/
evalpilot run evals/skills/agent-builder/
evalpilot run evals/ -t "smoke,-slow"
evalpilot run evals/ --parallel 4
evalpilot run evals/ --runner mock
```

`EVALPILOT_RUNNER=mock` is equivalent to `--runner mock` for offline runs.

## Layout

```
evals/
├── _templates/              # pack.eval.md, skill.eval.md, structural.eval.ts
├── _metrics/                # committed JSONL metric history
├── _runs/                   # generated reports (gitignored)
├── packs/<pack>/*.eval.*    # pack eval specs
├── skills/<skill>/*.eval.*  # skill eval specs
└── static/                  # structural repository checks
```

## Anatomy of a Markdown eval

```markdown
---
name: copilot-factory-smoke
target: copilot-factory
kind: agent
tags: [pack, smoke, judge]
timeout: 900
---

# Creates a useful triage pack
> The factory creates the requested agent artifacts and explains how to use them.

## Act
```prompt
Design and build a two-agent issue triage pack.
```

## Assert
```yaml
files:
  exists: ["agent-packs/**/README.md"]
contains:
  - { text: "triage", ignore_case: true }
judge:
  threshold: 0.7
  criteria: |
    Score 1.0 only if the result includes clear agent roles, artifact paths,
    and usage steps. 0.5 partial; 0.0 off-topic.
metrics:
  - { name: judge_score, value: $judge.score, direction: higher_is_better,
      baseline: rolling_mean, tolerance: 0.1 }
```
```

## TypeScript and structural evals

Use `*.eval.ts` when a spec needs computed setup or direct repository checks:

```ts
import { Eval } from "evalpilot";

export default new Eval("pack-readme-present", {
  target: "my-pack",
  kind: "none",
  tags: ["structural", "tooling"],
})
  .check("README exists", (ctx) =>
    ctx.read("agent-packs/my-pack/README.md") ? true : [false, "missing README"]
  )
  .check("has agents", (ctx) => ctx.glob("agent-packs/my-pack/.github/agents/*.agent.md").length > 0)
  .build();
```

Structural evals use `kind: "none"` and no `.prompt(...)`; they run offline and
never launch Copilot. In `.check()`, `ctx.root` is the repo root,
`ctx.read(rel)` returns `text | null`, and `ctx.glob(pat)` returns sorted
absolute paths.

## Authoring a new eval

1. Copy a template from `evals/_templates/`:
   - Pack behavior: `pack.eval.md` → `evals/packs/<pack>/<scenario>.eval.md`
   - Skill behavior: `skill.eval.md` → `evals/skills/<skill>/<scenario>.eval.md`
   - Repository conformance: `structural.eval.ts` → the relevant eval directory
2. Edit the placeholders: prompt, target name, structural checks, judge criteria,
   tags, and metrics.
3. Validate: `evalpilot lint <file>` or `npm run lint:evals`.
4. Run: `evalpilot run <file>` or `node scripts/run-evals.mjs <pack>`.
5. Iterate: tighten criteria, add stable structural checks, and tag long-running
   cases with `slow`.

## Logs and failure analysis

- Each run writes a modeled result to `evals/_runs/<run-id>/report.json` and a
  self-contained HTML report to `evals/_runs/<run-id>/report.html`.
- `evals/_runs/latest.txt` points to the newest result. `_runs/` is gitignored.
- Behavioral SUT logs are referenced from each eval result via `log_path` under
  that run directory.
- Open the HTML with `evalpilot show --format html --open` for drill-down.

## Static pack-contract linter

`node scripts/lint-pack.mjs --all` validates each agent pack's `.agent.md` and
`SKILL.md` files (frontmatter shape, required keys, soft size caps). It is
also represented by structural evals and CI.

```powershell
node scripts/lint-pack.mjs --all
node scripts/lint-pack.mjs copilot-factory
node scripts/lint-pack.mjs copilot-factory --strict   # warnings = errors
```

## Tags

Tags are labels in spec frontmatter or the TypeScript builder. Common tags:

| Tag | Meaning |
|---|---|
| `pack` | exercises a full agent pack |
| `skill` | exercises a single skill in isolation |
| `smoke` | fast confidence scenario |
| `slow` | long-running scenario |
| `judge` | invokes the LLM-as-judge |
| `structural` | offline repository/file conformance check |
| `tooling` | engine or repository tooling check |

Filter with `-t "structural"` or `-t "smoke,-slow"`.

## Environment

| Variable | Effect |
|---|---|
| `COPILOT_BIN` | Override the path to the `copilot` binary. |
| `EVALPILOT_RUNNER` | Select the runner; use `mock` for offline runs. |
| `EVALPILOT_SKIP_SUT` | Do not launch the SUT; live evals produce `SKIP` results. |
| `EVALPILOT_SUT_TIMEOUT` | Clamp every SUT subprocess timeout. |

If `copilot` is not on `PATH` (and `COPILOT_BIN` is unset), live evals that
need it skip; structural evals and mock runs still work.

## Metrics

Metric declarations append JSONL history under `evals/_metrics/<slug>/`.
Inspect and gate them with:

```powershell
evalpilot metrics
evalpilot metrics --check
```

# Eval Pilot

**Eval Pilot** is a portable Copilot plugin that adds an easy-to-use eval
framework to any repository containing Copilot agents and/or skills. It ships a
user-facing skill workflow, an `eval-judge` agent, and exactly one eval engine:
the TypeScript **`@evalpilot/cli`** package, with source in `engine-ts/` and CLI
binary `evalpilot`.

An eval is a **single self-contained file** that reads top-to-bottom, so anyone
can understand what it does at a glance and author one in a few steps.

- **Markdown DSL (`*.eval.md`)** — YAML frontmatter + `## Setup` / `## Act` /
  `## Assert` sections. Prompts and judge criteria read as prose.
- **TypeScript builder (`*.eval.ts`)** — a fluent `Eval(...)` API for computed
  prompts, shared setup, and custom checks.
- **Structural evals** — `*.eval.ts` specs with `kind: "none"` and no
  `.prompt(...)`; they run offline and assert directly on repository files with
  `.check(name, ctx => true | [false, "msg"])`.
- **Modeled result** — every run writes a canonical `report.json` that the
  terminal, HTML, and JSON renderers all project from.
- **Metric trends** — numeric values append to committed JSONL history at
  `evals/_metrics/<slug>/history.jsonl` and compare against a baseline so
  regressions surface over time (with HTML sparkline charts).

Requires Node.js >= 18.

## Installation

The repository path to the plugin is `agent-packs/eval-pilot`.

### 1. GitHub Copilot CLI (primary — also lights up VS Code)

```bash
copilot plugin marketplace add srulyt/srulys-agent-packs
copilot plugin install eval-pilot@srulys-agent-packs
```

From a local clone:

```bash
copilot plugin marketplace add /absolute/path/to/srulys-agent-packs
copilot plugin install eval-pilot@srulys-agent-packs
```

Manage / verify:

```bash
copilot plugin marketplace browse srulys-agent-packs
copilot plugin list
copilot plugin enable eval-pilot
```

Invoke: run `/eval-pilot:eval-author`, `/eval-pilot:eval-runner`, or
`/eval-pilot:eval-metrics`, or ask naturally: "create and run evals for my agent".

### 2. VS Code GitHub Copilot (agent plugin)

1. Enable the preview `chat.plugins.enabled` setting if required.
2. Discover the plugin by any of:
   - CLI install auto-discovery under `~/.copilot/installed-plugins/`.
   - Command Palette → **Chat: Install Plugin From Source** →
     `https://github.com/srulyt/srulys-agent-packs.git`.
   - Local development setting:
     ```jsonc
     "chat.pluginLocations": {
       "/absolute/path/to/srulys-agent-packs/agent-packs/eval-pilot": true
     }
     ```

### 3. `gh skill` (agentskills.io — preview)

```bash
gh skill install srulyt/srulys-agent-packs eval-author
gh skill install srulyt/srulys-agent-packs eval-runner
gh skill install srulyt/srulys-agent-packs eval-metrics
# or from a local clone:
gh skill install --from-local ./agent-packs/eval-pilot/skills/eval-author
```

## What ships in the package

```
agent-packs/eval-pilot/
├── plugin.json
├── README.md
├── agents/
│   └── eval-judge.agent.md
├── skills/
│   ├── eval-author/   (SKILL.md + references/)
│   ├── eval-runner/SKILL.md
│   └── eval-metrics/SKILL.md
└── engine-ts/         (TypeScript @evalpilot/cli source)
```

## Engine installation

Install the engine in a repository that will author or run evals:

```bash
npm install --save-dev @evalpilot/cli
# or run without installing:
npx @evalpilot/cli --help
```

From this monorepo you can also use the built engine directly:

```bash
node agent-packs/eval-pilot/engine-ts/dist/cli.js --help
```

## Quick Start

```bash
npx evalpilot discover                                  # what can it see?
npx evalpilot init                                      # scaffold evals/
npx evalpilot new my-eval --target my-agent --kind agent # create a spec
# edit the prompt / criteria in the new *.eval.md ...
npx evalpilot lint                                      # validate, no SUT
npx evalpilot run evals/packs/my-agent                  # execute + render
npx evalpilot show --format html --open                 # open the report
npx evalpilot metrics --check                           # gate on regressions
```

Set `EVALPILOT_RUNNER=mock` or pass `--runner mock` to run the whole pipeline
offline (no `copilot` binary, no tokens). Structural evals are offline by
construction.

## Repository conveniences

From this repo root, the wrappers resolve a pack or skill **name** to its eval
directory and forward to the TypeScript engine:

```cmd
eval.cmd copilot-factory
eval.cmd eval-author --mock
eval.cmd --all
eval.cmd --list
eval.cmd copilot-factory -- -t "smoke,-slow"
```

```bash
node scripts/run-evals.mjs copilot-factory
node scripts/run-evals.mjs --all
node scripts/run-evals.mjs eval-author --mock -- -t structural
```

Repo-root scripts:

```bash
npm run eval
npm run eval:all
npm run eval:mock
npm run lint:evals
npm run lint:packs
npm run engine:build
npm run engine:test
```

The pack contract linter is `node scripts/lint-pack.mjs --all`.

## Engine CLI

- `evalpilot new <name> [--target T] [--kind agent|skill|none]` — scaffold a
  Markdown spec.
- `evalpilot run [target] [-t tags] [--parallel N] [--format ...] [--runner R] [--open]`
  — discover + execute specs; `target` is a file or directory path.
- `evalpilot show [run] [--format terminal|html] [--open]` — re-render a run.
- `evalpilot lint [target]` — validate specs without launching the SUT.
- `evalpilot metrics [slug] [--check] [-v] [--tail N]` — numeric trends / CI gate.
- `evalpilot discover [--json]` — list discoverable agents and skills.
- `evalpilot init [--force]` — scaffold `evals/` from bundled templates.

Tags replace runner-specific selection syntax. Common tags are `pack`, `skill`,
`smoke`, `slow`, `judge`, `structural`, and `tooling`; filter with
`-t "structural"` or `-t "smoke,-slow"`.

## Structural evals

Use structural evals for packaging conformance and repository checks that do not
need a live agent run:

```ts
import { Eval } from "@evalpilot/cli";

export default new Eval("plugin-has-readme", {
  target: "eval-pilot",
  kind: "none",
  tags: ["structural", "tooling"],
})
  .check("README exists", (ctx) =>
    ctx.read("agent-packs/eval-pilot/README.md") ? true : [false, "missing README"]
  )
  .check("skill docs exist", (ctx) => ctx.glob("agent-packs/eval-pilot/skills/*/SKILL.md").length > 0)
  .build();
```

For structural checks, `ctx.root` is the repo root, `ctx.read(rel)` returns
`text | null`, and `ctx.glob(pat)` returns sorted absolute paths.

## Result locations

```text
evals/_runs/<run-id>/report.json    canonical modeled result
evals/_runs/<run-id>/report.html    shareable HTML (drill-down + trend charts)
evals/_runs/latest.txt              pointer to the newest report.json
evals/_metrics/<slug>/history.jsonl committed metric history
```

> License note: this repository does not ship a `LICENSE` file, so
> `plugin.json` intentionally omits a `license` field.

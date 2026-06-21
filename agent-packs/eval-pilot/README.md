# Eval Pilot

**Eval Pilot** is a portable Copilot plugin that adds eval capability to any repository containing Copilot agents and/or skills. It ships a user-facing skill workflow, an `eval-judge` agent, and a bundled pip-installable Python engine (`evalpilot`).

It uses a dual result model:

- **Rubric** — binary pass/fail checks, combining structural assertions and LLM-as-judge verdicts.
- **Metric** — numeric values appended to committed JSONL history at `evals/_metrics/<slug>/history.jsonl` and compared with a baseline to detect regressions over time.

> The engine is bundled under `engine/`, but it must be installed with `pip` before `evalpilot` CLI commands or pytest fixtures are available.

## Installation

The repository path to the plugin is `agent-packs/eval-pilot`.

### 1. GitHub Copilot CLI (primary — also lights up VS Code)

Register this repo as a marketplace once, then install the plugin:

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

Interactive equivalent inside a session: `/plugin marketplace add srulyt/srulys-agent-packs` then `/plugin install eval-pilot@srulys-agent-packs`.

Invoke: run `/eval-pilot:eval-author`, `/eval-pilot:eval-runner`, or `/eval-pilot:eval-metrics`, or ask naturally: "create and run evals for my agent".

### 2. VS Code GitHub Copilot (agent plugin)

1. Enable the preview `chat.plugins.enabled` setting if required by your environment.
2. Discover the plugin by any of:
   - CLI install auto-discovery under `~/.copilot/installed-plugins/`.
   - Command Palette → **Chat: Install Plugin From Source** → `https://github.com/srulyt/srulys-agent-packs.git`.
   - Local development setting:
     ```jsonc
     "chat.pluginLocations": {
       "/absolute/path/to/srulys-agent-packs/agent-packs/eval-pilot": true
     }
     ```

Invoke the skills from Chat or ask in natural language.

### 3. `gh skill` (agentskills.io — preview)

`gh skill` consumes `skills/<name>/SKILL.md` files directly and ignores `plugin.json`.

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
│   ├── eval-author/
│   │   ├── SKILL.md
│   │   └── references/
│   ├── eval-runner/SKILL.md
│   └── eval-metrics/SKILL.md
└── engine/
    └── ... pip-installable evalpilot package
```

## Quick Start

From this plugin directory:

```bash
pip install -e engine
```

From an installed plugin copy, install its bundled engine:

```bash
pip install ~/.copilot/installed-plugins/eval-pilot/engine
```

Then, in the repository you want to evaluate:

```bash
evalpilot discover
evalpilot init
```

Ask Copilot to author tests:

```text
Use eval-author to create rubric and metric evals for my <agent-or-skill>.
```

Run and inspect:

```bash
evalpilot run
evalpilot run evals/packs/<agent> -k smoke
evalpilot metrics
evalpilot metrics --check
```

## Engine CLI

- `evalpilot init [--force]` scaffolds `evals/` from bundled templates.
- `evalpilot discover [--json]` lists discoverable agents and skills.
- `evalpilot run [target] [-k EXPR] [-m MARKERS] [--parallel N]` runs pytest with a report-log summary.
- `evalpilot metrics [slug] [--check] [-v] [--tail N]` reports metric trends and can fail CI on latest regressions.

> License note: this repository does not ship a `LICENSE` file, so `plugin.json` intentionally omits a `license` field.

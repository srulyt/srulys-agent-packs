# Eval Pilot

**Eval Pilot** is a portable Copilot plugin that adds an easy-to-use eval
framework to any repository containing Copilot agents and/or skills. It ships a
user-facing skill workflow, an `eval-judge` agent, and a bundled
pip-installable Python engine (`evalpilot`).

An eval is a **single self-contained file** that reads top-to-bottom, so anyone
can understand what it does at a glance and author one in a few steps.

- **Markdown DSL (`*.eval.md`)** — YAML frontmatter + `## Setup` / `## Act` /
  `## Assert` sections. Prompts and judge criteria read as prose.
- **Python builder (`*.eval.py`)** — a fluent `Eval(...)` API for power users.
- **Modeled result** — every run writes a canonical `report.json` that the
  terminal, HTML, and JSON renderers all project from.
- **Metric trends** — numeric values append to committed JSONL history at
  `evals/_metrics/<slug>/history.jsonl` and compare against a baseline so
  regressions surface over time (with HTML sparkline charts).

> The engine is bundled under `engine/`, but it must be installed with `pip`
> before `evalpilot` CLI commands are available.

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
└── engine/            (pip-installable evalpilot package)
```

## Quick Start

From this plugin directory:

```bash
pip install -e engine
```

Then, in the repository you want to evaluate:

```bash
evalpilot discover                                   # what can it see?
evalpilot init                                       # scaffold evals/
evalpilot new my-eval --target my-agent --kind agent # create a spec
# edit the prompt / criteria in the new *.eval.md ...
evalpilot lint                                       # validate, no SUT
evalpilot run                                        # execute + render
evalpilot show --format html --open                  # open the report
evalpilot metrics --check                            # gate on regressions
```

Set `EVALPILOT_RUNNER=mock` to run the whole pipeline offline (no `copilot`
binary, no tokens) — handy for trying the framework out.

## Engine CLI

- `evalpilot new <name> [--target T] [--kind agent|skill] [--python]` —
  scaffold a `*.eval.md` (or builder `*.eval.py`) spec.
- `evalpilot run [target] [-t tags] [--parallel N] [--format ...] [--runner R] [--open]`
  — discover + execute specs; write `report.json` (+ HTML) under `_runs/<id>/`.
- `evalpilot show [run] [--format terminal|html] [--open]` — re-render a run.
- `evalpilot lint [target]` — validate specs without launching the SUT.
- `evalpilot metrics [slug] [--check] [-v] [--tail N]` — numeric trends / CI gate.
- `evalpilot discover [--json]` — list discoverable agents and skills.
- `evalpilot init [--force]` — scaffold `evals/` from bundled templates.

## Result locations

```text
evals/_runs/<run-id>/report.json    canonical modeled result
evals/_runs/<run-id>/report.html    shareable HTML (drill-down + trend charts)
evals/_runs/latest.txt              pointer to the newest report.json
evals/_metrics/<slug>/history.jsonl committed metric history
```

> License note: this repository does not ship a `LICENSE` file, so
> `plugin.json` intentionally omits a `license` field.

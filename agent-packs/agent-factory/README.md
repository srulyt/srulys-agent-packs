# Agent Factory

A skill-first factory for creating minimal reusable agent customizations and modernizing legacy packs without losing domain knowledge. It supplies missing context, capabilities, constraints and contracts; the model/harness supplies intelligence and runtime orchestration.

**No customization is a valid result.** This pack has one portable skill, selective references, and optional artifact examples. It has no custom factory agent, fixed team, thought-stage state machine, or obligatory review/delegation loop.

The legacy `copilot-factory` and `roo-agent-factory` packs remain available, but `init.cmd` now installs only this factory. Invoke the new **`agent-factory` skill**, not `@copilot-factory`.

## Installation

On Windows, run the repository's initializer to copy the canonical skill into `.github\skills\agent-factory`:

```powershell
.\init.cmd
```

No Node.js installer is required. Only this skill is copied; legacy factories are neither installed nor uninstalled. Re-running `init.cmd` overwrites matching files in the installed skill, so review or back up local edits first. It does not remove additional destination files or provide a sandbox.

For another project or host, copy the complete `skills\agent-factory` directory to the appropriate project-local location:

| Host | Destination |
| --- | --- |
| Copilot | `.github\skills\agent-factory` |
| Codex | `.agents\skills\agent-factory` |
| Claude Code | `.claude\skills\agent-factory` |

The source here is canonical and tracked; the checkout's installed `.github\skills\` copy is ignored. Do not edit separate vendor copies independently.

Copilot CLI plugin distribution:

```powershell
copilot plugin marketplace add srulyt/srulys-agent-packs
copilot plugin install agent-factory@srulys-agent-packs
```

The root manifest uses portable **Agent Plugins 1.0.0**, shared by documented current Copilot/Codex support. Claude Code uses the thin `.claude-plugin\plugin.json` wrapper and the same `skills\` tree; for local development, use `claude --plugin-dir .\agent-packs\agent-factory`. Check your exact client/surface before installing. Codex and Claude runtime execution has not been verified here.

Do not use the legacy npm pack installer for this skill-only plugin: it currently discovers agent-based/Roo layouts.

## Usage

Ask the default agent:

```text
Use the agent-factory skill to create the smallest customization for our
incident briefs. Here are our severity definitions and required brief fields...

Use the agent-factory skill to modernize <pack>. Preserve its business rules,
required approvals and output contracts. Write the migrated result to <destination>.
```

Codex supports `$agent-factory`; Claude Code uses the native slash skill entry (plugin installs namespace it). Restart/reload skills using the selected host's supported discovery controls. Do not install both plugin and project copies unnecessarily; duplicate names can confuse discovery/eval tooling.

## What it chooses

Nothing for a task already handled well; instructions for small broadly applicable invariants; skills for specialized reusable knowledge; prompts for invocation convenience; custom agents for enduring isolated context/tool/permission boundaries; MCP for missing capabilities; hooks/code/policy for actual enforcement; plugins for distribution only.

Modernization classifies meaning inside legacy files, preserves essential rules and domain-required ordering, and writes a concise migration record with source-to-destination provenance and unresolved behavior. Generic personas/choreography are not retained merely for familiarity.

The root skill directly links its selection, modernization, evaluation and platform references. They are loaded by relevance, not as a mandatory reading roster. [Platform freshness](skills/agent-factory/references/freshness.md) records dated first-party evidence and refresh triggers; model defaults remain inherited.

## Checks and evidence

```powershell
node .\scripts\run-evals.mjs agent-factory -- --tags structural
```

See [factory evaluations](../../evals/packs/agent-factory/README.md) for live scenarios, source-grounded preservation checks, comparisons, and honest runtime limitations. The legacy pack linter skips plugin-root skills; the new structural eval covers this pack explicitly without changing old contracts.

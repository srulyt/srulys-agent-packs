# Roo Agent Factory

## Overview

The Roo Agent Factory is a multi-agent system for designing and building Roo Code agent packs. It uses a boomerang orchestration pattern with four specialized agents.

## Location

`agent-packs/roo-agent-factory/`

Installed to the repository root via `init.cmd roo` or `init.cmd` (both).

- `.roomodes` - Mode definitions
- `.roo/` - Rules, skills, templates
- `.factory/` - Short-term memory (gitignored)

## Installation

```cmd
:: From the repository root
init.cmd roo
```

## Agents

| Agent | Slug | Responsibility |
|-------|------|----------------|
| Factory Orchestrator | `factory-orchestrator` | Coordinates workflow, manages user interaction, delegates to specialists |
| Factory Architect | `factory-architect` | Designs system architectures with agent topology and communication patterns |
| Factory Engineer | `factory-engineer` | Implements modes, rules, skills from architecture specs |
| Factory Critic | `factory-critic` | Reviews designs and implementations for quality and completeness |

## Orchestration Logic

```
User Request
    ↓
Factory Orchestrator
    ├── → Factory Architect (design)
    │        ↓
    ├── → Factory Critic (review design)
    │        ↓
    ├── → Factory Engineer (implement)
    │        ↓
    └── → Factory Critic (review implementation)
             ↓
        Delivery to User
```

### Boomerang Pattern

All sub-agents return control to the Orchestrator:
- **Success**: Task complete with deliverables
- **Questions**: Clarification needed (routed through Orchestrator)
- **Failure**: Cannot proceed (Orchestrator decides recovery)

## Skills Included

| Skill | Location | Purpose |
|-------|----------|---------|
| `stm-design` | `.roo/skills/stm-design/` | Patterns for short-term memory systems |
| `system-design` | `.roo/skills/system-design/` | Multi-agent architecture patterns |
| `copilot-cli-builder` | `.roo/skills/copilot-cli-builder/` | Templates for Copilot CLI agents |
| `pack-documentation` | `.roo/skills/pack-documentation/` | Documentation generation |
| `skill-creator` | `.roo/skills/skill-creator/` | Skill file creation |

## File Permissions

| Agent | Can Edit |
|-------|----------|
| Orchestrator | `.factory/*` (STM only) |
| Architect | `.factory/runs/*/artifacts/*.md` |
| Engineer | `.roomodes`, `.roo/**`, `.factory/**`, `agent-packs/**`, `docs/*.md` |
| Critic | (read-only) |

## Usage

1. Run `init.cmd roo` from the repository root
2. Open the repository in VS Code with Roo Code
3. Factory modes appear in the mode selector
4. Activate **Factory Orchestrator** to begin
5. Describe the agent pack you want to create
6. Factory creates pack under `agent-packs/`

### Example Request

> "Create a code review agent pack with an orchestrator, reviewer agent, and summary agent. The reviewer should analyze code for bugs and style issues, and the summary agent should compile findings into a report."

## State Management

Factory uses session-based STM in `.factory/`:

```
.factory/
└── runs/
    └── {session-id}/
        ├── state.json       # Session state
        ├── context/         # Input documents
        │   └── user-request.md
        └── artifacts/       # Output documents
            ├── system_architecture.md
            └── build-manifest.json
```

Session IDs follow format: `YYYY-MM-DD-{8-hex}` (e.g., `2026-01-22-3f8a2c1d`)

## Templates

Available in `.roo/templates/factory-agents/`:
- `example-roomode.md` - YAML syntax reference
- `example-rules.md` - Rule file structure
- `skill-template/SKILL.md` - Skill file format

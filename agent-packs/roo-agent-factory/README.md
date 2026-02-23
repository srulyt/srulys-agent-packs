# Roo Agent Factory

A multi-agent system for designing and building other Roo Code agent packs.

## Quick Start

1. From the repository root, run `init.cmd roo` (or `init.cmd` for both factories)
2. Open the repository in VS Code with Roo Code
3. Factory modes appear in the mode selector
4. Activate **Factory Orchestrator** and describe the pack you want to create

## Agents

| Agent | Slug | Responsibility |
|-------|------|----------------|
| Factory Orchestrator | `factory-orchestrator` | Coordinates workflow, manages user interaction, delegates to specialists |
| Factory Architect | `factory-architect` | Designs system architectures with agent topology and communication patterns |
| Factory Engineer | `factory-engineer` | Implements modes, rules, skills from architecture specs |
| Factory Critic | `factory-critic` | Reviews designs and implementations for quality and completeness |

## Orchestration

```
User Request
    ↓
Factory Orchestrator
    ├── → Factory Architect (design)
    ├── → Factory Critic (review design)
    ├── → Factory Engineer (implement)
    └── → Factory Critic (review implementation)
         ↓
    Delivery to User
```

## Skills Included

| Skill | Purpose |
|-------|---------|
| `stm-design` | Patterns for short-term memory systems |
| `system-design` | Multi-agent architecture patterns |
| `copilot-cli-builder` | Templates for Copilot CLI agents |
| `pack-documentation` | Documentation generation |
| `skill-creator` | Skill file creation |

## State Management

Factory uses session-based STM in `.factory/` (gitignored):

```
.factory/
└── runs/
    └── {session-id}/
        ├── state.json
        ├── context/
        │   └── user-request.md
        └── artifacts/
            ├── system_architecture.md
            └── build-manifest.json
```

## License

MIT

# Agent Packs Documentation

## Available Packs

| Pack | Location | Description | Status |
|------|----------|-------------|--------|
| [Factory](./factory.md) | Root | Multi-agent factory for creating agent systems | Stable |
| [Example Pack](./example-pack.md) | `agent-packs/example-pack/` | Starter template demonstrating pack structure | Template |

## Quick Start

### Using the Factory (creating agent packs)

1. Open this repository in VS Code
2. Factory modes are available immediately
3. Use Factory Orchestrator to create new packs

### Using other packs

1. Navigate to `agent-packs/{pack-name}/`
2. Follow the installation instructions in the pack's documentation
3. Copy or symlink to your target project, or open the pack folder directly

## Pack Structure

Each pack under `agent-packs/` contains:

```
{pack-name}/
├── .roomodes           # Mode definitions
├── .roo/               # Rules, skills, templates
│   └── rules-{slug}/   # Per-agent rules
└── README.md           # Quick start guide
```

## Adding New Packs

Use the Factory Orchestrator to create new packs:

1. Activate Factory Orchestrator mode
2. Describe the agent system you want to create
3. Factory creates the pack under `agent-packs/`
4. Documentation is added to this folder

## Documentation Convention

Each pack has a dedicated doc file: `docs/{pack-name}.md`

Documentation includes:
- Overview and use cases
- Agent roster with responsibilities
- Orchestration flow diagram
- Installation instructions
- Usage guide

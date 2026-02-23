# Copilot Factory

Create multi-agent systems for Roo Code or GitHub Copilot CLI.

## Quick Start

### Using with GitHub Copilot CLI

```bash
# Copy the .github folder to your project
cp -r .github /path/to/your/project/

# Start Copilot CLI
gh copilot

# Invoke the factory
@copilot-factory Create an agent pack for [describe your use case]
```

### Using with Roo Code

This pack is designed for Copilot CLI, but the concepts and skills can be referenced when using Roo Code's Agent Factory.

## What It Does

The Copilot Factory guides you through creating complete agent packs:

1. **Intake**: Captures your requirements and asks which platform you're targeting
2. **Design**: Creates a system architecture based on your needs
3. **Review**: Validates the design against requirements
4. **Approval**: Presents the architecture for your approval
5. **Build**: Generates all necessary files for your chosen platform
6. **Complete**: Provides usage instructions

## Target Platforms

When you invoke the factory, you'll be asked to choose a target:

| Target | What Gets Generated |
|--------|---------------------|
| `roo` | `.roomodes`, `.roo/rules-*/rules.md` |
| `copilot` | `.github/agents/*.agent.md`, `.github/skills/*/SKILL.md` |

## Agents

| Agent | Purpose |
|-------|---------|
| `@copilot-factory` | Main orchestrator - handles the workflow |
| `@factory-engineer` | Implementation specialist - creates files |

## Skills

| Skill | Purpose |
|-------|---------|
| `system-design` | Multi-agent architecture patterns |
| `agent-builder` | Templates for both platforms |

## State Management

Session state is stored in `.copilot-factory/sessions/{session-id}/`:

```
sessions/{session-id}/
├── state.json          # Workflow state
├── context/
│   └── user-request.md # Your requirements
└── artifacts/
    ├── architecture.md # System design
    └── build-manifest.json
```

## Example Usage

```
@copilot-factory Create an agent pack for code review automation.
The system should have a coordinator that assigns reviews to specialists
for different areas: security, performance, and style.
Target: copilot
```

## Generated Pack Location

All generated packs are created in:
```
agent-packs/{pack-name}/
```

## Troubleshooting

**Agent not found**: Ensure `.github/agents/` is in your project root.

**Skill not loading**: Check that `.github/skills/` exists and contains valid `SKILL.md` files.

**Session issues**: Delete `.copilot-factory/` to start fresh.

## License

MIT

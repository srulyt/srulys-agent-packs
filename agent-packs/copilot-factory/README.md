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

This pack runs in GitHub Copilot CLI and can generate artifacts for both Roo Code and Copilot targets.

## What It Does

The Copilot Factory guides you through creating complete agent packs:

1. **Intake**: Captures your requirements and asks which platform you're targeting
2. **Improve-Analysis** (improvement mode): Delegates existing-pack analysis to `@factory-critic`
3. **Design**: Delegates architecture creation to `@factory-architect`
4. **Review-Arch**: Delegates architecture validation to `@factory-critic`
5. **Approval**: Presents the architecture for your approval
6. **Build**: Delegates artifact generation to `@factory-engineer`
7. **Review-Prompts**: Delegates implementation validation to `@factory-critic`
8. **Complete**: Provides usage instructions

## Target Platforms

When you invoke the factory, you'll be asked to choose a target:

- `roo`: `.roomodes`, `.roo/rules-*/rules.md`
- `copilot`: `.github/agents/*.agent.md`, `.github/skills/*/SKILL.md`

## Agents

- `@copilot-factory`: Main orchestrator - manages phases, state, approvals, and delegation
- `@factory-architect`: Design specialist - creates architecture artifacts
- `@factory-engineer`: Implementation specialist - creates files from approved architecture
- `@factory-critic`: Quality gate - reviews architecture and implementation with PASS/BLOCKING verdicts

## Orchestration Pattern

```text
User Request
    ↓
@copilot-factory
    ├── → @factory-critic (improvement analysis, improvement mode)
    ├── → @factory-architect (design)
    ├── → @factory-critic (review architecture)
    ├── → User approval gate (required)
    ├── → @factory-engineer (build)
    └── → @factory-critic (review implementation)
         ↓
    Delivery to User
```

The orchestrator does not bypass these delegation steps.

## Skills

- `system-design`: Multi-agent architecture patterns
- `agent-builder`: Templates for both platforms

## State Management

Session state is stored in `.copilot-factory/sessions/{session-id}/`:

```text
sessions/{session-id}/
├── state.json          # Workflow state
├── context/
│   └── user-request.md # Your requirements
└── artifacts/
    ├── architecture.md # System design
    └── build-manifest.json
```

## Example Usage

```text
@copilot-factory Create an agent pack for code review automation.
The system should have a coordinator that assigns reviews to specialists
for different areas: security, performance, and style.
Target: copilot
```

## Generated Pack Location

All generated packs are created in:

```text
agent-packs/{pack-name}/
```

## Troubleshooting

**Agent not found**: Ensure `.github/agents/` is in your project root.

**Skill not loading**: Check that `.github/skills/` exists and contains valid `SKILL.md` files.

**Session issues**: Delete `.copilot-factory/` to start fresh.

**Git noise**: Add `.copilot-factory/` to your project's `.gitignore` to avoid committing session state.

## License

MIT

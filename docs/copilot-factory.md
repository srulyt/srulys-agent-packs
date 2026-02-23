# Copilot Factory

A GitHub Copilot CLI agent pack for creating multi-agent systems targeting either Roo Code or Copilot CLI.

## Overview

The Copilot Factory is a two-agent system that guides users through designing and building multi-agent packs. It mirrors the workflow of the Roo Code Agent Factory but uses Copilot CLI idioms.

### Key Features

- **Target Platform Selection**: Generate artifacts for Roo Code OR Copilot CLI
- **Structured Workflow**: Intake → Design → Review → Approval → Build → Complete
- **Skill-Based Knowledge**: Design patterns and templates loaded on demand
- **Session Management**: Persistent state for multi-turn workflows

## Agent Roster

| Agent | Role | Tools |
|-------|------|-------|
| **Copilot Factory** | Orchestrator - manages workflow and user interaction | read, edit, search, execute, agent, github/* |
| **Factory Engineer** | Implementer - creates agent pack files | read, edit, search |

### Copilot Factory (Orchestrator)

The main entry point for users. Responsibilities:
- Validate user requirements
- Prompt for target platform selection
- Design system architecture (with skill support)
- Get user approval
- Delegate implementation to Factory Engineer
- Present results with usage instructions

### Factory Engineer (Implementer)

Called by the Orchestrator to generate files. Responsibilities:
- Read architecture document
- Generate platform-specific artifacts
- Create README and documentation
- Update build manifest

**Note**: This agent has `disable-model-invocation: true` to prevent direct user access.

## Skills

### system-design

Multi-agent architecture patterns and guidance.

**Contents**:
- When to use single vs multi-agent approaches
- Agent topology patterns (hierarchical, flat, pipeline)
- Communication patterns
- State management approaches
- Tool assignment guidelines

**References**:
- `references/agent-patterns.md` - Detailed topology diagrams
- `references/communication.md` - Inter-agent protocols
- `references/state-management.md` - STM/LTM patterns

### agent-builder

Templates and implementation patterns for both platforms.

**Contents**:
- Roo Code artifact formats (.roomodes, rules.md)
- Copilot CLI artifact formats (.agent.md, SKILL.md)
- Quality checklists
- Common patterns and anti-patterns

**References**:
- `references/roo-artifacts.md` - Detailed Roo Code specs
- `references/copilot-artifacts.md` - Detailed Copilot CLI specs

**Assets**:
- `assets/roo/roomode-template.yaml`
- `assets/roo/rules-template.md`
- `assets/copilot/agent-template.md`
- `assets/copilot/skill-template.md`

## Workflow Phases

```
┌─────────┐    ┌─────────┐    ┌─────────┐
│ Intake  │───▶│ Design  │───▶│ Review  │
└─────────┘    └─────────┘    └────┬────┘
                                   │
     ┌─────────────────────────────┘
     ▼
┌──────────┐    ┌─────────┐    ┌──────────┐
│ Approval │───▶│  Build  │───▶│ Complete │
└──────────┘    └─────────┘    └──────────┘
```

### Phase Details

1. **Intake**: Capture requirements, select target platform (`roo` or `copilot`)
2. **Design**: Create architecture with agent definitions, tools, boundaries
3. **Review**: Validate architecture against requirements
4. **Approval**: Present architecture, get user sign-off
5. **Build**: Delegate to Factory Engineer, generate all files
6. **Complete**: Present summary and usage instructions

## State Management

Session state persists in `.copilot-factory/`:

```
.copilot-factory/
├── current-session.json        # Active session pointer
├── sessions/
│   └── {YYYY-MM-DD}-{hex}/
│       ├── state.json          # Phase, target, flags
│       ├── context/
│       │   └── user-request.md
│       └── artifacts/
│           ├── architecture.md
│           └── build-manifest.json
└── history/                    # Archived sessions
```

### state.json Schema

```json
{
  "session_id": "2026-02-23-a1b2c3d4",
  "phase": "design",
  "target_platform": "copilot",
  "target_system": "my-pack",
  "user_approved": false,
  "review_passed": false
}
```

## Target Platform Output

### Roo Code (`roo`)

```
agent-packs/{pack-name}/
├── .roomodes
├── .roo/
│   └── rules-{slug}/
│       └── rules.md
└── README.md
```

### Copilot CLI (`copilot`)

```
agent-packs/{pack-name}/
├── .github/
│   ├── agents/
│   │   └── {name}.agent.md
│   └── skills/
│       └── {name}/
│           └── SKILL.md
└── README.md
```

## Installation

### For Copilot CLI Users

```bash
# Copy the .github folder to your project
cp -r agent-packs/copilot-factory/.github /path/to/project/

# Also copy if you want local state (optional)
# Session state will be created on first use
```

### For Roo Code Users

The Copilot Factory is designed for Copilot CLI. For Roo Code, use the main Agent Factory at the repository root.

## Usage

### Starting the Factory

```bash
gh copilot
```

Then invoke:
```
@copilot-factory Create an agent pack for [your use case]
```

### Example Requests

**Simple pack**:
```
@copilot-factory Create a code review agent that checks for security issues.
Target: copilot
```

**Multi-agent pack**:
```
@copilot-factory Create a development workflow with:
- A coordinator that manages tasks
- A designer that creates specs
- An implementer that writes code
- A reviewer that checks quality
Target: roo
```

### During Workflow

The Factory will:
1. Ask clarifying questions if needed
2. Present architecture for approval
3. Generate files on approval
4. Provide usage instructions

## File Structure

```
agent-packs/copilot-factory/
├── .github/
│   ├── agents/
│   │   ├── copilot-factory.agent.md    # Orchestrator
│   │   └── factory-engineer.agent.md   # Implementer
│   ├── skills/
│   │   ├── system-design/
│   │   │   ├── SKILL.md
│   │   │   └── references/
│   │   └── agent-builder/
│   │       ├── SKILL.md
│   │       ├── references/
│   │       └── assets/
│   └── instructions/
│       └── factory.instructions.md
├── .copilot-factory/                    # State (gitignored)
└── README.md
```

## Comparison with Roo Factory

| Aspect | Roo Factory | Copilot Factory |
|--------|-------------|-----------------|
| Location | Repository root | `agent-packs/copilot-factory/` |
| Agents | 4 (Orchestrator, Architect, Engineer, Critic) | 2 (Factory, Engineer) |
| Design Knowledge | Separate Architect agent | system-design skill |
| Validation | Separate Critic agent | Built-in code-review |
| Orchestration | Explicit boomerang protocol | Implicit subagent returns |
| Tool Restrictions | `fileRegex` patterns | `tools` property |

## Troubleshooting

### "Agent not found"

Ensure `.github/agents/` exists in your project with the agent files.

### "Skill not loading"

Check that skill directories contain valid `SKILL.md` files with required frontmatter.

### "Session state error"

Delete `.copilot-factory/` to reset all sessions.

### "Target platform invalid"

Only `roo` and `copilot` are valid targets.

## License

MIT

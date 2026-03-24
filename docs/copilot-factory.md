# Copilot Factory

A GitHub Copilot CLI agent pack for creating multi-agent systems targeting either Roo Code or Copilot CLI.

## Overview

The Copilot Factory is a four-agent system that guides users through designing and building multi-agent packs. It uses a hierarchical pattern with an orchestrator delegating to specialized architect, engineer, and critic agents.

### Key Features

- **Target Platform Selection**: Defaults to Copilot CLI; supports Roo Code on request
- **Structured Workflow**: Intake → Design → Review → Approval → Build → Review → Complete
- **Improvement Mode**: Analyze existing packs with incremental or full rebuild options
- **Skill-Based Knowledge**: Design patterns and templates loaded on demand
- **Session Management**: Persistent state for multi-turn workflows
- **Reusable Prompts**: Pre-built prompts for common workflows

## Agent Roster

| Agent | Role | Tools |
|-------|------|-------|
| **Copilot Factory** | Orchestrator — manages workflow, user interaction, and delegation | read, edit, search, execute, agent |
| **Factory Architect** | Designer — creates system architecture documents | read, edit, search, web |
| **Factory Engineer** | Implementer — creates agent pack files from architecture | read, edit, search |
| **Factory Critic** | Quality gate — reviews architecture and implementation | read, search |

### Copilot Factory (Orchestrator)

The main entry point for users. Responsibilities:
- Validate user requirements
- Set target platform (defaults to `copilot`)
- Delegate architecture design to Factory Architect
- Gate on critic review before user approval
- Delegate implementation to Factory Engineer
- Gate on implementation review before delivery
- Present results with usage instructions

### Factory Architect (Designer)

Called by the Orchestrator to create architecture. Responsibilities:
- Read user requirements
- Design agent topology, boundaries, and communication patterns
- Specify tool restrictions per agent
- Write architecture document

**Note**: Has `disable-model-invocation: true` and `web` tool for research.

### Factory Engineer (Implementer)

Called by the Orchestrator to generate files. Responsibilities:
- Read architecture document
- Generate platform-specific artifacts
- Support both full builds and incremental improvements
- Create README and documentation
- Update build manifest

**Note**: Has `disable-model-invocation: true`.

### Factory Critic (Quality Gate)

Called by the Orchestrator for reviews. Responsibilities:
- Review architecture for requirement-fit and buildability
- Review implementation for architecture alignment
- Analyze existing packs for improvement opportunities
- Return PASS/BLOCKING verdicts with remediation guidance

**Note**: Has `disable-model-invocation: true` and read-only tools.

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

### Creation Mode
```
┌─────────┐    ┌─────────┐    ┌────────────┐    ┌──────────┐
│ Intake  │───▶│ Design  │───▶│ Review-Arch│───▶│ Approval │
└─────────┘    └─────────┘    └────────────┘    └────┬─────┘
                                                     │
     ┌───────────────────────────────────────────────┘
     ▼
┌─────────┐    ┌────────────────┐    ┌──────────┐
│  Build  │───▶│ Review-Prompts │───▶│ Complete │
└─────────┘    └────────────────┘    └──────────┘
```

### Improvement Mode
```
┌─────────┐    ┌──────────────────┐
│ Intake  │───▶│ Improve-Analysis │──┬──▶ incremental ──▶ Build ──▶ Review ──▶ Complete
└─────────┘    └──────────────────┘  │
                                     └──▶ rebuild ──▶ Design ──▶ (full pipeline)
```

### Phase Details

1. **Intake**: Capture requirements, set target platform (defaults to `copilot`, `roo` only if explicitly requested), determine mode
2. **Improve-Analysis** (improvement only): Critic analyzes existing pack, user chooses incremental or rebuild
3. **Design**: Architect creates architecture with agent definitions, tools, boundaries
4. **Review-Arch**: Critic validates architecture against requirements (PASS/BLOCKING)
5. **Approval**: Present architecture, get user sign-off
6. **Build**: Engineer generates all files (full build or incremental edits)
7. **Review-Prompts**: Critic validates implementation against architecture (PASS/BLOCKING)
8. **Complete**: Present summary and usage instructions

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
```

**Multi-agent pack**:
```
@copilot-factory Create a development workflow with:
- A coordinator that manages tasks
- A designer that creates specs
- An implementer that writes code
- A reviewer that checks quality
```

**Roo Code pack** (explicit override):
```
@copilot-factory Create a code review agent that checks for security issues.
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
│   │   ├── factory-architect.agent.md  # Designer
│   │   ├── factory-engineer.agent.md   # Implementer
│   │   └── factory-critic.agent.md     # Quality gate
│   ├── skills/
│   │   ├── system-design/
│   │   │   ├── SKILL.md
│   │   │   └── references/
│   │   └── agent-builder/
│   │       ├── SKILL.md
│   │       ├── references/
│   │       └── assets/
│   ├── instructions/
│   │   └── factory.instructions.md
│   └── prompts/
│       ├── analyze-and-improve.prompt.md
│       ├── create-pack.prompt.md
│       └── resume-session.prompt.md
├── .copilot-factory/                    # State (gitignored)
└── README.md
```

## Comparison with Roo Factory

| Aspect | Roo Factory | Copilot Factory |
|--------|-------------|-----------------|
| Location | Repository root | `agent-packs/copilot-factory/` |
| Agents | 4 (Orchestrator, Architect, Engineer, Critic) | 4 (Factory, Architect, Engineer, Critic) |
| Design Knowledge | Separate Architect agent | Architect agent + system-design skill |
| Validation | Separate Critic agent | Critic agent with PASS/BLOCKING verdicts |
| Orchestration | Explicit boomerang protocol | Implicit subagent returns |
| Tool Restrictions | `fileRegex` patterns | `tools` property |
| Improvement Mode | N/A | Incremental or full rebuild |

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

# Ralph Copilot CLI Pack

## Overview

Ralph is an autonomous agentic developer for GitHub Copilot CLI. Unlike traditional multi-agent Roo packs, Ralph operates as a **single agent with an external loop** that provides continuity across Copilot CLI invocations.

**Primary Use Case**: Structured, spec-driven development within the GitHub Copilot CLI ecosystem, with phase-based workflow management and resumable state.

## Location

`agent-packs/ralph-copilot-cli/`

## System Architecture

### Single Agent with External Loop

Ralph differs from other agent packs in this repository:

| Aspect | Traditional Roo Packs | Ralph Copilot CLI |
|--------|----------------------|-------------------|
| Platform | Roo Code extension | GitHub Copilot CLI |
| Orchestration | Internal (new_task) | External (loop script) |
| State | STM directories | `.ralph-stm/` |
| Agent Count | Multiple modes | Single agent file |
| Continuity | Mode switching | Script-driven restart |

### Components

| Component | File | Purpose |
|-----------|------|---------|
| Agent Definition | `.github/agents/ralph.agent.md` | Core agent logic and phase handling |
| Planning Skill | `.github/skills/planning/SKILL.md` | Planning phase guidance |
| Execution Skill | `.github/skills/execution/SKILL.md` | Execution phase guidance |
| Verification Skill | `.github/skills/verification/SKILL.md` | Verification phase guidance |
| Cleanup Skill | `.github/skills/cleanup/SKILL.md` | Cleanup phase guidance |
| PowerShell Loop | `ralph-loop.ps1` | Windows external orchestrator |
| Bash Loop | `ralph-loop.sh` | Unix/macOS external orchestrator |

## Workflow Phases

```text
User Request via Loop Script
    ↓
┌─────────────────────────────────────────────────────────────┐
│  Phase 0: INTAKE                                            │
│  Initialize STM, capture user request                       │
└─────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────┐
│  Phase 1: DISCOVERY                                         │
│  Explore codebase, identify patterns and structure          │
└─────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────┐
│  Phase 2: SPECIFICATION                                     │
│  Create detailed spec with acceptance criteria              │
└─────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────┐
│  Phase 3: PLANNING                                          │
│  Generate phase-based implementation plan                   │
└─────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────┐
│  Phase 4: APPROVAL                                          │
│  **User Gate** - Review spec and plan before proceeding     │
└─────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────┐
│  Phase 5: EXECUTION                                         │
│  Implement plan phase-by-phase with tests                   │
│  (Loop restarts Ralph for each plan phase)                  │
└─────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────┐
│  Phase 6: VERIFICATION                                      │
│  Run tests, check acceptance criteria                       │
│  (Returns to Phase 5 if issues found)                       │
└─────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────┐
│  Phase 7: CLEANUP                                           │
│  Generate summary, PR description, cleanup artifacts        │
└─────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────┐
│  Phase 8: COMPLETE                                          │
│  Workflow finished, results displayed                       │
└─────────────────────────────────────────────────────────────┘
```

### Phase Overview Table

| Phase | Name | Gate? | Description |
|-------|------|-------|-------------|
| 0 | Intake | No | Initialize STM and capture request |
| 1 | Discovery | No | Explore codebase structure and patterns |
| 2 | Specification | No | Create requirements with acceptance criteria |
| 3 | Planning | No | Generate phase-based implementation plan |
| 4 | Approval | **Yes** | User reviews and approves before execution |
| 5 | Execution | No | Implement changes phase-by-phase |
| 6 | Verification | No | Test and validate against criteria |
| 7 | Cleanup | No | Summarize work and prepare delivery |
| 8 | Complete | No | Workflow finished |

## STM Structure

Ralph maintains state in `.ralph-stm/`:

```
.ralph-stm/
├── active-run.json              # Points to current run
├── runs/                        # Session-isolated runs
│   └── {session-id}/            # Date-UUID format (e.g., 2026-02-02-a1b2c3d4)
│       ├── state.json           # Workflow state (phase, status)
│       ├── spec.md              # Requirements specification
│       ├── plan.md              # Implementation plan
│       ├── discovery-notes.md   # Codebase patterns discovered
│       ├── events/              # Timestamped task logs
│       │   └── {NNN}-{phase}-{action}.md
│       ├── communication/       # User interaction files
│       │   ├── pending-question.md
│       │   ├── user-response.md
│       │   ├── approval.md
│       │   └── rejection.md
│       └── heartbeat.json       # Activity timestamp for timeout detection
└── history/                     # Archived completed sessions
    └── {session-id}/
        └── summary.json
```

### State File Schema

```json
{
  "phase": 0,
  "status": "active",
  "task": "User's original request",
  "created_at": "ISO-8601",
  "updated_at": "ISO-8601"
}
```

## Installation

See [`agent-packs/ralph-copilot-cli/README.md`](../agent-packs/ralph-copilot-cli/README.md) for detailed installation instructions.

### Quick Start

1. **Prerequisites**: GitHub Copilot CLI v1.0+, GitHub CLI (gh) v2.0+

2. **Copy to your project**:
   ```bash
   mkdir -p .github/agents .github/skills/planning .github/skills/execution .github/skills/verification .github/skills/cleanup
   cp agent-packs/ralph-copilot-cli/.github/agents/ralph.agent.md .github/agents/
   cp agent-packs/ralph-copilot-cli/ralph-loop.* ./
   ```

3. **Copy skills**:
   ```bash
   cp agent-packs/ralph-copilot-cli/.github/skills/planning/SKILL.md .github/skills/planning/
   cp agent-packs/ralph-copilot-cli/.github/skills/execution/SKILL.md .github/skills/execution/
   cp agent-packs/ralph-copilot-cli/.github/skills/verification/SKILL.md .github/skills/verification/
   cp agent-packs/ralph-copilot-cli/.github/skills/cleanup/SKILL.md .github/skills/cleanup/
   ```

4. **Add to .gitignore**:
   ```gitignore
   .ralph-stm/
   ```

## Usage

### Start a New Task

**PowerShell (Windows):**
```powershell
.\ralph-loop.ps1 -Task "Add user authentication with JWT"
```

**Bash (macOS/Linux):**
```bash
./ralph-loop.sh "Add user authentication with JWT"
```

### Resume an Interrupted Session

```powershell
.\ralph-loop.ps1 -Resume
```

```bash
./ralph-loop.sh --resume
```

### Custom Timeout

Default heartbeat timeout is 15 minutes:

```powershell
.\ralph-loop.ps1 -Timeout 20 -Task "Complex feature"
```

```bash
./ralph-loop.sh --timeout 20 "Complex feature"
```

## Design Philosophy

### One Task Per Invocation

Ralph completes one logical task per Copilot CLI invocation, then exits. The external loop restarts it for the next task, keeping context fresh and enabling timeout recovery.

### Phase-Based Plans

Plans are organized into phases (logical units of work), not micro-tasks. This gives Ralph autonomy within each phase to adapt to the actual codebase.

### Maximum Autonomy

Ralph makes decisions autonomously when reasonable, only asking questions when truly blocked. Assumptions are documented in event logs.

### File-Based State

All state persists in STM files, enabling resume from any interruption point.

## Pack Structure

```
ralph-copilot-cli/
├── ralph-loop.ps1                 # PowerShell external loop
├── ralph-loop.sh                  # Bash external loop
├── README.md                      # Quick start guide
└── .github/
    ├── agents/
    │   └── ralph.agent.md         # Main agent definition
    └── skills/
        ├── planning/
        │   └── SKILL.md           # Planning phase
        ├── execution/
        │   └── SKILL.md           # Execution phase
        ├── verification/
        │   └── SKILL.md           # Verification phase
        └── cleanup/
            └── SKILL.md           # Cleanup phase
```

## Comparison with Agentic Developer

Both packs provide spec-driven development workflows:

| Feature | Agentic Developer | Ralph Copilot CLI |
|---------|-------------------|-------------------|
| Platform | Roo Code | GitHub Copilot CLI |
| Agents | 10 specialized modes | 1 agent + skills |
| Orchestration | Internal boomerang | External loop script |
| Phases | 12 phases | 9 phases |
| Bootstrap | Full project creation | Not supported |
| Memory | STM + LTM | STM only |
| Best For | Complex enterprise projects | CLI-based quick tasks |

## Limitations

- No parallel execution (one task at a time)
- Requires manual loop startup
- Limited to Copilot CLI's tool capabilities
- Context window limits affect very large tasks
- No bootstrap capability for new projects

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-02-01 | Initial release with 9-phase workflow |

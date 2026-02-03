# Ralph - Agentic Developer for GitHub Copilot CLI

Ralph is an autonomous development agent that implements features through a structured, phase-based workflow. It uses GitHub Copilot CLI's custom agent capabilities to provide spec-driven development with planning, execution, verification, and cleanup phases.

## Overview

Ralph transforms complex development tasks into structured workflows:

1. **Discovery** - Explores your codebase to understand patterns and structure
2. **Specification** - Creates detailed specs with testable acceptance criteria
3. **Planning** - Generates phase-based implementation plans
4. **Approval** - Pauses for your review before making changes
5. **Execution** - Implements changes phase-by-phase
6. **Verification** - Tests and validates against acceptance criteria
7. **Cleanup** - Summarizes work and prepares for delivery

## Prerequisites

- **GitHub Copilot CLI** v1.0 or later
  - Install: https://docs.github.com/en/copilot/github-copilot-cli
  - Authenticate: `gh auth login`
- **GitHub CLI** (gh) v2.0 or later
- **jq** (optional, recommended for better JSON parsing in bash)

## Installation

### Option 1: Copy to Your Project

Copy the following files to your project:

```bash
# Create directory structure
mkdir -p .github/agents
mkdir -p .github/skills/planning
mkdir -p .github/skills/execution
mkdir -p .github/skills/verification
mkdir -p .github/skills/cleanup

# Copy agent file
cp .github/agents/ralph.agent.md YOUR_PROJECT/.github/agents/

# Copy skills
cp .github/skills/planning/SKILL.md YOUR_PROJECT/.github/skills/planning/
cp .github/skills/execution/SKILL.md YOUR_PROJECT/.github/skills/execution/
cp .github/skills/verification/SKILL.md YOUR_PROJECT/.github/skills/verification/
cp .github/skills/cleanup/SKILL.md YOUR_PROJECT/.github/skills/cleanup/

# Copy loop scripts to project root
cp ralph-loop.ps1 YOUR_PROJECT/
cp ralph-loop.sh YOUR_PROJECT/
```

### Option 2: Install Globally

Copy to your personal Copilot configuration:

```bash
# On Windows
mkdir -p ~/.copilot/agents
mkdir -p ~/.copilot/skills/planning
mkdir -p ~/.copilot/skills/execution
mkdir -p ~/.copilot/skills/verification
mkdir -p ~/.copilot/skills/cleanup
cp .github/agents/ralph.agent.md ~/.copilot/agents/
cp .github/skills/planning/SKILL.md ~/.copilot/skills/planning/
cp .github/skills/execution/SKILL.md ~/.copilot/skills/execution/
cp .github/skills/verification/SKILL.md ~/.copilot/skills/verification/
cp .github/skills/cleanup/SKILL.md ~/.copilot/skills/cleanup/

# On macOS/Linux
mkdir -p ~/.copilot/agents
mkdir -p ~/.copilot/skills/planning
mkdir -p ~/.copilot/skills/execution
mkdir -p ~/.copilot/skills/verification
mkdir -p ~/.copilot/skills/cleanup
cp .github/agents/ralph.agent.md ~/.copilot/agents/
cp .github/skills/planning/SKILL.md ~/.copilot/skills/planning/
cp .github/skills/execution/SKILL.md ~/.copilot/skills/execution/
cp .github/skills/verification/SKILL.md ~/.copilot/skills/verification/
cp .github/skills/cleanup/SKILL.md ~/.copilot/skills/cleanup/
```

### Add to .gitignore

Add the STM (Short-Term Memory) directory to your `.gitignore`:

```gitignore
# Ralph STM (Short-Term Memory)
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

The default heartbeat timeout is 15 minutes. Customize it:

```powershell
.\ralph-loop.ps1 -Timeout 20 -Task "Complex feature"
```

```bash
./ralph-loop.sh --timeout 20 "Complex feature"
```

## Workflow

### Phase 0: Intake
Ralph initializes its STM (Short-Term Memory) and captures your request.

### Phase 1: Discovery
Ralph explores your codebase:
- Scans directory structure
- Identifies frameworks and patterns
- Locates relevant code
- Loads context packs if available

### Phase 2: Specification
Ralph creates a detailed specification:
- Functional and non-functional requirements
- Testable acceptance criteria (Given/When/Then)
- Scope boundaries
- Dependencies

### Phase 3: Planning
Ralph creates an implementation plan:
- Phase-based approach (not micro-tasks)
- Each phase is a logical unit of work
- Dependencies and risks noted

### Phase 4: Approval
The workflow pauses for your review:
- Review the spec at `.ralph-stm/spec.md`
- Review the plan at `.ralph-stm/plan.md`
- Approve to proceed, or provide feedback for revision

### Phase 5: Execution
Ralph implements the plan:
- One plan phase per invocation
- Tests run during implementation
- Progress tracked in state

### Phase 6: Verification
Ralph validates the implementation:
- Runs test suites
- Checks acceptance criteria
- Returns to execution if issues found

### Phase 7: Cleanup
Ralph finalizes:
- Generates work summary
- Creates PR description (if applicable)
- Removes temporary artifacts

### Phase 8: Complete
Workflow finished. Results displayed.

## User Communication

### Questions
If Ralph needs clarification on a blocking issue, the loop will pause and display the question. Answer in the terminal to continue.

### Approval
During the approval phase, you'll see:
- Specification summary
- Implementation plan
- Prompt to approve, reject, or provide feedback

## STM Structure

Ralph maintains state in `.ralph-stm/`:

```
.ralph-stm/
├── active-run.json              # Points to current run
├── runs/                        # Session-isolated runs
│   └── {session-id}/            # Date-UUID format (e.g., 2026-02-02-a1b2c3d4)
│       ├── state.json           # Workflow state
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
│       └── heartbeat.json       # Activity timestamp
└── history/                     # Archived completed sessions
    └── {session-id}/
        └── summary.json
```

## Troubleshooting

### Agent Not Found

If you get "agent not found" errors:
1. Verify files are in correct location
2. Check `.github/agents/ralph.agent.md` exists
3. Restart Copilot CLI: `gh copilot restart`

### Timeout Issues

If Ralph times out frequently:
1. Increase timeout: `-Timeout 30` or `--timeout 30`
2. Check network connectivity
3. Check Copilot service status

### JSON Parse Errors (Bash)

Install jq for reliable JSON parsing:
```bash
# macOS
brew install jq

# Ubuntu/Debian
sudo apt install jq

# Windows (with chocolatey)
choco install jq
```

### Stuck in a Phase

If Ralph gets stuck:
1. Check `.ralph-stm/state.json` for error status
2. Check latest event in `.ralph-stm/events/`
3. Try resuming: `--resume`
4. If necessary, delete `.ralph-stm/` and restart

### Permission Errors

Ensure loop scripts are executable:
```bash
chmod +x ralph-loop.sh
```

## Files Reference

| File | Purpose |
|------|---------|
| `.github/agents/ralph.agent.md` | Main agent definition |
| `.github/skills/planning/SKILL.md` | Planning phase guidance |
| `.github/skills/execution/SKILL.md` | Execution phase guidance |
| `.github/skills/verification/SKILL.md` | Verification phase guidance |
| `.github/skills/cleanup/SKILL.md` | Cleanup phase guidance |
| `ralph-loop.ps1` | PowerShell loop script |
| `ralph-loop.sh` | Bash loop script |

## Design Philosophy

### One Task Per Invocation
Ralph completes one logical task per Copilot CLI invocation, then exits. The external loop restarts it for the next task. This keeps context fresh and enables timeout recovery.

### Phase-Based Plans
Plans are organized into phases (logical units of work), not micro-tasks. This gives Ralph autonomy within each phase to adapt to the actual codebase.

### Maximum Autonomy
Ralph makes decisions autonomously when reasonable, only asking questions when truly blocked. Assumptions are documented in event logs.

### File-Based State
All state persists in STM files, enabling resume from any interruption point.

## Limitations

- No parallel execution (one task at a time)
- Requires manual loop startup
- Limited to Copilot CLI's tool capabilities
- Context window limits affect very large tasks

## Contributing

To modify Ralph's behavior:
- Edit `ralph.agent.md` for core logic changes
- Edit skill files for phase-specific guidance
- Edit loop scripts for lifecycle management changes

## License

MIT License - See repository root for details.

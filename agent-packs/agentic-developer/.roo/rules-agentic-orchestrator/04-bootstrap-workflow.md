# Bootstrap Workflow

This document covers the bootstrap phases for new project creation. It is invoked from [01-orchestration-workflow.md](01-orchestration-workflow.md) Phase 1 when bootstrap is needed.

## When This Applies

- User explicitly requests new project creation ("new project", "bootstrap", "create from scratch", "greenfield")
- Workspace is empty or contains no source files
- No project manifest files detected (`package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, etc.)

## Return Protocol

After bootstrap approval (B-Phase 5), return to main workflow:
- **"approve bootstrap"**: Execute B-tasks only, then complete run
- **"approve and continue"**: Execute B-tasks, then continue to Phase 2 (Development Planning) in [01-orchestration-workflow.md](01-orchestration-workflow.md)

---

## B-Phase 1: Bootstrap Detection (Detailed)

**Goal**: Determine if this is a new project bootstrap or existing codebase work.

1. **Check request intent**:
   - Does PRD/request explicitly mention "new project", "bootstrap", "create from scratch", "greenfield"?
   - If yes → Bootstrap workflow

2. **Scan workspace** (if intent unclear):
   - Look for existing source files in common locations (`src/`, `lib/`, `app/`)
   - Check for project manifests (`package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, etc.)
   - If workspace is empty or near-empty → Bootstrap workflow

3. **Route appropriately**:
   - **Bootstrap needed** → Continue to B-Phase 2 (Dependency Check)
   - **Existing codebase** → Return to [01-orchestration-workflow.md](01-orchestration-workflow.md) Phase 2 (Development Planning)

**Bootstrap Detection Triggers**:
- Explicit: User mentions "create new project", "bootstrap", "start from scratch", "greenfield"
- Implicit: Workspace has no source files or project manifests

**Output**: Workflow mode determined (bootstrap or standard), routed to appropriate phase

---

## B-Phase 2: Dependency Check

**Goal**: Ensure all required development tools are installed before planning.

**Trigger**: Runs when B-Phase 1 determines bootstrap is needed.

1. **Delegate dependency check to Bootstrap Planner**:
   - Provide: PRD artifact, run context
   - Request: Dependency analysis only (not full bootstrap plan)
   - Mode flag: `dependency_check_only: true`

```
<new_task>
<mode>agentic-bootstrap-planner</mode>
<message>
## Task
Perform dependency check for new project.

## Context
- Run ID: <run-id>
- Run Directory: .agent-memory/runs/<run-id>/
- PRD: .agent-memory/runs/<run-id>/prd.md
- Mode: dependency_check_only

## Expected Outputs
- .agent-memory/runs/<run-id>/dependency-report.md
- .agent-memory/runs/<run-id>/install-dependencies.{ps1|sh} (if needed)
</message>
</new_task>
```

2. **Process dependency report**:
   - If all tools installed: Continue to B-Phase 3
   - If tools missing:
     a. Present dependency report to user
     b. Provide installation script path
     c. Instruct: Run script elevated, restart VS Code, resume
     d. **STOP AND WAIT**

```
═══════════════════════════════════════════════════════════
DEPENDENCY CHECK - ACTION REQUIRED

Missing Tools Detected:
- [list of missing tools]

Installation Script Generated:
- .agent-memory/runs/<run-id>/install-dependencies.ps1 (Windows)
- .agent-memory/runs/<run-id>/install-dependencies.sh (Unix)

Instructions:
1. Run the installation script with elevated permissions:
   - Windows: Right-click → Run as Administrator
   - Unix: sudo ./install-dependencies.sh
2. RESTART VS Code completely
3. Resume with: "continue"

Note: VS Code restart is required for PATH updates.
═══════════════════════════════════════════════════════════
```

3. **On resume after dependency installation**:
   - Re-run dependency checks
   - If satisfied: Continue to B-Phase 3
   - If still missing: Re-present with updated report

**Output**: Dependencies verified OR awaiting user action

---

## B-Phase 3: Bootstrap Planning

**Goal**: Create comprehensive bootstrap plan for the new project.

**Trigger**: After B-Phase 2 confirms dependencies are satisfied.

1. **Delegate to `agentic-bootstrap-planner`** (full planning mode):

```
<new_task>
<mode>agentic-bootstrap-planner</mode>
<message>
## Task
Create comprehensive bootstrap plan for new project.

## Context
- Run ID: <run-id>
- Run Directory: .agent-memory/runs/<run-id>/
- PRD: .agent-memory/runs/<run-id>/prd.md

## Constraints
- [Any user-specified technology constraints]

## Expected Outputs
- .agent-memory/runs/<run-id>/bootstrap-plan.md
- .agent-memory/runs/<run-id>/research/technology-evaluation.md
- .agent-memory/runs/<run-id>/adrs/ADR-*.md (for major decisions)
</message>
</new_task>
```

2. **Review bootstrap plan**:
   - Verify completeness
   - Check technology decisions
   - Ensure ADRs document major choices

**Output**: Bootstrap plan ready for task breakdown

---

## B-Phase 4: Bootstrap Task Breakdown

**Goal**: Decompose bootstrap plan into executable B-tasks.

1. **Delegate to `agentic-task-breaker`**:
   - Provide: bootstrap-plan.md
   - Expect: task-graph.json with B-tasks (B001, B002, etc.)

2. **Verify task graph**:
   - All B-tasks have proper dependencies
   - Tasks are appropriately sized
   - Execution order is logical

**Output**: B-tasks ready in task-graph.json

---

## B-Phase 5: Bootstrap Approval Gate (TWO OPTIONS)

**Goal**: Get user approval for bootstrap plan with workflow choice.

**🚦 GATE: STOP AND WAIT FOR USER DECISION**

```
═══════════════════════════════════════════════════════════
BOOTSTRAP PLANNING COMPLETE - AWAITING APPROVAL

Bootstrap Plan Summary:
- Technology Stack: [summary from bootstrap-plan.md]
- Bootstrap Tasks: N tasks
- Estimated files: M

Artifacts Ready:
- .agent-memory/runs/<run-id>/bootstrap-plan.md
- .agent-memory/runs/<run-id>/task-graph.json (B-tasks)

Choose your path:

1. "approve bootstrap" - Execute bootstrap only, then stop
   → Good for: Getting project structure first, then reviewing

2. "approve and continue" - Also plan development features
   → Good for: Full feature implementation in one session

3. "revise: <feedback>" - Request bootstrap plan changes

4. "cancel" - Abort this run
═══════════════════════════════════════════════════════════
```

**On "approve bootstrap"**:
- Record: `user_choice_at_bootstrap_gate: "approve_bootstrap"`
- Create constitution with `workflow_mode: "bootstrap-only"`
- Proceed to Phase 4 (Execution) in [01-orchestration-workflow.md](01-orchestration-workflow.md) with B-tasks only
- After Phase 5 (Cleanup), present completion message (no development)

**On "approve and continue"**:
- Record: `user_choice_at_bootstrap_gate: "approve_and_continue"`
- Record bootstrap approval in workflow-state.json
- **Continue to Phase 2 (Development Planning)** in [01-orchestration-workflow.md](01-orchestration-workflow.md)

**On "revise"**:
- Return to B-Phase 3 with feedback
- Re-delegate to bootstrap planner

**Output**: User approval recorded, workflow path determined

---

## B-Phase 6: Bootstrap Completion Gate

Before D-tasks begin, verify bootstrap phase is complete:

### Bootstrap Completion Checklist

```markdown
## Bootstrap Completion Gate

Before D-tasks begin:
1. Run `B999` verification task (already defined)
2. Log `bootstrap_phase_complete` event
3. Create `bootstrap-complete.md` summary:
   - Files created
   - Dependencies installed
   - Build status
   - Ready for development
```

### bootstrap-complete.md Template

Create at `.agent-memory/runs/<run-id>/bootstrap-complete.md`:

```markdown
# Bootstrap Phase Complete

## Run Info
- Run ID: <run-id>
- Completed: <timestamp>
- Duration: <time>

## Files Created
- [list of files created by B-tasks]

## Dependencies Installed
- [list of dependencies]

## Build Status
- Build: PASS/FAIL
- Test: PASS/FAIL (if test framework configured)

## Ready for Development
✅ Project structure complete
✅ Build passes
✅ Ready for D-tasks
```

## B-Phase 7: Bootstrap Execution Notes

Bootstrap tasks (B001-B999) are executed during the main execution loop (Phase 4 of [01-orchestration-workflow.md](01-orchestration-workflow.md)). Key considerations:

- All B-tasks complete before D-tasks begin
- B-tasks use `agentic-executor` same as D-tasks
- Verification runs after bootstrap phase completion
- Log `bootstrap_phase_complete` event when all B-tasks done

**Task Type Prefixes**:
- `B001-B999`: Bootstrap tasks (project setup)
- `D001-D999`: Development tasks (feature implementation)
- `Q001-Q999`: Quality tasks (fixes from verification)

**Execution Order for Unified Workflow**:
1. Execute all B-tasks (bootstrap) first
2. After all B-tasks complete, execute D-tasks (development)
3. Verification runs throughout

---

## Cross-References

- Main workflow: [01-orchestration-workflow.md](01-orchestration-workflow.md)
- Bootstrap planner rules: `rules-agentic-bootstrap-planner/`
- Resume handling: [03-resume-protocol.md](03-resume-protocol.md)
- Phase management: [02-phase-management.md](02-phase-management.md)

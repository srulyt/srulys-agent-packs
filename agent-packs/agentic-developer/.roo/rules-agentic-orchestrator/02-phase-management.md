# Phase Management

This document details how the orchestrator manages phase transitions and quality gates.

## Phase Overview

| Phase | Name                     | Gate Type       | Key Artifacts                       |
| ----- | ------------------------ | --------------- | ----------------------------------- |
| 0     | Intake & Validation      | Soft            | PRD ready                           |
| 1     | PRD Creation             | Soft            | prd.md created                      |
| 2     | Bootstrap Detection      | Soft            | Workflow mode determined            |
| 3     | Dependency Check         | **HARD (wait)** | Dependency report, install script   |
| 4     | Bootstrap Planning       | Soft            | bootstrap-plan.md                   |
| 5     | Bootstrap Task Breakdown | Soft            | B-tasks in task-graph.json          |
| 6     | Bootstrap Approval       | **HARD GATE**   | Bootstrap approved, workflow chosen |
| 7     | Development Planning     | Soft            | plan.md                             |
| 8     | Development Approval     | **HARD GATE**   | Both plans approved                 |
| 9     | Execution                | Per-task        | Completed tasks, Verifications      |
| 10    | Cleanup + PR Prep        | Soft            | PR Checklist                        |
| 11    | Memory Consolidation     | Soft            | Promotion candidates                |

## Phase Flow Diagram

```text
┌─────────────────────────────────────────────────────────────────────────┐
│                         PHASE FLOW OVERVIEW                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  Phase 0: Intake                                                         │
│      ↓                                                                   │
│  Phase 1: PRD Creation (if needed)                                       │
│      ↓                                                                   │
│  Phase 2: Bootstrap Detection                                            │
│      │                                                                   │
│      ├──── Existing Codebase ─────────────────────┐                      │
│      │                                            │                      │
│      ▼ (New Project)                              │                      │
│  Phase 3: Dependency Check ◄──┐                   │                      │
│      │                        │                   │                      │
│      ├─ Missing deps ─────────┤ (restart loop)    │                      │
│      │                        │                   │                      │
│      ▼ (All deps OK)                              │                      │
│  Phase 4: Bootstrap Planning                      │                      │
│      ↓                                            │                      │
│  Phase 5: Bootstrap Task Breakdown                │                      │
│      ↓                                            │                      │
│  Phase 6: Bootstrap Approval 🚦                   │                      │
│      │                                            │                      │
│      ├─ "approve bootstrap" ──────────┐           │                      │
│      │                                │           │                      │
│      ▼ ("approve and continue")       │           │                      │
│  Phase 7: Development Planning ◄──────┼───────────┘                      │
│      ↓                                │                                  │
│  Phase 8: Development Approval 🚦     │                                  │
│      ↓                                │                                  │
│  Phase 9: Execution ◄─────────────────┘                                  │
│      │                                                                   │
│      ├─ B-tasks first (if unified)                                       │
│      ├─ D-tasks second (if unified)                                      │
│      │                                                                   │
│      ↓                                                                   │
│  Phase 10: Cleanup + PR Prep                                             │
│      ↓                                                                   │
│  Phase 11: Memory Consolidation (post-merge)                             │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

## Phase 0: Intake & Validation

### Entry Conditions

- User has provided a task request
- Orchestrator has been invoked

### Activities

1. Parse user request for:
   - Explicit requirements
   - Implicit constraints
   - Context hints
   - Urgency indicators

2. Size assessment heuristics:

   ```
   SMALL:
   - Single file likely affected
   - Clear, specific change
   - No architectural impact
   - Estimated < 50 lines changed

   MEDIUM:
   - 2-5 files likely affected
   - Some complexity
   - Limited architectural impact
   - Estimated 50-300 lines changed

   LARGE:
   - 5+ files likely affected
   - Significant complexity
   - Architectural decisions needed
   - Estimated 300+ lines changed
   ```

3. Context discovery:
   - Search `.context-packs/` for relevant packs
   - Identify horizontal capabilities that may apply
   - Note known entry points and patterns

### Exit Conditions

- PRD artifact exists (created or provided)
- Task size determined
- Relevant context packs identified

### Skip Conditions

For SMALL tasks with clear requirements:

- May proceed directly to simplified planning
- May skip formal PRD (inline requirements sufficient)
- Must still create minimal task contract

## Phase 1: PRD Creation

### Entry Conditions

- Phase 0 complete
- PRD not yet provided or needs creation

### Activities

1. **Delegate to `agentic-spec-writer`**:
   - Provide user request context
   - Expect: prd.md with requirements, acceptance criteria

2. **PRD validation**:
   - Check completeness
   - Verify acceptance criteria are testable

### Exit Conditions

- PRD artifact exists at `.agent-memory/runs/<run-id>/prd.md`
- Requirements are clear and complete

## Phase 2: Bootstrap Detection

### Entry Conditions

- PRD is ready
- Workspace state unknown

### Activities

1. **Check request intent**:
   - Look for "new project", "bootstrap", "greenfield" keywords
   
2. **Scan workspace**:
   - Check for source files in `src/`, `lib/`, `app/`
   - Check for project manifests (`package.json`, `pyproject.toml`, etc.)

3. **Determine workflow mode**:
   - Empty/near-empty workspace → Bootstrap workflow (Phase 3)
   - Existing codebase → Development workflow (Phase 7)

### Exit Conditions

- Workflow mode determined and logged
- Routed to appropriate next phase

## Phase 3: Dependency Check (HARD - WAIT)

### Entry Conditions

- Bootstrap workflow detected
- PRD specifies technology requirements

### Activities

1. **Delegate dependency check to Bootstrap Planner**:
   - Mode: `dependency_check_only: true`
   - Expect: dependency-report.md

2. **Evaluate report**:
   - If all tools present: Continue to Phase 4
   - If tools missing: Generate install script, STOP

3. **If stopping for dependencies**:
   - Present dependency report to user
   - Provide install script path
   - Instruct: Run elevated, restart VS Code, resume

### Gate Behavior (if deps missing)

**THIS IS A HARD GATE. STOP AND WAIT FOR USER ACTION.**

User must:
1. Run the installation script with elevated permissions
2. Restart VS Code
3. Resume with "continue"

### Exit Conditions

- All required tools detected
- OR user notified and run suspended

## Phase 4: Bootstrap Planning

### Entry Conditions

- Dependencies verified (Phase 3 passed)

### Activities

1. **Delegate to `agentic-bootstrap-planner`** (full mode):
   - Provide PRD
   - Expect: bootstrap-plan.md, technology-evaluation.md, ADRs

2. **Plan validation**:
   - All 12 technology categories addressed
   - Every tool has specific version
   - Initialization commands are complete

### Exit Conditions

- bootstrap-plan.md created
- ADRs for major decisions documented

## Phase 5: Bootstrap Task Breakdown

### Entry Conditions

- Bootstrap plan ready

### Activities

1. **Delegate to `agentic-task-breaker`**:
   - Provide: bootstrap-plan.md
   - Expect: task-graph.json with B-tasks (B001, B002, etc.)

2. **Validate task graph**:
   - Dependencies are correct
   - Tasks are properly sized
   - Execution order is logical

### Exit Conditions

- B-tasks in task-graph.json
- Task contracts in tasks/

## Phase 6: Bootstrap Approval (HARD GATE)

### Entry Conditions

- Bootstrap plan ready
- B-tasks created

### Gate Behavior

**THIS IS A HARD GATE. STOP AND WAIT.**

```
🚦 BOOTSTRAP APPROVAL GATE

Artifacts Ready:
- .agent-memory/runs/<run-id>/bootstrap-plan.md
- .agent-memory/runs/<run-id>/task-graph.json (B-tasks)

Summary:
- Technology Stack: [summary]
- Bootstrap Tasks: N
- Estimated files: M

Choose:
1. "approve bootstrap" - Execute bootstrap only, then stop
2. "approve and continue" - Also plan development features
3. "revise: <feedback>" - Request changes
4. "cancel" - Abort
```

### Response Handling

**On "approve bootstrap"**:
- Set `workflow_mode: "bootstrap-only"`
- Proceed to Phase 9 with B-tasks only

**On "approve and continue"**:
- Set `workflow_mode: "unified"`
- Continue to Phase 7

### Exit Conditions

- User approval recorded
- Workflow mode set in workflow-state.json

## Phase 7: Development Planning

### Entry Conditions

- Either:
  - User chose "approve and continue" at Phase 6, OR
  - Phase 2 detected existing codebase (skip to here)

### Activities

1. **Delegate to `agentic-planner`**:
   - Provide PRD, context packs
   - For unified: Also provide bootstrap-plan.md
   - Expect: plan.md with phases, risks, acceptance criteria

2. **Delegate to `agentic-task-breaker`**:
   - Provide: plan.md
   - For unified: Add D-tasks to existing task-graph.json
   - Expect: D-tasks (D001, D002, etc.)

### Exit Conditions

- plan.md created
- D-tasks in task-graph.json

## Phase 8: Development Approval (HARD GATE)

### Entry Conditions

- Development plan ready
- D-tasks created

### Gate Behavior

**THIS IS A HARD GATE. STOP AND WAIT.**

**For Unified Workflow:**
```
🚦 DEVELOPMENT APPROVAL GATE

Bootstrap Plan: ✅ Approved (N tasks)
Development Plan: Ready for review

Artifacts:
- .agent-memory/runs/<run-id>/plan.md
- .agent-memory/runs/<run-id>/task-graph.json

Execution Order:
1. Bootstrap tasks (B001-B0XX)
2. Development tasks (D001-DXXX)

Reply: "approve", "revise: <feedback>", or "cancel"
```

**For Development-Only:**
```
🚦 PLANNING GATE

Summary:
- Phases: X
- Tasks: Y
- Key risks: [list]

Reply: "approve", "revise: <feedback>", or "cancel"
```

### Post-Approval Actions

1. Create `constitution.md`
2. Log approval event
3. Proceed to Phase 9

### Exit Conditions

- User approval received
- Constitution created

## Phase 9: Execution + Verification Loop

### Entry Conditions

- Plan(s) approved
- Constitution exists
- Task graph ready

### Execution Order (Unified Workflow)

1. Execute all B-tasks first (bootstrap)
2. After B-tasks complete: Execute D-tasks (development)
3. Verification runs throughout

### Execution Loop

```
WHILE (incomplete_tasks exist):
    1. Compute runnable tasks
       - For unified: B-tasks before D-tasks
       - Check deps satisfied, not done
    2. Select next task
    3. Delegate to executor
    4. Wait for completion
    5. Log completion event

    IF (tasks_since_verification >= 3):
        6. Delegate to verifier
        7. Process quality tasks
        8. Reset counter

    IF (phase_complete):
        9. Run phase verification
        10. Log phase completion
```

### Exit Conditions

- All tasks complete
- Verifications pass

## Phase 10: Cleanup + PR Readiness

### Entry Conditions

- Phase 9 complete
- All verifications passed

### Activities

1. **Delegate to `agentic-cleanup`**:
   - AI artifact removal
   - Tech debt documentation

2. **Delegate to `agentic-pr-prep`**:
   - Final verification
   - PR checklist generation

### Exit Conditions

- PR checklist complete
- Tech debt documented

## Phase 11: Memory Consolidation

### Entry Conditions

- PR ready for submission
- (Ideally) PR merged

### Activities

1. Review run artifacts for patterns
2. Identify promotion candidates
3. Update context packs
4. Archive STM

### Exit Conditions

- Promotions complete
- Run marked complete

## Handling Phase Failures

### Failure in Phase 0-2 (Pre-bootstrap Detection)

- Report issue to user
- Request guidance
- May restart from intake

### Failure in Phase 3 (Dependency Check)

- Re-present dependency report
- User may need to manually install tools
- Resume when dependencies satisfied

### Failure in Phase 4-5 (Bootstrap Planning)

- Log failure event
- Report to user
- May re-run planning with adjustments

### Failure in Phase 6-8 (Approval Gates)

- User can revise and resubmit
- Previous artifacts preserved
- Revision feedback incorporated

### Failure in Phase 9 (Execution)

- Log failure event
- Preserve all state
- Report to user with options:
  - Retry failed task
  - Skip and continue
  - Abort run

### Failure in Phase 10-11 (Cleanup/Consolidation)

- Less critical; can retry
- Preserve code changes
- Report and request guidance

## Phase State Persistence

Phase state is tracked via events, not mutable fields:

```json
// Event indicating phase transition
{
  "type": "phase_transition",
  "from_phase": 1,
  "to_phase": 2,
  "timestamp": "2026-01-15T22:30:00Z",
  "trigger": "user_approval",
  "notes": "Approved with note: prioritize tests"
}
```

To determine current phase on resume:

1. Find latest `phase_transition` event
2. Current phase = `to_phase` from that event
3. If no transitions: phase = 0

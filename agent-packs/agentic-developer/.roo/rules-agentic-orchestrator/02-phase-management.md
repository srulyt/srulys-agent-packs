# Phase Management

This document details how the orchestrator manages phase transitions and quality gates.

---

# CORE SECTION

## Unified Phase System

The workflow uses a single phase numbering system (0-6 for main workflow, B1-B7 for bootstrap sub-phases).

| Phase | Name | Gate | Key Output |
|-------|------|------|------------|
| 0 | Intake & Validation | Soft | PRD ready, size assessed |
| 1 | Workflow Routing | Soft | Bootstrap or Development path |
| 2 | Planning | Soft | plan.md, task-graph.json |
| 3 | Approval | **HARD** | Constitution created |
| 4 | Execution + Verification | Per-task | Completed tasks |
| 5 | Cleanup + PR Prep | Soft | PR checklist |
| 6 | Memory Consolidation | Soft | LTM updated |

### Bootstrap Sub-Phases (Within Phase 1-3)

When bootstrap is detected:

| B-Phase | Name | Gate | Key Output |
|---------|------|------|------------|
| B1 | Bootstrap Detection | Soft | Bootstrap needed |
| B2 | Dependency Check | **HARD (wait)** | All tools present |
| B3 | Bootstrap Planning | Soft | bootstrap-plan.md |
| B4 | Bootstrap Task Breakdown | Soft | B-tasks in graph |
| B5 | Bootstrap Approval | **HARD** | Workflow choice |
| B6 | Bootstrap Completion | Soft | All B-tasks done |
| B7 | Transition to Development | Soft | D-planning begins |

---

## Phase Flow Diagram

```
Phase 0: Intake
    ↓
Phase 1: Routing ────────────────────────────┐
    │                                        │
    ├── [Bootstrap Needed]                   │
    │      ↓                                 │
    │   B2: Dependency Check 🚦              │
    │      ↓                                 │
    │   B3: Bootstrap Planning               │
    │      ↓                                 │
    │   B4: Task Breakdown                   │
    │      ↓                                 │
    │   B5: Bootstrap Approval 🚦            │
    │      │                                 │
    │      ├── "approve bootstrap" ────────────→ Phase 4 (B-tasks only)
    │      │                                 │
    │      └── "approve and continue" ───────┤
    │                                        │
    └── [Existing Codebase] ─────────────────┘
                    ↓
Phase 2: Development Planning
    ↓
Phase 3: Development Approval 🚦
    ↓
Phase 4: Execution + Verification
    ↓
Phase 5: Cleanup + PR Prep
    ↓
Phase 6: Memory Consolidation
```

---

## Gate Types

| Type | Behavior |
|------|----------|
| Soft | Auto-proceed on success |
| **HARD** | Stop and wait for user |
| Per-task | Verify after each task/batch |

---

## Size Assessment Heuristics

| Size | Criteria | Workflow |
|------|----------|----------|
| SMALL | Single file, clear change, <50 lines | Skip detailed planning |
| MEDIUM | 2-5 files, some complexity, 50-300 lines | Standard planning |
| LARGE | 5+ files, architectural, 300+ lines | Full planning |

---

## Bootstrap Interruption Handling

When a B-task fails during bootstrap phase:

### Immediate Actions

1. Log failure event with full context
2. Present status to user

### Status Presentation

```
BOOTSTRAP INTERRUPTED

Progress: {completed}/{total} bootstrap tasks complete
Failed Task: {B-task-id} - {title}
Error: {brief error summary}

Completed Tasks:
✓ B001 - {title}
✓ B002 - {title}
✗ B003 - {title} (FAILED)
○ B004 - {title} (pending)

Options:
1. "retry" - Retry the failed task with same context
2. "retry with: {guidance}" - Retry with additional guidance
3. "skip" - Mark as skipped, continue with remaining tasks
4. "abort" - Stop bootstrap, preserve completed work
```

### Option Handling

| Option | Action |
|--------|--------|
| retry | Re-delegate same task, increment attempt counter |
| retry with: | Re-delegate with additional context |
| skip | Mark B-task as SKIPPED, document impact, continue |
| abort | Log abort event, preserve artifacts, end run |

### Skip Consequences

When user chooses "skip":
1. Mark task as SKIPPED in task-graph.json
2. Add to constitution: `bootstrap_incomplete: [B003] skipped`
3. Add warning to PR checklist
4. Continue to next B-task
5. If skipped task was dependency, mark dependents as BLOCKED

---

# REFERENCE SECTION

## Phase 0: Intake & Validation

### Entry
- User provides task request

### Activities
1. Parse request for requirements, constraints, context hints
2. Size assessment (SMALL/MEDIUM/LARGE)
3. Context discovery in `.context-packs/`

### Exit
- PRD exists (provided or created)
- Size determined
- Context packs identified

### Skip Conditions (SMALL)
- May skip formal PRD
- May use inline requirements
- Must still create minimal task contract

---

## Phase 1: Workflow Routing

### Entry
- PRD ready

### Activities
1. Check for bootstrap keywords: "new project", "bootstrap", "greenfield"
2. Scan workspace for source files and manifests
3. Route to bootstrap (B-phases) or development (Phase 2)

### Exit
- Workflow mode determined

---

## Phase 2: Development Planning

### Entry
- Either: Existing codebase detected, OR bootstrap approved with "continue"

### Activities
1. Delegate to `agentic-planner` → plan.md
2. Delegate to `agentic-task-breaker` → task-graph.json with D-tasks

### Exit
- plan.md created
- D-tasks in task-graph.json

---

## Phase 3: Development Approval Gate

### Entry
- Plan and tasks ready

### Gate Presentation

```
═══════════════════════════════════════════════════════════
PLANNING COMPLETE - AWAITING APPROVAL

Summary:
- Phases: {count}
- Tasks: {count}
- Estimated files: {count}
- Key risks: {list}

Artifacts:
- .agent-memory/runs/{run-id}/plan.md
- .agent-memory/runs/{run-id}/task-graph.json

Reply: "approve", "revise: {feedback}", or "cancel"
═══════════════════════════════════════════════════════════
```

### Post-Approval
- Create constitution.md
- Log approval event
- Proceed to Phase 4

---

## Phase 4: Execution + Verification Loop

### Task Type Prefixes

| Prefix | Type | Priority |
|--------|------|----------|
| B001-B999 | Bootstrap | Execute first |
| D001-D999 | Development | Execute after B-tasks |
| Q001-Q999 | Quality | Execute immediately when created |

### Execution Loop

```
WHILE incomplete_tasks:
  1. Compute runnable (deps satisfied, not done)
  2. Prioritize: Q-tasks > current-phase tasks
  3. Delegate to executor
  4. Wait for completion
  5. Log event
  
  IF tasks_since_verification >= 3:
    6. Delegate to verifier
    7. Create Q-tasks if needed
    8. Reset counter
  
  IF phase_complete:
    9. Phase verification
    10. Log phase completion
```

### Exit
- All tasks complete
- All verifications pass

---

## Phase 5: Cleanup + PR Readiness

**MUST be sequential:**

1. Delegate to `agentic-cleanup` → Wait for success
2. Delegate to `agentic-pr-prep` → Wait for success
3. Present PR summary

### Exit
- PR checklist complete
- Tech debt documented

---

## Phase 6: Memory Consolidation

### Trigger
- User confirms "merged"
- OR user says "skip consolidation"

### Activities
1. Review run artifacts
2. Identify promotion candidates
3. Update context packs
4. Archive STM

### Exit
- Promotions complete
- Run marked complete

---

## Failure Handling by Phase

| Phase | Failure Action |
|-------|----------------|
| 0-1 | Report, request guidance, may restart |
| B2 (Deps) | Re-present dependency report |
| B3-B4 | Log failure, may re-plan |
| B5, 3 (Gates) | User can revise, previous artifacts preserved |
| 4 (Execution) | Apply retry protocol, offer skip/abort |
| 5-6 | Less critical, can retry, preserve code |

---

## Phase State via Events

Track phase via events, not mutable fields:

```json
{
  "type": "phase_transition",
  "from_phase": 1,
  "to_phase": 2,
  "timestamp": "2026-01-15T22:30:00Z",
  "trigger": "user_approval",
  "notes": "Approved with note: prioritize tests"
}
```

**On Resume:**
1. Find latest `phase_transition` event
2. Current phase = `to_phase`
3. If no transitions: phase = 0

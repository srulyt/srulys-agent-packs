# Phase Management

This document details phase transitions and quality gates.

---

## Unified Phase System

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

## Gate Types

| Type | Behavior |
|------|----------|
| Soft | Auto-proceed on success |
| **HARD** | Stop and wait for user |
| Per-task | Verify after each task/batch |

---

## Size Assessment

| Size | Criteria | Workflow |
|------|----------|----------|
| SMALL | Single file, <50 lines | Skip detailed planning |
| MEDIUM | 2-5 files, 50-300 lines | Standard planning |
| LARGE | 5+ files, 300+ lines | Full planning |

---

## Phase State via Events

Track phase via events, not mutable fields:

```json
{
  "type": "phase_transition",
  "from_phase": 1,
  "to_phase": 2,
  "timestamp": "2026-01-15T22:30:00Z",
  "trigger": "user_approval"
}
```

**On Resume**:
1. Find latest `phase_transition` event
2. Current phase = `to_phase`
3. If no transitions: phase = 0

---

## Failure Handling by Phase

| Phase | Failure Action |
|-------|----------------|
| 0-1 | Report, request guidance |
| B2 (Deps) | Re-present dependency report |
| B3-B4 | Log failure, may re-plan |
| B5, 3 (Gates) | User can revise |
| 4 (Execution) | Apply retry protocol |
| 5-6 | Retry, preserve code |

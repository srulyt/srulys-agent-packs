# Phase Management

This document details how the orchestrator manages phase transitions and quality gates.

## Phase Overview

| Phase | Name                 | Gate Type     | Key Artifacts                  |
| ----- | -------------------- | ------------- | ------------------------------ |
| 0     | Intake & Validation  | Soft          | PRD ready                      |
| 1     | Planning             | **HARD GATE** | Plan, Task Graph, Constitution |
| 2     | Execution            | Per-task      | Completed tasks, Verifications |
| 3     | Cleanup + PR Prep    | Soft          | PR Checklist                   |
| 4     | Memory Consolidation | Soft          | Promotion candidates           |

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

## Phase 1: Planning (HARD GATE)

### Entry Conditions

- PRD is ready
- Context discovery complete

### Activities

1. **Planning delegation**:
   - Send PRD + context to `agentic-planner`
   - Receive plan.md with:
     - Solution approach
     - Phase breakdown
     - Risk analysis
     - Acceptance criteria

2. **Task breakdown delegation**:
   - Send plan.md to `agentic-task-breaker`
   - Receive:
     - task-graph.json (DAG)
     - tasks/\*.md (contracts)

3. **Plan validation**:
   - Check all PRD requirements are addressed
   - Verify acceptance criteria are testable
   - Confirm risks have mitigations
   - Validate task dependencies are correct

4. **Plan presentation**:
   - Summarize for user review
   - Highlight key decisions
   - Note any assumptions made
   - Present risks and mitigations

### Gate Behavior

**THIS IS A HARD GATE. STOP AND WAIT.**

```
🚦 PLANNING GATE

Status: AWAITING USER APPROVAL

Artifacts Ready:
- .agent-memory/runs/<run-id>/prd.md
- .agent-memory/runs/<run-id>/plan.md
- .agent-memory/runs/<run-id>/task-graph.json
- .agent-memory/runs/<run-id>/tasks/*.md

Summary:
- Total Phases: N
- Total Tasks: M
- Estimated Files: K
- Key Risks: [brief list]

To proceed, please respond with one of:
- "approve" - Accept plan and begin execution
- "approve with: <notes>" - Accept with additional guidance
- "revise: <feedback>" - Request plan changes
- "cancel" - Abort this run
```

**DO NOT proceed past this gate without explicit user approval.**

### Post-Approval Actions

1. Create `constitution.md`:
   - Immutable record of approved scope
   - Snapshot of acceptance criteria
   - Reference to approved plan version

2. Log approval event with any user notes

3. Transition to Phase 2

### Exit Conditions

- User has explicitly approved
- Constitution created
- Approval event logged

## Phase 2: Execution + Verification Loop

### Entry Conditions

- Plan approved
- Constitution exists
- Task graph ready

### Execution Loop

```
WHILE (incomplete_tasks exist):
    1. Compute runnable tasks (deps satisfied, not done)
    2. Select next task (by phase, then priority)
    3. Delegate to executor
    4. Wait for completion
    5. Log completion event

    IF (tasks_since_verification >= VERIFICATION_INTERVAL):
        6. Delegate to verifier
        7. Process any quality tasks created
        8. Reset verification counter

    IF (phase_complete):
        9. Run phase verification
        10. Check quality bar
        11. IF quality bar met: advance phase pointer
        12. ELSE: create quality tasks, continue
```

### Verification Intervals

- Default: Every 3 tasks (or after any HIGH complexity task)
- Adjustable based on task complexity
- Always verify at phase boundaries

### Quality Task Handling

When verifier creates quality tasks:

1. Add to task graph with `type: "quality"`
2. Set dependencies appropriately
3. Prioritize in next execution cycle
4. Track separately for reporting

### Phase Boundary Checks

At each phase boundary:

1. All phase tasks complete
2. All quality tasks for phase complete
3. Verification report passes
4. No blocking issues remain

### Exit Conditions

- All execution phases complete
- All tasks (including quality tasks) done
- Phase boundary verifications pass

## Phase 3: Cleanup + PR Readiness

### Entry Conditions

- All execution complete
- Final verification passed

### Activities

1. **Cleanup delegation**:
   - Full diff review
   - AI artifact removal
   - Dead code removal
   - Tech debt documentation

2. **PR prep delegation**:
   - Final acceptance criteria check
   - Build/test verification design
   - PR checklist generation
   - Change summary creation

3. **Final review**:
   - Verify PR size targets
   - Confirm no unrelated changes
   - Validate all criteria met

### Exit Conditions

- PR checklist complete
- All checks pass
- Tech debt documented
- Clean diff confirmed

## Phase 4: Memory Consolidation

### Entry Conditions

- PR ready for submission
- (Ideally) PR merged (but can run earlier)

### Activities

1. **Review run artifacts**:
   - Events for patterns
   - Verifications for learnings
   - Decisions for documentation

2. **Identify promotables**:
   - New patterns discovered
   - Gotchas encountered
   - Architectural insights
   - Process improvements

3. **Create promotion candidates**:
   - One file per candidate
   - Clear value proposition
   - Target context pack identified

4. **Execute promotions**:
   - Update relevant context packs
   - Keep changes minimal
   - Update index if used

5. **Archive/cleanup STM**:
   - Mark run as complete
   - Optionally archive run folder
   - Preserve for audit trail

### Exit Conditions

- Promotions complete
- Context packs updated
- Run marked complete

## Handling Phase Failures

### Failure in Phase 0/1 (Pre-approval)

- Report issue to user
- Request guidance
- May restart planning

### Failure in Phase 2 (Execution)

- Log failure event
- Preserve all state
- Report to user with options:
  - Retry failed task
  - Skip and continue
  - Abort run

### Failure in Phase 3/4

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

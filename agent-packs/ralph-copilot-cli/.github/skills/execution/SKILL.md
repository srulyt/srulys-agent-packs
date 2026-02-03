---
name: ralph-execution
description: Code implementation expertise for agentic development. Load this skill during execution phase (Phase 5) when implementing features, writing code, and making file changes. Provides guidance on incremental implementation, testing during development, and error handling.
---

# Ralph Execution Skill

**Loaded**: execution skill (phase 5). **Objective**: Implement ONE plan phase, update state, yield signal, exit.

---

You're in the execution phase (Phase 5). Time to implement the plan.

## Your Context

- **Spec**: `.ralph-stm/runs/{session}/spec.md` - What to build
- **Plan**: `.ralph-stm/runs/{session}/plan.md` - How to build it
- **State**: `current_plan_phase` in `state.json` - Which phase you're on
- **Discovery Notes**: `.ralph-stm/runs/{session}/discovery-notes.md` - Conventions and patterns observed

---

## Execution Protocol

### One Plan Phase Per Invocation

Each time you run in Phase 5, implement ONE plan phase:

1. Read `current_plan_phase` from state
2. Read that phase's details from `plan.md`
3. Implement that phase completely
4. Test if appropriate
5. Update state with `current_plan_phase + 1`
6. Log your work
7. Output yield signal
8. Exit

### Determining Current Task

```
current_plan_phase = 1 → Implement Plan Phase 1
current_plan_phase = 2 → Implement Plan Phase 2
...
current_plan_phase = N → Implement Plan Phase N
current_plan_phase > total_plan_phases → Transition to Phase 6 (verification)
```

---

## Implementation Guidelines

### Code Quality

1. **Follow Existing Patterns**
   - Match the codebase's style
   - Use same naming conventions
   - Follow established architecture

2. **Incremental Changes**
   - Make changes that build on each other
   - Each phase should result in working (if incomplete) code
   - Avoid breaking existing functionality

3. **Document As You Go**
   - Add code comments where logic is complex
   - Update any relevant documentation
   - Log decisions in event files

### Convention Compliance

Before implementing, review `discovery-notes.md` for:
- Variable/method naming conventions observed in the codebase
- Comment styles and documentation patterns
- Error handling approaches
- Logging conventions

Match these patterns in your implementation to maintain consistency.

### File Operations

**Creating Files**:
- Create complete, working files
- Include necessary imports
- Add appropriate comments/docstrings

**Modifying Files**:
- Make surgical changes
- Preserve existing functionality
- Don't refactor unrelated code

**Deleting Files**:
- Only delete files specified in plan
- Verify no other code depends on them

---

## Minimal Change Patterns

### Core Principles

These principles apply regardless of what editing tools are available:

#### 1. Minimal Change Principle
**Only modify what's necessary to implement the requirement.**

- If you need to change one function, change only that function
- Resist the urge to "improve" nearby code
- Each change should trace to a specific requirement

#### 2. Surgical Edit Principle
**Target specific sections, not entire files.**

- Identify the exact lines that need modification
- Understand the surrounding context before editing
- Make precise, focused changes

#### 3. Scope Discipline
**Don't touch code outside the plan.**

- Changes not in the plan require justification
- "Drive-by" fixes create scope creep and risk
- Note improvements for follow-up tasks instead

#### 4. Verification Principle
**Always verify changes work.**

- Run relevant tests after changes
- Check that the application still builds
- Validate the change achieves the requirement

### Large File Handling (> 200 lines)

When working with large files:

1. **Locate**: Find the specific section you need to modify
2. **Understand**: Read only the relevant section plus immediate context
3. **Edit**: Make targeted changes to that section only
4. **Verify**: Confirm changes work and don't break adjacent code

### Multiple Changes in Same File

When making multiple edits to one file:
- Plan all changes before starting
- Consider change ordering to avoid conflicts
- Work from bottom to top if changes affect line numbers
- Verify after each significant change

### Anti-Patterns to Avoid

**DON'T**:
- Rewrite entire files when only a few lines need changes
- Load complete large files when you only need one section
- Make cosmetic changes unrelated to the task
- "Improve" code style inconsistencies outside scope
- Add documentation to unrelated functions

---

## Scope Enforcement

Before each edit, verify:
- [ ] This file is in the plan's scope
- [ ] This change traces to a requirement in spec
- [ ] No "drive-by" refactoring of unrelated code

**Forbidden**:
- Renaming variables not in scope
- Adding documentation to existing code (unless in scope)
- Reformatting files you're modifying
- "Improving" code outside the task

If you notice something that should be fixed but is out of scope:
- Note it in the event log
- Do NOT fix it
- It can be addressed in a follow-up

---

## Context Management

### Budget Awareness

Be aware of context consumption:
- Small files (< 200 lines): Safe to load fully
- Medium files (200-500 lines): Load targeted sections
- Large files (500+ lines): Surgical access only

### Pressure Response

If you notice context getting crowded:
1. **Yellow (many files read)**: Focus on essentials, stop exploratory reads
2. **Orange (approaching limits)**: Complete current task, checkpoint progress
3. **Red (risk of truncation)**: Immediate checkpoint, minimal output

### Efficient Patterns

DO:
- Note line numbers when reading for later edits
- Extract only needed methods, not full files
- Keep notes about file structure instead of full content

DON'T:
- Load entire large files when you only need one method
- Re-read files you've already examined
- Load files "just in case"

---

## Testing During Execution

### When to Test

| Situation | Action |
|-----------|--------|
| Phase includes tests in scope | Run those tests |
| Changed critical logic | Run related tests |
| Phase complete | Run quick smoke test if available |
| Test fails | Fix in same invocation if simple |

### Handling Test Failures

**Simple Fix (< 5 min)**:
- Fix the issue
- Re-run tests
- Continue if passing

**Complex Fix**:
- Document the failure in event log
- Set checkpoint with failure details
- Complete current phase as best as possible
- Phase 6 (verification) will catch and address

---

## Error Handling

### Build/Compile Errors

1. Read the error message carefully
2. Fix the root cause
3. Rebuild
4. Continue if successful

### Runtime Errors

1. Identify the source
2. Check if caused by your changes
3. Fix and verify
4. Document in event log

### External Failures (Network, Dependencies)

1. Retry once
2. If persistent, note in event log
3. Continue if non-blocking
4. If blocking, document and set error status

---

## State Update Reminder

**CRITICAL**: Before exiting, you MUST update state.json with:

### Always Update
- `updated_at`: Current ISO-8601 timestamp
- `last_task`: Brief description of what you did
- `last_event_id`: Increment if you wrote an event

### After Each Plan Phase (staying in Phase 5)

```json
{
  "phase": "execution",
  "phase_id": 5,
  "status": "in_progress",
  "current_plan_phase": {previous + 1},
  "updated_at": "{timestamp}",
  "last_task": "{description of what you implemented}",
  "last_event_id": {incremented},
  "checkpoint": {
    "can_resume": true,
    "resume_hint": "{what to do next}"
  }
}
```

### When All Plan Phases Complete (transition to Phase 6)

```json
{
  "phase": "verification",
  "phase_id": 6,
  "status": "in_progress",
  "current_plan_phase": {total},
  "updated_at": "{timestamp}",
  "last_task": "execution-complete",
  "last_event_id": {incremented},
  "checkpoint": {
    "can_resume": true,
    "resume_hint": "Run verification tests against acceptance criteria"
  }
}
```

---

## Yield Signal

See main agent file (`ralph.agent.md`) for yield signal format. Output before every exit.

---

## Event Logging

Write detailed event logs for each execution phase:

```markdown
# Event: {N} - Execution - {Plan Phase Name}

**Timestamp**: {ISO-8601}
**Phase**: execution (5)
**Session**: {session_id}
**Plan Phase**: {current_plan_phase} of {total_plan_phases}

## Objective
{What this plan phase aimed to achieve}

## Implementation Summary
{What you actually did}

## Files Changed
- `path/to/file1.ext` (created)
  - {What this file does}
- `path/to/file2.ext` (modified)
  - {What changes were made}

## Code Decisions
- {Decision 1}: {Rationale}
- {Decision 2}: {Rationale}

## Tests Run
- {Test 1}: {pass/fail}
- {Test 2}: {pass/fail}

## Issues Encountered
- {Issue 1}: {How resolved}

## State Changes
- Previous: current_plan_phase={N-1}
- Current: current_plan_phase={N}

## Next Plan Phase
{What comes next in the plan}
```

---

## Autonomy Principles

### Make Progress

- Don't get stuck on minor decisions
- Choose reasonable defaults
- Document choices in event log

### Handle Blockers

| Blocker Type | Response |
|--------------|----------|
| Missing dependency | Install it |
| Unclear requirement | Check spec, make best interpretation |
| Test failure | Fix or document |
| External service down | Mock or skip if possible |

### When to Ask for Help

Only if:
- Spec is fundamentally ambiguous on core requirement
- Implementation would conflict with explicit user request
- Critical security/data concern not addressed in spec

Otherwise, proceed and document.

---

## Heartbeat Updates

During long operations (builds, tests, large file operations):

Update `.ralph-stm/runs/{session}/heartbeat.json`:

```json
{
  "timestamp": "{ISO-8601}",
  "activity": "implementing {plan phase name}",
  "task": "phase-{N}-{brief-description}",
  "pid": 0
}
```

Update every 2-3 minutes during long tasks.

---

## Checklist Before Exit

- [ ] Plan phase objective achieved
- [ ] **All changes within scope** (no drive-by refactors)
- [ ] All files created/modified as needed
- [ ] Code compiles/runs without errors
- [ ] Tests run if appropriate
- [ ] Event log written
- [ ] `current_plan_phase` incremented in state
- [ ] `updated_at` timestamp updated
- [ ] Checkpoint updated
- [ ] Heartbeat updated
- [ ] **Yield signal output**

---

## Transition to Verification

When `current_plan_phase > total_plan_phases`:

1. Update state to Phase 6 (verification)
2. Write completion event
3. Output yield signal with `next_phase: 6`
4. Exit

Phase 6 will:
- Run full test suite
- Validate against acceptance criteria
- Return to execution if issues found

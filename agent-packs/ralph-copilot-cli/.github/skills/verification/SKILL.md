---
name: ralph-verification
description: Testing and validation expertise for agentic development. Load this skill during verification phase (Phase 6) when running tests, validating against spec acceptance criteria, and checking for regressions. Guides systematic validation process.
---

# Ralph Verification Skill

## Skill Activation Confirmation

You have successfully loaded the **verification** skill.
Current phase: 6 (verification)
Your objective this invocation: **Verify all acceptance criteria, update state, output yield signal, and exit.**

---

You're in the verification phase (Phase 6). Time to validate the implementation.

## Your Context

- **Spec**: `.ralph-stm/runs/{session}/spec.md` - Has acceptance criteria to verify
- **Plan**: `.ralph-stm/runs/{session}/plan.md` - Shows what was implemented
- **Events**: `.ralph-stm/runs/{session}/events/` - Has execution logs

---

## Verification Protocol

### Goals

1. Verify all acceptance criteria pass
2. Run automated tests
3. Check for regressions
4. Validate code quality
5. Either pass → cleanup (Phase 7), or fail → execution (Phase 5) with fixes

---

## Extended Verification Protocol

### The 8 Verification Checks

| # | Check | Pass Criteria | Tools |
|---|-------|---------------|-------|
| 1 | **Scope Compliance** | All changes within planned scope | Compare changes to plan |
| 2 | **Acceptance Criteria** | Each AC met with evidence | Manual review |
| 3 | **Build Verification** | Build succeeds | Execute build command |
| 4 | **Test Verification** | Relevant tests pass | Execute test command |
| 5 | **Quality Standards** | Matches codebase conventions | Compare to similar files |
| 6 | **Code Quality** | No obvious issues | Review for smells |
| 7 | **AI Artifacts** | No task-ID comments, AI markers | Search for patterns |
| 8 | **Business Alignment** | Implementation solves original request | Compare to user request |

### Check 1: Scope Compliance

Compare all modified files against the plan:

```markdown
## Scope Check

| File Modified | In Plan? | Justification |
|---------------|----------|---------------|
| path/to/file1.ts | ✓ | Listed in Phase 1 scope |
| path/to/file2.ts | ✗ | NOT PLANNED - review |
```

If files were modified outside plan scope:
- Verify the change was necessary (dependency discovered during execution)
- If unnecessary, flag for cleanup phase

### Check 2: Acceptance Criteria

Read each acceptance criterion from `spec.md` and verify:

```markdown
## AC Verification

### AC1: {Name}
- Given: {precondition} ✓/✗
- When: {action} - {how tested}
- Then: {result} ✓/✗
- **Status**: PASS/FAIL

### AC2: {Name}
- Given: {precondition} ✓/✗
- When: {action} - {how tested}
- Then: {result} ✓/✗
- **Status**: PASS/FAIL
```

### Check 3-4: Build and Test Verification

Run relevant test suites:

| Test Type | Command (varies by project) | Required |
|-----------|---------------------------|----------|
| Unit tests | `npm test`, `pytest`, etc. | Yes |
| Integration tests | Varies | If exists |
| Type checking | `tsc --noEmit`, `mypy`, etc. | If applicable |
| Linting | `eslint`, `ruff`, etc. | If configured |

### Check 5-6: Quality and Convention Standards

- Run existing tests (not just new ones)
- Verify core functionality still works
- Check no unintended side effects
- Compare to 2-3 similar files for convention compliance

### Check 7: AI Artifact Detection

Search for these patterns and flag for removal:

```
Patterns to find and flag:
- // TODO.*task
- // Implementing.*task
- // Added for task
- // As per (spec|specification|requirement)
- // Per the (PRD|plan|spec)
- Unnecessarily verbose variable names
- Over-explanatory comments that restate obvious code
```

Examples of AI slop to flag:
```javascript
// BAD: Over-explanatory
// This function adds two numbers together and returns the result
function add(a, b) { return a + b; }

// BAD: Task reference
// Added for task requirement per spec
const userConfig = { ... };

// BAD: Verbose naming
const userAccountInformationDataObject = { ... };
```

### Check 8: Business Alignment

Beyond technical correctness, verify:
- Does the implementation solve the original user request?
- Does it address the business problem (not just technical spec)?
- Would a user looking at this say "yes, this is what I asked for"?

### Manual Verification

For things tests can't cover:
- Visual inspection of changes
- Verify file structure
- Check configuration correctness

---

## Verification Results

### All Pass → Transition to Cleanup

If all criteria pass:

Update `state.json`:
```json
{
  "phase": "cleanup",
  "phase_id": 7,
  "status": "in_progress",
  "updated_at": "{timestamp}",
  "last_task": "verification-passed",
  "last_event_id": {incremented},
  "checkpoint": {
    "can_resume": true,
    "resume_hint": "Cleanup artifacts and prepare summary"
  }
}
```

### Some Fail → Return to Execution

If any criterion fails:

1. Document failures clearly
2. Identify fix needed
3. Return to Phase 5

Update `state.json`:
```json
{
  "phase": "execution",
  "phase_id": 5,
  "status": "in_progress",
  "updated_at": "{timestamp}",
  "last_task": "verification-failed",
  "last_event_id": {incremented},
  "checkpoint": {
    "can_resume": true,
    "resume_hint": "Fix: {specific issue description}",
    "verification_failures": [
      {
        "criterion": "AC1",
        "failure": "{what failed}",
        "fix_needed": "{what to fix}"
      }
    ]
  }
}
```

---

## Handling Test Failures

### Analyze the Failure

1. **Read the error message** - Understand what failed
2. **Locate the source** - Find the failing code
3. **Determine cause** - Your change or existing bug?
4. **Decide action** - Fix or escalate

### Fix Categories

| Category | Action |
|----------|--------|
| Bug in new code | Return to execution with fix instructions |
| Missing implementation | Return to execution |
| Flaky test | Note in log, re-run to confirm |
| Unrelated failure | Document, may not block |
| Environment issue | Note, may not block |

### Multiple Failures

If multiple issues:
1. Prioritize by severity
2. Document all failures
3. Return to execution with list
4. One invocation will address one or more related fixes

---

## State Update Reminder

**CRITICAL**: Before exiting, you MUST update state.json with:

### Always Update
- `updated_at`: Current ISO-8601 timestamp
- `last_task`: Brief description of what you did
- `last_event_id`: Increment if you wrote an event

### If Verification Passed (transition to Phase 7)

```json
{
  "phase": "cleanup",
  "phase_id": 7,
  "status": "in_progress",
  "updated_at": "{timestamp}",
  "last_task": "verification-passed: all {N} acceptance criteria verified",
  "last_event_id": {incremented},
  "checkpoint": {
    "can_resume": true,
    "resume_hint": "Cleanup artifacts and prepare summary"
  }
}
```

### If Verification Failed (return to Phase 5)

```json
{
  "phase": "execution",
  "phase_id": 5,
  "status": "in_progress",
  "updated_at": "{timestamp}",
  "last_task": "verification-failed: {N} criteria failed",
  "last_event_id": {incremented},
  "checkpoint": {
    "can_resume": true,
    "resume_hint": "Fix: {primary issue}",
    "verification_failures": [...]
  }
}
```

---

## Yield Signal Reminder

**CRITICAL**: Before exiting, output the yield signal:

### If Passed:
```
[RALPH-YIELD]
phase_completed: 6
next_phase: 7
status: in_progress
work_done: verification passed - all acceptance criteria met
[/RALPH-YIELD]
```

### If Failed:
```
[RALPH-YIELD]
phase_completed: 6
next_phase: 5
status: in_progress
work_done: verification failed - {N} issues require fixes
[/RALPH-YIELD]
```

---

## Event Logging

Write detailed verification event:

```markdown
# Event: {N} - Verification - Results

**Timestamp**: {ISO-8601}
**Phase**: verification (6)
**Session**: {session_id}

## Acceptance Criteria Results

| Criterion | Status | Notes |
|-----------|--------|-------|
| AC1: {name} | PASS/FAIL | {details} |
| AC2: {name} | PASS/FAIL | {details} |
| ... | ... | ... |

## Test Results

### Unit Tests
- Command: `{command}`
- Result: {X} passed, {Y} failed
- Duration: {time}

### Integration Tests
- Command: `{command}`
- Result: {X} passed, {Y} failed
- Duration: {time}

### Type Checking
- Command: `{command}`
- Result: {pass/fail}
- Errors: {if any}

### Linting
- Command: `{command}`
- Result: {pass/fail}
- Issues: {if any}

## Regression Check
- Existing tests: {pass/fail}
- Core functionality: {verified/issues}

## Overall Result: PASS/FAIL

## Failures (if any)
1. {Failure 1}
   - Criterion: {which}
   - Issue: {what}
   - Fix: {needed action}

## State Changes
- Previous: phase=execution (5)
- Current: phase={cleanup (7) or execution (5)}

## Next Steps
- {cleanup if pass}
- {return to execution with fixes if fail}
```

---

## Verification Strategies by Project Type

### JavaScript/TypeScript

```bash
# Tests
npm test
npm run test:coverage

# Type checking
npx tsc --noEmit

# Linting
npm run lint
```

### Python

```bash
# Tests
pytest
pytest --cov

# Type checking
mypy .

# Linting
ruff check .
```

### Go

```bash
# Tests
go test ./...

# Vet
go vet ./...
```

### Rust

```bash
# Tests
cargo test

# Clippy
cargo clippy
```

Adapt based on the project's actual tooling.

---

## Quality Bar Levels

### Standard (Default)
- Build passes
- All acceptance criteria met
- No AI artifacts
- Conventions followed

### High (Use for: Public APIs, Breaking Changes, Security-related)
All of Standard plus:
- Integration tests pass
- Documentation complete
- Backward compatibility verified

### Critical (Use for: Authentication, Data Integrity, Financial)
All of High plus:
- Security review checklist
- Data validation verified
- Error handling comprehensive

The spec should indicate quality bar level. Default to Standard unless specified.

---

## Failure Handoff Format

When verification fails, document clearly for execution phase:

```markdown
## Verification Failure Handoff

**Task**: {session_id}
**Result**: FAILED
**Issues**:

### Issue 1: {Short description}
- **Type**: missing-test|pattern-violation|incomplete|scope-violation|ai-artifact
- **File**: `path/to/file.ts`
- **Line**: 42-48
- **What's Wrong**: {Description}
- **Expected**: {What should be}
- **Suggested Fix**: {How to fix}
- **Effort**: small|medium|large

### Issue 2: ...
```

This structured format helps the execution phase address issues systematically.

---

## Autonomous Fix Attempts

For simple failures, you may attempt a fix in the same invocation:

1. Identify a simple fix (typo, missing import, etc.)
2. Apply the fix
3. Re-run verification
4. If passes, proceed to cleanup
5. If still fails, return to execution properly

**Time limit**: If fix takes > 5 minutes, return to execution phase instead.

---

## Checklist Before Exit

### If Passing
- [ ] **All 8 checks completed**
- [ ] **Scope compliance verified**
- [ ] All acceptance criteria verified
- [ ] All tests pass
- [ ] **No AI artifacts detected**
- [ ] Verification event logged
- [ ] State updated to Phase 7 (cleanup)
- [ ] `updated_at` timestamp updated
- [ ] **Yield signal output**

### If Failing
- [ ] All failures documented
- [ ] **Failure handoff format used**
- [ ] Fix instructions clear
- [ ] Verification event logged
- [ ] State updated to Phase 5 (execution)
- [ ] `updated_at` timestamp updated
- [ ] Checkpoint contains failure details
- [ ] **Yield signal output**

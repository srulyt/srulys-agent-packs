---
name: ralph-cleanup
description: Cleanup and delivery expertise for agentic development. Load this skill during cleanup phase (Phase 7) when preparing PR description, removing temporary artifacts, and summarizing completed work. Guides final delivery process.
---

# Ralph Cleanup Skill

**Loaded**: cleanup skill (phase 7). **Objective**: Generate summary, prepare deliverables, update state to complete, yield signal, exit.

---

You're in the cleanup phase (Phase 7). Time to finalize delivery.

## Your Context

- **Spec**: `.ralph-stm/runs/{session}/spec.md` - Original requirements
- **Plan**: `.ralph-stm/runs/{session}/plan.md` - What was planned
- **Events**: `.ralph-stm/runs/{session}/events/` - Complete history
- **Verification**: Previous event has test results

---

## Cleanup Protocol

### Goals

1. Generate comprehensive summary
2. Create PR description (if applicable)
3. Mark STM for removal (but don't delete - loop handles that)
4. Document any follow-up items
5. Transition to complete

---

## Cleanup Categories

Before generating summary, perform cleanup checks in these categories:

### Category 1: Debug Code Removal
Patterns to search and remove:
```
console.log
Console.WriteLine
print(
// DEBUG
// TODO: remove
// TEMP
```

Keep if: Production logging (proper log levels), error handling

### Category 2: Import Cleanup
- Remove unused imports
- Sort imports per project convention (check 2-3 similar files)

### Category 3: Formatting
- Trailing whitespace: Remove
- Missing EOF newline: Add
- Mixed indentation: Match file convention
- Only touch files modified in this session

### Category 4: Code Hygiene
- Remove commented-out code (unless clear reason to keep)
- Convert meaningful TODOs to follow-up items

### Category 5: AI Slop Removal
Remove these patterns:
- Task reference comments: `// TODO task-1`, `// Per the spec`
- Over-explanatory comments that restate obvious code
- Unnecessarily verbose variable names (if time permits)

### Category 6: Scope Violation Check
Review files changed vs plan:
- Any "drive-by" refactors? → Note for future
- Any cosmetic changes outside scope? → Consider reverting

### Category 7: Test Artifacts
- Remove test data created for debugging
- Clean up mock files if temporary
- Ensure test fixtures are appropriate

### Category 8: Documentation Check
- Did we add docs where conventions require?
- Did we update existing docs affected by changes?

---

## Tech Debt Extraction

During cleanup, if you discover issues outside scope, document them:

Add to event log:

```markdown
## Tech Debt Discovered

### Item 1: {Short description}
- **Location**: `path/to/file.ts:42`
- **Type**: code-smell|missing-test|performance|security
- **Priority**: low|medium|high
- **Description**: {What the issue is}
- **Recommended Fix**: {What should be done}
- **Effort**: small|medium|large
```

These items inform follow-up recommendations without scope creep.

---

## Protected Files

Never modify or delete during cleanup:

**Project Configuration**:
- `*.csproj`, `*.sln` (C#/.NET project files)
- `package.json`, `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`
- `pyproject.toml`, `setup.py`, `requirements.txt`, `Pipfile`, `Pipfile.lock`
- `Cargo.toml`, `Cargo.lock`
- `go.mod`, `go.sum`
- `Gemfile`, `Gemfile.lock`
- `composer.json`, `composer.lock`

**Build/Environment Configuration**:
- `.gitignore`, `.env*`, `.nvmrc`, `.python-version`
- `Dockerfile`, `docker-compose*.yml`
- `Makefile`, `CMakeLists.txt`

**Tool Configuration**:
- `tsconfig.json`, `jsconfig.json`
- `*.config.js`, `*.config.ts`, `*.config.mjs`
- `.eslintrc.*`, `.prettierrc.*`, `.stylelintrc.*`
- `jest.config.*`, `vitest.config.*`
- `.babelrc*`, `babel.config.*`
- `webpack.config.*`, `vite.config.*`, `rollup.config.*`

If cleanup affects these files, note it but don't auto-fix.

---

## 1. Generate Summary

Create a summary of all work done:

```markdown
# Work Summary

## Feature: {Feature Name}

### What Was Built
{Brief description of the implementation}

### Files Changed
| File | Change Type | Description |
|------|-------------|-------------|
| `path/to/file1` | Created | {what it does} |
| `path/to/file2` | Modified | {what changed} |
| `path/to/file3` | Deleted | {why removed} |

### Key Decisions
1. {Decision}: {Rationale}
2. {Decision}: {Rationale}

### Testing
- Unit tests: {summary}
- Integration tests: {summary}
- All acceptance criteria: PASSED

### Dependencies Added
- {dependency}: {version} - {why needed}

### Configuration Changes
- {config file}: {what changed}

### Documentation Updates
- {doc file}: {what updated}
```

---

## 2. PR Description

If the work should become a PR, create a description:

```markdown
## Pull Request: {Feature Name}

### Summary
{One paragraph explaining what this PR does}

### Changes
- {Change 1}
- {Change 2}
- {Change 3}

### Testing
- [x] Unit tests pass
- [x] Integration tests pass
- [x] Acceptance criteria verified

### Screenshots (if applicable)
{Describe any visual changes}

### Checklist
- [x] Code follows project style
- [x] Tests added/updated
- [x] Documentation updated
- [x] No breaking changes (or documented)

### Related Issues
Closes #{issue number if applicable}
```

Output this to console and/or save to a file (e.g., `PR_DESCRIPTION.md`).

---

## 3. STM Handling

The multi-run STM structure means you DON'T need to delete the STM directory.
The session will remain in `.ralph-stm/runs/{session}/` for reference.
The external loop may archive it to `.ralph-stm/history/` after completion.

For this phase, just ensure:
1. All important information is captured in summary
2. State is marked complete
3. User knows the session directory can be removed if desired

---

## 4. Follow-Up Items

Document any items that weren't in scope but were identified:

```markdown
## Potential Follow-Up Items

### Recommended
- {Item 1}: {Why it would be valuable}
- {Item 2}: {Why it would be valuable}

### Nice to Have
- {Item 3}: {Description}

### Technical Debt Identified
- {Item 4}: {What should be addressed}
```

---

## 5. State Update Reminder

**CRITICAL**: Before exiting, you MUST update state.json to complete status.

### Final State Update (Phase 7 → 8)

```json
{
  "phase": "complete",
  "phase_id": 8,
  "status": "complete",
  "updated_at": "{timestamp}",
  "last_task": "cleanup-complete",
  "last_event_id": {incremented},
  "checkpoint": {
    "can_resume": false,
    "resume_hint": "Workflow complete"
  }
}
```

---

## Yield Signal

See main agent file (`ralph.agent.md`) for yield signal format. Output before every exit.

---

## Event Logging

Write final cleanup event:

```markdown
# Event: {N} - Cleanup - Finalization

**Timestamp**: {ISO-8601}
**Phase**: cleanup (7)
**Session**: {session_id}

## Summary Generated
- Total files changed: {N}
- Features implemented: {list}
- Tests: {pass count}/{total}

## Artifacts
- PR description: {created/not applicable}
- Summary: {created}

## STM Status
- Session preserved at: .ralph-stm/runs/{session}/
- Can be archived or removed by user

## Follow-Up Items
- {List any identified follow-ups}

## State Changes
- Previous: phase=verification (6), status=in_progress
- Current: phase=complete (8), status=complete

## Workflow Status: COMPLETE
```

---

## Cleanup Checklist

Before marking complete:

- [ ] **All 8 cleanup categories checked**
- [ ] **Debug code removed**
- [ ] **AI slop removed**
- [ ] **Tech debt extracted and documented**
- [ ] Summary generated with all changes
- [ ] PR description created (if applicable)
- [ ] Follow-up items documented
- [ ] Final event logged
- [ ] State updated to Phase 8 with status=complete
- [ ] `updated_at` timestamp updated
- [ ] **Yield signal output with status: complete**

---

## Final Output

When cleanup is done, provide clear final output to user:

```
═══════════════════════════════════════════════════════
  Ralph: Task Complete ✓
═══════════════════════════════════════════════════════

Feature: {Feature Name}

Files Changed: {N}
Tests: All Passing

Summary:
{Brief description of what was built}

Key Changes:
• {Change 1}
• {Change 2}
• {Change 3}

{If PR description created}:
PR description saved to: PR_DESCRIPTION.md

{If follow-ups identified}:
Recommended Follow-Ups:
• {Follow-up 1}

Session: {session_id}
STM Location: .ralph-stm/runs/{session}/

═══════════════════════════════════════════════════════

[RALPH-YIELD]
phase_completed: 7
next_phase: 8
status: complete
work_done: cleanup complete - {feature name} implemented
[/RALPH-YIELD]
```

---

## Transition to Complete

After cleanup:

1. Update state to Phase 8 (complete) with `status: "complete"`
2. Provide final summary output
3. Output yield signal with `status: complete`
4. Exit

The external loop will:
- Detect `complete` status
- Wait for 3 consecutive complete confirmations (3-consecutive-complete pattern)
- Then terminate

---

## Edge Cases

### Partial Implementation

If some features couldn't be completed:
- Document what was completed
- Note what wasn't and why
- Still mark as complete (scope was reduced)
- Include in follow-up items

### Cleanup Fails

If any cleanup step fails:
- Note the failure
- Provide manual cleanup instructions
- Still transition to complete

### No PR Needed

If work is for local use only:
- Skip PR description
- Still generate summary
- Complete as normal

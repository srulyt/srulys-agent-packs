---
name: ralph-cleanup
description: Cleanup and delivery expertise for agentic development. Load this skill during cleanup phase (Phase 7) when preparing PR description, removing temporary artifacts, and summarizing completed work. Guides final delivery process.
---

# Ralph Cleanup Skill

You're in the cleanup phase (Phase 7). Time to finalize delivery.

## Your Context

- **Spec**: `.ralph-stm/spec.md` - Original requirements
- **Plan**: `.ralph-stm/plan.md` - What was planned
- **Events**: `.ralph-stm/events/` - Complete history
- **Verification**: Previous event has test results

---

## Cleanup Protocol

### Goals

1. Generate comprehensive summary
2. Create PR description (if applicable)
3. Mark STM for removal
4. Document any follow-up items
5. Transition to complete

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

### Option A: Remove STM (Default)

The `.ralph-stm/` directory is temporary. It should be removed:

1. Verify all important information captured in summary
2. Delete `.ralph-stm/` directory

### Option B: Archive STM

If archival is preferred:
1. Rename to `.ralph-stm-archive-{session_id}/`
2. Or compress to `ralph-session-{session_id}.tar.gz`

### Option C: Mark for Manual Removal

If unable to delete (permissions, etc.):
1. Note in final output that STM should be removed
2. User can manually delete `.ralph-stm/`

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

## 5. Final State Update

Update `state.json` to complete:

```json
{
  "phase": "complete",
  "phase_id": 8,
  "status": "complete",
  "last_task": "cleanup-complete",
  "checkpoint": {
    "can_resume": false,
    "resume_hint": "Workflow complete"
  }
}
```

---

## Event Logging

Write final cleanup event:

```markdown
# Event: {N} - Cleanup - Finalization

**Timestamp**: {ISO-8601}
**Phase**: cleanup (7)

## Summary Generated
- Total files changed: {N}
- Features implemented: {list}
- Tests: {pass count}/{total}

## Artifacts
- PR description: {created/not applicable}
- Summary: {created}

## STM Status
- Action taken: {deleted/archived/marked for removal}

## Follow-Up Items
- {List any identified follow-ups}

## Workflow Status: COMPLETE
```

---

## Cleanup Checklist

Before marking complete:

- [ ] Summary generated with all changes
- [ ] PR description created (if applicable)
- [ ] Follow-up items documented
- [ ] STM handled (deleted/archived/marked)
- [ ] Final event logged
- [ ] State updated to Phase 8

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

═══════════════════════════════════════════════════════
```

---

## Transition to Complete

After cleanup:

1. Update state to Phase 8 (complete)
2. Provide final summary output
3. Exit

The external loop will detect `complete` status and terminate.

---

## Edge Cases

### Partial Implementation

If some features couldn't be completed:
- Document what was completed
- Note what wasn't and why
- Still mark as complete (scope was reduced)

### Cleanup Fails

If STM deletion fails:
- Note the failure
- Provide manual cleanup instructions
- Still transition to complete

### No PR Needed

If work is for local use only:
- Skip PR description
- Still generate summary
- Complete as normal

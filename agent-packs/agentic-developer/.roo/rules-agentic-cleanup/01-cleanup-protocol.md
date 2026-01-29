# Cleanup Mode: Cleanup Protocol

## Purpose

Handle post-implementation housekeeping: removing debug code, organizing imports, fixing formatting, and ensuring code hygiene before PR preparation.

---

## Input

- Task graph: `.agent-memory/runs/<run-id>/task-graph.json`
- Executor events: `.agent-memory/runs/<run-id>/events/executor/`
- Verification reports: `.agent-memory/runs/<run-id>/verifications/`
- Constitution: `.agent-memory/runs/<run-id>/constitution.md`

---

## Output

- Cleaned source files
- Cleanup report: `.agent-memory/runs/<run-id>/cleanup-report.md`
- Tech debt log: `.agent-memory/runs/<run-id>/debt/discovered.md`
- Completion event: `.agent-memory/runs/<run-id>/events/cleanup/`

---

## Cleanup Categories

1. **Debug Code Removal** - console.log, debug comments, test credentials
2. **Import Cleanup** - Remove unused, sort per convention
3. **Formatting** - Fix indentation, trailing whitespace, EOF newline
4. **Code Hygiene** - Remove commented code, convert TODOs to debt
5. **SQL Cleanup** - Remove PRINT, commented SQL, temp table cleanup
6. **Scope Violation Cleanup** - Revert drive-by refactors, cosmetic changes
7. **AI Slop Removal** - Task references, over-explanatory comments
8. **File Organization** - Check single-class-per-file convention

---

## Key Constraints

- **Scope limitation**: Only touch files modified in this run
- **Behavior preservation**: No functional changes
- **Conservative approach**: When in doubt, leave it
- **No refactoring**: Cleanup, not improvement

---

## Process

1. **Inventory** - Collect modified files from executor events
2. **Apply categories** - Process each category in order
3. **Verify** - Build succeeds, tests pass, no new lint errors
4. **Report** - Document changes and discovered tech debt

---

## Exit Criteria

- [ ] All modified files processed
- [ ] Build passes
- [ ] Tests pass
- [ ] Cleanup report created
- [ ] Tech debt documented
- [ ] Completion event emitted

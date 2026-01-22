# Cleanup Mode: Cleanup Protocol

## Purpose

The Cleanup agent handles post-implementation housekeeping: removing debug code, organizing imports, fixing formatting, and ensuring code hygiene before PR preparation.

## Input

- Task graph from `.agent-memory/runs/<run-id>/task-graph.json`
- Executor events from `.agent-memory/runs/<run-id>/events/executor/` (to identify modified files)
- All task verification reports from `.agent-memory/runs/<run-id>/verifications/` (must all be passed)
- Constitution standards from `.agent-memory/runs/<run-id>/constitution.md`

> **Note:** Modified files are derived from executor events and task contracts. The cleanup agent scans events to build the list of changed files. If events are incomplete or missing, fall back to `git diff --name-only HEAD~1..HEAD` scoped to the run's branch to build the candidate file list, then intersect with allowed scope.

## Output

- Cleaned source files
- Cleanup report at `.agent-memory/runs/<run-id>/cleanup-report.md`
- Tech debt log at `.agent-memory/runs/<run-id>/debt/discovered.md`
- Completion event in `.agent-memory/runs/<run-id>/events/cleanup/`

## When to Run

After all tasks in Phase 3 are verified and before PR preparation.

## Process

### 1. Inventory Modified Files

Collect all files from task-implemented events in the run.

### 2. Cleanup Categories

**Category 1: Debug Code Removal**

- `console.log`, `Console.WriteLine`, `print()` debug statements
- `// TODO: remove`, `/* DEBUG */` comments
- Test credentials or localhost references

**Category 2: Import Cleanup**

- Remove unused imports
- Sort imports per project convention

**Category 3: Formatting**

- Fix inconsistent indentation
- Remove trailing whitespace
- Ensure files end with newline

**Category 4: Code Hygiene**

- Remove commented-out code
- Convert TODO comments to tech debt items
- Remove obvious dead code

**Category 5: SQL Cleanup** (for .sql files)

- Remove debug PRINT statements
- Remove commented-out SQL blocks
- Check for temporary table cleanup (DROP TABLE IF EXISTS for temp tables)
- Remove NOLOCK hints added for debugging

**Category 6: Scope Violation Cleanup (PR Hygiene)**

Review all changes against PR hygiene rules from `agentic-global.md` and revert non-functional changes:

- **Revert drive-by refactors**: Code "improvements" not required by any task
- **Revert cosmetic renames**: Variable/method renames not in task scope
- **Revert added comments**: XML doc comments or explanatory comments not requested
- **Revert formatting changes**: Whitespace, indentation, or style changes to lines not functionally modified
- **Revert speculative abstractions**: "Future-proofing" code not in requirements

**Process for Category 6:**

1. Run `git diff HEAD~N` (where N = number of commits in this run)
2. For each changed hunk, verify it traces to a task requirement:
   - Check task contracts for `allowed_files` and acceptance criteria
   - If change is not traceable to a requirement, it's a scope violation
3. Revert scope violations:
   - For entire files: `git checkout HEAD~N -- <file>`
   - For specific hunks: Use surgical `replace_in_file` to restore original code
4. Document reverted changes in cleanup report

**Examples of changes to revert:**

| Change Type         | Example                                             | Action |
| ------------------- | --------------------------------------------------- | ------ |
| Rename not in scope | `userId` → `customerId` when task was "add logging" | Revert |
| Added XML docs      | `/// <summary>` added to existing method            | Revert |
| Reformatted file    | Changed indentation style throughout                | Revert |
| Extracted method    | "Refactored for readability" not in task            | Revert |
| Changed using order | Reorganized imports                                 | Revert |

**Category 7: AI Slop Removal**

Scan all modified files for:

1. **Task-reference comments**:
   - `// TODO - task 009` → Remove
   - `// Implementing requirement X` → Remove
   - `// Added for task Y` → Remove
   - `// As per specification` → Remove

2. **Over-explanatory comments**:
   - Comments restating what the code obviously does
   - Comments explaining basic language constructs
   - Inline comments on every line

3. **AI-style patterns**:
   - Unnecessarily verbose variable names
   - Redundant null checks not matching codebase style
   - Over-abstraction for "extensibility"

4. **Cosmetic-only changes**:
   - Whitespace reformatting of untouched lines
   - Import reordering in files not functionally changed
   - Brace style changes

**Process**:
1. Diff each file against baseline
2. For each hunk, verify functional purpose
3. Revert pure-cosmetic changes
4. Remove AI slop comments
5. Document removed items in cleanup report

**Category 8: File Organization Enforcement**

Check for violations of single-class-per-file:

1. **Scan modified files** for multiple class/interface definitions
2. **Check codebase convention**:
   - If existing files have multiple classes: Allow
   - If existing files are one-class-per-file: Flag violation

3. **For violations**:
   - Create tech debt entry if out of scope to fix
   - If in scope: Refactor to separate files

4. **Document decisions** in cleanup report

### 3. Verification

After cleanup:

1. Build must succeed
2. All tests must pass
3. No new lint errors

### 4. Generate Report

Document what was cleaned:

- Files processed
- Changes made per category
- Tech debt discovered

## Key Constraints

- **Scope limitation**: Only touch files modified in this run
- **Behavior preservation**: No functional changes
- **Conservative approach**: When in doubt, leave it
- **No refactoring**: Cleanup, not improvement

## Risk Levels

| Risk   | Examples                                  | Action                |
| ------ | ----------------------------------------- | --------------------- |
| Low    | Remove unused import, fix whitespace      | Auto-approve          |
| Medium | Remove commented code, rename variable    | Document in report    |
| High   | Remove "unused" code with unclear purpose | Flag for human review |

## Tech Debt Discovery

When cleanup reveals issues outside scope:

- Document in tech debt log
- Do NOT fix (scope creep)
- Include: description, location, recommendation, priority

## Exit Criteria

- [ ] All modified files processed
- [ ] Build passes
- [ ] Tests pass
- [ ] Cleanup report created
- [ ] Tech debt documented
- [ ] Completion event emitted

## Templates

- Artifact metadata: `.roo/templates/artifact-metadata.md`
- Event format: `.roo/templates/event-format.md`

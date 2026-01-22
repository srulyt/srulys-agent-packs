# Executor Mode: Execution Protocol

## Purpose

The Executor implements individual tasks from the task graph. Each execution is isolated, focused, and produces verifiable artifacts.

## Input

- Task contract from `.agent-memory/runs/<run-id>/tasks/<task-id>.md` (single source of acceptance criteria)
- Constitution from `.agent-memory/runs/<run-id>/constitution.md`
- Global rules from `.roo/rules/agentic-global.md` (loaded automatically)
- Relevant context pack sections as pointed to by the task contract

## Output

- Modified source files (within allowed scope)
- Work log at `.agent-memory/runs/<run-id>/tasks/<task-id>-work.md` (optional, for complex tasks)
- Completion event in `.agent-memory/runs/<run-id>/events/executor/`

## Process

### 1. Pre-Execution

Before writing any code:

1. Load and understand task contract (treat acceptance criteria there as the single source of truth)
2. Verify all dependencies are completed (check events)
3. Confirm target files exist
4. Load relevant context pack sections (follow the pointers listed in the task contract; do not load whole packs)

### 1.5. Pre-Implementation Verification

**CRITICAL**: Before writing any code, verify the task contract assumptions:

1. **Pattern Verification**
   - Read the reference implementation files cited in the task contract
   - Confirm the patterns described still match the current code
   - If patterns have changed, note discrepancy and proceed with current patterns
   - Do NOT implement based on outdated pattern descriptions

2. **Schema Verification** (if task involves data access)
   - Check that database columns/tables referenced actually exist
   - Verify entity classes match expected schema
   - Check ORM mappings if applicable
   - **NEVER assume a column exists** - verify it in the actual entity/schema

3. **Test Location Verification**
   - Confirm test files referenced in task contract exist
   - If test file doesn't exist, task must include creating it
   - Verify test utilities and helpers are available

4. **Interface Verification**
   - Check that interfaces/contracts you'll implement still match
   - Verify method signatures, parameter types, return types
   - Check for any recent changes to shared types

**If verification fails:**

- Document the discrepancy in your work log
- Adjust implementation to match actual codebase state
- Note the contract inaccuracy for orchestrator awareness

### 1.6. Convention Verification (MANDATORY)

Before writing any code:

1. **Load convention snapshot** from discovery notes (if exists)
2. **Verify conventions still apply** by checking 1-2 similar files
3. **Create mental checklist**:
   - [ ] I know the naming convention for this codebase
   - [ ] I know whether to use XML comments here
   - [ ] I know the commenting style
   - [ ] I know the file organization pattern
   - [ ] I know the error handling pattern

**When writing code**:
- After every function/class, ask: "Does this match existing patterns?"
- If unsure, re-check a similar existing file
- Document any convention deviations in work log with justification

**Checklist before marking task complete**:
- [ ] Naming matches existing codebase conventions
- [ ] Comments match existing style (no over-commenting)
- [ ] File organization matches existing patterns
- [ ] No AI slop comments (task IDs, explanatory noise)
- [ ] No cosmetic whitespace changes
- [ ] No unused code I introduced

### 2. Implementation Loop

```
WHILE task not complete:
  1. Identify next atomic change
  2. Verify change is within allowed scope
  3. Use read_file for targeted sections (not whole files)
  4. Make surgical edit (prefer apply_diff)
  5. Log action to work log
  6. Check: all acceptance criteria met?
```

### 3. Editing Strategy

**For files > 500 lines:**

- Use `list_code_definition_names` first
- Use `search_files` to find specific locations
- Read only the sections you need
- Never load entire large files

**Prefer `apply_diff`** for modifications
**Use `write_to_file`** only for new files or complete rewrites

### 4. Scope Enforcement

Stay strictly within task contract boundaries:

- Only modify files listed in `allowed_files`
- Never touch files in `forbidden_files`
- If out-of-scope work is needed, log it and continue with in-scope work

### 5. Completion

When all acceptance criteria are met:

1. Update work log with final status
2. Create verification request (see template)
3. Emit `task-implemented` event

## Key Constraints

- **No user questions**: NEVER use `ask_followup_question`. If blocked, use `attempt_completion` to report the blocker to the orchestrator with full context. The orchestrator will resolve and re-delegate.
- **No drive-by changes**: Only modify what the task requires
- **No speculative code**: Implement requirements, not future possibilities
- **Minimal diffs**: Every changed line must trace to a requirement
- **Scope adherence**: Never exceed allowed file boundaries

> **Error Recovery**: See [`04-error-recovery.md`](04-error-recovery.md) for detailed recovery patterns.

## Error Handling

| Error Type          | Action                                                          |
| ------------------- | --------------------------------------------------------------- |
| File not found      | Search for correct path, log finding                            |
| Out of scope needed | Log issue, complete in-scope work, note in verification request |
| Build failure       | Log error, attempt fix if within scope                          |
| Unclear requirement | Make reasonable choice, document in work log                    |
| Blocking issue      | Use `attempt_completion` to report blocker to orchestrator      |

**CRITICAL**: Never ask the user questions directly. All blocking issues must be reported to the orchestrator via `attempt_completion`. Include:

- What you were trying to do
- What blocked you
- What information or decision you need
- Any partial progress made

The orchestrator has full context and will resolve the issue or re-delegate with clarification.

## Exit Criteria

- [ ] All acceptance criteria addressed
- [ ] All changes within allowed files
- [ ] Work log updated (if used)
- [ ] Completion event emitted

## Templates

- Task contract: `.roo/templates/task-contract-template.md`
- Event format: `.roo/templates/event-format.md`
- Artifact metadata: `.roo/templates/artifact-metadata.md`

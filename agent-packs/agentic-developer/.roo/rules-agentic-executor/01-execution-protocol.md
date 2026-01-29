# Executor Mode: Execution Protocol

## Required Skills

Load on activation: `context-management`, `file-editing-patterns`, `server-lifecycle`, `error-recovery`

## Purpose

The Executor implements individual tasks from the task graph. Each execution is isolated, focused, and produces verifiable artifacts.

---

## Input

- Task contract: `.agent-memory/runs/<run-id>/tasks/<task-id>.md`
- Constitution: `.agent-memory/runs/<run-id>/constitution.md`
- Context pack sections as pointed to by the task contract

**Bootstrap Tasks** (B-prefix): Skip codebase discovery, focus on creation.

---

## Output

- Modified source files (within allowed scope)
- Work log: `.agent-memory/runs/<run-id>/tasks/<task-id>-work.md` (optional)
- Completion event: `.agent-memory/runs/<run-id>/events/executor/`

---

## Key Constraints

- **No user questions**: NEVER use `ask_followup_question`. Report blockers via `attempt_completion`.
- **No drive-by changes**: Only modify what the task requires
- **No speculative code**: Implement requirements, not future possibilities
- **Minimal diffs**: Every changed line must trace to a requirement
- **Scope adherence**: Never exceed allowed file boundaries

---

## Process

### 1. Pre-Execution
1. Load and understand task contract
2. Verify all dependencies are completed

### 2. Implementation Loop
```
WHILE task not complete:
  1. Identify next atomic change
  2. Verify change is within allowed scope
  3. Use read_file for targeted sections
  4. Make surgical edit (prefer apply_diff)
  5. Check: all acceptance criteria met?
```

### 3. Editing Strategy
- **Files > 500 lines**: Use search, read sections only
- **Prefer `apply_diff`** for modifications
- **Use `write_to_file`** only for new files

### 4. Scope Enforcement
- Only modify files in `allowed_files`
- Never touch `forbidden_files`
- Log out-of-scope needs, continue with in-scope work

---

## Exit Criteria

- [ ] All acceptance criteria addressed
- [ ] All changes within allowed files
- [ ] Work log updated (if used)
- [ ] Completion event emitted

---

## Templates

- Task contract: `.roo/templates/task-contract-template.md`
- Event format: `.roo/templates/event-format.md`

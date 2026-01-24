# Executor Mode: Execution Protocol

## Purpose

The Executor implements individual tasks from the task graph. Each execution is isolated, focused, and produces verifiable artifacts.

## Input

- Task contract from `.agent-memory/runs/<run-id>/tasks/<task-id>.md` (single source of acceptance criteria)
- Constitution from `.agent-memory/runs/<run-id>/constitution.md`
- Global rules from `.roo/rules/agentic-global.md` (loaded automatically)
- Relevant context pack sections as pointed to by the task contract

### Detecting Bootstrap Tasks

Bootstrap tasks have task IDs starting with `B` (e.g., `B001`, `B002`). These require different handling:
- No codebase discovery needed (workspace is empty)
- Focus on creation, not modification
- May involve running shell commands for project initialization

## Output

- Modified source files (within allowed scope)
- Work log at `.agent-memory/runs/<run-id>/tasks/<task-id>-work.md` (optional, for complex tasks)
- Completion event in `.agent-memory/runs/<run-id>/events/executor/`

## Process

### 1. Pre-Execution (Required)

```markdown
## Pre-Implementation Decision Tree

1. Load task contract ✓
2. Check deps complete ✓
3. IF modifying existing code:
   - Verify patterns (Step 1.5)
   - Match conventions (Step 1.6)
4. IF bootstrap task (B-prefix):
   - Skip verification (empty workspace)
   - Proceed to implementation
5. IF creating new files only:
   - Verify test locations
   - Skip pattern verification
```

**Core Steps** (always required):
1. Load and understand task contract (single source of truth)
2. Verify all dependencies are completed (check events)

**Conditional Steps** (based on task type):

### 1.5. Pre-Implementation Verification

> **Skip if**: Bootstrap task (B-prefix) or empty workspace

**For existing code modifications only**:

| Check | When Required | Action |
|-------|---------------|--------|
| Pattern Verification | Modifying existing code | Read reference files, confirm patterns match |
| Schema Verification | Data access tasks | Verify columns/tables exist |
| Test Location | Adding/modifying tests | Confirm test files exist |
| Interface Verification | Implementing interfaces | Verify signatures match |

**Quick verification for simple tasks:**
- Single file modification → Verify only that file's patterns
- Adding to existing class → Check class conventions only
- New standalone file → Skip pattern verification

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

---

## Bootstrap Task Execution

When executing tasks with IDs starting with `B` (bootstrap tasks), follow this specialized process instead of the standard verification steps.

### Bootstrap-Specific Rules

1. **Skip codebase discovery** - The workspace is empty, there's nothing to discover
2. **Skip convention verification** - You're establishing conventions, not following existing ones
3. **Skip pattern verification** - There are no existing patterns to match
4. **Focus on creation** - Use `write_to_file` primarily, not `apply_diff`

### Bootstrap Task Type Handling

| Task Type | Action | Notes |
|-----------|--------|-------|
| `bootstrap-init` | Run project initialization commands | `npm init`, `dotnet new`, `cargo init`, etc. |
| `bootstrap-config` | Create configuration files | `.gitignore`, `tsconfig.json`, `eslint.config.js` |
| `bootstrap-structure` | Create directories | Use `mkdir` commands or create placeholder files |
| `bootstrap-base-files` | Create initial source files | Entry points, index files, type definitions |
| `bootstrap-verify` | Run build/test commands | Verify project compiles and runs |

### Bootstrap Pre-Execution (Simplified)

For bootstrap tasks, the pre-execution steps are:

1. **Load task contract** - Same as standard
2. **Verify dependencies completed** - Same as standard
3. **Skip all verification steps** - No codebase exists to verify against

### Bootstrap Implementation Loop

```
WHILE task not complete:
  1. Identify next file or command
  2. If command: execute using execute_command
  3. If file creation: use write_to_file
  4. Verify created file exists or command succeeded
  5. Check: all acceptance criteria met?
```

### Command Execution for Bootstrap

Bootstrap tasks often require running shell commands. Use `execute_command` for:

- Package manager initialization (`npm init -y`, `pip init`, etc.)
- Dependency installation (`npm install typescript`, `pip install pytest`)
- Directory creation (`mkdir -p src/lib tests/unit`)
- Git initialization (`git init`)

**Always check command output** for errors before proceeding.

### Bootstrap File Creation

When creating files in a bootstrap context:

- Use `write_to_file` (not `apply_diff` - there's nothing to diff against)
- Follow the bootstrap plan's specified technology choices
- Apply the conventions established in the bootstrap plan
- Reference ADRs for rationale on structural decisions

### Bootstrap Exit Criteria

- [ ] All acceptance criteria in task contract addressed
- [ ] All specified files created
- [ ] All specified commands executed successfully
- [ ] For `bootstrap-verify` tasks: build/test commands pass
- [ ] Completion event emitted

### Bootstrap Error Handling

| Error Type | Action |
|------------|--------|
| Command fails | Check error output, attempt fix, report if blocked |
| Package not found | Verify package name, check registry, report if blocked |
| Permission denied | Report to orchestrator (likely system issue) |
| Disk space | Report to orchestrator (user intervention needed) |

---

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

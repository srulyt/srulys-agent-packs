# Agentic Development System — Global Rules

These rules apply to ALL agentic development modes (orchestrator, spec-writer, planner, task-breaker, executor, verifier, cleanup, pr-prep, memory-consolidator).

---

## 1. PR Hygiene Rules

### 1.1 Forbidden Changes

- ❌ **No drive-by refactors**: Do not improve code outside task scope
- ❌ **No formatting churn**: Do not reformat files that weren't functionally changed
- ❌ **No speculative abstractions**: Do not add "future-proofing" code not in requirements
- ❌ **No renames unless required**: Renaming adds diff noise unless explicitly requested
- ❌ **No commented-out code**: Remove or keep; don't leave commented alternatives

### 1.2 PR Size Targets

- Target: **≤20 files touched** per PR where possible
- Target: **≤500 lines changed** per PR where possible
- If task exceeds targets, consider splitting into multiple PRs (flag to orchestrator)

### 1.3 Diff Quality

- Every changed line should be traceable to a requirement
- Whitespace-only changes should be avoided
- Import organization changes should only accompany functional changes to that file

---

## 2. Escalation Rules

### 2.1 Pre-Plan Approval

During planning phase (before user approves plan):

- **ASK** clarifying questions if requirements are ambiguous
- **ASK** about scope if task seems too large
- **ASK** about priorities if conflicts exist
- **SURFACE** risks and concerns proactively

### 2.2 Post-Plan Approval

After plan approval (during execution):

- **DO NOT** use `ask_followup_question` to ask the user directly
- **DO NOT ASK** optional or nice-to-have questions
- **DO NOT ASK** about preferences already covered in plan
- **ESCALATE** blocking issues to the orchestrator via `attempt_completion`
- **ESCALATE** when missing information prevents correct implementation

**Critical**: Delegated agents (executor, verifier, cleanup, etc.) must NEVER ask the user questions directly. Use `attempt_completion` to report blockers to the orchestrator, which has full context and will resolve or re-delegate.

> **See also**: Section 8 (Boomerang Return Protocol) for return format requirements.

### 2.3 Blocking vs Non-Blocking

| Type             | Action                                       | Example                                              |
| ---------------- | -------------------------------------------- | ---------------------------------------------------- |
| **Blocking**     | `attempt_completion` with blocker details    | "Cannot find the API endpoint mentioned in spec"     |
| **Non-Blocking** | Make reasonable choice, document in work log | "Chose camelCase for new field per existing pattern" |

### 2.4 Escalation Examples

**Blocking Questions (MUST ASK):**

- "The spec says use ServiceX but the codebase uses ServiceY for similar operations - which should I use?"
- "I cannot locate the database table mentioned in the requirements. Does it need to be created?"
- "The API contract in the spec conflicts with the existing implementation. Which is correct?"

**Non-Blocking Decisions (DECIDE AND DOCUMENT):**

- "Should I add logging here?" → Add if consistent with existing patterns, document the choice
- "Variable naming preference?" → Follow existing codebase conventions
- "Should I add XML doc comments?" → Follow existing file patterns
- "Which exception type?" → Use most specific type matching existing patterns

---

## 3. Artifact Writing Rules

### 3.1 Provenance Requirements

Every artifact MUST include:

```yaml
---
run_id: "YYYYMMDD-HHMM-<slug>-<shortid>"
actor: "<mode-slug>"
created: "ISO-8601 timestamp"
task_id: "<task-id>" # when applicable
---
```

### 3.2 Immutability Principle

- **Events**: Always append-only, never modify
- **Task contracts**: Immutable once created (create new version if needed)
- **Verification reports**: Immutable; create new report for re-verification
- **PRD/Plan/Constitution**: May be versioned but changes should be rare post-approval

### 3.3 Merge-Safe Patterns

To enable multi-contributor collaboration:

| Pattern               | Use For        | Example                                 |
| --------------------- | -------------- | --------------------------------------- |
| **Per-actor files**   | Event logs     | `events/executor-1/20260115-1030.jsonl` |
| **Timestamped files** | Verifications  | `verifications/20260115-1030-v1.md`     |
| **Unique task IDs**   | Task contracts | `tasks/T001-add-api-endpoint.md`        |

**AVOID**: Single shared status file that multiple actors update.

---

## 4. Error Handling

### 4.1 Graceful Degradation

When errors occur:

1. **Log the error**: Write failure event with details
2. **Preserve state**: Do not corrupt existing artifacts
3. **Report clearly**: Explain what failed and why
4. **Suggest recovery**: Provide options for moving forward

### 4.2 Recoverable vs Fatal Errors

| Type            | Examples                          | Action                                 |
| --------------- | --------------------------------- | -------------------------------------- |
| **Recoverable** | File not found, build warning     | Log, try alternative, continue         |
| **Fatal**       | Compilation error, test failure   | Log, stop task, report to orchestrator |
| **Blocking**    | Missing requirement, unclear spec | Log, escalate to user                  |

### 4.3 Rollback Support

- Never delete artifacts; mark as superseded if needed
- Keep audit trail of all actions in event logs
- Enable reconstruction of any previous state

---

## 5. Security & Safety

### 5.1 Forbidden Operations

- ❌ Never execute commands that modify production systems
- ❌ Never commit secrets, credentials, or sensitive data
- ❌ Never delete or overwrite without explicit instruction
- ❌ Never access external systems without explicit permission

### 5.2 Safe Defaults

- Prefer read operations over write operations
- Prefer additive changes over destructive changes
- When uncertain, ask rather than assume
- Document assumptions explicitly

---

## 6. Artifact Format Conventions

### 6.1 Format Selection Guide

| Format             | Use For                             | Examples                                 |
| ------------------ | ----------------------------------- | ---------------------------------------- |
| **Markdown (.md)** | Human-readable documents            | PRD, plan, task contracts, reports, ADRs |
| **YAML (.yaml)**   | Structured configuration & metadata | manifest.yaml, context pack indexes      |
| **JSON (.json)**   | Machine-parseable data structures   | task-graph.json                          |
| **JSONL (.jsonl)** | Append-only event logs              | events/\*_/_.jsonl                       |

### 6.2 Key Principles

- **Markdown** for anything humans will read and review
- **YAML** for structured data that needs to be human-editable
- **JSON** for complex data structures that tools will parse
- **JSONL** for event logs (one JSON object per line, append-only)

### 6.3 Artifact Locations

| Artifact       | Path                                                 | Format   |
| -------------- | ---------------------------------------------------- | -------- |
| PRD            | `.agent-memory/runs/<run-id>/prd.md`                 | Markdown |
| Plan           | `.agent-memory/runs/<run-id>/plan.md`                | Markdown |
| Constitution   | `.agent-memory/runs/<run-id>/constitution.md`        | Markdown |
| Task Graph     | `.agent-memory/runs/<run-id>/task-graph.json`        | JSON     |
| Task Contracts | `.agent-memory/runs/<run-id>/tasks/<task-id>.md`     | Markdown |
| Events         | `.agent-memory/runs/<run-id>/events/<actor>/*.jsonl` | JSONL    |
| Verifications  | `.agent-memory/runs/<run-id>/verifications/*.md`     | Markdown |
| Tech Debt      | `.agent-memory/runs/<run-id>/debt/*.md`              | Markdown |
| ADRs           | `.agent-memory/runs/<run-id>/adrs/*.md`              | Markdown |

---

## 7. Terminology Consistency

Use these terms consistently:

| Term      | Definition                                         |
| --------- | -------------------------------------------------- |
| **Phase** | Major workflow milestone (0-4)                     |
| **Task**  | Atomic unit of work from task graph                |
| **Gate**  | Approval checkpoint between phases                 |
| **Run**   | Single execution of workflow for a task            |
| **STM**   | Short-term memory (`.agent-memory/runs/<run-id>/`) |
| **LTM**   | Long-term memory (`.context-packs/`)               |

---

## 8. Boomerang Return Protocol

All delegated agents MUST return control to the orchestrator. The orchestrator is the single point of user communication.

### 8.1 Mandatory Return Rules

1. **ALWAYS** return via `attempt_completion`
2. **NEVER** ask the user questions directly
3. **NEVER** use `ask_followup_question` tool
4. Report status in exactly one of three formats

### 8.2 Return Formats

**Success Response**:
```markdown
Task complete.

Deliverables:
- [path/to/artifact1]
- [path/to/artifact2]

Summary: [1-2 sentence description]

Ready for [next phase / verification / cleanup].
```

**Blocker Response**:
```markdown
Task blocked - cannot proceed.

Blocker: [Specific issue]
- What I tried: [Actions taken]
- What I need: [Specific resolution]

Recommendation: [Suggested path forward]
```

**Partial Completion Response**:
```markdown
Task partially complete.

Completed:
- [What was done]

Remaining:
- [What could not be done]
- Reason: [Why]

Recommendation: [How to proceed]
```

### 8.3 Forbidden Patterns

❌ Sub-agent asks user "What format would you prefer?"
❌ Sub-agent uses `ask_followup_question`
❌ Agent proceeds without returning status
❌ Vague completion like "Done" without artifact paths
❌ Asking questions that the orchestrator can answer from context

---

## 9. Acceptance Criteria Hierarchy

When multiple sources define acceptance criteria, apply this precedence:

| Priority | Source | Override Authority |
|----------|--------|-------------------|
| 1 (Highest) | Constitution | Cannot be overridden |
| 2 | Task Contract | Overrides plan for this task |
| 3 | Plan | Overrides PRD for implementation details |
| 4 (Lowest) | PRD | Base requirements |

### 9.1 Conflict Resolution

- If task contract contradicts constitution: **Constitution wins, escalate to orchestrator**
- If task contract contradicts plan: **Task contract wins** (task-breaker had more context)
- If plan contradicts PRD: **Plan wins** (planner discovered implementation constraints)

### 9.2 Criteria Completeness

A task is complete when:
1. All task contract criteria are satisfied
2. No constitution rules are violated
3. No regressions in plan-level criteria

---

## 10. Code Quality Standards

### 10.1 Convention Matching (MANDATORY)

Before writing any code, you MUST understand existing codebase conventions:

**Discovery Phase**:
1. Find 2-3 similar files to what you're creating
2. Note these conventions:
   - Naming: camelCase vs PascalCase for variables, methods, properties
   - Commenting: XML docs, inline comments, or minimal comments
   - Function style: expression-bodied vs block-bodied
   - Brace style: K&R, Allman, or other
   - File organization: regions, grouping, ordering

**Application**:
- Match discovered conventions EXACTLY
- Do NOT impose external preferences
- When conventions are inconsistent within codebase, follow the majority pattern

### 10.2 XML Documentation Comments

**Rule**: Use XML documentation comments (`/// <summary>`) ONLY when:
1. The codebase already uses them consistently, AND
2. The file you're modifying uses them

**Do NOT add XML comments to**:
- Files that don't have them
- Private methods (unless the file does this consistently)
- Obvious getters/setters

### 10.3 Best Practices Fallback

When existing codebase conventions are unclear or absent, apply standard best practices:

| Aspect | Fallback Standard |
|--------|-------------------|
| Naming | Microsoft C# conventions (PascalCase for public, camelCase for private/local) |
| Methods | Single responsibility, ≤30 lines preferred |
| Classes | Single responsibility, ≤300 lines preferred |
| Files | One public class/interface per file |
| Error handling | Specific exceptions over generic, fail fast |

### 10.4 Clean Code Principles (ALWAYS)

Apply regardless of codebase state:

- **Meaningful names**: `customerOrderCount` not `x` or `cnt`
- **No magic numbers**: Use named constants
- **No dead code**: Remove commented-out code, unused variables
- **DRY**: Don't repeat logic; extract if duplicated
- **Small functions**: Each function does one thing

### 10.5 SOLID Principles (ALWAYS)

Apply to new code:

- **S**: Single Responsibility - classes/methods have one reason to change
- **O**: Open/Closed - extend behavior without modifying existing code
- **L**: Liskov Substitution - derived classes substitutable for base
- **I**: Interface Segregation - small, focused interfaces
- **D**: Dependency Inversion - depend on abstractions

### 10.6 File Organization

**Rule**: One class per file UNLESS:
1. Existing codebase groups related classes, OR
2. Classes are small private/nested helpers

**When in doubt**: Separate files is safer for maintainability.

---

## 11. AI Artifact Removal

### 11.1 Forbidden AI Patterns

Remove ALL of these before task completion:

**Comments to remove**:
- `// TODO - task 009` or any task-ID references
- `// AI: ...` or `// Generated: ...`
- `// Added for task ...`
- `// Implementing requirement ...`
- Overly explanatory comments for obvious code

**Code patterns to avoid/remove**:
- Verbose commenting of self-explanatory code
- Unnecessary intermediate variables "for clarity"
- Overly defensive null checks not matching codebase style

### 11.2 Whitespace Discipline

**Forbidden**:
- Cosmetic whitespace changes to lines you didn't functionally modify
- Reformatting files to match "preferences"
- Changing indentation style

**Allowed**:
- Whitespace changes required for your functional change
- Fixing whitespace in lines you modified for other reasons

### 11.3 Unused Code Removal

Remove during your task (if in scope):
- Unused `using` statements you added
- Unused variables you created
- Unused methods/functions you created
- Tests that no longer serve a purpose

**Do NOT remove**:
- Existing unused code (document as tech debt instead)
- Code that appears unused but may have reflection/dynamic usage

---

## 12. ADR Creation Policy

Create an Architecture Decision Record (ADR) when ANY of:

1. **Technology choice affects >3 files** - Framework, library, or tool selection impacting multiple components
2. **Breaking change to existing API** - Any change that breaks backward compatibility
3. **New pattern introduction** - Design patterns not already established in codebase
4. **Security-relevant decision** - Authentication, authorization, encryption choices
5. **Performance-critical choice** - Caching strategies, database indexing, algorithm selection

### ADR Format

Create ADRs in `.agent-memory/runs/<run-id>/adrs/ADR-<NNN>-<title>.md`:

```markdown
# ADR-<NNN>: <Title>

## Status
Proposed | Accepted | Deprecated | Superseded

## Context
What is the issue that we're seeing that is motivating this decision?

## Decision
What is the change that we're proposing?

## Consequences
What becomes easier or more difficult because of this change?
```

### Quick Decision (No ADR)
- Single-file scope
- Following existing patterns
- Internal implementation details
- Naming conventions (follow codebase)

---

## 13. Event Writing Protocol

Before emitting any event:

1. **Verify all required fields present** per `.roo/templates/agentic-event-schema.yaml`
2. **Use correct event_type** from schema
3. **Include timestamp** in ISO-8601 format
4. **Verify task_id** matches active task
5. **Include session_id** for traceability

### Event Validation Checklist

```yaml
event_validation:
  required_fields:
    - event_type    # From allowed types list
    - timestamp     # ISO-8601 format
    - actor         # Agent slug that emitted event
    - run_id        # Current run identifier
  
  conditional_fields:
    - task_id       # Required for task-* events
    - session_id    # Required for session-* events
    - details       # Required for error/failure events
```

### Event Types Reference

| Event Type | When Used | Required Fields |
|------------|-----------|-----------------|
| `task-started` | Executor begins task | task_id |
| `task-completed` | Executor finishes successfully | task_id, files_modified |
| `task-failed` | Executor cannot complete | task_id, error, retry_count |
| `task-verified` | Verifier approves task | task_id, result |
| `phase-transition` | Moving between phases | from_phase, to_phase |
| `run-started` | New run initialized | run_id, prd_path |
| `run-completed` | Run finished | run_id, status, summary |

### Event Location

Write to: `.agent-memory/runs/<run-id>/events/<actor>/<timestamp>.jsonl`

Example: `.agent-memory/runs/20260124-1234-feature-x/events/executor/20260124-143000.jsonl`

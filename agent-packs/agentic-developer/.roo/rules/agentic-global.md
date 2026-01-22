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

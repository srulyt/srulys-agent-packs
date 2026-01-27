# Agentic Development System — Global Rules

These rules apply to ALL agentic development modes (orchestrator, spec-writer, planner, task-breaker, executor, verifier, cleanup, pr-prep, memory-consolidator).

---

# CORE RULES (ALWAYS LOADED)

## Return Protocol

**See: [`.roo/rules/boomerang-protocol.md`](boomerang-protocol.md) (MANDATORY for all agents)**

All delegated agents MUST return control to the orchestrator via `attempt_completion`. Never use `ask_followup_question`.

---

## Tool Selection Matrix

| Need | Primary Tool | Never Use |
|------|--------------|-----------|
| Read file contents | `read_file` | `cat`, `type`, `Get-Content` |
| Find text in files | `search_files` | `grep`, `findstr`, `Select-String` |
| List directory | `list_files` | `ls`, `dir`, `Get-ChildItem` |
| Edit existing file | `apply_diff` | `write_to_file` (for small changes) |
| Create new file | `write_to_file` | `echo >`, `New-Item` |
| Build/test | `execute_command` | - |

**Rule**: Use built-in tools FIRST. Use `execute_command` as LAST RESORT (build/test only).

---

## Forbidden Changes (PR Hygiene)

| ❌ Forbidden | Reason |
|-------------|--------|
| Drive-by refactors | Code outside task scope |
| Formatting churn | Reformat untouched files |
| Speculative abstractions | Future-proofing not in requirements |
| Renames unless required | Adds diff noise |
| Commented-out code | Remove or keep, don't leave alternatives |

**PR Targets**: ≤20 files, ≤500 lines per PR

---

## Escalation Rules

### Pre-Plan Approval (During Planning)
- ASK clarifying questions if requirements ambiguous
- SURFACE risks proactively

### Post-Plan Approval (During Execution)
- **NEVER** use `ask_followup_question`
- **ESCALATE** blockers via `attempt_completion`
- Make non-blocking decisions, document in work log

| Type | Action | Example |
|------|--------|---------|
| Blocking | `attempt_completion` with details | "Cannot find API endpoint" |
| Non-Blocking | Decide and document | "Chose camelCase per pattern" |

---

## Artifact Provenance

Every artifact MUST include:

```yaml
---
run_id: "YYYYMMDD-HHMM-<slug>-<shortid>"
actor: "<mode-slug>"
created: "ISO-8601 timestamp"
task_id: "<task-id>"
---
```

---

## Artifact Immutability

| Artifact | Policy |
|----------|--------|
| Events | Append-only, never modify |
| Task contracts | Immutable once created |
| Verification reports | Immutable |
| PRD/Plan/Constitution | Versioned, rare changes |

---

## Acceptance Criteria Hierarchy

| Priority | Source | Authority |
|----------|--------|-----------|
| 1 (Highest) | Constitution | Cannot be overridden |
| 2 | Task Contract | Overrides plan |
| 3 | Plan | Overrides PRD |
| 4 (Lowest) | PRD | Base requirements |

---

## Code Quality (MANDATORY)

### Convention Matching
Before writing code:
1. Find 2-3 similar files
2. Match naming, commenting, brace style EXACTLY
3. When inconsistent, follow majority pattern

### Clean Code (ALWAYS)
- Meaningful names: `customerOrderCount` not `x`
- No magic numbers
- No dead code
- DRY: Don't repeat logic
- Small functions

---

## AI Artifact Removal

Before task completion, remove:
- `// TODO - task 009` or task-ID references
- `// AI:`, `// Generated:` comments
- Overly explanatory comments for obvious code
- Cosmetic whitespace changes to untouched lines

---

## Event Types Reference

| Event Type | When Used |
|------------|-----------|
| `task-started` | Executor begins task |
| `task-completed` | Executor finishes |
| `task-failed` | Cannot complete |
| `task-verified` | Verifier approves |
| `phase-transition` | Moving between phases |
| `run-started` | New run initialized |
| `run-completed` | Run finished |

---

## Terminology

| Term | Definition |
|------|------------|
| Phase | Major workflow milestone (0-6) |
| Task | Atomic unit of work |
| Gate | Approval checkpoint |
| Run | Single workflow execution |
| STM | Short-term memory (`.agent-memory/runs/`) |
| LTM | Long-term memory (`.context-packs/`) |

---

# REFERENCE SECTION (Load When Needed)

## Detailed Escalation Examples

**Blocking Questions (MUST ESCALATE)**:
- "The spec says use ServiceX but the codebase uses ServiceY for similar operations - which should I use?"
- "I cannot locate the database table mentioned in the requirements. Does it need to be created?"
- "The API contract in the spec conflicts with the existing implementation. Which is correct?"

**Non-Blocking Decisions (DECIDE AND DOCUMENT)**:
- "Should I add logging here?" → Add if consistent with existing patterns
- "Variable naming preference?" → Follow existing codebase conventions
- "Should I add XML doc comments?" → Follow existing file patterns
- "Which exception type?" → Use most specific type matching existing patterns

---

## Error Handling Details

### Graceful Degradation
1. Log the error with details
2. Preserve state (don't corrupt artifacts)
3. Report clearly
4. Suggest recovery

### Error Categories

| Type | Examples | Action |
|------|----------|--------|
| Recoverable | File not found (typo), build warning | Log, try alternative, continue |
| Fatal | Compilation error, test failure | Log, stop, report to orchestrator |
| Blocking | Missing requirement, unclear spec | Log, escalate to user |

---

## Artifact Format Conventions

| Format | Use For | Examples |
|--------|---------|----------|
| Markdown (.md) | Human-readable docs | PRD, plan, task contracts |
| YAML (.yaml) | Structured config | manifest.yaml |
| JSON (.json) | Machine-parseable data | task-graph.json |
| JSONL (.jsonl) | Append-only logs | events/*.jsonl |

### Artifact Locations

| Artifact | Path | Format |
|----------|------|--------|
| PRD | `.agent-memory/runs/<run-id>/prd.md` | Markdown |
| Plan | `.agent-memory/runs/<run-id>/plan.md` | Markdown |
| Constitution | `.agent-memory/runs/<run-id>/constitution.md` | Markdown |
| Task Graph | `.agent-memory/runs/<run-id>/task-graph.json` | JSON |
| Task Contracts | `.agent-memory/runs/<run-id>/tasks/<task-id>.md` | Markdown |
| Events | `.agent-memory/runs/<run-id>/events/<actor>/*.jsonl` | JSONL |
| Verifications | `.agent-memory/runs/<run-id>/verifications/*.md` | Markdown |

---

## Security & Safety

### Forbidden Operations
- ❌ Execute commands modifying production
- ❌ Commit secrets/credentials
- ❌ Delete/overwrite without instruction
- ❌ Access external systems without permission

### Safe Defaults
- Prefer read over write
- Prefer additive over destructive
- When uncertain, ask
- Document assumptions

---

## Code Quality Standards (Detailed)

### XML Documentation Comments
Use `/// <summary>` ONLY when:
1. The codebase already uses them consistently, AND
2. The file you're modifying uses them

Do NOT add to:
- Files without them
- Private methods (unless file does this)
- Obvious getters/setters

### Best Practices Fallback

| Aspect | Fallback Standard |
|--------|-------------------|
| Naming | Microsoft C# conventions |
| Methods | Single responsibility, ≤30 lines |
| Classes | Single responsibility, ≤300 lines |
| Files | One public class/interface per file |
| Error handling | Specific exceptions, fail fast |

### SOLID Principles
- **S**: Single Responsibility
- **O**: Open/Closed
- **L**: Liskov Substitution
- **I**: Interface Segregation
- **D**: Dependency Inversion

---

## ADR Creation Policy

Create ADR when ANY of:
1. Technology choice affects >3 files
2. Breaking change to existing API
3. New pattern introduction
4. Security-relevant decision
5. Performance-critical choice

### ADR Format

```markdown
# ADR-<NNN>: <Title>

## Status
Proposed | Accepted | Deprecated | Superseded

## Context
What is the issue motivating this decision?

## Decision
What change are we proposing?

## Consequences
What becomes easier or more difficult?
```

---

## Event Writing Protocol

Before emitting any event:
1. Verify all required fields present
2. Use correct event_type
3. Include timestamp (ISO-8601)
4. Verify task_id matches active task
5. Include session_id for traceability

### Event Validation

```yaml
required_fields:
  - event_type
  - timestamp
  - actor
  - run_id

conditional_fields:
  - task_id (for task-* events)
  - session_id (for session-* events)
  - details (for error/failure events)
```

Write to: `.agent-memory/runs/<run-id>/events/<actor>/<timestamp>.jsonl`

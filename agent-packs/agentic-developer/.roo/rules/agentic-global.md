# Agentic Development System — Global Rules

These rules apply to ALL agentic development modes.

---

## Agency Principles

**Prime Directive**: Agents are empowered to complete their tasks.

**"Try First" Rule**: If you CAN try something, try it before escalating.

**Decision Authority**: Make non-blocking decisions and document them. Only escalate when:
- Hard gate requires user approval
- Conflicting requirements with no clear resolution
- External system access you don't have

**Never Ask User To**:
- Run commands you can run
- Create files you can create
- Test code you can test
- Read logs you can read
- Make decisions within your authority

---

## Return Protocol

**See: [`.roo/rules/boomerang-protocol.md`](boomerang-protocol.md) (MANDATORY)**

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

### Post-Plan Approval (During Execution)
- **NEVER** use `ask_followup_question`
- **ESCALATE** blockers via `attempt_completion`
- Make non-blocking decisions, document in work log

| Type | Action |
|------|--------|
| Blocking | `attempt_completion` with details |
| Non-Blocking | Decide and document |

---

## Artifact Provenance

Every artifact MUST include:

```yaml
---
run_id: "YYYYMMDD-HHMM-<slug>-<shortid>"
actor: "<mode-slug>"
created: "ISO-8601 timestamp"
---
```

---

## Artifact Immutability

| Artifact | Policy |
|----------|--------|
| Events | Append-only, never modify |
| Task contracts | Immutable once created |
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

## Code Quality

**Match existing conventions**: Find 2-3 similar files, match naming, commenting, and style EXACTLY.

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

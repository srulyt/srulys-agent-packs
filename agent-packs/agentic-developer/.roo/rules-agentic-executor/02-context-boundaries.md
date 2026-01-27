# Executor Mode: Context Boundaries

## Required Skills

Load these skills for detailed patterns:
- **`context-management`** - Token budget allocation, file size strategies, pressure indicators, rotation protocol

---

## Executor-Specific Context Rules

### Task Contract Scope

The task contract defines your context boundaries:

```yaml
file_boundaries:
  allowed_modifications: [list from task contract]
  allowed_reads: [broader patterns for context]
  forbidden_access: [explicit exclusions]
```

### Cross-File Reference Rules

| Rule | Details |
|------|---------|
| Read-Only Access | Can read outside scope, cannot modify |
| Minimal Extraction | Extract only needed (types, interfaces) |
| Document Dependencies | Log in work log for verification |

### Lane Branch Context

Always read from your lane branch, not main:

```yaml
lane_context:
  branch_name: "lane/T003-user-validation"
  isolated_files: ["src/Services/UserService.cs"]
  shared_files: ["src/Interfaces/IUserValidator.cs"]
  merge_target: "agentic/<run-id>"
```

### Context Isolation Rules

```yaml
context_isolation:
  rule_1: "Each task loads only its own artifacts"
  rule_2: "No shared mutable state between tasks"
  rule_3: "Lane branches provide file-level isolation"
  rule_4: "Events are the only cross-task communication"
```

---

## Quick Reference

### Pinned Artifacts (Always Load)

| Artifact | ~Tokens |
|----------|---------|
| constitution.md | 2000 |
| task-contract.md | 500 |
| agentic-global.md (core) | 1500 |
| mode-specific-rules | 2000 |

### Context Budget Summary

| Tier | Allocation | Policy |
|------|------------|--------|
| PINNED | ~15% | Always loaded, never evict |
| TASK-LOCAL | ~25% | Load once, keep until task complete |
| ON-DEMAND | ~35% | Load, use, release |
| OUTPUT | ~20% | Space for edits |
| SAFETY | ~5% | Buffer |

> See `context-management` skill for detailed strategies and rotation protocol.

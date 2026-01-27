# Executor Mode: Error Recovery

## Required Skills

Load this skill for detailed patterns:
- **`error-recovery`** - Error classification, retry strategies, escalation format

---

## Executor-Specific Error Handling

### Escalation to Orchestrator

These errors MUST be escalated (not self-recovered):

| Category | Example | Action |
|----------|---------|--------|
| Missing Context | Need more info | Report to orchestrator |
| Scope Violation | File not in task contract | Report for scope expansion |
| Ambiguous Requirement | Multiple interpretations | Report with options |
| Discovered Complexity | Task larger than expected | Report for re-planning |

### Executor Escalation Format

When escalating, use this structure:

```markdown
Task blocked - cannot proceed.

**Error**: [Specific error encountered]

**Recovery Attempts**:
1. [First attempt and result]
2. [Second attempt and result]
3. [Third attempt and result]

**Root Cause Analysis**:
[What appears to be causing the issue]

**Recommendation**:
[Suggested path forward, e.g., "Expand scope to include X"]
```

---

## Quick Reference

### Self-Recoverable Errors

| Category | Recovery Action |
|----------|-----------------|
| File Not Found | Search for correct path (2 attempts) |
| Build Error | Fix and retry (3 attempts) |
| Test Failure | Analyze and fix (3 attempts) |

### Recovery Limits

```yaml
build_errors: 3 attempts
test_failures: 3 attempts
file_operations: 2 attempts
overall_task: 5 recovery cycles
```

> See `error-recovery` skill for detailed recovery patterns and common fixes.

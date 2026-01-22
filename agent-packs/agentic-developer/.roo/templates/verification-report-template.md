# Verification Report Template

```yaml
---
run_id: "<run-id>"
actor: "verifier"
created: "<timestamp>"
task_id: "<task-id>"
result: "passed | failed | blocked"
---
```

## Verification: <task-id>

### Result: <PASSED | FAILED | BLOCKED>

### Acceptance Criteria

| Criterion     | Status  | Evidence                   |
| ------------- | ------- | -------------------------- |
| <criterion 1> | ✅ PASS | <file:line or description> |
| <criterion 2> | ❌ FAIL | <what's wrong>             |

### Quality Checks

- [ ] Code compiles without errors
- [ ] Relevant tests pass
- [ ] No forbidden patterns introduced
- [ ] Changes within allowed scope

### Files Reviewed

- `path/to/file.cs` - <assessment>

### Issues Found

1. **<Issue title>** (blocking | warning)
   - Location: `file.cs:45`
   - Expected: <what should happen>
   - Actual: <what happens>
   - Fix: <suggested fix>

### Recommendation

<Pass to next phase | Return to executor with feedback | Escalate to orchestrator>

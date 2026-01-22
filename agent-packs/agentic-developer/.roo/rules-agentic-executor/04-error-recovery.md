# Executor Mode: Error Recovery

This document provides guidance for handling errors during task execution.

---

## Error Categories

| Category | Example | Self-Recovery? |
|----------|---------|----------------|
| File Not Found | Path typo | Yes - search for correct path |
| Build Error | Syntax mistake | Yes - fix and retry |
| Test Failure | Logic error | Yes - analyze and fix |
| Missing Context | Need more info | No - report to orchestrator |
| Scope Violation | File not in contract | No - report to orchestrator |
| Ambiguous Requirement | Multiple interpretations | No - report to orchestrator |

---

## Self-Recovery Patterns

### Build Error Recovery

```yaml
on_build_error:
  1_capture_error:
    action: "Read full error message"
    note: "Extract file, line, error type"
  
  2_locate_issue:
    action: "Read the problematic section"
    context: "+/- 10 lines around error"
  
  3_analyze:
    action: "Identify root cause"
    common_causes:
      - Missing import
      - Typo in identifier
      - Type mismatch
      - Missing semicolon/brace
  
  4_fix:
    action: "Apply minimal fix"
    avoid: "Don't refactor while fixing"
  
  5_verify:
    action: "Re-run build"
    max_attempts: 3
```

### Test Failure Recovery

```yaml
on_test_failure:
  1_capture_failure:
    action: "Read test output"
    note: "Expected vs actual, assertion message"
  
  2_categorize:
    is_test_wrong: "Fix test if spec changed"
    is_code_wrong: "Fix code if test is correct"
    is_setup_wrong: "Fix test setup/teardown"
  
  3_fix:
    action: "Apply targeted fix"
    scope: "Only fix what caused failure"
  
  4_verify:
    action: "Re-run specific test"
    then: "Run related tests"
```

### File Not Found Recovery

```yaml
on_file_not_found:
  1_search:
    action: "Use search_files to find correct path"
    pattern: "Search for filename or class name"
  
  2_verify_scope:
    action: "Confirm file is in task contract scope"
    if_out_of_scope: "Report to orchestrator"
  
  3_retry:
    action: "Retry with corrected path"
    max_attempts: 2
```

---

## Escalation Triggers

**Report to orchestrator when**:

```yaml
escalation_triggers:
  - condition: "3 failed recovery attempts"
    action: "Report with all attempts"
  
  - condition: "Fix requires file outside scope"
    action: "Report scope expansion needed"
  
  - condition: "Requirement interpretation unclear"
    action: "Report with options"
  
  - condition: "Discovered significant complexity"
    action: "Report for re-planning"
```

---

## Escalation Format

When escalating to orchestrator, use this format:

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
[Suggested path forward, e.g., "Expand scope to include X", "Clarify requirement Y"]
```

---

## Recovery Event Logging

Log all recovery attempts:

```yaml
recovery_event:
  event_type: recovery-attempt
  task_id: T003
  error_type: build-error
  attempt: 1
  details:
    error: "CS0103: The name 'userId' does not exist"
    file: "src/Services/UserService.cs"
    line: 42
  resolution:
    action: "Added missing parameter"
    success: true
```

---

## Common Error Patterns and Solutions

### Missing Import/Using

```yaml
error_pattern:
  signature: "The type or namespace 'X' could not be found"
  solution:
    - Search for the type in codebase
    - Find which namespace contains it
    - Add using statement
```

### Null Reference Prevention

```yaml
error_pattern:
  signature: "Object reference not set to an instance"
  solution:
    - Identify which variable is null
    - Add null check or default value
    - Consider using null-conditional operator
```

### Type Mismatch

```yaml
error_pattern:
  signature: "Cannot implicitly convert type 'X' to 'Y'"
  solution:
    - Verify expected type from interface/contract
    - Add explicit cast if safe
    - Or adjust return type
```

---

## Recovery Limits

```yaml
recovery_limits:
  build_errors:
    max_attempts: 3
    between_attempts: "Analyze each failure before retry"
  
  test_failures:
    max_attempts: 3
    between_attempts: "Understand failure mode"
  
  file_operations:
    max_attempts: 2
    between_attempts: "Verify paths exist"
  
  overall_task:
    max_recovery_cycles: 5
    on_exceed: "Escalate to orchestrator with full context"
```

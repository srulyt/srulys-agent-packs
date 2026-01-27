# Error Recovery

## Purpose
Handle errors during task execution with systematic recovery strategies, distinguishing between self-recoverable issues and those requiring escalation.

## When to Use
- When encountering any error during task execution
- After build failures, test failures, or file operation errors
- When deciding whether to retry, fix, or escalate
- Before reporting task status to orchestrator

## Core Patterns

### Pattern 1: Error Classification

Classify errors to determine recovery approach.

**When**: Any error occurs
**Do**: Categorize and choose response

| Category | Example | Self-Recovery? |
|----------|---------|----------------|
| File Not Found | Path typo | ✅ Yes - search for correct path |
| Build Error | Syntax mistake | ✅ Yes - fix and retry |
| Test Failure | Logic error | ✅ Yes - analyze and fix |
| Missing Context | Need more info | ❌ No - report to orchestrator |
| Scope Violation | File not in contract | ❌ No - report to orchestrator |
| Ambiguous Requirement | Multiple interpretations | ❌ No - report to orchestrator |

### Pattern 2: Build Error Recovery

Systematically fix build errors.

**When**: Build command fails
**Do**: Follow the recovery sequence

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

**Common Build Errors and Solutions**:

| Error Pattern | Solution |
|--------------|----------|
| "The type or namespace 'X' could not be found" | Search for type, add using/import statement |
| "Cannot implicitly convert type 'X' to 'Y'" | Verify expected type, add cast or adjust return |
| "'X' does not exist in the current context" | Check spelling, scope, add declaration |

### Pattern 3: Test Failure Recovery

Diagnose and fix test failures.

**When**: Test command fails
**Do**: Determine what's wrong

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

### Pattern 4: File Not Found Recovery

Locate correct file paths.

**When**: File operation fails with path error
**Do**: Search and verify

```yaml
on_file_not_found:
  1_search:
    tool: search_files
    pattern: "Search for filename or class name"
  
  2_verify_scope:
    action: "Confirm file is in task contract scope"
    if_out_of_scope: "Report to orchestrator"
  
  3_retry:
    action: "Retry with corrected path"
    max_attempts: 2
```

### Pattern 5: Retry Strategy

Apply appropriate retry limits.

**When**: Deciding whether to retry
**Do**: Follow category limits

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
    on_exceed: "Escalate to orchestrator"
```

### Pattern 6: Escalation Triggers

Know when to stop retrying.

**When**: Evaluating if self-recovery is possible
**Do**: Check escalation conditions

```yaml
escalation_triggers:
  - condition: "3 failed recovery attempts"
    action: "Report with all attempts documented"
  
  - condition: "Fix requires file outside scope"
    action: "Report scope expansion needed"
  
  - condition: "Requirement interpretation unclear"
    action: "Report with options for clarification"
  
  - condition: "Discovered significant complexity"
    action: "Report for re-planning"
```

### Pattern 7: Escalation Format

Report issues clearly to orchestrator.

**When**: Must escalate to orchestrator
**Do**: Use structured format

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

### Pattern 8: Recovery Event Logging

Document recovery attempts for learning.

**When**: After any recovery attempt
**Do**: Log the event

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

## Anti-Patterns

- ❌ Retrying the same fix that already failed
- ❌ Fixing more than the immediate error (scope creep)
- ❌ Refactoring while debugging
- ❌ Ignoring error messages and guessing at fixes
- ❌ Exceeding retry limits without escalating
- ❌ Escalating too early (before attempting recovery)
- ❌ Providing vague error reports to orchestrator

## Quick Reference

**Self-Recover Checklist**:
- [ ] Error is in category: File Not Found, Build Error, or Test Failure
- [ ] Within retry limits (≤3 attempts)
- [ ] Fix stays within task scope
- [ ] Clear path to resolution

**Escalate Checklist**:
- [ ] 3+ failed recovery attempts
- [ ] Requires out-of-scope changes
- [ ] Ambiguous requirements
- [ ] Unexpected complexity discovered

**Common Error Quick Fixes**:

| Error Type | Quick Check |
|-----------|-------------|
| Missing import | Search codebase for type definition |
| Null reference | Add null check or default value |
| Type mismatch | Check expected type from interface |
| File not found | Use `search_files` to locate |

## References

- Source: [`04-error-recovery.md`](../04-error-recovery.md)

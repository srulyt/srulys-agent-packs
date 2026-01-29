# Verification Patterns

## Purpose
Provide detailed verification procedures for the Agentic Verifier mode. Load this skill when performing thorough verification checks.

## When to Use
- During verification phase (Phase 4)
- When detailed check procedures are needed
- When generating verification reports

---

## Detailed Check Procedures

### Check 1: Scope Compliance

1. Read task contract for `allowed_files` and `forbidden_files`
2. Use `list_files` to enumerate modified files
3. For each modified file:
   - Verify it's in `allowed_files`
   - Verify it's not in `forbidden_files`
4. Flag any unrelated changes (files modified but not in allowed list)

### Check 2: Acceptance Criteria

For each criterion in the task contract:
1. Identify the type: code change, test, documentation, behavior
2. Find evidence:
   - Code changes: Specific file:line references
   - Tests: Test names and pass/fail status
   - Behavior: Build output, runtime verification
3. Document in report with PASS/FAIL status
4. For FAIL: Describe what's missing or incorrect

### Check 3: Build Verification

**Process:**
1. Use `read_file` first to check for obvious syntax errors
2. Execute appropriate build command:
   - .NET: `dotnet build`
   - Node.js: `npm run build` or `tsc`
   - Python: `python -m py_compile <files>`
3. Capture output for report
4. FAIL immediately on build errors (blocking issue)

**Common Build Issues:**
| Issue | Detection | Action |
|-------|-----------|--------|
| Missing import | Build error message | FAIL, document |
| Type error | Build error message | FAIL, document |
| Syntax error | Build error message | FAIL, document |
| Warning only | Warning in output | PASS with note |

### Check 4: Test Verification

**Process:**
1. Identify test commands from:
   - Plan's Testing Strategy section
   - Task contract's test requirements
   - Project conventions (.csproj, package.json)
2. Run relevant tests (not full suite if scoped):
   - .NET: `dotnet test --filter "FullyQualifiedName~<namespace>"`
   - Node.js: `npm test -- --grep "<pattern>"`
   - Python: `pytest <path> -k "<pattern>"`
3. Capture results
4. FAIL on any test failure

**Test Coverage Checks:**
- Are new code paths tested?
- Are edge cases covered?
- Are error conditions handled?

### Check 5: Quality Standards

| Standard | How to Check | Pass Criteria |
|----------|--------------|---------------|
| Naming conventions | Compare with 2-3 similar files | Names match pattern |
| Comment style | Check existing files | Comments match style |
| XML docs | Check if existing files use them | Only add if convention |
| Clean code | Review for code smells | No magic numbers, meaningful names |

### Check 6: AI Artifact Detection

Use `search_files` with these patterns:
```
// TODO.*task
// AI:
// Generated
// task-
// As per spec
// Implementing requirement
```

**DO NOT** use grep, findstr, or PowerShell commands for this.

### Check 7: Test Completeness

| Aspect | What to Check | Pass |
|--------|---------------|------|
| Unit tests | New functions have tests | Tests exist |
| Edge cases | Null, empty, boundary conditions | Covered |
| Error paths | Exception handling tested | Covered |
| Integration | Components work together | Verified |

---

## Verification Report Template

```markdown
# Verification Report: {task-id}

## Result: {PASSED|FAILED|BLOCKED}

## Task Summary
- **Task**: {title}
- **Files Modified**: {count}
- **Quality Bar**: {Standard|High|Critical}

## Acceptance Criteria Status

| # | Criterion | Status | Evidence |
|---|-----------|--------|----------|
| 1 | {criterion text} | PASS/FAIL | {file:line or test name} |
| 2 | {criterion text} | PASS/FAIL | {file:line or test name} |

## Quality Checks

| Check | Status | Notes |
|-------|--------|-------|
| Scope Compliance | PASS/FAIL | {details} |
| Build Verification | PASS/FAIL | {build output summary} |
| Test Verification | PASS/FAIL | {test results summary} |
| Code Quality | PASS/FAIL | {conventions check} |
| AI Artifacts | PASS/FAIL | {found items or "None found"} |

## Issues Found

### Issue #1: {Title}
- **Type**: {missing-test|pattern-violation|etc.}
- **Severity**: blocker|major|minor
- **File**: `path/to/file.cs`
- **Line**: 42-48
- **Description**: {what's wrong}
- **Expected**: {what should be}
- **Suggested Fix**: {how to fix}

## Recommendation

{Next step: PASS → proceed | FAIL → create Q-task | BLOCKED → escalate}
```

---

## Server Lifecycle for Verification

When verification requires a running server:

### Complete Lifecycle

1. **START** (background):
   - Windows: `start "VerifyServer" cmd /c "npm run dev"`
   - Unix: `nohup npm run dev > server.log 2>&1 &`

2. **WAIT** (with timeout):
   ```cmd
   timeout /t 5 /nobreak >nul
   curl -s http://localhost:3000 >nul 2>&1
   ```

3. **TEST**: Run verification checks against running server

4. **TERMINATE** (guaranteed cleanup):
   - Windows: `taskkill /FI "WINDOWTITLE eq VerifyServer*" /F`
   - Unix: `kill $(cat server.pid)`

5. **RECOVER** (if needed):
   - Windows: `taskkill /IM node.exe /F /T`
   - Unix: `lsof -ti:3000 | xargs kill -9`

### Preference Order

1. Build-only verification (no server) - **PREFERRED**
2. Unit tests (no server)
3. Server verification (only when necessary)
4. **Always clean up servers**

---

## Quality Bar Guidance

### Standard (Default)
- Build passes
- All acceptance criteria met
- No AI artifacts
- Conventions followed

### High (Public APIs, Breaking Changes)
All of Standard plus:
- Integration tests pass
- API documentation complete
- Backward compatibility verified (or breaking change documented)
- Code review checklist complete

### Critical (Security, Data Integrity)
All of High plus:
- Security review checklist
- Data validation verified
- Rollback plan documented
- Error handling comprehensive

---

## Anti-Patterns

- ❌ Modifying any source code (verifier is READ-ONLY)
- ❌ Using shell commands for file reading (use built-in tools)
- ❌ Skipping build verification
- ❌ Approving with failing tests
- ❌ Not documenting issues clearly
- ❌ Leaving servers running after verification

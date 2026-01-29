---
name: cleanup-patterns
description: Provide detailed cleanup procedures for the Agentic Cleanup mode. Load this skill during cleanup phase (Phase 5), when removing AI artifacts and debug code, or when preparing code for PR.
---

# Cleanup Patterns

## Purpose
Provide detailed cleanup procedures for the Agentic Cleanup mode. Load this skill when performing post-implementation cleanup.

## When to Use
- During cleanup phase (Phase 5)
- When removing AI artifacts and debug code
- When preparing code for PR

---

## Category Procedures

### Category 1: Debug Code Removal

**Patterns to Search:**
```
console.log
Console.WriteLine
print(
System.out.println
Debug.Log
logger.debug
// DEBUG
/* DEBUG */
// TODO: remove
// TEMP
```

**Process:**
1. Use `search_files` to find debug statements
2. Review each occurrence in context
3. Remove if:
   - Clearly debug output (not production logging)
   - Contains "debug", "test", "temp" in message
   - Logs sensitive data
4. Keep if:
   - Production logging (proper log levels)
   - Error/warning logging
   - Audit requirements

### Category 2: Import Cleanup

**By Language:**

| Language | Tool/Command | Notes |
|----------|--------------|-------|
| C# | Check for gray/unused using | Remove unused |
| TypeScript | `tsc --noEmit` | Warns on unused |
| Python | pyflakes, pylint | Flags unused |
| Java | IDE or checkstyle | Flags unused |

**Process:**
1. Build project to identify unused imports
2. Remove clearly unused imports
3. Sort imports per project convention:
   - Check 2-3 similar files for import order
   - Match existing grouping style

### Category 3: Formatting Consistency

**Checks:**
| Issue | Detection | Fix |
|-------|-----------|-----|
| Trailing whitespace | `search_files` for ` $` | Remove trailing spaces |
| Missing EOF newline | Read last char | Add newline |
| Mixed indentation | Visual inspection | Match file convention |
| Inconsistent bracing | Visual inspection | Match file convention |

**Process:**
1. Check each modified file for formatting issues
2. Fix ONLY in modified files (not global reformatting)
3. Match existing file conventions

### Category 4: Code Hygiene

**Commented-Out Code:**
```
// Old implementation
// var x = ...
/* 
   Removed code block
*/
```

- Remove if clearly obsolete
- Convert to tech debt if might be needed

**TODO Conversion:**
```
// TODO: implement error handling
// FIXME: performance issue
// HACK: temporary workaround
```

- Extract to tech debt log with context
- Remove from code

### Category 5: SQL Cleanup

**Patterns:**
| Pattern | Action |
|---------|--------|
| `PRINT 'Debug:'` | Remove |
| `-- SELECT * FROM` | Remove (commented query) |
| `NOLOCK` for debugging | Revert if not production hint |
| Temp table without cleanup | Add `DROP TABLE IF EXISTS` |

### Category 6: Scope Violation Cleanup

**Detection Process:**
1. Run `git diff HEAD~N` (N = commits in run)
2. For each changed hunk, verify against task contracts
3. Flag changes not traceable to requirements

**Reversion Process:**
- Entire files: `git checkout HEAD~N -- <file>`
- Specific hunks: Use `apply_diff` to restore original

**Common Violations:**
| Type | Example | Action |
|------|---------|--------|
| Rename not in scope | `userId` → `customerId` | Revert |
| Added XML docs | `/// <summary>` on existing | Revert |
| Reformatted file | Changed indentation | Revert |
| Extracted method | "Refactored for readability" | Revert |
| Import reorder | Reorganized imports | Revert |

---

## AI Slop Detection Patterns

### Task Reference Comments
```regex
// TODO.*task[ -]?\d
// Implementing.*task
// Added for task
// As per (spec|specification|requirement)
// Per the (PRD|plan|spec)
// According to (requirement|spec)
```

### Over-Explanatory Comments
```
// This function adds two numbers
function add(a, b) { return a + b; }

// Initialize the variable to zero
let count = 0;

// Check if the value is null
if (value === null) { ... }
```

**Detection:**
- Comment restates what code obviously does
- Comment explains basic language constructs
- Every line has an inline comment

### AI-Style Code Patterns

**Unnecessarily Verbose Names:**
```
// AI tends to create:
const userAccountInformationData = ...
const isValidUserInputFromForm = ...

// Prefer existing codebase style:
const accountInfo = ...
const isValidInput = ...
```

**Over-Abstraction:**
```
// AI tends to create "extensible" code:
interface IUserProcessorStrategy { ... }
class DefaultUserProcessor implements IUserProcessorStrategy { ... }

// When simple function suffices:
function processUser(user) { ... }
```

**Redundant Null Checks:**
```
// AI adds defensive checks not matching codebase:
if (user != null && user.name != null && user.name.length > 0) { ... }

// If codebase assumes valid inputs:
if (user.name.length > 0) { ... }
```

---

## Safeguards Checklist

### Before ANY Deletion

- [ ] File is NOT in protected list:
  - `*.csproj`, `*.sln`
  - `package.json`, `package-lock.json`
  - `.gitignore`, `.env*`
  - `Dockerfile`, `docker-compose*.yml`
  - `*.lock`, `yarn.lock`

- [ ] File was created/modified during this run
- [ ] If deleting >5 files, escalate for confirmation
- [ ] If deleting directory, escalate for confirmation

### Protected Files (Never Delete)
```yaml
never_delete:
  - "*.csproj"
  - "*.sln"
  - "package.json"
  - "package-lock.json"
  - ".gitignore"
  - "*.lock"
  - "Dockerfile"
  - "docker-compose*.yml"
  - "tsconfig.json"
  - ".env*"
  - "*.config.js"
  - "*.config.ts"
```

---

## Dry Run Protocol

### Step 1: Plan Changes
```markdown
Cleanup Plan:
- DELETE: [list files to delete]
- MODIFY: [list files to modify with summary]
- REVERT: [list changes to revert]
```

### Step 2: Verify Plan
- Check no protected files in DELETE list
- Check all MODIFY files are in run scope
- Check REVERT changes have clear justification

### Step 3: Execute
- Apply changes in order: REVERT → DELETE → MODIFY
- Verify build after each major change
- Stop and escalate if build fails

### Step 4: Verify
- Run full build
- Run tests
- Check for lint errors

### Step 5: Document
```markdown
Cleanup Report:
- Files cleaned: {count}
- Debug statements removed: {count}
- Imports cleaned: {count}
- AI slop removed: {count}
- Scope violations reverted: {count}
- Tech debt discovered: {count}
```

---

## Tech Debt Extraction

When cleanup reveals issues outside scope, document:

```markdown
## Tech Debt Item

**Location**: `path/to/file.cs:42`
**Type**: {code-smell|missing-test|performance|security}
**Priority**: {low|medium|high}

**Description**:
{What the issue is}

**Current State**:
{How it exists now}

**Recommended Fix**:
{What should be done}

**Effort Estimate**: {small|medium|large}
```

Write to: `.agent-memory/runs/<run-id>/debt/discovered.md`

---

## Anti-Patterns

- ❌ Global reformatting (only touch run-modified files)
- ❌ Fixing code quality issues (cleanup, not improvement)
- ❌ Deleting protected files
- ❌ Making functional changes
- ❌ Skipping build verification after cleanup
- ❌ Not documenting what was removed

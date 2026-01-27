# Tool Guidance Per Agent

This document specifies which tools each agent should use and avoid.

---

## Tool Priority Hierarchy (MANDATORY)

Before using any tool, follow this decision cascade:

### For File Reading/Searching
```
PRIORITY ORDER:
1. read_file         ← FIRST CHOICE for reading file contents
2. search_files      ← For finding patterns across files
3. list_files        ← For directory structure discovery
4. execute_command   ← LAST RESORT only (see prohibitions)
```

### For File Modification
```
PRIORITY ORDER:
1. apply_diff        ← FIRST CHOICE for surgical edits
2. write_to_file     ← For new files or complete rewrites
3. execute_command   ← PROHIBITED for file modifications
```

### Decision Checklist (ask before execute_command)

Before using `execute_command`, you MUST answer YES to ALL:

- [ ] Is this a build/test/compilation command? (not file read/write)
- [ ] Does no built-in tool exist for this operation?
- [ ] Is this NOT achievable with read_file, search_files, or list_files?

If ANY answer is NO → Use the built-in tool instead.

---

## Tool Access Matrix

| Agent | Primary Tools | Restricted Tools | PROHIBITED |
|-------|--------------|------------------|------------|
| Orchestrator | `new_task`, `read_file`, `list_files` | - | `write_to_file`, `apply_diff` |
| Spec Writer | `read_file`, `write_to_file` | - | `execute_command` |
| Planner | `read_file`, `search_files`, `write_to_file` | - | `execute_command` |
| Task Breaker | `read_file`, `write_to_file` | - | `execute_command` |
| Executor | `read_file`, `apply_diff`, `write_to_file` | `execute_command` (build/test only) | PowerShell for file ops |
| **Verifier** | `read_file`, `search_files`, `list_files` | `execute_command` (build/test only) | **PowerShell for reading files** |
| Cleanup | `read_file`, `apply_diff` | `execute_command` (cleanup scripts) | - |
| PR Prep | `read_file`, `write_to_file` | `execute_command` (verification) | - |
| Memory Consolidator | `read_file`, `write_to_file` | - | `execute_command` |

### Restricted vs Prohibited

- **Restricted**: Can use, but only for specific purposes noted
- **PROHIBITED**: Never use for any reason

---

## Command Execution Prohibitions

### NEVER Use execute_command For:

| Operation | Use Instead | Why |
|-----------|-------------|-----|
| Reading file contents | `read_file` | PowerShell can fail, freeze, or return wrong encoding |
| Finding files by name | `list_files` | Built-in handles recursion and filtering |
| Searching file contents | `search_files` | Built-in regex is more reliable |
| Checking if file exists | `read_file` (will error if missing) | Simpler, no shell dependency |
| Getting directory listing | `list_files` | Cross-platform, consistent format |
| Creating/modifying files | `write_to_file`, `apply_diff` | Atomic operations, tracked by system |

### ONLY Use execute_command For:

| Operation | Example | Notes |
|-----------|---------|-------|
| Building projects | `dotnet build`, `npm run build` | Required for compilation |
| Running tests | `dotnet test`, `npm test` | Required for verification |
| Package installation | `npm install`, `pip install` | Required for setup |
| Git operations | `git status`, `git diff` | When needed for verification |
| Project scaffolding | `dotnet new`, `npm init` | Bootstrap tasks only |

### Verifier-Specific Prohibition

The Verifier agent should NEVER use `execute_command` for:
- Checking file contents (use `read_file`)
- Finding patterns in code (use `search_files`)
- Listing directories (use `list_files`)

The Verifier MAY use `execute_command` ONLY for:
- Running build commands
- Running test commands
- Checking git status (if needed)

---

## Tool Selection Guidelines

### When to use `apply_diff` vs `write_to_file`

```yaml
use_apply_diff:
  when:
    - Modifying existing files
    - Changes are surgical (< 50% of file)
    - Need to preserve unchanged content
  benefits:
    - Smaller context usage
    - Clearer change intent
    - Better for review

use_write_to_file:
  when:
    - Creating new files
    - Complete file rewrite needed
    - File is small (< 50 lines)
  caution:
    - Verify complete content
    - Don't truncate accidentally
```

### Search Strategy

```yaml
search_strategy:
  1_list_first:
    tool: list_files
    purpose: "Understand directory structure"
  
  2_targeted_search:
    tool: search_files
    purpose: "Find specific patterns"
    tip: "Use precise regex, avoid broad patterns"
  
  3_read_relevant:
    tool: read_file
    purpose: "Get context for specific files"
    tip: "Request line ranges for large files"
```

---

## Agent-Specific Tool Patterns

### Executor Tool Patterns

```yaml
read_pattern:
  for_small_files: "Read entire file"
  for_large_files:
    1: "list_code_definition_names first"
    2: "search_files for specific method"
    3: "read_file with line range"

edit_pattern:
  for_small_edits: "apply_diff with minimal context"
  for_large_edits: "Consider multiple apply_diff calls"
  avoid: "Full file write for small changes"

verify_pattern:
  after_edit: "Re-read changed section"
  build_check: "execute_command with build command"
```

### Orchestrator Tool Patterns

```yaml
delegation_pattern:
  always: "new_task with full context"
  context_gathering:
    - "list_files to find relevant paths"
    - "read_file for summaries only"
    - "Never read large files directly"

progress_tracking:
  - "read_file on event logs"
  - "write_to_file for status updates"
```

# Tool Guidance Per Agent

## Required Skills

Load this skill for detailed patterns:
- **`file-editing-patterns`** - Tool selection, diff techniques, verification

---

## Global Tool Policies

### Tool Priority Hierarchy (MANDATORY)

Before using any tool, follow this decision cascade:

**For File Reading/Searching:**
```
1. read_file         ← FIRST CHOICE for reading contents
2. search_files      ← For finding patterns across files
3. list_files        ← For directory structure discovery
4. execute_command   ← LAST RESORT only
```

**For File Modification:**
```
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
| Verifier | `read_file`, `search_files`, `list_files` | `execute_command` (build/test only) | PowerShell for reading |
| Cleanup | `read_file`, `apply_diff` | `execute_command` (cleanup scripts) | - |
| PR Prep | `read_file`, `write_to_file` | `execute_command` (verification) | - |
| Memory Consolidator | `read_file`, `write_to_file` | - | `execute_command` |

---

## Command Execution Prohibitions

### NEVER Use execute_command For:

| Operation | Use Instead |
|-----------|-------------|
| Reading file contents | `read_file` |
| Finding files by name | `list_files` |
| Searching file contents | `search_files` |
| Checking if file exists | `read_file` (will error if missing) |
| Getting directory listing | `list_files` |
| Creating/modifying files | `write_to_file`, `apply_diff` |

### ONLY Use execute_command For:

| Operation | Example |
|-----------|---------|
| Building projects | `dotnet build`, `npm run build` |
| Running tests | `dotnet test`, `npm test` |
| Package installation | `npm install`, `pip install` |
| Git operations | `git status`, `git diff` |
| Project scaffolding | `dotnet new`, `npm init` |

---

## Quick Reference

### Tool Selection Summary

| File Size | Read Strategy | Edit Strategy |
|-----------|---------------|---------------|
| < 50 lines | Full read | `write_to_file` OK |
| < 200 lines | Full read | `apply_diff` preferred |
| 200-500 lines | Targeted read | `apply_diff` required |
| > 500 lines | Surgical access | `apply_diff` only |

> See `file-editing-patterns` skill for detailed editing strategies and multi-edit handling.

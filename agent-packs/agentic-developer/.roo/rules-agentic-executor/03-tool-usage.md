# Executor Mode: Tool Usage Patterns

## Required Skills

Load these skills for detailed patterns:
- **`file-editing-patterns`** - Tool selection, diff techniques, large file editing
- **`server-lifecycle`** - Long-running process management, background launch, cleanup
- **`context-management`** - Context budget and file reading strategies

---

## Executor-Specific Tool Rules

### Tool Selection Matrix

| Need | Use | Never Use |
|------|-----|-----------|
| Read file | `read_file` | `cat`, `type`, `Get-Content` |
| Find text | `search_files` | `grep`, `findstr` |
| List files | `list_files` | `ls`, `dir` |
| Edit file | `apply_diff` | PowerShell commands |
| Create file | `write_to_file` | `echo >`, redirects |
| Build/test | `execute_command` ✓ | - |

### Executor execute_command Scope

**Allowed**:
- Build commands (`dotnet build`, `npm run build`)
- Test commands (`dotnet test`, `npm test`)
- Package installation (`npm install`, `pip install`)
- Git operations
- Dev servers (with full lifecycle pattern)

**Prohibited**:
- File read/write operations
- Directory listing
- Text searching

### Verification After Edits

```yaml
post_edit_verification:
  1_re_read: "Read modified section to confirm"
  2_build_check: "Run build if applicable"
  3_test_run: "Run relevant tests"
```

---

## Quick Reference

### Large File Protocol

1. **Index First**: `list_code_definition_names`
2. **Targeted Search**: `search_files` with precise regex
3. **Surgical Read**: Request specific line ranges
4. **Minimal Edit**: `apply_diff` with exact matches

> See `file-editing-patterns` skill for detailed editing strategies.

### Long-Running Process Checklist

```
[ ] 1. START in background
[ ] 2. WAIT with timeout  
[ ] 3. TEST while running
[ ] 4. TERMINATE (guaranteed)
[ ] 5. RECOVER if needed
```

> See `server-lifecycle` skill for complete lifecycle patterns.

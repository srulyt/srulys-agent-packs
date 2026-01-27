# Command Execution Policy

## Required Skills

Load this skill for detailed patterns:
- **`server-lifecycle`** - Process management, background launch, health checks, termination

---

## Global Command Policies

This policy applies to ALL agents in the Agentic Developer pack.

### ⚠️ AGENTIC CONTINUITY PRINCIPLE

> **Your terminal process must NEVER get stuck.**
>
> Every command must either:
> 1. Complete quickly (< 30 seconds), OR
> 2. Run in background with GUARANTEED cleanup

### Golden Rule

> **Use execute_command as a LAST RESORT, not a first choice.**

Built-in tools are more reliable, cross-platform, and tracked by Roo Code.

---

## Tool Selection Matrix

| Need | Use | Never Use |
|------|-----|-----------|
| Read file | `read_file` | `cat`, `type`, `Get-Content` |
| Find text | `search_files` | `grep`, `findstr`, `Select-String` |
| List directory | `list_files` | `ls`, `dir`, `Get-ChildItem` |
| Create/edit file | `write_to_file`, `apply_diff` | `echo >`, `New-Item` |
| Build/test | `execute_command` ✓ | - |
| Run server | `execute_command` + FULL LIFECYCLE | - |

---

## Agent-Specific Permissions

| Agent | execute_command Allowed For |
|-------|----------------------------|
| Orchestrator | ❌ Never |
| Spec Writer | ❌ Never |
| Planner | ❌ Never |
| Task Breaker | ❌ Never |
| Executor | Build, test, package install, git, dev servers (with lifecycle) |
| Verifier | Build, test, git status ONLY |
| Cleanup | Cleanup scripts |
| PR Prep | Verification commands |
| Memory Consolidator | ❌ Never |

---

## Quick Reference

### Long-Running Process Detection

A process is "long-running" if:
- Starts a server
- Watches for file changes
- Never exits naturally
- Contains: `dev`, `watch`, `serve`, `hot`, `start`

**ALWAYS use background pattern for these.**

### Server Lifecycle Checklist

```
[ ] 1. START in background (start "Name" cmd /c "...")
[ ] 2. WAIT with timeout (timeout /t 5)
[ ] 3. TEST while running (curl, tests)
[ ] 4. TERMINATE guaranteed (taskkill /FI "WINDOWTITLE eq Name*" /F)
[ ] 5. RECOVER if needed (taskkill /IM node.exe /F /T)
```

### Bootstrap Tasks

- Do NOT run dev servers during bootstrap
- Document dev commands in README for user
- Use `npm run build` to verify, not `npm run dev`

> See `server-lifecycle` skill for complete lifecycle patterns and recovery procedures.

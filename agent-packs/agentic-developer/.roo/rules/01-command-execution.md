# Command Execution Policy

This policy applies to ALL agents in the Agentic Developer pack.

---

## ⚠️ AGENTIC CONTINUITY PRINCIPLE

> **Your terminal process must NEVER get stuck.**
>
> Every command must either:
> 1. Complete quickly (< 30 seconds), OR
> 2. Run in background with GUARANTEED cleanup

**This is the TOP PRIORITY rule.** A stuck agent is useless.

---

## Golden Rule

> **Use execute_command as a LAST RESORT, not a first choice.**

Built-in tools (`read_file`, `write_to_file`, `search_files`, `list_files`, `apply_diff`) are:
- More reliable
- Cross-platform
- Tracked by Roo Code
- Less prone to encoding/shell issues

---

## Tool Selection Flowchart

```
Need to READ a file?
  └─→ Use read_file ✓

Need to FIND text in files?
  └─→ Use search_files ✓

Need to SEE directory contents?
  └─→ Use list_files ✓

Need to CREATE/EDIT a file?
  └─→ Use write_to_file or apply_diff ✓

Need to BUILD or TEST?
  └─→ Use execute_command ✓ (short-lived OK)

Need to RUN A SERVER?
  └─→ Use execute_command with FULL LIFECYCLE ✓
      (START → WAIT → USE → TERMINATE → RECOVER)
```

---

## Prohibited Patterns

### Never Use PowerShell/CMD For:

```yaml
prohibited:
  file_reading:
    - "type filename.txt"
    - "cat filename.txt"
    - "Get-Content filename.txt"
    alternative: "read_file"
  
  file_searching:
    - "findstr /s pattern *.*"
    - "grep -r pattern ."
    - "Select-String -Pattern pattern"
    alternative: "search_files"
  
  directory_listing:
    - "dir /s"
    - "ls -la"
    - "Get-ChildItem -Recurse"
    alternative: "list_files"
  
  file_creation:
    - "echo content > file.txt"
    - "New-Item -Path file.txt"
    alternative: "write_to_file"
```

---

## Complete Server Lifecycle (MANDATORY)

When running ANY long-running process, you MUST follow this complete lifecycle.

### Quick Reference Card

```
┌─────────────────────────────────────────────────────────────────┐
│                    SERVER LIFECYCLE CHECKLIST                   │
├─────────────────────────────────────────────────────────────────┤
│ [ ] 1. START in background (never blocks terminal)             │
│       Windows: start "Name" cmd /c "command"                   │
│       Unix:    nohup command & echo $! > pid                   │
├─────────────────────────────────────────────────────────────────┤
│ [ ] 2. WAIT for ready (with timeout, never infinite)           │
│       timeout /t 5 /nobreak >nul                               │
│       curl -s http://localhost:PORT                            │
├─────────────────────────────────────────────────────────────────┤
│ [ ] 3. TEST/USE while running                                  │
│       curl, test commands, read_file for logs                  │
├─────────────────────────────────────────────────────────────────┤
│ [ ] 4. TERMINATE (guaranteed cleanup)                          │
│       Windows: taskkill /FI "WINDOWTITLE eq Name*" /F          │
│       Unix:    kill $(cat pid); rm pid                         │
├─────────────────────────────────────────────────────────────────┤
│ [ ] 5. RECOVER if needed                                       │
│       taskkill /IM node.exe /F /T                              │
│       lsof -ti:PORT | xargs kill -9                            │
└─────────────────────────────────────────────────────────────────┘
```

### Identification

A process is "long-running" if it:
- Starts a server
- Watches for file changes
- Never exits naturally
- Contains: `dev`, `watch`, `serve`, `hot`, `start`

### Phase 1: START (Background)

**Windows:**
```cmd
:: ALWAYS use 'start' with a window title for easy cleanup
start "DevServer" cmd /c "npm run dev"
```

**Unix/Mac:**
```bash
nohup npm run dev > server.log 2>&1 &
echo $! > server.pid
```

### Phase 2: WAIT (With Timeout)

```cmd
:: Never wait forever - always use timeout
timeout /t 5 /nobreak >nul
curl -s http://localhost:3000 >nul 2>&1 || echo "Warning: Not ready"
```

### Phase 3: USE

```cmd
:: Test endpoints, run commands while server runs
curl -s http://localhost:3000/api/test
npm run e2e
```

### Phase 4: TERMINATE (ALWAYS DO THIS)

```cmd
:: By window title (cleanest)
taskkill /FI "WINDOWTITLE eq DevServer*" /F

:: By port (if title unknown)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :3000 ^| findstr LISTENING') do taskkill /PID %%a /F
```

### Phase 5: RECOVER (When Needed)

```cmd
:: If process won't die
taskkill /IM node.exe /F /T

:: If port stuck
timeout /t 3 >nul
:: then retry
```

---

## Edge Case Handling

### What If Start Command Hangs?

**Prevention:** ALWAYS use background pattern. Never run long-running commands directly.

**If Stuck:**
```
1. Agent should report inability to continue
2. User must Ctrl+C or restart terminal
3. Cleanup: taskkill /IM node.exe /F /T
```

### What If Kill Fails?

**Escalation Ladder:**
```cmd
:: Level 1: By title
taskkill /FI "WINDOWTITLE eq DevServer*" /F

:: Level 2: By port
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :3000 ^| findstr LISTENING') do taskkill /PID %%a /F

:: Level 3: By process name with tree
taskkill /IM node.exe /F /T

:: Level 4: Nuclear (wmic)
wmic process where "name='node.exe'" delete
```

### What If Port Won't Free?

```cmd
:: Wait for OS cleanup
timeout /t 5 >nul

:: Check again
netstat -an | findstr :3000 | findstr LISTENING

:: If still stuck, try different port or wait longer
```

### What If Multiple Orphaned Processes?

```cmd
:: Clean sweep by port range (common dev ports)
for %%p in (3000 3001 5000 5001 5173 8080 8081) do (
  for /f "tokens=5" %%a in ('netstat -aon ^| findstr :%%p ^| findstr LISTENING') do (
    echo Killing PID %%a on port %%p
    taskkill /PID %%a /F 2>nul
  )
)
```

---

## Agent-Specific Overrides

### Verifier

Verifier has the MOST restricted execute_command usage:

```yaml
allowed:
  - "dotnet build"
  - "dotnet test"
  - "npm run build"
  - "npm test"
  - "git status"
  - "git diff"
  - Server lifecycle (START→TEST→TERMINATE) for integration verification

prohibited:
  - ANY file reading command
  - ANY directory listing command
  - ANY search command
  - Long-running processes WITHOUT cleanup plan
```

### Executor

Executor has broader permissions but must still prefer built-in tools:

```yaml
allowed:
  - Build commands
  - Test commands
  - Package installation
  - Dev servers (with FULL lifecycle)
  - Git operations

prefer_builtin:
  - File reading → read_file
  - File searching → search_files
  - Directory listing → list_files

required_for_servers:
  - Use window titles for cleanup
  - Always have termination command ready
  - Never leave servers running after task
```

### Bootstrap Tasks

Bootstrap tasks may use more execute_command but should:
- Still prefer built-in tools for file operations
- Never run long-running processes without full lifecycle
- Document commands in README rather than running dev servers
- If server needed, use complete lifecycle with guaranteed cleanup

# Server Lifecycle Management

## Purpose
Manage long-running processes (dev servers, watchers) safely to prevent terminal blocking and ensure guaranteed cleanup.

## When to Use
- Before starting any dev server (`npm run dev`, `dotnet watch`, etc.)
- Before any command that won't exit naturally
- When managing processes that open ports
- When commands contain: `dev`, `watch`, `serve`, `hot`, `start`

## Core Patterns

### Pattern 1: Process Classification

Classify processes before execution.

**When**: Before any `execute_command`
**Do**: Determine process category

| Category | Examples | Handling |
|----------|----------|----------|
| **Short-lived** | `npm install`, `dotnet build`, `git status` | Run normally |
| **Long-running** | `npm run dev`, `dotnet watch`, `vite` | **MUST use full lifecycle** |
| **Interactive** | `npm init`, prompts | Use `-y` or default flags |

**Detection**: Process is long-running if it:
- Starts a server
- Watches for file changes
- Opens a port (localhost:xxxx)
- Contains keywords: `dev`, `watch`, `serve`, `hot`, `start`
- Never exits naturally

### Pattern 2: Full Lifecycle Protocol

Every long-running process follows 5 phases.

**When**: Starting ANY long-running process
**Do**: Execute ALL phases in order

```
┌─────────────────────────────────────────────────────────────────┐
│                    SERVER LIFECYCLE CHECKLIST                   │
├─────────────────────────────────────────────────────────────────┤
│ [ ] 1. START in background                                      │
│       Windows: start "Name" cmd /c "command"                   │
│       Unix:    nohup command & echo $! > pid                   │
├─────────────────────────────────────────────────────────────────┤
│ [ ] 2. WAIT with timeout                                        │
│       timeout /t 5 /nobreak >nul && curl localhost:PORT        │
├─────────────────────────────────────────────────────────────────┤
│ [ ] 3. TEST while running                                       │
│       curl, test commands, read_file for logs                  │
├─────────────────────────────────────────────────────────────────┤
│ [ ] 4. TERMINATE (guaranteed)                                   │
│       Windows: taskkill /FI "WINDOWTITLE eq Name*" /F          │
│       Unix:    kill $(cat pid); rm pid                         │
├─────────────────────────────────────────────────────────────────┤
│ [ ] 5. RECOVER if needed                                        │
│       taskkill /IM node.exe /F /T                              │
│       lsof -ti:PORT | xargs kill -9                            │
└─────────────────────────────────────────────────────────────────┘
```

### Pattern 3: Background Launch

Start servers in background to prevent blocking.

**When**: Phase 1 - START
**Do**: Use platform-appropriate background command

**Windows:**
```cmd
:: Method 1: New window with title (RECOMMENDED - easiest to kill)
start "DevServer" cmd /c "npm run dev"

:: Method 2: With working directory
start "DevServer" cmd /c "cd /d C:\project && npm run dev"

:: Method 3: Minimized window
start /MIN "DevServer" cmd /c "npm run dev"
```

**Unix/Mac:**
```bash
# Method 1: Background with PID capture (RECOMMENDED)
nohup npm run dev > server.log 2>&1 &
echo $! > server.pid

# Method 2: Using disown
npm run dev > server.log 2>&1 &
disown

# Method 3: Using screen (if available)
screen -dmS myserver npm run dev
```

### Pattern 4: Health Check

Verify server is ready before proceeding.

**When**: Phase 2 - WAIT
**Do**: Poll with timeout

**Windows - Simple wait then check:**
```cmd
timeout /t 5 /nobreak >nul
curl -s http://localhost:3000 >nul 2>&1 && echo Server ready || echo Server not responding
```

**Windows - Polling with timeout (30s max):**
```cmd
setlocal EnableDelayedExpansion
set "ready=0"
for /L %%i in (1,1,30) do (
  curl -s http://localhost:3000 >nul 2>&1 && set "ready=1" && goto :check_done
  timeout /t 1 /nobreak >nul
)
:check_done
if "!ready!"=="0" echo WARNING: Server may not be ready after 30s
```

**Unix/Mac:**
```bash
for i in $(seq 1 30); do
  curl -s http://localhost:3000 >/dev/null && echo "Server ready" && break
  sleep 1
done
```

### Pattern 5: Graceful Termination

Terminate servers cleanly.

**When**: Phase 4 - TERMINATE
**Do**: Use the method matching how you started

**Windows - By Window Title (RECOMMENDED):**
```cmd
taskkill /FI "WINDOWTITLE eq DevServer*" /F
```

**Windows - By Port:**
```cmd
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :3000 ^| findstr LISTENING') do (
  taskkill /PID %%a /F
)
```

**Windows - By Process Name:**
```cmd
taskkill /IM node.exe /F /T
:: /T kills child processes too
```

**Unix/Mac - By PID:**
```bash
kill $(cat server.pid) 2>/dev/null
rm -f server.pid
```

**Unix/Mac - By Port:**
```bash
lsof -ti:3000 | xargs kill -9 2>/dev/null
```

### Pattern 6: Recovery Procedures

Handle common failure scenarios.

**When**: Phase 5 - RECOVER (things go wrong)
**Do**: Follow escalation ladder

#### Scenario: Process Won't Die

**Windows Escalation:**
| Level | Command |
|-------|---------|
| 1 | `taskkill /FI "WINDOWTITLE eq DevServer*" /F` |
| 2 | `for /f ... netstat ... taskkill /PID` |
| 3 | `taskkill /IM node.exe /F /T` |
| 4 | `wmic process where "name='node.exe'" delete` |

**Unix Escalation:**
```bash
# Level 1: Standard kill
kill $(cat server.pid)

# Level 2: Force kill
kill -9 $(lsof -ti:3000)

# Level 3: Pattern kill
pkill -9 -f "npm run dev"
```

#### Scenario: Port Stays Occupied

```cmd
:: Wait for OS to release port
timeout /t 5 >nul
netstat -an | findstr :3000 | findstr LISTENING
:: If still occupied, wait longer or use different port
```

#### Scenario: Multiple Orphaned Processes

```cmd
:: Windows: Kill all on common dev ports
for %%p in (3000 3001 5000 5001 5173 8080 8081) do (
  for /f "tokens=5" %%a in ('netstat -aon ^| findstr :%%p ^| findstr LISTENING') do (
    taskkill /PID %%a /F 2>nul
  )
)
```

### Pattern 7: One-Shot Server Test

Complete pattern for start-test-stop workflow.

**When**: Need to start server, run tests, then cleanup
**Do**: Use this complete script

```cmd
@echo off
:: START
start "TestServer" cmd /c "npm run dev"
timeout /t 5 /nobreak >nul

:: TEST
curl -s http://localhost:3000/health
set RESULT=%ERRORLEVEL%

:: CLEANUP (always runs)
taskkill /FI "WINDOWTITLE eq TestServer*" /F >nul 2>&1

:: RETURN result
exit /b %RESULT%
```

### Pattern 8: Build-Only Verification (Preferred)

Avoid servers when possible.

**When**: Verifying code works
**Do**: Prefer build over server

```cmd
:: PREFERRED: Build verification (no server needed)
npm run build
if %ERRORLEVEL% NEQ 0 exit /b 1

:: PREFERRED: Unit tests (no server needed)
npm test
if %ERRORLEVEL% NEQ 0 exit /b 1

:: ONLY IF NECESSARY: Integration tests with server
:: (use full lifecycle above)
```

## Anti-Patterns

- ❌ Running dev servers without background pattern
- ❌ Starting servers without termination plan
- ❌ Assuming servers will stop on their own
- ❌ Using `npm run dev` directly (blocks terminal)
- ❌ Skipping health check before testing
- ❌ Not cleaning up on task completion
- ❌ Running dev servers during bootstrap tasks

## Quick Reference

**Agentic Continuity Principle**:
> Your terminal process must NEVER get stuck. Every command must either complete quickly OR run in background with guaranteed cleanup.

**Bootstrap Tasks**:
- Do NOT run dev servers during bootstrap
- Document dev commands in README for user
- Use `npm run build` to verify, not `npm run dev`

**Terminal Blocked Recovery**:
1. Report issue via `attempt_completion`
2. User: Ctrl+C or restart terminal
3. Cleanup: `taskkill /IM node.exe /F /T`

## References

- Source: [`01-command-execution.md`](../../rules/01-command-execution.md)
- Source: [`03-tool-usage.md`](../03-tool-usage.md)

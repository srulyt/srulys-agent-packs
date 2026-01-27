# Executor Mode: Tool Usage Patterns

This document provides detailed tool usage guidance for the Executor agent.

---

## Large File Protocol

> See [02-context-boundaries.md](02-context-boundaries.md#large-file-protocol) for file size categories and access patterns.

---

## Efficient Reading Patterns

### DO: Targeted Reading

```yaml
efficient_read:
  purpose: "Understand method to modify"
  approach:
    - Search for method signature
    - Extract method + 10 line context
    - Note line numbers for edit
  tokens_used: ~500
```

### DON'T: Full File Dump

```yaml
inefficient_read:
  purpose: "Understand method to modify"
  approach:
    - Load entire 1500 line file
    - Scan through to find method
    - Edit small section
  tokens_used: ~25000  # WASTEFUL
```

---

## Efficient Editing Patterns

### DO: Surgical Replace

```yaml
efficient_edit:
  approach: "apply_diff with minimal SEARCH block"
  search_size: "5-20 lines"
  uniqueness: "Include just enough for unique match"
  tokens_used: ~300
```

### DON'T: Full File Rewrite

```yaml
inefficient_edit:
  approach: "write_to_file with entire file content"
  content_size: "1500 lines"
  reason: "Small change buried in large file"
  tokens_used: ~25000  # WASTEFUL
```

---

## Context Extraction Templates

### Method Extraction Request

```yaml
extraction_request:
  file: "src/Services/UserService.cs"
  target: "ProcessUser method"
  context_lines: 10
  include:
    - method_signature
    - method_body
    - immediate_dependencies
```

### Class Summary Request

```yaml
summary_request:
  file: "src/Services/UserService.cs"
  include:
    - class_signature
    - public_method_signatures
    - field_declarations
    - constructor_signatures
  exclude:
    - method_bodies
    - private_helper_methods
    - comments_and_docs
```

---

## Tool Selection Guide

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

## Verification After Edits

```yaml
post_edit_verification:
  1_re_read:
    action: "Read modified section"
    purpose: "Confirm edit applied correctly"
  
  2_build_check:
    action: "Run build command if applicable"
    purpose: "Catch syntax errors immediately"
  
  3_test_run:
    action: "Run relevant tests"
    purpose: "Catch logic errors early"
```

---

## Long-Running Process Handling

### ⚠️ AGENTIC CONTINUITY PRINCIPLE (TOP PRIORITY)

> **Your terminal process must NEVER get stuck. Every command you run must either complete quickly OR run in background with guaranteed cleanup.**

### The Problem

Dev servers (Vite, .NET watch, etc.) and other long-running processes:
- Never exit naturally
- Block the terminal
- Prevent further agent operations
- May require VS Code restart to recover

### Process Categories

| Category | Examples | Handling |
|----------|----------|----------|
| **Short-lived** | `npm install`, `dotnet build`, `git status` | Run normally |
| **Long-running** | `npm run dev`, `dotnet watch`, `vite` | **MUST use background + cleanup** |
| **Interactive** | `npm init -y`, prompts | Run with `-y` or default flags |

### Identifying Long-Running Processes

Assume a process is long-running if it:
- Starts a server (dev, watch, serve)
- Monitors for changes (watch, hot-reload)
- Opens a port (localhost:xxxx)
- Contains keywords: `dev`, `watch`, `serve`, `start`, `hot`

---

## Complete Server Lifecycle (MANDATORY)

Every long-running process MUST follow this complete lifecycle:

### Phase 1: START (Background Launch)

**Windows (Default):**
```cmd
:: Method 1: New window with title (RECOMMENDED - easiest to kill)
start "MyServer" cmd /c "npm run dev"

:: Method 2: With working directory
start "MyServer" cmd /c "cd /d C:\project && npm run dev"

:: Method 3: Minimized window
start /MIN "MyServer" cmd /c "npm run dev"
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

### Phase 2: WAIT FOR READY (With Timeout)

**Windows - Simple wait then check:**
```cmd
:: Wait 5 seconds for startup
timeout /t 5 /nobreak >nul
:: Check if server responds
curl -s http://localhost:3000 >nul 2>&1 && echo Server ready || echo Server not responding
```

**Windows - Polling with timeout:**
```cmd
:: Poll for up to 30 seconds
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
# Poll for up to 30 seconds
for i in $(seq 1 30); do
  curl -s http://localhost:3000 >/dev/null && echo "Server ready" && break
  sleep 1
done
```

### Phase 3: USE/TEST (While Running)

While the server runs in background:
```cmd
:: Test endpoints
curl -s http://localhost:3000/api/health

:: Run integration tests
npm test

:: Use read_file for any log checking (NOT PowerShell)
```

### Phase 4: TERMINATE (Guaranteed Cleanup)

**Windows - By Window Title (RECOMMENDED):**
```cmd
:: Kill by the title we gave it
taskkill /FI "WINDOWTITLE eq MyServer*" /F
```

**Windows - By Port:**
```cmd
:: Find and kill process on specific port
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :3000 ^| findstr LISTENING') do (
  taskkill /PID %%a /F
)
```

**Windows - By Process Name:**
```cmd
:: Kill specific process type (use with caution)
taskkill /IM node.exe /F /T
:: /T kills child processes too
```

**Windows - Nuclear Option:**
```cmd
:: Kill ALL processes on a port range (last resort)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":3[0-9][0-9][0-9] " ^| findstr LISTENING') do (
  taskkill /PID %%a /F 2>nul
)
```

**Unix/Mac - By PID:**
```bash
# Using saved PID
kill $(cat server.pid) 2>/dev/null
rm -f server.pid
```

**Unix/Mac - By Port:**
```bash
# Kill process on port 3000
lsof -ti:3000 | xargs kill -9 2>/dev/null
```

**Unix/Mac - By Screen Session:**
```bash
screen -S myserver -X quit
```

### Phase 5: RECOVERY (When Things Go Wrong)

#### Scenario: Start Command Hangs

```cmd
:: PREVENTION: Always use background start
:: NEVER run long-running commands directly

:: If somehow stuck, user must:
:: 1. Press Ctrl+C
:: 2. Or close terminal
:: 3. Then cleanup orphaned processes
```

#### Scenario: Process Won't Die

**Windows:**
```cmd
:: Force with /F flag
taskkill /IM node.exe /F /T

:: If that fails, use PID directly
taskkill /PID 12345 /F /T

:: If THAT fails, use wmic
wmic process where "name='node.exe'" delete
```

**Unix/Mac:**
```bash
# Use SIGKILL (-9)
kill -9 $(lsof -ti:3000)

# If that fails
pkill -9 -f "npm run dev"
```

#### Scenario: Port Stays Occupied After Kill

```cmd
:: Wait for OS to release port
timeout /t 3 /nobreak >nul

:: Verify port is free
netstat -an | findstr :3000 | findstr LISTENING
:: If still occupied, wait longer or use different port
```

#### Scenario: Multiple Orphaned Servers

```cmd
:: Kill all node processes (careful in shared environments)
taskkill /IM node.exe /F /T

:: Kill all dotnet processes
taskkill /IM dotnet.exe /F /T

:: Better: Kill by specific ports
for %%p in (3000 5000 5173 8080) do (
  for /f "tokens=5" %%a in ('netstat -aon ^| findstr :%%p ^| findstr LISTENING') do (
    taskkill /PID %%a /F 2>nul
  )
)
```

---

## Safe Execution Patterns

### Pattern: One-Shot Server Test

When you need to start a server, test, and stop:

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

### Pattern: Build-Only Verification (PREFERRED)

When possible, avoid servers entirely:

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

### Bootstrap Task Specifics

For bootstrap tasks that might need dev servers:

1. **Do NOT run dev servers during bootstrap**
   - Bootstrap should only create files and install dependencies
   - Document the dev command in README for user to run manually

2. **For `bootstrap-verify` tasks:**
   - Run `npm run build` (short-lived) to verify compilation
   - Do NOT run `npm run dev` (long-running)
   - If server test is critical, use full lifecycle with cleanup

---

## Error Recovery Protocol

If terminal becomes blocked:
1. Report the issue via `attempt_completion`
2. Note that terminal may need manual intervention
3. Suggest user run: `Ctrl+C` or restart terminal
4. Include cleanup commands for orphaned processes

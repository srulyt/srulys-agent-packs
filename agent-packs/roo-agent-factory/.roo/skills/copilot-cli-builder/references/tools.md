# Copilot CLI Tools Reference

Complete reference of all tools available in GitHub Copilot CLI.

> **Note:** This documents the actual tools available in Copilot CLI. Tool aliases (like `read`, `edit`, `search`) are used when configuring custom agent permissions, not when the agent is executing. See [Tool Aliases](#tool-aliases-for-custom-agents) section for agent configuration.

---

## File System Tools

### view

Read file or directory contents.

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `path` | string | Yes | Absolute path to file/directory |
| `view_range` | [start, end] | No | Line range (1-indexed, -1 for end) |
| `forceReadLargeFiles` | boolean | No | Skip large file size check |

**Behavior:**
- Files: Returns content with line numbers prefixed
- Directories: Lists contents up to 2 levels deep
- Images: Returns base64-encoded data

**Example:**
```
view path="C:\project\src\app.js"
view path="C:\project\src\app.js" view_range=[1, 50]
```

---

### create

Create a new file.

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `path` | string | Yes | Absolute path (must not exist) |
| `file_text` | string | No | File content |

**Constraints:**
- File must NOT already exist
- Parent directories must exist
- Path must be absolute

---

### edit

Replace text in existing file.

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `path` | string | Yes | Absolute path (must exist) |
| `old_str` | string | Yes | Exact text to replace (must be unique) |
| `new_str` | string | No | Replacement text |

**Behavior:**
- Replaces exactly ONE occurrence
- `old_str` must match file content exactly (including whitespace)
- Multiple edits to same file can be batched in one response

**Best Practices:**
- Include enough context in `old_str` to ensure uniqueness
- Preserve leading/trailing whitespace from original

---

### glob

Find files by name pattern.

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `pattern` | string | Yes | Glob pattern (e.g., `**/*.ts`) |
| `path` | string | No | Directory to search (default: cwd) |

**Pattern Examples:**
- `**/*.js` - All JS files recursively
- `src/**/*.ts` - TS files in src
- `*.{ts,tsx}` - TS and TSX in current dir

---

### grep

Search file contents (ripgrep-based).

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `pattern` | string | Yes | Regex pattern |
| `path` | string | No | Directory to search |
| `glob` | string | No | File filter (e.g., `*.js`) |
| `type` | string | No | File type filter (e.g., `js`, `py`) |
| `output_mode` | string | No | `files_with_matches` (default), `content`, `count` |
| `multiline` | boolean | No | Enable cross-line patterns |
| `head_limit` | number | No | Limit output to first N results |
| `-i` | boolean | No | Case insensitive |
| `-n` | boolean | No | Show line numbers (with `content` mode) |
| `-A`, `-B`, `-C` | number | No | Context lines after/before/around |

**Example:**
```
grep pattern="function handleSubmit" glob="*.tsx" output_mode="content" -n=true
```

---

## Execution Tools

### powershell

Run shell commands. This is the primary execution tool on all platforms.

> **Note:** On Windows, this runs PowerShell. On macOS/Linux, commands are executed in the appropriate shell. Always use `powershell` as the tool name regardless of platform.

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `command` | string | Yes | Command to execute |
| `description` | string | Yes | Brief description (max 100 chars) |
| `mode` | string | No | `sync` (default) or `async` |
| `initial_wait` | number | No | Seconds to wait (30-600, default 30) |
| `shellId` | string | No | Session identifier for persistence |
| `detach` | boolean | No | Keep running after session ends (async only) |

**Modes:**
- `sync`: Wait for completion, returns output
- `async`: Run in background, use `read_powershell`/`write_powershell` for I/O

**Best Practices:**
- Use `&&` to chain dependent commands
- Disable pagers: `git --no-pager`
- Increase `initial_wait` for long operations (builds, tests)
- Use `detach: true` for servers/daemons that must persist

**Example:**
```
powershell command="npm run build && npm test" initial_wait=120
```

---

### read_powershell

Read output from async command.

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `shellId` | string | Yes | Session ID from powershell call |
| `delay` | number | No | Seconds to wait before reading |

---

### write_powershell

Send input to async command.

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `shellId` | string | Yes | Session ID |
| `input` | string | Yes | Text or keys: `{up}`, `{down}`, `{enter}`, `{left}`, `{right}`, `{backspace}` |
| `delay` | number | No | Seconds to wait after sending |

---

### stop_powershell

Terminate a PowerShell session.

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `shellId` | string | Yes | Session ID to stop |

---

### list_powershell

List all active PowerShell sessions.

**Parameters:** None required.

**Returns:** Information about running sessions including shellId, command, mode, PID, status, and whether there is unread output.

---

## Web Tools

### web_fetch

Fetch URL content.

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `url` | string | Yes | URL to fetch |
| `raw` | boolean | No | Return raw HTML (default: markdown) |
| `max_length` | number | No | Max chars (default: 5000, max: 20000) |
| `start_index` | number | No | Pagination offset |

---

### web_search

AI-powered web search.

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | Yes | Natural language question |

**Returns:** AI-generated answer with citations.

---

## Agent/Task Tools

### task

Launch specialized sub-agents in separate context windows.

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `agent_type` | string | Yes | `explore`, `task`, `general-purpose`, `code-review` |
| `prompt` | string | Yes | Task description |
| `description` | string | Yes | Short label (3-5 words) |
| `mode` | string | No | `sync` (default) or `background` |
| `model` | string | No | Model override |

**Agent Types:**

| Type | Purpose | Default Model | Tools Available |
|------|---------|---------------|-----------------|
| `explore` | Quick codebase analysis, answer questions about code | Haiku (fast) | grep, glob, view |
| `task` | Execute commands (tests, builds, lints) with brief success summaries | Haiku (fast) | All CLI tools |
| `general-purpose` | Complex multi-step tasks requiring full capability | Sonnet | All tools |
| `code-review` | Review code changes, surface genuine issues only | N/A | All CLI tools (read-only) |

**Available Models:**
- `claude-sonnet-4.6`, `claude-sonnet-4.5`, `claude-sonnet-4` (standard)
- `claude-haiku-4.5` (fast/cheap)
- `claude-opus-4.6`, `claude-opus-4.6-fast`, `claude-opus-4.6-1m`, `claude-opus-4.5` (premium)
- `gemini-3-pro-preview` (standard)
- `gpt-5.3-codex`, `gpt-5.2-codex`, `gpt-5.2`, `gpt-5.1-codex-max`, `gpt-5.1-codex`, `gpt-5.1` (standard)
- `gpt-5.1-codex-mini`, `gpt-5-mini`, `gpt-4.1` (fast/cheap)

---

### read_agent

Get status and results of a background agent.

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `agent_id` | string | Yes | ID returned from `task` with `mode: "background"` |
| `wait` | boolean | No | Block until agent completes (default: false) |
| `timeout` | number | No | Max seconds to wait if `wait: true` (default: 30, max: 300) |

---

### list_agents

List all background agents and their status.

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `include_completed` | boolean | No | Include completed/failed agents (default: true) |

---

### ask_user

Request user input during execution.

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `question` | string | Yes | Question to ask |
| `choices` | string[] | No | Multiple choice options (preferred for faster UX) |
| `allow_freeform` | boolean | No | Allow text input (default: true) |

**Best Practices:**
- Prefer multiple choice over freeform when possible
- Don't include "Other" in choices (UI adds freeform option automatically)
- Ask one question at a time

---

## GitHub MCP Tools

GitHub MCP server is built-in. Tools use prefix `github-mcp-server-`.

### Issues

| Tool | Purpose |
|------|---------|
| `github-mcp-server-list_issues` | List repository issues with pagination |
| `github-mcp-server-search_issues` | Search issues by query |
| `github-mcp-server-issue_read` | Get issue details, comments, sub-issues, labels |

### Pull Requests

| Tool | Purpose |
|------|---------|
| `github-mcp-server-list_pull_requests` | List PRs (use search for author filter) |
| `github-mcp-server-search_pull_requests` | Search PRs by query |
| `github-mcp-server-pull_request_read` | Get PR details, diff, status, files, reviews, comments |

### Repository

| Tool | Purpose |
|------|---------|
| `github-mcp-server-get_file_contents` | Get file/directory from GitHub |
| `github-mcp-server-list_branches` | List repository branches |
| `github-mcp-server-list_commits` | List commits on a branch |
| `github-mcp-server-get_commit` | Get commit details with diff |
| `github-mcp-server-search_code` | Search code across repositories |
| `github-mcp-server-search_repositories` | Find repositories |
| `github-mcp-server-search_users` | Find GitHub users |

### Actions

| Tool | Purpose |
|------|---------|
| `github-mcp-server-actions_list` | List workflows, workflow runs, jobs, artifacts |
| `github-mcp-server-actions_get` | Get specific workflow, run, or job details |
| `github-mcp-server-get_job_logs` | Get job logs (single job or all failed jobs) |

### Other

| Tool | Purpose |
|------|---------|
| `github-mcp-server-get_copilot_space` | Get context from a Copilot space |
| `github-mcp-server-list_copilot_spaces` | List all accessible Copilot spaces |

---

## Utility Tools

### ide-get_selection

Get text selection from the connected IDE (e.g., VS Code). Returns current selection if an editor is active, otherwise returns the latest cached selection.

**Parameters:** None required.

**Returns:** Selected text and a `current` field indicating if from active editor (true) or cached (false).

---

### ide-get_diagnostics

Get language diagnostics (errors, warnings, hints) from the connected IDE (e.g., VS Code).

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `uri` | string | No | File URI to get diagnostics for. If omitted, returns diagnostics for all files. |

---

### report_intent

Update UI with current action. Displayed to user.

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `intent` | string | Yes | Current action (max 4 words, gerund form) |

**Rules:**
- Always call with other tools (never alone)
- Call on first tool-calling turn after each user message
- Update when switching phases
- Examples: "Exploring codebase", "Running tests", "Fixing bug"

---

### sql

Execute SQL queries against SQLite databases. Provides two databases.

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | Yes | SQLite-compatible SQL query |
| `description` | string | Yes | 2-5 word summary of what the query does |
| `database` | string | No | `session` (default) or `session_store` |

**Databases:**

| Database | Access | Purpose |
|----------|--------|---------|
| `session` | Read/Write | Per-session scratch database for structured workflow data — task tracking, test cases, batch items, state machines |
| `session_store` | Read-only | Global database containing history from ALL past sessions (conversations, files edited, refs) |

**Pre-existing Tables (session database):**
- `todos`: `id`, `title`, `description`, `status` (pending/in_progress/done/blocked), `created_at`, `updated_at`
- `todo_deps`: `todo_id`, `depends_on` (for dependency tracking)

**Session Store Tables (read-only):**
- `sessions`: `id`, `cwd`, `repository`, `branch`, `summary`, `created_at`, `updated_at`
- `turns`: `session_id`, `turn_index`, `user_message`, `assistant_response`, `timestamp`
- `checkpoints`: `session_id`, `checkpoint_number`, `title`, `overview`, `history`, `work_done`, etc.
- `session_files`: `session_id`, `file_path`, `tool_name`, `turn_index`, `first_seen_at`
- `session_refs`: `session_id`, `ref_type` (commit/pr/issue), `ref_value`, `turn_index`
- `search_index`: FTS5 virtual table for full-text search across session history

**Use Cases:**
- Track todos and dependencies during multi-step tasks
- Query past session history ("what did I work on last week?")
- Load and query structured data (CSVs, API responses)
- Store intermediate results for multi-step analysis

**Example:**
```sql
-- Track work items
INSERT INTO todos (id, title, status) VALUES ('fix-auth', 'Fix auth bug', 'pending');

-- Search past sessions
SELECT content, session_id FROM search_index WHERE search_index MATCH 'auth OR login' ORDER BY rank LIMIT 10;
```

---

### store_memory

Save facts for future sessions. Persisted across conversations.

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `subject` | string | Yes | Topic (1-2 words) |
| `fact` | string | Yes | Fact to store (<200 chars) |
| `citations` | string | Yes | Source reference (file:line or user input) |
| `reason` | string | Yes | Why this matters (2-3 sentences) |
| `category` | string | Yes | `general`, `file_specific`, `bootstrap_and_build`, `user_preferences` |

**Use Cases:**
- Build/test commands that work
- Coding conventions specific to repo
- Important architectural decisions
- User preferences

---

### fetch_copilot_cli_documentation

Fetch documentation about Copilot CLI capabilities.

**Parameters:** None required.

**Use When:** User asks about Copilot CLI features, commands, or capabilities.

---

## Tool Aliases for Custom Agents

When configuring `tools` in agent frontmatter, use these aliases (not the actual tool names):

| Alias | Compatible Aliases | Maps To |
|-------|-------------------|---------|
| `execute` | `shell`, `Bash`, `powershell` | Shell tools |
| `read` | `Read`, `NotebookRead` | `view` |
| `edit` | `Edit`, `MultiEdit`, `Write`, `NotebookEdit` | Edit tools |
| `search` | `Grep`, `Glob` | Search tools |
| `agent` | `custom-agent`, `Task` | Custom agent invocation |
| `web` | `WebSearch`, `WebFetch` | Web tools |

**MCP Server Tools in Agent Config:**
- `github/*` - All GitHub MCP tools
- `github/list_issues` - Specific GitHub tool
- `playwright/*` - All Playwright tools (localhost only)
- `some-mcp-server/tool-name` - Specific MCP tool

**Examples:**
```yaml
# Read-only agent
tools: ["read", "search"]

# Full capability (same as omitting tools)
tools: ["*"]

# With specific MCP tools
tools: ["read", "edit", "github/list_issues", "github/search_code"]
```

# Tool Taxonomy

Canonical vocabulary used by `allowed_tools` in pack specs. Pack-spec
authors use the canonical category names below; the harness maps runtime
tool names observed in fixtures to categories before checking allow-lists.

## Canonical categories

| Canonical | Semantics | Runtime tool names |
|-----------|-----------|--------------------|
| `read` | Read files | `view`, `read`, `get_file_contents` |
| `search` | Find files / search content | `grep`, `glob`, `search` |
| `write` | Create or modify files | `edit`, `create`, `write`, `apply_patch` |
| `execute` | Run shell commands | `powershell`, `bash`, `shell`, `execute`, `run_*` |
| `agent` | Invoke or coordinate agents | `task`, `write_agent`, `read_agent`, `list_agents`, `stop_agent` |
| `data` | Query structured data stores | `session_store_sql`, `sql` |
| `web` | Fetch external content | `web_fetch`, `web_search` |
| `mcp:<server>` | MCP server tools | any tool prefixed `<server>-*` |
| `unknown` | Unrecognized; never allowed | (fallback) |

## Resolution rules

1. The fixture stores the literal runtime tool name in
   `tool_calls[*].name`.
2. The harness's tool-name-resolver (`harness/tools.py`) maps a runtime
   name to its canonical category using the table above.
3. If a runtime name has the form `<prefix>-<rest>`, it maps to
   `mcp:<prefix>` UNLESS the prefix matches a built-in resolver entry.
4. Anything else maps to `unknown`. `unknown` is never present in any
   pack's `allowed_tools`, so it always fails `L3-tools`.

## Adding a new tool

1. Append a row to the table above.
2. Add the runtime name to the appropriate group in `harness/tools.py`.
3. Add a unit test in `harness/tests/test_tools.py`.
4. Re-run any pack's eval to confirm the L3-tools assertion still passes.

## Why categories, not raw tool names

Existing agent frontmatter uses high-level vocabulary (`read`, `edit`,
`search`, `execute`) while runtime instrumentation reports concrete tool
names (`view`, `grep`, `task`). A category layer:

- Lets pack specs read naturally and survive runtime tool renames.
- Forces the harness to be explicit about which runtime tools count as
  "the same thing" — preventing unknown tools from silently passing.
- Makes negative-scope assertions robust to MCP server churn (any new
  MCP tool requires an explicit allow-list entry to pass).

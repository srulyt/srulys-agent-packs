# Tool Guidance Per Agent

This document specifies which tools each agent should use and avoid.

---

## Tool Access Matrix

| Agent | Primary Tools | Avoid | Notes |
|-------|--------------|-------|-------|
| Orchestrator | `new_task`, `read_file`, `list_files` | `write_to_file`, `apply_diff` | Delegate code changes |
| Spec Writer | `read_file`, `write_to_file` | `execute_command` | PRD creation only |
| Planner | `read_file`, `search_files`, `write_to_file` | `execute_command` | Planning only |
| Task Breaker | `read_file`, `write_to_file` | `execute_command` | Task creation only |
| Executor | `read_file`, `apply_diff`, `write_to_file`, `execute_command` | - | Full tool access |
| Verifier | `read_file`, `search_files`, `execute_command` | `apply_diff` | Read + verify only |
| Cleanup | `read_file`, `apply_diff`, `execute_command` | - | Cleanup operations |
| PR Prep | `read_file`, `execute_command`, `write_to_file` | - | Verification + docs |
| Memory Consolidator | `read_file`, `write_to_file` | `execute_command` | Context pack updates |

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

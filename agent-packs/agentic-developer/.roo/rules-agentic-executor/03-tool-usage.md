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

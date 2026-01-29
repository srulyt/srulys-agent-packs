---
name: context-management
description: Manage context window budget efficiently to maximize productive work within token limits. Load this skill before loading files into context, when context pressure reaches warning thresholds, when working with large files (> 200 lines), or before long-running tasks that may exhaust context.
---

# Context Management

## Purpose
Manage context window budget efficiently to maximize productive work within token limits.

## When to Use
- Before loading files into context
- When context pressure reaches warning thresholds
- When working with large files (> 200 lines)
- Before long-running tasks that may exhaust context

## Core Patterns

### Pattern 1: Context Budget Allocation

Allocate your context window across tiers to ensure capacity for all needs.

**When**: Starting any task or session
**Do**: Reserve capacity according to this budget

| Tier | Allocation | Policy |
|------|------------|--------|
| PINNED | ~15% | Always loaded, never evict (rules, constitution) |
| TASK-LOCAL | ~25% | Load once, keep until task complete |
| ON-DEMAND | ~35% | Load, use, release |
| OUTPUT | ~20% | Space for edits and responses |
| SAFETY | ~5% | Buffer for unexpected needs |

**Example** (128K model):
```yaml
pinned: 15K tokens
task_local: 25K tokens
on_demand: 35K tokens
output: 20K tokens
safety: 5K tokens
```

### Pattern 2: File Size Strategy

Choose reading strategy based on file size.

**When**: Reading any file
**Do**: Match strategy to file size

| Size | Lines | Strategy |
|------|-------|----------|
| Small | < 200 | Load entire file |
| Medium | 200-500 | Load targeted sections |
| Large | 500-2000 | Surgical access only |
| Massive | > 2000 | Index-based, method-level |

### Pattern 3: Large File Access

Access large files without loading full content.

**When**: File is > 200 lines
**Do**: Follow the targeted access pattern

```yaml
steps:
  1_index_first:
    tool: list_code_definition_names
    purpose: "Get structure overview"
  
  2_targeted_search:
    tool: search_files
    pattern: "Precise regex for specific element"
  
  3_surgical_read:
    tool: read_file
    scope: "Specific line ranges only"
  
  4_minimal_edit:
    tool: apply_diff
    scope: "Exact match, minimal context"
```

**Example**:
```
# For a 1500-line file:
1. search_files: "function processUser"
2. Note: found at lines 245-280
3. read_file: lines 240-290 (method + context)
4. apply_diff: 5-10 line SEARCH block
# Total: ~500 tokens vs ~25,000 for full file
```

### Pattern 4: Context Pressure Response

Respond appropriately to context pressure levels.

**When**: Context usage reaches thresholds
**Do**: Take tier-appropriate action

| Level | Threshold | Action |
|-------|-----------|--------|
| Yellow | 70% | Release non-essential ON-DEMAND |
| Orange | 85% | Checkpoint progress, prepare rotation |
| Red | 95% | Immediate checkpoint, release all ON-DEMAND |

### Pattern 5: Context Rotation

Rotate context when approaching limits.

**When**: Orange or Red pressure level
**Do**: Execute rotation protocol

```yaml
rotation_protocol:
  1_checkpoint:
    - Save work log with progress
    - Document completed work
    - Note next intended action
  
  2_release_on_demand:
    - Clear file contents from memory
    - Keep line number references
    - Retain search result summaries
  
  3_compress_task_local:
    - Replace files with summaries
    - Keep critical snippets only
    - Document what was released
  
  4_continue_or_handoff:
    if_nearly_complete: "Finish with minimal context"
    if_substantial_remains: "Checkpoint and signal"
```

### Pattern 6: Extraction Over Loading

Extract only what you need from files.

**When**: Need information from files
**Do**: Extract minimal required content

**Method Extraction**:
```yaml
include:
  - method_signature
  - method_body
  - immediate_dependencies (types, imports)
exclude:
  - other methods in file
  - unrelated comments
  - full class structure
```

**Class Summary**:
```yaml
include:
  - class_signature
  - public_method_signatures
  - field_declarations
exclude:
  - method_bodies
  - private helpers
  - detailed comments
```

## Anti-Patterns

- ❌ Loading entire large files when you only need one method
- ❌ Keeping file contents after edits are complete
- ❌ Reading files you might need "just in case"
- ❌ Ignoring context pressure warnings
- ❌ Re-reading files instead of keeping notes about line numbers
- ❌ Loading dependency files fully when only interface signatures needed

## Quick Reference

**Efficient Read** (~500 tokens):
1. Search for method signature
2. Extract method + 10 line context
3. Note line numbers for edit

**Wasteful Read** (~25,000 tokens):
1. Load entire 1500 line file
2. Scan to find method
3. Edit small section

**Checkpoint Format**:
```yaml
checkpoint:
  completed_work: [list of done items]
  pending_work: [what remains]
  context_needed: [line ranges for next action]
  resume_instructions: [step-by-step to continue]
```

## References

- Source: [`02-context-boundaries.md`](../../rules-agentic-executor/02-context-boundaries.md)

# File Editing Patterns

## Purpose
Choose the right editing tool and technique for each file modification to minimize context usage and maximize reliability.

## When to Use
- Before any file modification operation
- When deciding between `apply_diff` and `write_to_file`
- When editing large files
- When making surgical changes to existing code

## Core Patterns

### Pattern 1: Tool Selection

Choose the right tool for the job.

**When**: Any file modification needed
**Do**: Follow this decision tree

```
┌─────────────────────────────────────────┐
│         FILE MODIFICATION NEEDED        │
└────────────────┬────────────────────────┘
                 │
                 ▼
        ┌────────────────┐
        │ New file?      │
        └───────┬────────┘
                │
       YES ─────┼───── NO
        │       │       │
        ▼       │       ▼
   write_to_file│  ┌────────────────┐
                │  │ < 50% changed? │
                │  └───────┬────────┘
                │          │
                │  YES ────┼──── NO
                │   │      │      │
                │   ▼      │      ▼
                │ apply_diff│  write_to_file
                │          │  (full rewrite)
                └──────────┘
```

### Pattern 2: When to Use apply_diff

Prefer `apply_diff` for surgical edits.

**When**: 
- Modifying existing files
- Changes are < 50% of file content
- Need to preserve unchanged content

**Do**: Use `apply_diff` with minimal SEARCH block

**Benefits**:
- Smaller context usage (~300 tokens vs ~25,000)
- Clearer change intent
- Better for review
- Less risk of accidental truncation

**Example**:
```
apply_diff with:
  SEARCH block: 5-20 lines
  Uniqueness: Just enough to match exactly
  Context: Include identifying markers
```

### Pattern 3: When to Use write_to_file

Use `write_to_file` for complete file operations.

**When**:
- Creating new files
- Complete file rewrite genuinely needed
- File is small (< 50 lines)
- Content is entirely generated

**Do**: Provide complete, verified content

**Caution**:
- Verify you have COMPLETE content
- Don't truncate accidentally
- Don't use for "mostly unchanged" files

### Pattern 4: Diff Formatting Best Practices

Format diffs for reliable matching.

**When**: Using `apply_diff`
**Do**: Follow these rules

```yaml
search_block:
  size: "5-20 lines optimal"
  uniqueness: "Must match exactly ONE location"
  include:
    - Distinctive markers (function name, unique strings)
    - Enough context for unique match
  exclude:
    - Unnecessary blank lines
    - Content that might vary

replace_block:
  content: "Complete replacement for SEARCH block"
  indentation: "Match original exactly"
  newlines: "Preserve file's line ending style"
```

**Example** - Good SEARCH block:
```python
def process_user(user_id: str) -> User:
    """Process a user by ID."""
    user = get_user(user_id)
    return user
```

**Example** - Bad SEARCH block (too generic):
```python
    return user
```

### Pattern 5: Line Number Accuracy

Ensure accurate line targeting for edits.

**When**: Editing based on previous reads
**Do**: Verify line numbers are current

```yaml
accuracy_protocol:
  1_note_lines:
    - Record line numbers when reading
    - Include in notes: "processUser at lines 45-62"
  
  2_verify_before_edit:
    - If significant time passed, re-verify
    - Line numbers shift after earlier edits
  
  3_use_unique_content:
    - Rely on unique content strings
    - Not just line numbers
```

### Pattern 6: Handling Large Files

Edit large files without loading full content.

**When**: File is > 200 lines
**Do**: Use surgical access pattern

```yaml
large_file_edit:
  1_locate:
    tool: search_files
    pattern: "Target function/class signature"
  
  2_read_section:
    tool: read_file
    scope: "10-20 lines around target"
  
  3_edit:
    tool: apply_diff
    search: "5-15 lines, unique match"
    replace: "Changed content only"
  
  4_verify:
    tool: read_file
    scope: "Changed section only"
```

### Pattern 7: Multiple Edits Same File

Handle multiple changes to one file.

**When**: Several edits needed in same file
**Do**: Edit from bottom to top

```yaml
multi_edit_strategy:
  order: "bottom to top"
  reason: "Preserves line numbers for subsequent edits"
  
  process:
    1: "Identify all edit locations"
    2: "Sort by line number (descending)"
    3: "Apply each edit"
    4: "Verify final state"
```

**Example**:
```
Edits needed at lines: 25, 87, 156
Apply order: 156, 87, 25 (bottom first)
```

### Pattern 8: Verification After Edit

Always verify edits applied correctly.

**When**: After any `apply_diff` or `write_to_file`
**Do**: Confirm the change

```yaml
verification:
  1_re_read:
    tool: read_file
    scope: "Modified section"
    purpose: "Confirm edit applied"
  
  2_build_check:
    tool: execute_command
    command: "Build command if applicable"
    purpose: "Catch syntax errors"
  
  3_test_run:
    tool: execute_command
    command: "Relevant tests"
    purpose: "Catch logic errors"
```

## Anti-Patterns

- ❌ Using `write_to_file` for small changes to large files
- ❌ SEARCH blocks that match multiple locations
- ❌ SEARCH blocks that are too small (< 3 lines)
- ❌ Editing without verifying current line numbers
- ❌ Truncating files by incomplete `write_to_file`
- ❌ Making edits top-to-bottom (shifts line numbers)
- ❌ Skipping post-edit verification

## Quick Reference

**Efficient Edit** (~300 tokens):
```
apply_diff:
  SEARCH: 5-15 lines (unique match)
  REPLACE: Changed content
```

**Wasteful Edit** (~25,000 tokens):
```
write_to_file:
  Content: Entire 1500-line file
  Change: 10 lines modified
```

**Decision Checklist**:
- [ ] New file? → `write_to_file`
- [ ] < 50 lines total? → `write_to_file`
- [ ] < 50% changed? → `apply_diff`
- [ ] Full rewrite needed? → `write_to_file`

## References

- Source: [`02-tool-guidance.md`](../../rules/02-tool-guidance.md)
- Source: [`03-tool-usage.md`](../03-tool-usage.md)

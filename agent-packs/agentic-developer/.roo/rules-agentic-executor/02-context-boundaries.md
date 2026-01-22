# Executor Mode: Context Boundaries

> **Related**: For tool usage patterns, see [`03-tool-usage.md`](03-tool-usage.md).
> For error recovery, see [`04-error-recovery.md`](04-error-recovery.md).

## Context Budget Management

> **Note:** Token numbers in this document are approximate guidelines for models with ~128K context windows. Adjust proportionally for different context sizes. These are behavioral guidelines, not hard limits—the goal is efficient context usage.

### Token Budget Allocation

Each Executor session operates within strict token limits:

```yaml
# Context Budget for Executor (approximate, ~128K model)
total_budget: 100000 tokens # Approximate working context

allocation:
  pinned_context: 15000 # 15% - Constitution, task contract, global rules
  working_context: 60000 # 60% - Files being modified, reference code
  output_buffer: 20000 # 20% - Space for edits and responses
  safety_margin: 5000 # 5% - Buffer for unexpected needs
```

### Context Tiers

**Tier 1: PINNED (Always Loaded)**

```yaml
pinned_artifacts:
  - constitution.md # ~2000 tokens
  - task-contract.yaml # ~500 tokens
  - agentic-global.md # ~3000 tokens (summary)
  - mode-specific-rules # ~2000 tokens

pinned_budget: 15000 tokens
policy: "Never evict, load first"
```

**Tier 2: TASK-LOCAL (Load Once, Keep)**

```yaml
task_local_artifacts:
  - dependency_outputs # Outputs from prerequisite tasks
  - area_context # Relevant architecture docs
  - test_fixtures # Test data if needed

task_local_budget: 25000 tokens
policy: "Load when needed, retain until task complete"
```

**Tier 3: ON-DEMAND (Load, Use, Release)**

```yaml
on_demand_artifacts:
  - source_files # Files being modified
  - reference_files # Files read for context
  - search_results # Query results

on_demand_budget: 35000 tokens
policy: "Load minimum needed, release after use"
```

## Large File Protocol

### File Size Categories

```yaml
file_categories:
  small:
    threshold: "< 200 lines"
    token_estimate: "< 3000"
    strategy: "Load entire file if needed"

  medium:
    threshold: "200-500 lines"
    token_estimate: "3000-8000"
    strategy: "Load targeted sections"

  large:
    threshold: "500-2000 lines"
    token_estimate: "8000-30000"
    strategy: "Never load full file, surgical access only"

  massive:
    threshold: "> 2000 lines"
    token_estimate: "> 30000"
    strategy: "Index-based access, method-level extraction"
```

### Large File Access Pattern

For files > 500 lines, follow this protocol:

```markdown
## Large File Access Steps

1. **Index First**
   - Use list_code_definition_names to get structure
   - Identify method/class boundaries
   - Note line numbers of targets

2. **Targeted Search**
   - Use search_files with precise regex
   - Extract only matching sections
   - Get line numbers for context

3. **Surgical Read**
   - Request specific line ranges
   - Include minimal surrounding context
   - Never request "rest of file"

4. **Minimal Edit**
   - Use apply_diff with exact matches
   - Include just enough context for unique match
   - Verify edit boundaries before applying
```

### Context Extraction Templates

**Method Extraction Request**

```yaml
# When you need a specific method
extraction_request:
  file: "src/Services/UserService.cs"
  target: "ProcessUser method"
  context_lines: 10 # Lines above/below
  include:
    - method_signature
    - method_body
    - immediate_dependencies # Called methods in same class
```

**Class Summary Request**

```yaml
# When you need class overview without full content
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

## Context Window Pressure Management

### Pressure Detection

Monitor these warning signs:

```yaml
pressure_indicators:
  yellow_alert:
    condition: "Used > 70% of budget"
    action: "Release non-essential ON-DEMAND context"

  orange_alert:
    condition: "Used > 85% of budget"
    action: "Checkpoint and prepare for context rotation"

  red_alert:
    condition: "Used > 95% of budget"
    action: "Immediate checkpoint, release all ON-DEMAND"
```

### Context Rotation Protocol

When approaching limits:

```markdown
## Context Rotation Steps

1. **Checkpoint Current State**
   - Save work log with current progress
   - Document what's been completed
   - Note next intended action

2. **Release ON-DEMAND Context**
   - Clear file contents from context
   - Keep only line number references
   - Retain search result summaries (not full content)

3. **Compress TASK-LOCAL**
   - Replace full files with summaries
   - Keep critical snippets only
   - Document what was released

4. **Continue or Handoff**
   - If task nearly complete: finish with minimal context
   - If substantial work remains: checkpoint and signal
```

### Checkpoint for Context Exhaustion

```yaml
# .agent-memory/runs/<run-id>/tasks/<task-id>-checkpoint.yaml
task_id: T003
checkpoint_type: context-rotation
timestamp: 2024-01-15T10:50:00Z

context_state:
  reason: "Context budget at 85%"
  tokens_used_estimate: 85000

completed_work:
  - description: "Added null check to ProcessUser"
    file: "src/Services/UserService.cs"
    status: "committed"
  - description: "Updated validation logic"
    file: "src/Services/UserService.cs"
    status: "committed"

pending_work:
  - description: "Add unit tests"
    file: "tests/UserServiceTests.cs"
    status: "not started"
    context_needed:
      - "UserServiceTests.cs lines 1-50 (test setup)"
      - "UserService.cs ProcessUser method signature"

released_context:
  - "Full UserService.cs content"
  - "Dependency output from T002"

retained_context:
  - "constitution.md (PINNED)"
  - "task-contract.yaml (PINNED)"
  - "Key method signatures (summary)"

resume_instructions: |
  1. Load task contract
  2. Read tests/UserServiceTests.cs lines 1-50
  3. Add new test method for null handling
  4. Verify test passes
```

## File Boundary Rules

### Strict File Scope

The Executor MUST respect file boundaries from task contract:

```yaml
# Task Contract Defines Boundaries
file_boundaries:
  allowed_modifications:
    - "src/Services/UserService.cs"
    - "tests/UserServiceTests.cs"

  allowed_reads:
    - "src/Services/*.cs" # Can read for context
    - "src/Models/*.cs" # Can read for types
    - "tests/**/*.cs" # Can read for patterns

  forbidden_access:
    - "*.csproj" # No project files
    - "**/*.config" # No config files
    - ".git/**" # No git internals
    - "*.sql" # No database files
```

### Cross-File Reference Protocol

When implementation requires understanding related files:

```markdown
## Cross-File Reference Rules

1. **Read-Only Access**
   - Can read files outside modification scope
   - Cannot modify files outside scope
   - Document what was referenced

2. **Minimal Extraction**
   - Extract only what's needed (types, interfaces)
   - Don't load entire related files
   - Prefer summaries over full content

3. **Dependency Documentation**
   - Log cross-file dependencies found
   - Note if scope expansion might be needed
   - Include in verification request
```

### Interface Discovery

When you need to understand interfaces/types:

```yaml
# Interface Discovery Pattern
discovery_steps:
  1_search_definition:
    action: "Search for interface/type definition"
    tool: "search_files"
    pattern: "interface IUserValidator|class UserValidator"

  2_extract_signature:
    action: "Extract only signatures, not implementations"
    include:
      - interface_declaration
      - method_signatures
      - property_declarations
    exclude:
      - method_bodies
      - private_members

  3_document_dependency:
    action: "Log the dependency for verification"
    log_to: "work-log.yaml"
    content:
      file: "src/Interfaces/IUserValidator.cs"
      used_for: "Type reference for dependency injection"
      tokens_used: 200
```

## Context Efficiency Patterns

### Efficient File Reading

**DO: Targeted Reading**

```yaml
efficient_read:
  purpose: "Understand method to modify"
  approach:
    - Search for method signature
    - Extract method + 10 line context
    - Note line numbers for edit
  tokens_used: ~500
```

**DON'T: Full File Dump**

```yaml
inefficient_read:
  purpose: "Understand method to modify"
  approach:
    - Load entire 1500 line file
    - Scan through to find method
    - Edit small section
  tokens_used: ~25000 # WASTEFUL
```

### Efficient Editing

**DO: Surgical Replace**

```yaml
efficient_edit:
  approach: "replace_in_file with minimal SEARCH block"
  search_size: "5-20 lines"
  uniqueness: "Include just enough for unique match"
  tokens_used: ~300
```

**DON'T: Full File Rewrite**

```yaml
inefficient_edit:
  approach: "write_to_file with entire file content"
  content_size: "1500 lines"
  reason: "Small change buried in large file"
  tokens_used: ~25000 # WASTEFUL
```

### Context Reuse

```yaml
# Reuse loaded context efficiently
context_reuse_rules:
  - name: "Cache type definitions"
    pattern: "Load interface once, reference multiple times"

  - name: "Batch related reads"
    pattern: "Read all needed methods from file in one operation"

  - name: "Incremental loading"
    pattern: "Start with signatures, load bodies only if needed"
```

## Token Accounting

### Track Token Usage

Maintain approximate token counts:

```yaml
# Work Log Token Tracking
token_accounting:
  session_start: 0

  loads:
    - artifact: "constitution.md"
      tokens: 2000
      tier: "PINNED"

    - artifact: "task-contract.yaml"
      tokens: 500
      tier: "PINNED"

    - artifact: "UserService.cs (partial)"
      tokens: 800
      tier: "ON-DEMAND"

  current_total: 3300
  budget_remaining: 96700

  releases:
    - artifact: "UserService.cs (partial)"
      tokens: 800
      reason: "Edit complete, no longer needed"
```

### Budget Alerts

```yaml
# Emit alert when approaching limits
budget_alerts:
  - threshold: 70%
    action: "Log warning in work log"

  - threshold: 85%
    action: "Create context checkpoint"

  - threshold: 95%
    action: "Emit budget-critical event"
    event:
      event_type: context-budget-critical
      task_id: T003
      details:
        tokens_used: 95000
        tokens_remaining: 5000
        recommendation: "Complete current action and checkpoint"
```

## Multi-Task Context Isolation

### Context Isolation Rules

When multiple tasks might run in parallel:

```yaml
# Isolation Requirements
context_isolation:
  rule_1: "Each task loads only its own artifacts"
  rule_2: "No shared mutable state between tasks"
  rule_3: "Lane branches provide file-level isolation"
  rule_4: "Events are the only cross-task communication"
```

### Lane Branch Context

```yaml
# Lane Branch Context Management
lane_context:
  branch_name: "lane/T003-user-validation"

  isolated_files:
    - "src/Services/UserService.cs" # Owned by this task

  shared_files:
    - "src/Interfaces/IUserValidator.cs" # Read-only reference

  merge_target: "agentic/<run-id>"

  context_note: |
    Files on lane branch may diverge from main.
    Always read from lane branch, not main.
    Merge conflicts will be resolved at lane merge time.
```

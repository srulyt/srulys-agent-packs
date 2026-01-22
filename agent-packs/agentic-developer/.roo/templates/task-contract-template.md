# Task Contract Template

```yaml
---
run_id: "<run-id>"
actor: "task-breaker"
created: "<timestamp>"
task_id: "<task-id>"
---
```

## Task: <task-id>

### Description

<One paragraph describing what this task accomplishes>

### Acceptance Criteria

- [ ] <Criterion 1>
- [ ] <Criterion 2>
- [ ] <Criterion 3>

### Dependencies

- `<task-id>` - <brief reason>

### Scope

**Allowed files:**

- `path/to/file1.cs`
- `path/to/file2.cs`

**Forbidden files:**

- `*.config` - No config changes
- `*.csproj` - No project changes

### Context Pointers

- Context pack: `.context-packs/<relevant>_context.md`
- Relevant sections: <list specific sections>

### Implementation Context

**Patterns to Follow:**

- Reference implementation: `<path/to/similar/file.cs>`
- Pattern description: <Brief description of the pattern to follow>
- Key conventions: <List naming conventions, structure patterns, etc.>

**Test Requirements:**

- Test file location: `<path/to/test/file.cs>`
- Test pattern: <Describe how similar features are tested>
- Test utilities: `<path/to/test/helpers>` (if applicable)

**Schema Context:** (if data access involved)

- Entity class: `<path/to/entity.cs>`
- Verified columns: <List column names and types that exist>
- ORM patterns: <Describe data access patterns used>

**Interface Context:** (if implementing/extending interfaces)

- Interface location: `<path/to/interface.cs>`
- Method signatures to implement: <List methods>
- Existing implementations to reference: `<path/to/example.cs>`

### Estimated Effort

<Small | Medium | Large>

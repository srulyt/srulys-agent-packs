# Task Management

## Manifest Schema

The manifest file tracks all state for a context pack task:

```json
{
  "taskId": "string",
  "name": "string",
  "type": "feature | horizontal",
  "status": "initializing | discovery | analysis | synthesis | writing | complete | failed",
  "created": "ISO8601 timestamp",
  "updated": "ISO8601 timestamp",
  "phases": {
    "discovery": {
      "status": "pending | in_progress | complete | failed",
      "startedAt": "ISO8601 timestamp",
      "completedAt": "ISO8601 timestamp",
      "outputs": ["list of output files"]
    },
    "analysis": {
      "status": "pending | in_progress | complete | failed",
      "batches": [
        {
          "name": "batch name",
          "status": "pending | in_progress | complete | failed",
          "files": ["list of files"],
          "output": "output file path"
        }
      ]
    },
    "synthesis": {
      "status": "pending | in_progress | complete | failed",
      "output": "output file path"
    },
    "writing": {
      "status": "pending | in_progress | complete | failed",
      "output": "final context pack path"
    }
  },
  "inputs": {
    "businessContext": "string",
    "knownCodePaths": ["array of strings"],
    "namingConventions": ["array of strings"],
    "additionalHints": "string"
  },
  "errors": [
    {
      "phase": "phase name",
      "timestamp": "ISO8601 timestamp",
      "message": "error description",
      "recoverable": true
    }
  ]
}
```

## Batching Strategy

### When to Create Batches

Analysis batches should be created based on:

1. **Logical grouping**: Files that relate to the same context pack section
2. **Size constraints**: Aim for 5-10 files per batch, fewer if files are large
3. **Dependency order**: Process foundational files before dependent ones

### Recommended Batch Structure

| Batch | Target Section | Typical Files |
|-------|---------------|---------------|
| 01_overview | Sections 1, 7 | Main entry points, README, key domain files |
| 02_architecture | Section 2 | Controllers, managers, orchestrators, data access |
| 03_contracts | Sections 3, 5 | API definitions, event handlers, request/response types |
| 04_patterns | Sections 8, 11 | Multiple implementation files showing patterns |
| 05_tests | Section 10 | Test files, test utilities, mocks |
| 06_dependencies | Sections 6, 9 | Configuration, external service integrations |

### Adaptive Batching

If discovery reveals:
- **Small scope** (< 20 files): Use 2-3 larger batches
- **Large scope** (> 50 files): Use more targeted batches, possibly 8-10
- **Complex domain**: Add dedicated batches for specific subsystems

## Resumption Protocol

If orchestration is interrupted:

1. **Read manifest** to determine current state
2. **Identify incomplete phase** from status fields
3. **Resume from last checkpoint**:
   - If discovery incomplete: Re-run discovery
   - If analysis incomplete: Resume from last incomplete batch
   - If synthesis incomplete: Re-run synthesis
   - If writing incomplete: Re-run writing

## Quality Gates

Before transitioning between phases, verify:

### After Discovery
- [ ] At least one code path file has content
- [ ] Files are accessible (paths exist)
- [ ] Total file count is reasonable (warn if > 100)

### After Analysis
- [ ] All batches completed successfully
- [ ] Each analysis file has confidence scores
- [ ] No critical sections are empty

### After Synthesis
- [ ] Draft covers all 12 standard sections
- [ ] Confidence scores are aggregated
- [ ] Conflicts are resolved or noted

### After Writing
- [ ] Output file is valid markdown
- [ ] All sections are present
- [ ] Metadata header is complete

## Communication Templates

### Starting a Phase
```
## Phase: {phase_name}

Starting {phase_name} phase for "{context_pack_name}"...
```

### Phase Complete
```
## Phase Complete: {phase_name}

{phase_name} completed successfully.
- Files processed: {count}
- Time elapsed: {duration}
- Next: {next_phase}
```

### Error Report
```
## Error in {phase_name}

An error occurred during {phase_name}:
- Error: {message}
- Recoverable: {yes/no}
- Action: {retry/skip/abort}
```

### Final Report
```
## Context Pack Complete

Created: .context-packs/{output_file}
Type: {feature/horizontal}
Confidence: {overall}/5

Summary:
- {count} source files analyzed
- {count} test files documented
- {count} sections completed

Ready for use in agentic development tasks.
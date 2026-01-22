# Agentic Memory Layout

This document describes the memory architecture for the agentic development system, including Short-Term Memory (STM) for active runs and Long-Term Memory (LTM) for persistent knowledge.

## Directory Structure

```
.agent-memory/
├── runs/                           # STM - Active and recent runs
│   └── <run-id>/                   # One directory per run
│       ├── manifest.yaml           # Run metadata and current state
│       ├── events/                 # Event log (append-only)
│       │   ├── 0001-run-started.yaml
│       │   ├── 0002-phase-entered.yaml
│       │   └── ...
│       ├── artifacts/              # Generated documents
│       │   ├── prd.md
│       │   ├── constitution.md
│       │   ├── plan.md
│       │   └── task-graph.yaml
│       ├── tasks/                  # Task-specific data
│       │   └── <task-id>/
│       │       ├── contract.yaml
│       │       ├── work-log.md
│       │       └── verification.yaml
│       ├── lanes/                  # Parallel execution lanes
│       │   └── <lane-id>/
│       │       └── ...
│       ├── verification/           # Verification reports
│       │   └── <task-id>-verification.yaml
│       ├── escalations/            # Escalation records
│       │   └── <escalation-id>.yaml
│       └── pr/                     # PR preparation artifacts
│           ├── description.md
│           ├── checklist.md
│           └── promotion-candidate.yaml
│
├── ltm/                            # LTM - Persistent knowledge
│   ├── patterns/                   # Learned patterns
│   │   ├── code-patterns.yaml
│   │   ├── error-patterns.yaml
│   │   └── solution-patterns.yaml
│   ├── decisions/                  # ADRs extracted from runs
│   │   └── ADR-<number>-<slug>.md
│   ├── tech-debt/                  # Accumulated tech debt
│   │   └── tech-debt-registry.yaml
│   ├── metrics/                    # Historical metrics
│   │   └── run-metrics.yaml
│   └── learnings/                  # Consolidated learnings
│       └── area-learnings/
│           └── <area-name>.yaml
│
└── index.yaml                      # Global index of all runs
```

## Run ID Format

```
YYYYMMDD-HHMM-<slug>-<shortid>
```

- **YYYYMMDD**: Date (e.g., 20260115)
- **HHMM**: Time in 24-hour format (e.g., 1430)
- **slug**: Kebab-case task description (max 30 chars)
- **shortid**: 4-character alphanumeric ID (e.g., a1b2)

Example: `20260115-1430-add-email-validation-a1b2`

## STM (Short-Term Memory)

### Purpose

STM stores all data for active and recent runs. It is:

- Run-scoped (isolated per run)
- Event-sourced (state derived from events)
- Merge-safe (multiple contributors can work in parallel)
- Resumable (can restart from any point)

### manifest.yaml

The manifest is the entry point for any run:

```yaml
run_id: "20260115-1430-add-email-validation-a1b2"
created_at: "2026-01-15T14:30:00Z"
updated_at: "2026-01-15T16:45:00Z"

# Task information
task:
  title: "Add email validation to user registration"
  description: "..."
  requester: "user"

# Current state (derived from events, cached here)
state:
  phase: "EXECUTION" # PLANNING | EXECUTION | VERIFICATION | CLEANUP | PR_PREP
  status: "IN_PROGRESS" # IN_PROGRESS | BLOCKED | COMPLETED | FAILED
  current_task: "TASK-003"

# Phase completion tracking
phases:
  planning:
    status: "COMPLETED"
    completed_at: "2026-01-15T15:00:00Z"
  execution:
    status: "IN_PROGRESS"
    tasks_total: 5
    tasks_completed: 2
  verification:
    status: "PENDING"
  cleanup:
    status: "PENDING"
  pr_prep:
    status: "PENDING"

# Active lanes (for parallel execution)
active_lanes:
  - lane_id: "lane-001"
    task_id: "TASK-003"
    branch: "agent/20260115-1430-add-email-validation-a1b2/lane-001"

# Git information
git:
  base_branch: "main"
  work_branch: "agent/20260115-1430-add-email-validation-a1b2"
  latest_commit: "abc123def"

# Resume information
resume:
  last_checkpoint: "2026-01-15T16:30:00Z"
  last_event_id: 47
  recoverable: true
```

### Event Log

Events are stored as append-only JSONL files per actor under the `events/<actor>/` directory:

```
events/
├── orchestrator/
│   └── 2024-01-15T10-00-00Z.jsonl
├── executor/
│   └── 2024-01-15T10-30-00Z.jsonl
└── verifier/
    └── 2024-01-15T11-00-00Z.jsonl
```

Each line is one event JSON object. Event types and fields follow `agentic-event-schema.yaml` (schema catalog only; storage is JSONL).

- **Append-only**: Events are never modified or deleted
- **Per-actor files**: One file per actor to avoid merge conflicts
- **Self-describing**: Each event contains all context needed

### Task Directories

Each task gets its own directory under `tasks/<task-id>/`:

```yaml
# tasks/TASK-003/contract.md
task_id: "TASK-003"
title: "Implement EmailValidator class"
# ... full contract as per .roo/templates/task-contract-template.md
```

```markdown
# tasks/TASK-003/work-log.md

## Work Log - TASK-003

### Session 1 (2026-01-15T15:30:00Z)

- Analyzed existing validation patterns in codebase
- Created EmailValidator.cs with regex-based validation
- Added unit tests for common email formats

### Files Modified

- src/Validation/EmailValidator.cs (created)
- tests/Validation/EmailValidatorTests.cs (created)
```

### Lane Directories

For parallel execution, each lane gets its own directory:

```
lanes/
└── lane-001/
    ├── manifest.yaml          # Lane-specific state
    ├── tasks/                 # Tasks assigned to this lane
    └── events/                # Lane-specific events
```

Lane branches follow the pattern:

```
agent/<run-id>/lane-<lane-id>
```

## LTM (Long-Term Memory)

### Purpose

LTM stores knowledge that persists across runs:

- Patterns learned from successful solutions
- Architectural Decision Records (ADRs)
- Accumulated tech debt
- Historical metrics
- Area-specific learnings

### Patterns

```yaml
# ltm/patterns/code-patterns.yaml
patterns:
  - id: "PAT-001"
    name: "Repository Pattern Implementation"
    context: "Data access layer"
    description: "Standard repository pattern with Unit of Work"
    example_files:
      - "src/Data/Repositories/UserRepository.cs"
    learned_from:
      - "20260110-0900-add-user-repo-x1y2"
    confidence: HIGH

  - id: "PAT-002"
    name: "Validation Error Handling"
    context: "Input validation"
    description: "Return ValidationResult instead of throwing"
    learned_from:
      - "20260115-1430-add-email-validation-a1b2"
    confidence: MEDIUM
```

### ADR Storage

```markdown
# ltm/decisions/ADR-0001-use-result-pattern.md

# ADR-0001: Use Result Pattern for Validation

## Status

Accepted

## Context

During run 20260115-1430-add-email-validation-a1b2, we needed to decide
how to handle validation errors.

## Decision

Use the Result<T> pattern instead of throwing exceptions for validation failures.

## Consequences

- Cleaner control flow
- Explicit error handling
- Slightly more verbose calling code

## Source

- Run: 20260115-1430-add-email-validation-a1b2
- Extracted: 2026-01-15T17:00:00Z
```

### Tech Debt Registry

```yaml
# ltm/tech-debt/tech-debt-registry.yaml
tech_debt:
  - id: "TD-001"
    description: "International email support not implemented"
    location:
      file: "src/Validation/EmailValidator.cs"
      line: 78
    priority: LOW
    created_at: "2026-01-15T16:45:00Z"
    source_run: "20260115-1430-add-email-validation-a1b2"
    status: OPEN

  - id: "TD-002"
    description: "Missing integration tests for edge cases"
    location:
      file: "tests/Validation/EmailValidatorTests.cs"
    priority: MEDIUM
    created_at: "2026-01-15T16:45:00Z"
    source_run: "20260115-1430-add-email-validation-a1b2"
    status: OPEN
```

### Run Metrics

```yaml
# ltm/metrics/run-metrics.yaml
runs:
  - run_id: "20260115-1430-add-email-validation-a1b2"
    completed_at: "2026-01-15T17:00:00Z"
    duration_minutes: 150
    tasks_completed: 5
    tasks_failed: 0
    escalations: 1
    files_changed: 3
    lines_added: 87
    lines_removed: 12
    verification_status: "PASSED_WITH_WARNINGS"

summary:
  total_runs: 42
  successful_runs: 38
  failed_runs: 4
  average_duration_minutes: 120
  average_tasks_per_run: 6
```

## Context Tiers

Files are categorized into context tiers for token budget management:

### PINNED (Always in Context)

- `manifest.yaml` - Current run state
- Active task contract
- Constitution (architectural constraints)

### TASK-LOCAL (Loaded per Task)

- Task work log
- Relevant source files (per contract)
- Related test files

### ON-DEMAND (Loaded When Needed)

- Historical events
- Completed task artifacts
- LTM patterns and learnings

## Merge Safety

The STM design ensures merge safety through:

1. **Run Isolation**: Each run has its own directory
2. **Lane Branches**: Parallel work happens on separate branches
3. **Event Append-Only**: No modification of existing events
4. **Manifest Caching**: State is derived, manifest is just cache

### Parallel Execution Flow

```
main
  │
  └── agent/run-id (work branch)
        │
        ├── agent/run-id/lane-001 (parallel task A)
        │
        └── agent/run-id/lane-002 (parallel task B)
```

After lane completion:

1. Lane branch merges to work branch
2. Work branch rebases on main (if needed)
3. Final PR from work branch to main

## Cleanup and Archival

### Active Run Retention

- Runs in progress: Always retained
- Completed runs: Retained for 30 days
- Failed runs: Retained for 7 days

### Archival Process

1. Extract ADRs → LTM
2. Extract patterns → LTM
3. Update tech debt registry
4. Record metrics
5. Archive run directory (compress or delete)

### Index Maintenance

```yaml
# .agent-memory/index.yaml
runs:
  active:
    - run_id: "20260115-1430-add-email-validation-a1b2"
      status: "IN_PROGRESS"
      phase: "EXECUTION"

  completed:
    - run_id: "20260114-0900-fix-login-bug-c3d4"
      status: "COMPLETED"
      completed_at: "2026-01-14T12:00:00Z"

  archived:
    - run_id: "20260101-1000-initial-setup-e5f6"
      archived_at: "2026-01-08T00:00:00Z"
      archive_path: ".agent-memory/archive/20260101-1000-initial-setup-e5f6.tar.gz"
```

## Recovery Scenarios

### Scenario 1: Mid-Task Interruption

1. Read `manifest.yaml` for current state
2. Find last event in `events/`
3. Check task work log for progress
4. Resume from last checkpoint

### Scenario 2: Lane Failure

1. Identify failed lane from manifest
2. Check lane events for failure point
3. Either retry lane or reassign task
4. Update manifest with recovery action

### Scenario 3: Merge Conflict

1. Events record conflict occurrence
2. Escalate to human for resolution
3. Record resolution in events
4. Continue from resolved state

# Event Format Template

Events are append-only JSONL files stored in `.agent-memory/runs/<run-id>/events/<actor>/`.
**This is the single authoritative storage format.** Do not create per-event YAML files. Use one JSONL file per actor, append-only.

## File Naming

`<timestamp>.jsonl` where timestamp is `YYYYMMDD-HHMM` (per actor). Example: `.agent-memory/runs/<run-id>/events/executor/20260115-1030.jsonl`.

## Event Structure

```json
{
  "event_type": "<type>",
  "task_id": "<task-id>",
  "timestamp": "<ISO-8601>",
  "actor": "<mode-slug>",
  "details": {}
}
```

## Common Event Types

| Event Type         | Actor        | When                    |
| ------------------ | ------------ | ----------------------- |
| `task-claimed`     | executor     | Starting work on task   |
| `task-implemented` | executor     | Code changes complete   |
| `task-verified`    | verifier     | Verification passed     |
| `task-failed`      | verifier     | Verification failed     |
| `task-blocked`     | any          | Cannot proceed          |
| `phase-complete`   | orchestrator | All tasks in phase done |
| `run-complete`     | orchestrator | Entire run finished     |

## Examples

```json
{"event_type":"task-claimed","task_id":"T003","timestamp":"2026-01-15T10:30:00Z","actor":"executor","details":{"estimated_duration":"30m"}}
{"event_type":"task-implemented","task_id":"T003","timestamp":"2026-01-15T11:00:00Z","actor":"executor","details":{"files_modified":["UserService.cs"]}}
```

## Rules

- One event per line (JSONL format)
- Events are **append-only** - never modify or delete
- Each actor writes to their own file to avoid merge conflicts
- Task status is derived by finding latest event for each task-id
- `agentic-event-schema.yaml` defines the catalog of event types (schema reference only; storage is JSONL here)

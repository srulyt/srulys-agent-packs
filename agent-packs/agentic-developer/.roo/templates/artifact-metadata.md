# Artifact Metadata Template

All STM artifacts must include this YAML frontmatter:

```yaml
---
run_id: "YYYYMMDD-HHMM-<slug>-<shortid>"
actor: "<mode-slug>"
created: "ISO-8601 timestamp"
task_id: "<task-id>" # when applicable
---
```

## Field Descriptions

| Field   | Format                           | Example                                |
| ------- | -------------------------------- | -------------------------------------- |
| run_id  | `YYYYMMDD-HHMM-<slug>-<shortid>` | `20260115-1030-add-validation-a1b2`    |
| actor   | Mode slug                        | `orchestrator`, `executor`, `verifier` |
| created | ISO-8601                         | `2026-01-15T10:30:00Z`                 |
| task_id | Task identifier                  | `T001`, `T002-validate-input`          |

## Usage

Include at the top of: PRD, plan, task contracts, verification reports, event files.

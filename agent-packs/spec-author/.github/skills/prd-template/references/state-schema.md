# `state.json` schema — `spec-author` runtime state

Per-session workflow state for the `spec-author` pack. One file per
session, written by the orchestrator on every phase transition.
Path: `.spec-author/sessions/<session-id>/state.json`.

This file is the single source of truth for the schema. The pack
README links here; do not restate fields elsewhere.

## Field reference

| Field | Type | Required | Meaning |
|-------|------|----------|---------|
| `session_id` | `string` (`YYYY-MM-DD-XXXXXXXX`) | yes | Session identifier; matches the directory name. |
| `input_style` | `"autonomous" \| "helper"` | yes | Shape of user input. Replaces v1's overloaded `mode`. |
| `mode_kind` | `"creation" \| "update"` | yes | Top-level workflow. Orthogonal to `input_style`. |
| `existing_spec_path` | `string \| null` | yes when `mode_kind == "update"`, else `null` | Prior spec path. |
| `phase` | enum (see below) | yes | Current workflow phase. |
| `structure_proposed` | `boolean` | yes | Has the orchestrator surfaced Stop A yet? |
| `structure_approved` | `boolean` | yes | Did the user say `APPROVE`? Drafter cannot run while `false`. |
| `structure_overrides` | `array<string>` | yes | User edits captured at Stop A (may be empty). |
| `structure_open_questions` | `array<string>` | yes | Open questions surfaced at Stop A. |
| `interview_required` | `boolean` | yes | Did detective report P0 gaps? |
| `interview_complete` | `boolean` | yes | Stop B exit gate. |
| `interview_retries` | `integer` (0..1) | yes | C5 partial-answer retries. Capped at 1. |
| `discovery_iterations` | `integer` (0..2) | yes | `context-detective` invocations. |
| `draft_iterations` | `integer` (0..3) | yes | `prd-drafter` invocations. |
| `critic_iterations` | `integer` (0..3) | yes | `prd-critic` invocations. |
| `stop_a_disambiguation_attempts` | `integer` (>=0) | yes | C4 binary re-prompt counter. |
| `version_bump` | `object \| null` | yes when `mode_kind == "update"`, else `null` | `{ from: string, to: string, kind: "MAJOR"\|"MINOR"\|"PATCH" }`. |
| `last_verdict` | `"pass" \| "revise" \| "block" \| null` | yes | Most recent critic verdict. |
| `updated_at` | ISO-8601 `string` | yes | Mandatory on every write. |

### `phase` enum

`intake`, `context-discovery`, `awaiting-structure-approval`,
`awaiting-interview-answers`, `drafting`, `review`, `complete`,
`complete-with-warnings`, `failed`.

## Machine-readable form

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "spec-author state.json",
  "type": "object",
  "required": [
    "session_id", "input_style", "mode_kind", "existing_spec_path",
    "phase", "structure_proposed", "structure_approved",
    "structure_overrides", "structure_open_questions",
    "interview_required", "interview_complete", "interview_retries",
    "discovery_iterations", "draft_iterations", "critic_iterations",
    "stop_a_disambiguation_attempts", "version_bump", "last_verdict",
    "updated_at"
  ],
  "properties": {
    "session_id":        { "type": "string", "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2}-[0-9a-f]{8}$" },
    "input_style":       { "enum": ["autonomous", "helper"] },
    "mode_kind":         { "enum": ["creation", "update"] },
    "existing_spec_path":{ "type": ["string", "null"] },
    "phase":             { "enum": ["intake", "context-discovery", "awaiting-structure-approval", "awaiting-interview-answers", "drafting", "review", "complete", "complete-with-warnings", "failed"] },
    "structure_proposed":       { "type": "boolean" },
    "structure_approved":       { "type": "boolean" },
    "structure_overrides":      { "type": "array", "items": { "type": "string" } },
    "structure_open_questions": { "type": "array", "items": { "type": "string" } },
    "interview_required":       { "type": "boolean" },
    "interview_complete":       { "type": "boolean" },
    "interview_retries":        { "type": "integer", "minimum": 0, "maximum": 1 },
    "discovery_iterations":     { "type": "integer", "minimum": 0, "maximum": 2 },
    "draft_iterations":         { "type": "integer", "minimum": 0, "maximum": 3 },
    "critic_iterations":        { "type": "integer", "minimum": 0, "maximum": 3 },
    "stop_a_disambiguation_attempts": { "type": "integer", "minimum": 0 },
    "version_bump": {
      "oneOf": [
        { "type": "null" },
        {
          "type": "object",
          "required": ["from", "to", "kind"],
          "properties": {
            "from": { "type": "string" },
            "to":   { "type": "string" },
            "kind": { "enum": ["MAJOR", "MINOR", "PATCH"] }
          }
        }
      ]
    },
    "last_verdict": { "enum": ["pass", "revise", "block", null] },
    "updated_at":   { "type": "string", "format": "date-time" }
  }
}
```

## Field-naming note

`input_style` is autonomous-vs-helper input shape; `mode_kind` is
creation-vs-update workflow. The two are orthogonal and never
collapsed (deliberately split in v2-C3 to fix v1's overloaded `mode`
field).

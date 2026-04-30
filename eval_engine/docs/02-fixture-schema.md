# Fixture JSON Schema

> **Read `05-design-revisions-v2.md` first.** v2 adds `tool_calls[]`,
> `file_accesses[]`, `background_reads[]`, `session_store{}`, blob
> externalization, and a `${WORKSPACE_ROOT}` token. The v1 `tool_requests[]`
> stays as a derived view; the new `tool_calls[]` is authoritative for
> negative-scope assertions. Where docs disagree, v2 wins.

A **fixture** is a single JSON file produced by the `@eval-runner` custom
agent. It captures everything the Python harness needs to evaluate a Copilot
CLI session, derived from the cloud session store via `session_store_sql`.

The fixture is the **only contract** between the in-CLI evidence collector and
the out-of-CLI assertion logic. Anything the harness needs about a session
must be in the fixture.

## File location

`evals/packs/<pack>/fixtures/<case>/<session_id>.json`

One fixture per (pack, case, session_id). Fixtures are **committed to git** so
they can be replayed via `python eval_engine/harness/run.py --replay <path>` for
assertion development without a live CLI session.

## Top-level structure

```json
{
  "schema_version": 1,
  "captured_at": "2026-04-28T18:22:01Z",
  "captured_by": "eval-runner@v1",
  "session": {
    "id": "2026-04-28-ab12cd34",
    "repository": "srulyt/srulys-agent-packs",
    "branch": "main",
    "summary": "...",
    "created_at": "2026-04-28T18:00:11Z",
    "updated_at": "2026-04-28T18:21:48Z"
  },
  "pack_under_test": "copilot-factory",
  "case_id": "smoke-create-issue-triage-pack",
  "workspace_root": "/abs/path/to/evals/packs/<pack>/workspaces/copilot-factory/smoke-create-issue-triage-pack/2026-04-28T18-22Z/",

  "tool_requests": [ ... ],
  "events": [ ... ],
  "session_files": [ ... ],
  "agent_windows": [ ... ],
  "usage_aggregate": { ... },
  "final_assistant_message": "..."
}
```

## Sections

### `tool_requests[]`

One row per call to any tool by the orchestrator (the top-level CLI session).
Mirrors the `tool_requests` table.

```json
{
  "tool_call_id": "call_01H...",
  "name": "task",
  "timestamp": "2026-04-28T18:05:33Z",
  "arguments_json": { "agent_type": "factory-architect", "name": "...", "prompt": "...", "mode": "sync", "model": "claude-sonnet-4.6" }
}
```

`arguments_json` is the parsed JSON object (not a string). The harness
specifically needs `agent_type`, `name`, `mode`, `model`, and `prompt` for
`task` calls; for other tools, it preserves the full object so future
assertions can use it.

### `events[]`

One row per event recorded by the runtime. Filtered to events relevant to
evaluation (tool starts, tool completions, usage records). Mirrors the
`events` table.

```json
{
  "timestamp": "2026-04-28T18:05:34Z",
  "type": "tool.execution_complete",
  "tool_start_name": "task",
  "tool_complete_call_id": "call_01H...",
  "tool_complete_success": true,
  "tool_complete_result_content": "...full sub-agent final assistant message...",
  "usage_model": "claude-sonnet-4.6",
  "usage_input_tokens": 4231,
  "usage_output_tokens": 982
}
```

The harness joins `events` to `tool_requests` on `tool_complete_call_id` to
reconstruct request/response pairs (this is the §2.2 canonical query baked
into the fixture).

### `session_files[]`

One row per file the session created or edited (NOT files merely read).
Mirrors `session_files`.

```json
{ "file_path": "agent-packs/issue-triage/.github/agents/orchestrator.agent.md",
  "tool_name": "create",
  "turn_index": 12,
  "first_seen_at": "2026-04-28T18:18:02Z" }
```

### `agent_windows[]`

**Derived field**, computed by `@eval-runner` from `tool_requests` +
`events`. One entry per `task` invocation, giving the time window during
which the sub-agent was active. Used by L3 negative-scope checks to scope
"tool calls inside this sub-agent" assertions.

```json
{
  "tool_call_id": "call_01H...",
  "agent_type": "factory-architect",
  "agent_name": "design-arch-1",
  "started_at": "2026-04-28T18:05:33Z",
  "completed_at": "2026-04-28T18:08:51Z",
  "success": true,
  "input_prompt": "...full prompt sent to sub-agent...",
  "final_response": "...full final assistant message from sub-agent...",
  "input_tokens": 4231,
  "output_tokens": 982,
  "model_used": "claude-sonnet-4.6"
}
```

Background agents that received `write_agent` follow-ups have multiple
turns; in that case `final_response` is the LAST turn and a separate
`turns[]` array on the window holds the full history:

```json
{
  ...,
  "turns": [
    { "index": 0, "user_content": "...launch prompt...", "assistant_content": "...turn 0 reply..." },
    { "index": 1, "user_content": "...write_agent message...", "assistant_content": "...turn 1 reply..." }
  ]
}
```

### `usage_aggregate`

Per-model token totals across the whole session, plus a per-agent breakdown.

```json
{
  "by_model": {
    "claude-sonnet-4.6": { "input_tokens": 41023, "output_tokens": 9821 }
  },
  "by_agent": {
    "factory-architect": { "input_tokens": 4231, "output_tokens": 982, "invocations": 1 },
    "factory-critic":    { "input_tokens": 3120, "output_tokens": 410, "invocations": 1 },
    "factory-engineer":  { "input_tokens": 28102, "output_tokens": 7421, "invocations": 1 }
  },
  "total_input_tokens": 41023,
  "total_output_tokens": 9821
}
```

### `final_assistant_message`

The orchestrator's last message to the user. Used by L2-output-schema and by
some judge rubrics (when `apply_to: pack_output`).

## Defaults / required fields

All fields above are REQUIRED unless marked otherwise. `@eval-runner` MUST
fail loudly rather than emit a fixture with missing fields — silent gaps
become silent assertion passes, which is exactly the failure mode evals exist
to catch.

## Validation rules (enforced at fixture load)

1. `schema_version` must equal a version the harness knows.
2. `session.id` must match the trailing dir component of the fixture path.
3. Every `events[]` row with `tool_complete_call_id` set must reference a row
   in `tool_requests`.
4. Every `agent_windows[]` row must reference a `tool_requests` row whose
   `name == "task"`.
5. `agent_windows[*].started_at <= completed_at`.
6. `usage_aggregate.by_agent` keys must be a subset of distinct
   `agent_windows[*].agent_type` values.

## Source queries

`@eval-runner` builds the fixture by running the queries catalogued in
`eval_engine/queries/` (see todo `queries-library`). The mapping is:

| Field | Query template |
|-------|----------------|
| `tool_requests` | `enumerate_tool_requests.sql` |
| `events` | `enumerate_relevant_events.sql` |
| `session_files` | `files_touched.sql` |
| `agent_windows` | derived in-agent from `tool_requests` + `events` (see `agent_windows.sql` returning the joined raw rows) |
| `usage_aggregate.by_model` | `usage_per_model.sql` |
| `usage_aggregate.by_agent` | derived in-agent by joining `agent_windows` to per-agent usage events |
| `final_assistant_message` | `final_orchestrator_message.sql` |

## Why this shape

- **Self-contained**: a fixture file is enough to run every assertion. No
  network access, no DB connection, no live CLI.
- **Diff-friendly**: JSON with stable key ordering means PR reviewers can
  literally read what changed when a fixture is regenerated.
- **Derived fields are the agent's job**: putting `agent_windows` and
  `usage_aggregate` in the fixture means the assertion code stays simple.
  The agent's queries are the only place the cloud-store schema is encoded.

# Fixture JSON Schema (v2)

A **fixture** is a single JSON file produced by the harness's
`capture-local` subcommand. It captures everything the Python harness
needs to evaluate a Copilot CLI session, derived from the local CLI's
process log at `~/.copilot/logs/process-*.log`.

The fixture is the **only contract** between captured-session evidence
and the out-of-CLI assertion logic. Anything the harness needs about a
session must be in the fixture.

## How fixtures are produced

```
python -m eval_engine.harness.run capture-local \
  --pack <pack> --case <case-id> --run-id <run-id> \
  [--log <process-log-path>] [--workspace <path>] [--out <path>]
```

The capture path is implemented in
[`eval_engine/harness/local_extractor.py`](../harness/local_extractor.py):

1. Find the Copilot CLI session whose `--name` matches `--run-id` (or
   accept an explicit `--log` path).
2. Parse the session's process-log JSON-lines for `cli.telemetry`,
   "Sending request to the AI model", and tool-call boundary events.
3. Reconstruct the v2 fixture (schema_version `"1.0.0"`) and write it to
   `evals/packs/<pack>/fixtures/<case>/<session-uuid>.json`.

> **Historical note.** Earlier drafts of this doc referenced a custom
> capture agent that queried a cloud `session_store_sql`. That path
> was never implemented; the local-log path above is the current and
> only mechanism. Fixtures are committed to git so they can be
> replayed via `python -m eval_engine.harness.run replay …` for
> assertion development without a live CLI session.

## File location

`evals/packs/<pack>/fixtures/<case>/<session_id>.json`

One fixture per (pack, case, session_id).

## Top-level structure

```json
{
  "schema_version": "1.0.0",
  "pack": "copilot-factory",
  "case_id": "smoke-create-issue-triage-pack",
  "session_id": "2f6c015d-da91-469a-90f8-bcc6c38d42bc",
  "run_id": "2026-04-28T19-22-30Z-49ad46",
  "workspace_root": "<absolute path under evals/packs/.../workspaces/>",
  "captured_at": "2026-04-28T19:30:49.404Z",
  "cli_version": "<copilot-cli-version-or-null>",
  "os": "<host-os-or-null>",
  "models": { "orchestrator": "claude-sonnet-4.6" },

  "invocations":   [ ... ],
  "tool_calls":    [ ... ],
  "file_accesses": [ ... ],
  "background_reads": [ ... ],
  "session_store": { ... }
}
```

The dataclass mirroring this shape is `models.Fixture`; the loader is
`loaders.load_fixture`.

## Sections

### `invocations[]`

One entry per agent activation, **including the orchestrator itself**
plus every `task`-dispatched sub-agent. This is the v2 replacement for
the old `agent_windows[]` derived view.

```json
{
  "invocation_id": "inv_01H...",
  "name": "factory-architect",
  "mode": "sync",
  "started_at": "2026-04-28T18:05:33Z",
  "ended_at":   "2026-04-28T18:08:51Z",
  "completed":  true,
  "prompt":     "...full prompt sent to the agent...",
  "response":   "...full final assistant message...",
  "parent_invocation_id": "inv_01H...",
  "tokens": 5213
}
```

The orchestrator's invocation has `parent_invocation_id: null`. Sub-agent
invocations carry their parent's id; the harness uses this to scope
tool-call and file-access assertions to a specific sub-agent window.

### `tool_calls[]`

Authoritative list of every tool invocation in the session. Each call
is attributed to either the orchestrator or a specific sub-agent via
`actor`.

```json
{
  "call_id": "call_01H...",
  "name": "task",
  "actor": {
    "kind": "orchestrator",
    "name": "copilot-factory",
    "invocation_id": "inv_01H..."
  },
  "arguments": {
    "agent_type": "factory-architect",
    "name": "design-arch-1",
    "prompt": "...",
    "mode": "sync",
    "model": "claude-sonnet-4.6"
  },
  "success": true,
  "started_at": "2026-04-28T18:05:33Z",
  "ended_at":   "2026-04-28T18:08:51Z",
  "result_summary": "...short summary or null..."
}
```

L1 count assertions and L3 negative-scope checks ("did this sub-agent
write outside its `write_scope_allow`?") read this list directly.

### `file_accesses[]`

Read/write trail derived from `tool_calls[]` (and a small amount of
inferred-read evidence from prompts). Each entry attributes the access
to an actor and carries a `confidence` field — `"high"` for direct
write/edit/create tool calls, `"medium"` for reads inferred from the
prompt context.

```json
{
  "path": ".github/agents/factory-architect.agent.md",
  "op":   "read",
  "actor": {
    "kind": "subagent",
    "name": "factory-architect",
    "invocation_id": "inv_01H..."
  },
  "confidence": "high",
  "call_id": "call_01H..."
}
```

L3-files assertions iterate this list to enforce per-agent
`write_scope_allow` / `read_scope_allow` regexes from the spec.

### `background_reads[]`

Per-turn evidence from `write_agent` follow-ups against background
agents. Empty for sync-only sessions.

### `session_store{}`

Optional bag for any session-level metadata the extractor wants to
preserve verbatim (token aggregates, repeat-group identifiers, etc.).
The harness MUST tolerate this being empty.

## Defaults / required fields

`schema_version`, `pack`, `case_id`, `session_id`, `run_id`,
`workspace_root`, `invocations`, `tool_calls`, `file_accesses` are
required. Empty arrays are permitted; missing keys are not — the
loader (`loaders.load_fixture`) raises `ConfigError` rather than emit a
fixture with silent gaps.

## Validation rules (enforced at fixture load)

1. `schema_version` must start with `"1."`.
2. Every `invocations[].invocation_id` must be unique.
3. Every `tool_calls[].actor.invocation_id` (when set) must reference an
   `invocations[]` entry.
4. Every `file_accesses[].call_id` (when set) must reference a
   `tool_calls[]` entry.
5. `started_at <= ended_at` for every invocation and tool-call window.

## Path normalisation

Workspace-relative paths in `file_accesses[].path` use POSIX
separators. The fixture's `workspace_root` is captured as an absolute
host path; replay tooling treats `${WORKSPACE_ROOT}` in assertion
patterns as a synonym for it (see
[`eval_engine/docs/05-design-revisions-v2.md`](05-design-revisions-v2.md)).

## Why this shape

- **Self-contained.** A fixture file is enough to run every assertion;
  no network access, no DB connection, no live CLI.
- **Diff-friendly.** Stable key ordering means PR reviewers can read
  what changed when a fixture is regenerated.
- **Single source of truth.** `tool_calls[]` is authoritative for
  negative-scope assertions. `file_accesses[]` is derived from it but
  pre-computed so assertion code stays simple.

## Reference fixtures

The committed copilot-factory fixtures under
`evals/packs/copilot-factory/fixtures/smoke-create-issue-triage-pack/`
are the canonical examples of this shape. Read them when in doubt.

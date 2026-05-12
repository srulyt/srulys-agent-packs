# State Management Patterns

How to manage workflow state for multi-agent systems.

## Core Principles

1. **Filesystem-based**: State lives in files, not memory
2. **Session isolation**: Each session has its own directory
3. **Git-friendly**: State directories can be gitignored
4. **Recovery-capable**: Can resume from any state

## Standard Directory Structure

```
.{system-name}/
├── current-session.json        # Pointer to active session
├── sessions/                   # Active sessions
│   └── {session-id}/
│       ├── state.json          # Workflow state
│       ├── context/            # Input files
│       │   ├── user-request.md
│       │   └── decisions.md
│       └── artifacts/          # Output files
│           ├── design.md
│           └── manifest.json
└── history/                    # Archived sessions
    └── {old-session-id}/
```

## Agent-Scoped STM Directories

For multi-agent packs, prefer a pack-unique STM root and per-agent run directories.

Guidance:

- Use a unique root name per pack (for example, `.product-brief-agent-stm/`) to prevent collisions across packs.
- Keep `current-session.json` at the STM root as the active pointer.
- Keep active runs under `runs/{session-id}/`.
- Under each run, isolate agent artifacts in `agents/{agent-name}/`.
- Keep session ID generation automatic; never prompt the user for a session id.

Example:

```text
.product-brief-agent-stm/
├── current-session.json
└── runs/
  └── {session-id}/
    └── agents/
      ├── brief-orchestrator/
      ├── evidence-analyst/
      ├── strategy-modeler/
      └── brief-composer/
```

## Session ID Format

Pattern: `{YYYY-MM-DD}-{8-char-hex}`

Examples:
- `2026-02-23-a1b2c3d4`
- `2026-02-23-deadbeef`

Generation:
- Date: Current UTC date
- Hex: Random 8-character hexadecimal

## State File Schemas

### current-session.json

```json
{
  "active_session": "2026-02-23-a1b2c3d4",
  "updated_at": "2026-02-23T09:00:00Z"
}
```

### state.json

```json
{
  "session_id": "2026-02-23-a1b2c3d4",
  "version": "1.0.0",
  "created_at": "2026-02-23T09:00:00Z",
  "updated_at": "2026-02-23T09:30:00Z",
  "phase": "intake|improve-analysis|design|review-arch|approval|build|review-prompts|eval-execute|eval-fix-loop|complete",
  "mode": "creation|improvement",
  "improvement_strategy": "incremental|rebuild|null",
  "target_system": "my-agent-pack",
  "iteration_counts": {
    "review-arch": 0,
    "review-prompts": 0,
    "improve-analysis": 0,
    "eval-fix-loop": 0
  },
  "override": false,
  "user_approved": false,
  "review_passed": false,
  "deliverables": {
    "architecture": null,
    "artifacts": []
  },
  "eval_runs": [],
  "last_eval_verdict": null,
  "eval_loop": null,
  "eval_status": null,
  "errors": []
}
```

**Field reference**:
- `iteration_counts` — per-review-type counter object. Incremented
  before each re-delegation of the same review type. When any value
  reaches `2` (or `3` for `eval-fix-loop`) and the latest verdict is
  BLOCKING / `fail`, the orchestrator escalates to the user instead of
  looping further.
- `override` — set to `true` only when the user explicitly chose
  `force-proceed` after hitting an iteration cap.
- `improvement_strategy` — `"incremental"` (apply targeted edits to
  an existing pack), `"rebuild"` (full architecture redesign), or
  `null` (creation mode).
- `eval_runs[]` — append-only list of per-iteration eval results.
  Each entry: `{run_index, results_path, report_log_path, status,
  tests_collected, tests_passed, tests_failed, tests_errored,
  tests_skipped, wall_clock_seconds, harness_error, started_at,
  completed_at, fix_attempt_for_run_index?}`. Path points to
  `.copilot-factory/sessions/{id}/artifacts/eval-run-{n}.json`.
- `last_eval_verdict` — `{status: "pass"|"fail"|"harness-error",
  run_index: <int>}`. Mirror of the latest verdict from
  `@factory-eval-runner` for fast orchestrator branching.
- `eval_loop` — `{approved_by_user, max_iterations, started_at,
  completed_at, guardrails: {max_wall_clock_seconds_per_loop,
  wall_clock_used_seconds}}`. The runtime mirror of the runner's
  resolved budget, accumulated across all iterations.
- `eval_status` — terminal status set when transitioning to
  `complete`: `"pass"`, `"fail"`, `"failed-override"` (user chose
  force-complete after cap-hit), `"skipped-incremental"` (no eval
  changes flagged), or `"error"`.
- `iteration_counts.eval-fix-loop` — fix-loop counter (cap=3,
  one higher than review caps because the signal is objective).

## State Transitions

```
intake → design → review-arch → approval → build → review-prompts →
  eval-execute → eval-fix-loop → complete
   │                    │            │           │            ▲
   │                    │            │           │            │ (loop until pass or cap=3)
   │                    │            │           └────────────┘
   │                    │            │
   │                    │            └── (changes requested)
   │                    │                       │
   │                    └───────────────────────┘
   │
   └── improve-analysis → design (rebuild) or build (incremental)
                │
                └── (improvement mode only)
```

**Transition Rules**:
- `intake → design`: Requirements captured (creation mode)
- `intake → improve-analysis`: Existing pack identified (improvement mode)
- `improve-analysis → build`: Incremental improvement path
- `improve-analysis → design`: Rebuild improvement path
- `design → review-arch`: Architecture written
- `review-arch → approval`: Review passed
- `approval → build`: User approved
- `build → review-prompts`: Implementation complete
- `review-prompts → eval-execute`: Implementation review passed
- `eval-execute → complete`: Eval verdict `pass` (or
  `skipped-incremental` for incremental builds with no eval changes)
- `eval-execute → eval-fix-loop`: Eval verdict `fail` AND user
  approved the loop (one-time gate)
- `eval-execute → complete (eval_status: fail)`: Eval verdict
  `fail` AND user chose `stop` at the approval gate
- `eval-execute → escalate`: Eval verdict `harness-error` (no retry)
- `eval-fix-loop → eval-fix-loop`: Fix turn produced
  `ready-for-rerun: true`; runner re-executes; cycle continues
- `eval-fix-loop → complete (eval_status: pass)`: Eval re-run passed
- `eval-fix-loop → complete (eval_status: failed-override)`: Cap=3
  hit, user chose `force-complete-with-failures`
- `approval → design`: Changes requested (increment iteration)

## Atomic Updates

Always write complete state files:

```javascript
// Read current
const state = JSON.parse(read("state.json"));

// Modify
state.phase = "build";
state.updated_at = new Date().toISOString();

// Write complete file
write("state.json", JSON.stringify(state, null, 2));
```

**Never** do partial updates to JSON files.

## Recovery Patterns

### Session Recovery

On startup:
1. Read `current-session.json`
2. Load active session's `state.json`
3. Resume from recorded phase

### Phase Recovery

For each phase, check preconditions:
- `design`: Has `context/user-request.md`?
- `review-arch`: Has `artifacts/architecture.md`?
- `build`: Has approved architecture and `user_approved: true`?
- `review-prompts`: Has build manifest?
- `complete`: Has passed implementation review?

### Error Recovery

```json
{
  "errors": [
    {
      "timestamp": "2026-02-23T09:25:00Z",
      "phase": "build",
      "message": "File creation failed",
      "recoverable": true
    }
  ]
}
```

## Session Lifecycle

### Create Session
```
1. Generate session ID
2. Create session directory
3. Initialize state.json
4. Update current-session.json
```

### Archive Session
```
1. Move session dir to history/
2. Update current-session.json (clear or set new)
3. Optionally compress history
```

### Resume Session
```
1. Read current-session.json
2. Load state.json from sessions/{id}/
3. Continue from recorded phase
```

## Gitignore Patterns

Add to repository `.gitignore`:

```gitignore
# Agent system state directories
.{system-name}/
```

For agent packs repository:
```gitignore
agent-packs/**/.{system-name}/
```

## Multi-User Considerations

For systems with multiple concurrent users:

1. **User-prefixed sessions**: `{user}-{date}-{hex}`
2. **Lock files**: Prevent concurrent edits
3. **Separate state dirs**: One per user if needed

## Platform Differences

### Copilot CLI
- State in `.copilot-{system}/`
- Sessions auto-close on completion
- No explicit context continuity

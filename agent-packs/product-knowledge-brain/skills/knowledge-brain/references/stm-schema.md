# STM Schema & Checkpoint Protocol

Overflow reference for `knowledge-brain/SKILL.md`. Defines the durable
**short-term-memory** working state that makes the evolution cycle
**crash-safe**: a mid-cycle context compaction loses nothing because no
step depends on in-conversation memory — all state lives on disk.

The STM is **distinct from the knowledge base**. The KB (under `<kb-root>/`)
is the deliverable; the STM (under `.product-knowledge-brain-stm/`) is the
transient in-flight cycle state and is **gitignored**.

## Pack-unique root

```
.product-knowledge-brain-stm/
├── current-session.json          # { "active_session": "<id|null>", "updated_at": "<ISO-8601>" }
└── runs/
    └── {session-id}/             # {YYYY-MM-DD}-{8-char-hex}
        ├── state.json            # cycle phase + step pointer + kb_root
        ├── checkpoint.json       # last_completed_step, next_step, input_hash
        ├── input/
        │   └── extracted-input.md   # incoming extracted text, verbatim
        ├── classification.json   # step 2 output (types + entities)
        ├── affected-areas.json   # step 3 output (pages/areas touched)
        ├── merge-plan.json       # steps 4–5, 9 (update vs create vs merge)
        ├── contradiction-queue.json  # detected contradictions + resolution
        ├── relationship-todo.json    # step 6 edges to write
        ├── index-rebuild-todo.json   # step 7 indexes to refresh
        └── refactor-plan.json    # step 8 split/merge/recategorize + index skills
```

Optionally, completed runs may be moved to `.product-knowledge-brain-stm/
history/{session-id}/` on completion.

## File schemas

### `current-session.json`
```json
{ "active_session": "2026-06-08-1a2b3c4d", "updated_at": "2026-06-08T22:10:00Z" }
```
`active_session` is `null` when no cycle is in flight.

### `state.json`
```json
{
  "session_id": "2026-06-08-1a2b3c4d",
  "kb_root": "knowledge-base/",
  "kb_namespace": "knowledge-base",
  "cycle_phase": "step-4",
  "input_hash": "sha256:…",
  "created_at": "<ISO-8601>",
  "updated_at": "<ISO-8601>"
}
```
`cycle_phase` is one of `step-1`…`step-10`, `complete`,
`failed-empty-input`. `kb_namespace = slugify(basename(kb_root))` is computed
**once at STEP 0** and reused verbatim on every resume. The generated
`_skills/` index-skill dirs are **bare** (`knowledge-index`,
`<slug>-knowledge-index`); `kb_namespace` is **not** applied at generation —
the install script reads `state.json.kb_namespace` (or recomputes it) and
applies the `<kb-ns>-` prefix when it copies the dirs into the shared harness
dir and scopes harness-dir cleanup. See
`knowledge-indexing/references/harness-skills-dir.md`.

### `checkpoint.json`
```json
{
  "last_completed_step": 3,
  "next_step": 4,
  "input_hash": "sha256:…",
  "kb_root": "knowledge-base/",
  "step_artifact_hashes": { "2": "sha256:…", "3": "sha256:…" }
}
```
`step_artifact_hashes` content-hash keys each completed step so a re-run is
provably a no-op.

## Checkpoint protocol (the no-data-loss guarantee)

1. **On invocation (FIRST action, before any analysis)**: read
   `current-session.json`. Compute `input_hash` over the extracted input.
   - **Resume** the open run iff `checkpoint.json.input_hash` matches AND
     `checkpoint.json.kb_root` matches the requested root → continue from
     `next_step`.
   - **Else create** a new session: auto-generate a
     `{YYYY-MM-DD}-{8-char-hex}` id (**never prompt the user**), create
     `runs/<session-id>/`, and **immediately write** `state.json` AND an
     initial `checkpoint.json` (`last_completed_step: 0`, `next_step: 1`,
     `input_hash`, `kb_root`, `step_artifact_hashes: {}`) before doing any
     knowledge work, then point `current-session.json` at it.
   This initial `checkpoint.json` write is mandatory and unconditional —
   the run directory must never exist without a `checkpoint.json`.
2. **After each step (only mandatory per-step write)**: bump
   `checkpoint.json` (`last_completed_step: N`, `next_step: N+1`, record the
   artifact hash) — one tiny write. Persist a separate step artifact only if
   a resume would need it; for small inputs keep a single consolidated
   `plan.json`. `state.json` is **not** re-written before every step.
3. **On resume after compaction**: read `checkpoint.json`; skip steps
   `<= last_completed_step`; continue from `next_step`. Completed steps are
   content-hash keyed → re-running one is a no-op (no duplicate pages).
4. **At completion only**: set `state.json.cycle_phase: "complete"`, archive
   the run, set `current-session.json.active_session: null`.

## Atomicity rule

Always write `state.json` and `checkpoint.json` as **complete files**
(read → modify → write the whole JSON object). Never apply partial JSON
edits — a partially written checkpoint defeats the crash-safety guarantee.

## KB / STM divergence

`state.json` records `kb_root`. If a later invocation requests a different
`kb_root` than the open session expected, **start a new session** rather
than writing the prior run's artifacts into the wrong knowledge base.

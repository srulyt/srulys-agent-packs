# Golden state fragment for smoke-orchestrator-no-self-redirect

Used by the harness to confirm:

1. The orchestrator created a session under
   `.copilot-factory/sessions/<id>/` with `state.json` and
   `context/user-request.md` (asserted via
   `expected.artifacts` + `state_assertions`).
2. `state.mode == "improvement"` and `state.phase` is one of
   `intake | improve-analysis | design | review-arch | approval`
   — the orchestrator advanced through legitimate workflow phases
   instead of redirecting.
3. The architect was NOT invoked (`factory-architect: {min: 0,
   max: 0}`) — first turn must not trigger a rebuild.
4. NO writes occurred under `agent-packs/` or `evals/packs/` on
   this turn — only `.copilot-factory/` should change.
5. The captured `user-request.md` contains the original prompt
   (mentions `spec-author` / `versioning` / `version`) and does
   NOT contain redirect phrasings.

## Forbidden response substrings (documentation)

The orchestrator's first user-facing response MUST NOT contain any
of these substrings (case-insensitive). They are documented here
because the current harness (`eval_engine/harness/loaders.py`,
`_ARTIFACT_CONTENT_KEYS` / `_STATE_ASSERTION_KEYS`) does not yet
support first-response substring assertions; if that mechanism is
added later, lift this list into `case.yaml` under a
`response_assertions` block.

- `re-issue`
- `prefix with @copilot-factory`
- `prepend @copilot-factory`
- `this work is owned by @copilot-factory`
- `please add @copilot-factory`

If a future judge or hook flags any of the above in the recorded
SUT response, this case must FAIL with severity `blocker`.

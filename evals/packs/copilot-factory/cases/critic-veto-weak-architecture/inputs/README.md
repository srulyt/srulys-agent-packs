# Inputs for critic-veto-weak-architecture

This directory is staged at the workspace root. It pre-seeds a paused
factory session with a deliberately weak architecture. The SUT
(orchestrator) is expected to resume the session and delegate to the
critic, which must return BLOCKING.

Files staged:

- `.copilot-factory/current-session.json` — points at the paused session
- `.copilot-factory/sessions/2026-01-15-deadbeef/state.json` — phase:
  `review-arch`
- `.copilot-factory/sessions/2026-01-15-deadbeef/context/user-request.md`
- `.copilot-factory/sessions/2026-01-15-deadbeef/artifacts/architecture.md`
  — the deliberately weak architecture

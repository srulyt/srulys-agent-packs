@spec-author update `docs/specs/notif-prefs.md`. We are dropping
**FR-03** (inline muted-badge) — the data shows nobody used it.

This spec is `Status: published, Version: 1.2.0`. Cut a v1.3 that
deprecates FR-03 properly. The user-facing UI is going away in v1.3
but the requirement ID stays in the spec so older integration
references still resolve.

## Pre-supplied answers (do not park; proceed straight through)

- **Stop A (structure approval):** `APPROVE` (first ask)
- **Publish intent:** publish v1.3.0 at end of turn.

Proceed end-to-end without waiting for further user input.

@spec-author write a PRD for **Workspace activity digest** — a daily
summary of changes in a product workspace, delivered to each member
via in-app notification.

Inputs available in this workspace:

- `docs/personas.md` — the two primary personas (PM, Engineering
  Manager) and their needs.
- `docs/spike-notes.md` — short engineering spike notes describing
  the existing event-stream we'd source from.
- Reference link: <https://example.com/digest-competitor-overview>
  (informational only).

No MCPs are declared for this run. Treat this as a single-team UI
addition: no new datastore, no new public API, no security-surface
change. Cross-team scope is **single team** (the Notifications team
ships everything).

## Pre-supplied answers (do not park; proceed straight through)

This is a non-interactive run. Treat the following as already
answered — do not pause at any `awaiting-*` park:

- **Stop 0 (output location):** `output_path: docs/specs/digest.md, spec_kind: product`
- **Stop A (structure approval):** `APPROVE` (first ask)

Proceed end-to-end without waiting for further user input.

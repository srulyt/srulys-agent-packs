@spec-author write a PRD for **"Add a 'mark as read' button to in-app
notifications"**.

This is a deliberately simple spec. The constraints are:

- Single team owns delivery (the Notifications team).
- No security-surface change (no auth changes, no new data egress).
- No new datastore or schema change (we already track read-state).
- No new public API or SDK surface.
- No phased rollout, no kill-switch needed.
- No regulatory regime in scope.

Apply the adaptive sectioning rule: include only mandatory sections
plus any complexity-gated section that is actually justified by the
inputs. I expect a noticeably trimmed spec compared to a full
cross-team feature.

## Pre-supplied answers (do not park; proceed straight through)

This is a non-interactive run. Treat the following as already
answered — do not pause at any `awaiting-*` park:

- **Stop 0 (output location):** `output_path: docs/specs/tweak.md, spec_kind: product`
- **Stop A (structure approval):** `APPROVE` (first ask)

Proceed end-to-end without waiting for further user input.

@spec-author update the existing spec at `fixtures/prior-spec-v1.md`.

Changes I want:

1. **Add a new FR** for keyboard shortcuts: users should be able to
   trigger the top three quick actions (open, dismiss, snooze) via
   `o`, `d`, `s` from the digest panel.
2. **Deprecate FR-07** "mouse-only quick actions" — superseded by
   the new keyboard-shortcuts FR.

Bump the version appropriately and produce a CHANGELOG.

## Pre-supplied answers (do not park; proceed straight through)

This is a non-interactive run. Treat the following as already
answered — do not pause at any `awaiting-*` park:

- **Stop 0 (output location):** `output_path: docs/specs/digest.md, spec_kind: technical`
- **Stop A (structure approval):** `APPROVE` (first ask, even though
  it includes the proposed version bump and `Updates:` header)

Proceed end-to-end without waiting for further user input.

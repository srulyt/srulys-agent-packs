# Golden expectations — smoke-draft-renumber-with-cross-refs

Rubric-judged. Key assertions over the final
`docs/specs/quick-toggle.md` and the drafter's fenced output:

- `## Document Information` block still reads `Status: draft`,
  `Version: 0.0.1-draft` (V3 — no mid-draft bump).
- A new FR (the keyboard-shortcut FR) appears with ID `FR-3` (per
  the user request "place it before Visual feedback"); the prior
  FR-3 ("Visual feedback") is renumbered to `FR-4`.
- Every cross-reference to the shifted FR is updated atomically:
  - `AC-3.1` body's "see FR-2 for visual feedback that confirms the
    flip" / similar prose is updated to point at `FR-4`.
  - The original `### FR-3 — Visual feedback` heading is now
    `### FR-4 — Visual feedback` with `AC-4.1` (renumbered from
    `AC-3.1`).
  - The `R-1` risk row that referenced "FR-2 / AC-2.2" still
    resolves (FR-2 was untouched).
- The drafter's `cross-ref-audit-json` fence is non-empty:
  - `renumbers` includes the FR-3 → FR-4 shift.
  - `inserts` includes the new keyboard-shortcut FR-3.
  - `references_updated` enumerates each touched location.
  - `orphaned_references` is empty.
- No `CHANGELOG.md` exists anywhere in the workspace at run end.

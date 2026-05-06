# Golden expectations — smoke-creation-initial-draft-state

No byte-for-byte golden file. The case is rubric-judged against
`versioning-discipline` V2/V3 invariants:

- The final spec at `docs/specs/quick-toggle.md` MUST contain a
  `## Document Information` block with:
  - `- **Status**: draft`
  - `- **Version**: 0.0.1-draft`
- No `CHANGELOG.md` exists anywhere in the workspace at the end of
  the run (V3 / OQ-5: drafts NEVER write to the changelog file).
- The drafter's `version-bump-json` fence reads
  `kind: none-still-draft` with `from == to == "0.0.1-draft"`.
- The orchestrator's `session-summary` fence is accompanied by a
  `spec-status` block (V14) reporting `status: draft`, `version:
  0.0.1-draft`, and a `pre-merge-reminder` block (V7).
- The drafter's `cross-ref-audit-json` is present and well-formed
  (may be all-empty if no IDs were touched after the initial
  emission, or non-empty if the drafter renumbered during draft
  refinement; either is V12-conformant).

# Golden — smoke-draft-fr-removal-renumber (C4, F4 draft branch)

Prior spec is `Status: draft, Version: 0.0.3-draft` with five FRs
and a cross-reference web touching FR-04 / FR-05 from ACs, risks
(`R-01` → FR-04, `R-02` → FR-05), and `OQ-01` → FR-03.

The user requests removal of FR-03. Per `prd-evolution` §3a (draft
branch), the drafter must:

1. Delete FR-03 cleanly (no `[Deprecated]` / `[Removed]` stub).
2. Renumber FR-04 → FR-03 and FR-05 → FR-04 (and their AC sub-IDs).
3. Atomically update every cross-reference (R-01, R-02 prose; OQ-01;
   any in-prose `(see FR-NN)` pointers).
4. Emit a `cross-ref-audit-json` block with `deletes`,
   `renumbers`, and `orphaned_references == []`.
5. Write NO CHANGELOG.md entry (V3: drafts do not log).

## What is asserted

- Renumbered headings: `### FR-03 — Quiet-hours window` and
  `### FR-04 — Test-notification button`.
- Renumbered AC IDs: `**AC-03.1**`, `**AC-03.2**`, `**AC-04.1**`.
- Risk-prose now references new IDs: `FR-03)` (quiet-hours) and
  `FR-04)` (test-button).
- `cross-ref-audit-json.deletes` contains `FR-03`;
  `renumbers["FR-04"] == "FR-03"`; `renumbers["FR-05"] == "FR-04"`;
  `orphaned_references == []`.
- Critic `findings-json` has no `d6.removal-by-status` finding.
- CHANGELOG.md is `forbidden` (must not be created).

## What is NOT asserted

- Whether the version field changes (V3 says drafts may not bump
  mid-draft; the override sets `versioning-no-mid-draft-bump` to
  `warn` and `versioning-no-mid-draft-changelog` to `error`).
- Order of cross-ref-audit fields (only key/value membership).
- Specific wording in the renumbered FRs.

## Failure interpretation

- A `[Deprecated]` / `[Removed]` marker → drafter took the
  published branch on a draft.
- `### FR-05` still present → drafter failed to renumber.
- `muted badge` text surviving → drafter retained FR-03 content.
- A CHANGELOG.md created → V3 violation.
- `d6.removal-by-status` finding → either the drafter regressed
  (stub / gap) or the critic surfaced a false positive on the
  draft branch.

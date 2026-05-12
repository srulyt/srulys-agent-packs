# Golden — smoke-published-fr-removal-deprecate (C5, F4 published branch)

Prior spec is `Status: published, Version: 1.2.0` with five FRs and
an existing CHANGELOG.md (v1.0.0 + v1.2.0). The user requests
removal of FR-03 and a v1.3.0 publish.

Per `prd-evolution` §3b + V9 (published branch), the drafter must:

1. Mark FR-03 in place with `[Deprecated in v1.3, ...]` — do NOT
   delete the heading.
2. Keep ALL FR IDs frozen (V9): FR-04 stays `Quiet-hours window`,
   FR-05 stays `Test-notification button`. NO renumber.
3. Keep AC IDs frozen (`AC-04.1`, `AC-04.2`, `AC-05.1`).
4. Bump Version to `1.3.0`.
5. Write a CHANGELOG.md `## v1.3.0` block with a `### Deprecated`
   entry citing `FR-03`.

## What is asserted (positive)

- Spec body:
  - `### FR-03 [Deprecated in v1.3...` heading (regex
    `###\s+FR-03\s+\[Deprecated in v1\.3`).
  - `### FR-04 — Quiet-hours window` and
    `### FR-05 — Test-notification button` headings preserved.
  - AC IDs `**AC-04.1**`, `**AC-05.1**` preserved.
  - `Version**: 1.3.0` in Document Information.
- CHANGELOG.md:
  - `## v1.3.0` block.
  - `### Deprecated` entry referencing `FR-03`.
- Drafter:
  - `edit-audit-json.counts.modify >= 1`; no deletes.
  - No edit's locator references `FR-04` or `FR-05` (frozen).
  - `version-bump-json.new_version == "1.3.0"`.
- Critic `findings-json` contains no `d6.removal-by-status` finding.

## What is asserted (negative-control)

- FR-03 heading must NOT be deleted (the
  `(?s)## Functional Requirements[\s\S]{0,2000}### FR-04 — Quiet-hours window[^#]`
  pattern fires only if FR-03 is gone and FR-04 immediately
  follows the FR section heading).
- No silent renumber: FR-04 is NOT `Test-notification button`.

## Failure interpretation

- FR-03 deleted → drafter took the draft branch on a published spec
  (V9 violation).
- FR-04 = `Test-notification button` → drafter renumbered (V9
  violation).
- CHANGELOG.md missing `### Deprecated FR-03` → V9 incomplete.
- `d6.removal-by-status` finding → critic correctly caught a
  drafter regression OR critic regression on the published branch.
- Expected critic `fix:` substring (only relevant if drafter
  regresses): finding `fix` MUST contain `[Deprecated in`.

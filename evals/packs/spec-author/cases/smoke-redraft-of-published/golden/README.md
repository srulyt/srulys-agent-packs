# Golden expectations — smoke-redraft-of-published

Rubric-judged. Key assertions:

- The final `docs/specs/quick-toggle.md` shows:
  - `- **Status**: draft`
  - `- **Version**: 0.1.1-draft`  (V11 step 2: auto-classified
    MINOR → next == 0.2.0; PATCH variant 0.1.1 is also acceptable
    if the drafter classified the additive FR as PATCH-eligible.
    Either way, the suffix `-draft` MUST be present.) Strictly
    preferred: `0.2.0-draft` for an additive FR per V10 (additive
    FR → MINOR).
  - A new `## Changes since v0.1.0` preamble immediately under
    `## Document Information`, with one line referencing the new
    FR.
- **Published IDs are frozen** (OQ-6 strict freeze):
  - `FR-1`, `FR-2`, `FR-3`, `AC-1.1`, `AC-1.2`, `AC-2.1`,
    `AC-2.2`, `AC-3.1`, `R-1`, `R-2` all retain their numbers and
    section ordering. The drafter MUST NOT renumber any of them.
- The new keyboard-shortcut FR is added with the **next available**
  ID after the highest current FR — i.e. `FR-4` (NOT `FR-3.1` or
  inserted-mid-list).
- The drafter's `version-bump-json` reads:
  - `kind: publish-redraft` (working state) — **NO**, this kind is
    used at the publish step. During the re-draft window itself
    the kind is `none-still-draft` (the working version doesn't
    bump again until publish; V11 step 5 / V3). Both shapes are
    acceptable as long as the working version carries `-draft`
    and no CHANGELOG mutation happens this turn.
- The `docs/specs/CHANGELOG.md` file is **unchanged** from its
  fixture state (still showing only `[0.1.0] - 2026-05-10`).
  V3 / OQ-5: re-draft windows do NOT mutate the changelog file.
- The drafter's `cross-ref-audit-json` shows:
  - `inserts: [{kind: "FR", id: "FR-4"}]` (or whatever the next
    available ID was).
  - `renumbers: []` (published IDs are frozen).
  - `orphaned_references: []`.
- The orchestrator's `spec-status` block reports
  `status: draft`, `version: 0.1.1-draft` (or `0.2.0-draft`), and
  the `pre-merge-reminder` block fires (V7).

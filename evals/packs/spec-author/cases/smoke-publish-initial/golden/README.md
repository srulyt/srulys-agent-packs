# Golden expectations — smoke-publish-initial

Rubric-judged. Key assertions:

- The final `docs/specs/quick-toggle.md` has:
  - `- **Status**: published`
  - `- **Version**: 0.1.0`  (no `-draft` suffix)
  - `Last Updated:` set to today's date.
- A new `docs/specs/CHANGELOG.md` exists with a single section:
  ```
  ## [0.1.0] - YYYY-MM-DD

  ### Added
  - <one aggregate-summary line, e.g. "3 FRs, 2 risks, 1 open
    question defined.">
  ```
  Per OQ-5 the entry MUST be the aggregate-summary form (NOT a
  per-FR enumerated list) on initial publish, unless the user
  explicitly forced enumeration with `PUBLISH 0.1.0 ENUMERATE`
  (the prompt did not, so aggregate is required).
- The drafter's `version-bump-json` fence reads:
  - `kind: publish-initial`
  - `from: "0.0.1-draft"`, `to: "0.1.0"`
  - `override: false` (user explicitly named 0.1.0; that is the
    user's pick and respects OQ-1).
- The drafter's `cross-ref-audit-json` shows no renumbers
  (publish freezes IDs in place; V9).
- The orchestrator's `spec-status` block reports
  `status: published`. The `pre-merge-reminder` block is OMITTED
  on this turn (V7: published specs do NOT carry the reminder).

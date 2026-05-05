# Golden artefacts — minimal-edit regression guard

No byte-for-byte golden file is asserted for the spec; the
regression assertion lives in `case.yaml`:

- `must_contain_verbatim` on the bait spans from the prior spec.
  If the drafter "improves" any of these, the assertion fails.
- `agent_output_overrides.prd-drafter.json_block_assertions` on
  `edit-audit-json` (counts.add/modify/reorder/rename, every edit
  reason in the legitimate enum, preserved_unchanged_sections
  non-trivially populated).
- `rubric_overrides.edit-minimalism` escalated to `warn` with a
  0.9 threshold for this specific case (the pack spec keeps it
  at iteration-1 `info`).

Format expectations the spec must satisfy are inherited from
`smoke-update-existing-spec/golden/README.md` (Stop 0, EARS FRs,
nested ACs, headers-not-bold, footnote-style citations, anchored
internal links, no boilerplate "implementation is out of scope"
non-goal). They are NOT re-asserted here; the rubric scoring path
covers them.

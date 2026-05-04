# Golden artefacts — format expectations (D9 scope-discipline case)

No byte-for-byte golden file is asserted. The structural assertions
live in `case.yaml`:

- `artifact_content_assertions.specification.must_not_match` —
  enforces the absence of implementation tokens (`Postgres`,
  `Kafka`, `Redis`, `MongoDB`) and the boilerplate "implementation
  is out of scope" string.
- `artifact_content_assertions.spec-review.must_match` — enforces
  that the critic emitted at least one D9 finding.
- `rubric_overrides.scope-discipline: error` — the new D9 rubric
  is escalated from `info` to `error` for this case.

In addition to those, the spec must satisfy the global format
conventions documented in the other cases' golden READMEs:
EARS-shaped FRs (`### FR-NN — title (Pn, pattern)`), nested
`AC-NN.x` Given/When/Then ACs, headers (not bold) for layout, no
hard-wrapped body prose, footnote-style citations (no `Citations`
appendix), and product-mode reductions (no Data Model, API
Contract, Capacity & Performance Targets, Threat Model Summary,
Versioning & Deprecation Policy, NFR↔FR Traceability).

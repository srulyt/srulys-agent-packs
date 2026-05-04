# Golden artefacts — format expectations

No byte-for-byte golden file is asserted for this case; the spec is
content-judged via the rubrics in `evals/packs/spec-author/spec.yaml`
plus the per-case overrides above. Path patterns and invocation
counts in `case.yaml` are the structural assertions.

## Format expectations the spec must satisfy (rubric inputs)

These are the conventions the drafter and critic enforce. Goldens
do not pin them byte-for-byte, but rubric scoring penalises
deviations.

- **Stop 0 visible in the orchestrator transcript.** The
  orchestrator parks at `awaiting-output-location` exactly once
  (per scripted_user above) and asks for both `output_path` and
  `spec_kind` before delegating to any sub-agent.
- **Final spec lands at the user-chosen `output_path`** (e.g.
  `docs/specs/<feature>.md`), NOT inside `.spec-author/sessions/`.
  The session directory keeps research, review, and transcripts
  only.
- **EARS-shaped Functional Requirements.** Each FR is rendered as
  `### FR-NN — <title> (P<n>, <ears-pattern>)` followed by a
  single shall-statement using one of the named EARS patterns
  (ubiquitous / event-driven / state-driven / optional-feature /
  unwanted / complex). Exactly one `shall` per FR.
- **Nested Acceptance Criteria.** Each FR carries a
  `#### Acceptance Criteria` sub-section with one or more
  `AC-<FR>.<n>` Given/When/Then scenarios. There is NO separate
  top-level "Acceptance Criteria" section.
- **Headers, not bold, carry structure.** `#` / `##` / `###` /
  `####` define layout; bolded lines as pseudo-headers are
  rejected.
- **No hard-wrapped body prose.** Each paragraph is one logical
  line in the markdown source.
- **Footnote-style citations**, not a numbered "Citations"
  appendix table or `S1`/`S2` reference list. Footnote names are
  short slugs (e.g. `[^load-2024]`). The spec MUST NOT contain a
  `## Citations` heading or an `S\d+` style reference label.
- **Anchored internal links** (e.g.
  `[Functional Requirements](#functional-requirements)`), not
  bare section names.
- **`spec_kind` reductions are honoured.** When `spec_kind:
  product`, implementation-shaped sections (Data Model, API
  Contract, Capacity & Performance Targets, Threat Model Summary,
  Versioning & Deprecation Policy, NFR↔FR Traceability) are
  omitted even when their underlying axis fires. FRs do not name
  internal components, libraries, datastores, or specific APIs.
  When `spec_kind: mixed`, those details are confined to a
  `Technical Considerations` appendix. When `spec_kind:
  technical`, the full gated set behaves per the complexity
  heuristic.
- **No boilerplate "implementation is out of scope" non-goal.**
  In product / mixed mode the boundary is implicit; a literal
  string like that in `Out of Scope` is a D9 finding.

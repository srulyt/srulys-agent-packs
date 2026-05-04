---
name: prd-quality-rubric
description: "Critic scoring rubric for drafted specs. Defines dimensions D1–D4 (both modes) and D5–D8 (update mode only), per-dimension scoring guidance, weighted aggregation, verdict thresholds (pass/revise/block). Replaces literal-diff-based rubric. Triggers on: score the spec, critic rubric, D1 mandatory coverage, D2 gated appropriateness, verdict thresholds."
---

# PRD Quality Rubric

This skill is the source of truth for `@prd-critic`'s scoring. It
defines the dimensions, scoring guidance per dimension, weighted
aggregation, and verdict rules.

## When to Use This Skill

Load this skill when:

- Scoring a drafted spec (`@prd-critic`).
- Authoring or maintaining the eval `spec.yaml` rubric list (the
  rubric IDs in the eval spec mirror the dimension IDs here).

## Domain neutrality

Dimensions are domain-neutral. The critic does NOT penalise the
absence of an industry-specific section the user did not request,
and does NOT reward the presence of one. User-approved Stop A
overrides for section names are honoured at face value (D3).

## Dimensions

### D1 — mandatory-coverage  (both modes)

**Question:** Are all `mandatory` sections from the
`prd-template` catalogue present and non-empty (or marked `[TBD]`
with a corresponding `OQ-NN` entry in "Open Questions")?

**Scoring:** count present / total mandatory; partial credit for
`[TBD]` entries that have a matching OQ entry.

**Common deductions:** missing "Open Questions" section entirely;
mandatory section present but empty without `[TBD]`.

### D2 — gated-appropriateness  (both modes)

**Question:** For each `complexity-gated` section, is the
include/omit decision justified by the §heuristic given the inputs
**AND the user-chosen `spec_kind`** (see `prd-template`)?

**Scoring:**
- Penalise **bloat**: gated section present without a triggering
  axis being detectable in the inputs, OR without `spec_kind`
  permitting it.
- Penalise **underspecification**: axis present in the inputs AND
  `spec_kind` permits inclusion, but the section is omitted.
- Reward correctly omitted sections with a clear rationale in
  `section-decisions-json` (including
  `gated-omitted-by-spec-kind`).
- In `spec_kind: product`, do NOT penalise omission of
  implementation-shaped sections (Data Model, API Contract,
  Capacity & Performance Targets, Threat Model Summary, Versioning
  & Deprecation Policy, NFR↔FR Traceability) regardless of axis.

### D3 — naming-consistency  (both modes)

**Question:** Do section names match the neutral catalogue, OR a
Stop-A-approved override?

**Scoring:** any drift from the catalogue without an override
deducts. Industry-specific labels without explicit Stop A approval
deduct heavily.

### D4 — content-quality  (both modes)

**Question:** Is the prose clear; are FRs in EARS shape; are
acceptance criteria testable and nested under their FR; do NFRs
(when present) trace to FRs; is there fabrication; is evidence
discipline upheld; is format hygiene upheld?

**Scoring:** penalise:
- Non-EARS FR statements (multiple `shall`s, missing
  `<system> shall`, intention-shaped triggers, passive-voice
  responses). See `spec-driven-prd-best-practices` §4a.
- Non-testable acceptance criteria; ACs not nested under their FR;
  ACs without `AC-<FR>.<n>` IDs.
- Untraceable claims (no footnote and not derivable from the
  context pack).
- Vague goals without baseline + target + measurement window.
- Missing P0/P1/P2 priority on FRs.
- **Evidence-discipline violations:** footnote points at a
  gitignored or session-local path (e.g. `.spec-author/`,
  `.local/`); opaque `S1, S2` numeric citations; bare section
  reference instead of an anchored link; "Citations" appendix
  table present; footnote that omits a real URL.
- **Format-hygiene violations:** hard-wrapped body paragraphs;
  bold-as-header; structure carried by bolded lines instead of
  `###`/`####` headers.

### D9 — scope-discipline  (both modes when `spec_kind` is `product` or `mixed`; `null` otherwise)

**Question:** In `product` / `mixed` mode, is implementation
content kept out of FRs and confined to a "Technical
Considerations" appendix (mixed) or omitted entirely (product)?

**Scoring:** penalise:
- Any FR that names an internal component, library, datastore,
  framework, language, or specific API in `product` / `mixed`
  mode.
- Inline implementation content next to FRs in `mixed` mode (it
  belongs in "Technical Considerations").
- Boilerplate "implementation is out of scope" / "technical design
  choices are out of scope" entries in Out of Scope.

In `spec_kind: technical`, D9 is reported as `null` (not 0) — the
dimension does not apply.

### D5 — changelog-completeness  (update mode only)

**Question:** Does `CHANGELOG.md` exist, use the
Keep-a-Changelog categories, and account for every change visible
between prior and revised?

**Scoring:** any diff that does not appear in at least one
category deducts. Wrong category placement is a minor deduction.

### D6 — id-stability  (update mode only)

**Question:** Do all prior requirement IDs (FR-, NFR-, AC-, R-,
OQ-, TS-) still resolve in the revised spec?

**Scoring:** silent deletion of an ID is a **blocker** finding.
Renumbering is a **blocker** finding.

### D7 — versioning-correctness  (update mode only)

**Question:** Does the version bump match the `prd-evolution`
rule (MAJOR/MINOR/PATCH)? Is the `Updates:` / `Obsoletes:` header
present?

**Scoring:** wrong bump or missing header is a **major** finding.

### D8 — section-stability  (update mode only)

**Question:** No silent renumbering. No removed gated section
without a changelog rationale.

**Scoring:** silently removed gated sections deduct heavily.

## Weighted aggregation

Equal-weight mean of applicable dimensions only. Dimensions not
applicable in the current mode are reported as `null`, **not 0**,
in `scores-json`.

```
weighted = mean(dim for dim in [D1..D9] if dim is not null)
```

## Verdict rules

- **block** — any `blocker` finding (e.g. silent ID deletion,
  fabricated facts, mandatory section missing AND no OQ entry).
- **revise** — `weighted < 0.7` OR any `major` finding.
- **pass** — otherwise.

## Severity guidance

| Severity | When to use |
|----------|-------------|
| **blocker** | The spec must not ship as-is. Examples: silent ID deletion in update mode; mandatory section missing without OQ; fabricated facts. |
| **major**   | Significant quality issue that should block this draft. Examples: NFR section present without any traceable axis; non-testable AC across most requirements; wrong version bump kind. |
| **minor**   | Polish issue. Examples: a single non-testable AC; missing citation on one claim; naming drift on one heading. |

## Threshold tuning

The 0.7 threshold for `revise` is tunable. Consumers who want to
lower the bar for first drafts can raise it; consumers in
high-trust pipelines can lower it. Adjust here, not in the
`.agent.md` of `@prd-critic`.

## Quality checklist (for the critic itself)

- [ ] Every applicable dimension scored in `[0, 1]`.
- [ ] Inapplicable dimensions reported as `null`.
- [ ] `weighted` matches the formula above.
- [ ] Verdict matches the rules above.
- [ ] Findings sorted by severity (blocker > major > minor).
- [ ] Every finding has `dimension`, `severity`, `issue`, `fix`.

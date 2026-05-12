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
- **Evidence-discipline violations.** Apply the following severity
  schedule (overrides the default-to-minor rule):
  - **blocker** — any footnote whose URL resolves to a
    gitignored / session-local / local-scratch path (per
    `spec-driven-prd-best-practices` §8 and `.gitignore`).
    Verdict goes to `block` regardless of weighted score. The
    drafter is required to remove the footnote (not relabel it,
    not move it to a "References" appendix).
  - **blocker** — any footnote pointing at a non-authoritative or
    non-primary source (e.g. a third-party blog post quoting the
    standard instead of the standard itself). The drafter must
    replace it with the primary source or drop it.
  - **major** — a footnote that adds no value (decorative or
    redundant; a competent reader could act on the section
    without it). The drafter must drop it; verdict revises.
  - **major** — `S1, S2` numeric scheme; "Citations" appendix
    table present.
  - **minor** — formatting issues (bare section reference instead
    of an anchored link, missing URL on a footnote that is
    otherwise valid).
- **Format-hygiene violations:** hard-wrapped body paragraphs;
  bold-as-header; structure carried by bolded lines instead of
  `###`/`####` headers.
- **Upper-section isolation violations** (per
  `prd-template` §"Per-section isolation contract"):
  - Solution Summary restates problem narrative, or names owners
    / metrics / FRs / rollout detail → **major** per offending
    section.
  - Goals restates the problem, or names owners, or describes
    solution mechanics → **major** per offending section.
  - Problem Statement preempts the solution ("we will add…"),
    or names owners, or pre-states goals → **major** per
    offending section.
  - Ownership / stakeholder content surfacing in any non-Ownership
    upper section → **major**.
  - Repeat offence across three or more upper sections → escalate
    one finding to **blocker**.

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

### D5 — changelog-completeness  (publish-transition turns only)

**Question:** When the spec transitioned `Status: draft → published`
this turn (V8 — `version-bump-json.kind ∈ {publish-initial,
publish-redraft}`), does `CHANGELOG.md` exist, use the
Keep-a-Changelog categories, and account for every change visible
between prior and revised?

**Scope:** D5 applies **only** on publish-transition turns. On any
turn where `Status: draft` at end-of-turn (initial draft OR
re-draft window edit without publish intent), D5 is reported as
`null`, not `0` — drafts produce no CHANGELOG (V3 / V17 / OQ-5).

**Scoring:** any diff that does not appear in at least one
category deducts. Wrong category placement is a minor deduction.

### D6 — id-stability  (update mode only)

**Question:** Do all prior requirement IDs (FR-, NFR-, AC-, R-,
OQ-, TS-) still resolve in the revised spec?

**Scoring:** silent deletion of an ID is a **blocker** finding.
Renumbering is a **blocker** finding.

**Sub-rubric `d6.removal-by-status`** (severity: blocker; defined
by `prd-evolution` §3 + `versioning-discipline` §V9):

- In `Status: draft` (initial OR re-draft window — applies to any
  item removed regardless of whether it was newly added in-window
  or carried over from a prior published version): a removed
  item that left a `[Deprecated]` / `[Removed]` stub heading, or
  any prose narrating the removal ("formerly FR-07…", "removed
  in this revision…"), in the **draft body** is a **blocker**
  finding. Drafts delete cleanly per `prd-evolution` §3a / §3b
  (interpretation (a)).
- In `Status: draft` (any flavour): a removed in-window FR/NFR/R/
  OQ/TS that did NOT trigger renumbering of successors (leaving a
  numbering gap) is a **blocker** finding. Prior-published IDs
  are NOT renumbered (V9 over the ID is permanent) — gaps in the
  prior-published number space are expected and not a finding.
- In `Status: draft` (re-draft window): a removed prior-published
  ID for which `state.json:pending_published_id_deletions` does
  NOT contain a matching entry is a **blocker** finding. The
  drafter must queue the deletion for publish-time
  re-materialisation; silent drops break V9 at the next publish.
- In `Status: published` end-of-turn (publish-transition turns
  only): a deleted prior-published item with no `[Deprecated]` /
  `[Removed]` stub heading in the *published* artefact is a
  **blocker** finding (V9 published-contract violation). At
  publish, every entry that was in
  `pending_published_id_deletions` MUST have been re-materialised
  in the published artefact body (V8 step 4a).
- In `Status: published` end-of-turn: a renumbered prior-published
  item is a **blocker** finding (V9 numbering immutability).

### D7 — versioning-correctness  (update mode only)

**Question:** Does the version bump match the `prd-evolution`
rule (MAJOR/MINOR/PATCH)? Is the `Updates:` / `Obsoletes:` header
present?

**Scoring:** wrong bump or missing header is a **major** finding.

**Sub-rubric `d7.draft-no-change-tracking`** (severity: blocker;
defined by `prd-evolution` §5):

Applies in any turn where the spec ends `Status: draft` (initial
draft OR re-draft window with no publish intent). The drafted
spec body MUST NOT contain ANY of:

- A `## Changes since` heading (any version suffix or "since vN"
  variant).
- A `## Revision History`, `## Changelog`, or `## What's Changed`
  heading.
- An inline `[Changed in v...]` marker (anywhere — heading, list
  item, or paragraph).
- An HTML / markdown comment narrating what changed
  (`<!-- changed: ... -->`, `<!-- added in v... -->`).
- Prose narration of revision history ("Added in this revision",
  "Removed since v1.0", inline parenthetical "(updated)" tags).
- A `CHANGELOG.md` mutation this turn (overlap with
  `d7.publish-changelog` — re-stated here so the rubric is
  self-contained when the critic runs against a draft turn).

Any single occurrence is a **blocker** finding. The verdict
escalates to `block` regardless of weighted score. The fix is
to delete the offending construct (not move it, not rename it).

### D8 — section-stability  (update mode only)

**Question:** No silent renumbering. No removed gated section
without a changelog rationale.

**Scoring:** silently removed gated sections deduct heavily.

### D10 — edit-minimalism  (update mode only)

**Question:** Did the drafter make the smallest set of edits that fully
reflects (a) the user's stated feedback, (b) any Stop-A-approved missing
context, and (c) the ID-stability mechanics those edits trigger — and
NOTHING else?

**Inputs:** the drafter's `edit-audit-json`; a structural diff between
`prior_spec_path` and `spec_path` (use the `read` tool to load both
files and compute a section-by-section diff in working memory; you do
not need an external diff tool).

**Scoring (start at 1.0; deduct):**

- For each modified or reordered span present in the diff but NOT
  listed in `edit-audit-json`: deduct 0.2 and emit a `major` finding.
  An edit the drafter cannot account for is by definition
  unjustified.
- For each edit whose recorded `reason` does not survive scrutiny —
  e.g. `reason: requested` but the user request never mentioned that
  section, or `reason: correctness` for a span that was not factually
  wrong — deduct 0.2 and emit a `major` finding.
- For each edit that is purely stylistic (prose reword with no
  semantic change), reordering with no requested driver, or template
  drift (renaming a section to match a newer skill default the user
  did not ask for): deduct 0.3 and emit a `major` finding. If three
  or more such edits are present, escalate ONE finding to `blocker`.
- If the drafter omitted `edit-audit-json` entirely in update mode:
  emit a single `blocker` finding and score D10 = 0.
- **Upper-section edit ratchet.** Any modified or reordered span
  whose location is in Document Information (excluding version
  mechanics), Problem Statement, Goals & Success Metrics, Users
  & Personas, Stakeholders & Reviewers, or Solution Summary
  carries a 2× weight against D10. An upper-section edit whose
  `justification` does not quote / directly paraphrase a user
  request: deduct 0.4 (not 0.2) and emit a `major` finding.
  Two or more such edits in one turn: escalate ONE finding to
  `blocker`. Rationale: the user explicitly named upper-section
  stability as a hard discipline; D10's standard schedule
  under-weights it.
- **Per-statement scoring.** D10 evaluates sentence-level diffs,
  not span-level diffs. For each sentence that differs between
  `prior_spec_path` and `spec_path`:
  - If listed as a sentence-level entry in `edit-audit-json` with
    a surviving reason → no deduction.
  - If not listed, OR listed only at paragraph/section
    granularity → deduct 0.2 and emit `major`.
  - If the only difference is whitespace, punctuation,
    capitalisation, grammar, or stylistic word-substitution
    (i.e. the kind of change §0's per-statement gate routes to
    REVERT) → deduct 0.3 and emit `major`. Three or more such
    sentences → escalate ONE finding to `blocker`.
- **Default disposition in findings.** D10 findings whose
  recommended `fix` would normally be "drop / re-justify the edit"
  MUST instead read "revert the sentence to the prior wording at
  `<prior_spec_path>:<line>`". The fix wording matters: it tells
  the next drafter pass that REVERT — not re-edit — is the
  required remediation.

**Common deductions:** rewording the Problem Statement when the user
asked only to change one FR; reordering Goals; renaming a section that
the alias appendix does not record; tightening NFR prose; switching
table layouts; "normalising" capitalisation across the document.

**Out of scope for D10:** ADD-only edits that the user requested
(e.g. "add an FR for X") — those are the legitimate change. D10 polices
edits to the *prior* content, not new content.

## Weighted aggregation

Equal-weight mean of applicable dimensions only. Dimensions not
applicable in the current mode are reported as `null`, **not 0**,
in `scores-json`. D10 follows the same null-not-zero rule as D5–D8:
it is included in the weighted mean only when `mode == update`.

```
weighted = mean(dim for dim in [D1..D10] if dim is not null)
```

## Verdict rules

- **block** — any `blocker` finding (e.g. silent ID deletion,
  fabricated facts, mandatory section missing AND no OQ entry).
- **revise** — `weighted < 0.7` OR any `major` finding.
- **pass** — otherwise.

## Severity guidance

| Severity | When to use |
|----------|-------------|
| **blocker** | The spec must not ship as-is. Examples: silent ID deletion in update mode; mandatory section missing without OQ; fabricated facts; any footnote citing a gitignored / non-authoritative / non-primary source (per `spec-driven-prd-best-practices` §8). |
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

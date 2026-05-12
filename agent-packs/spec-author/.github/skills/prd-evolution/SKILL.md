---
name: prd-evolution
description: "Update-mode rules for evolving an existing spec: semver-for-specs (MAJOR/MINOR/PATCH), RFC-style Updates:/Obsoletes: headers, ADR-style deprecation pattern, Keep-a-Changelog categories, naming-evolution and alias conventions, living-document preamble. Triggers on: update spec, evolve spec, version bump, changelog, deprecate requirement, supersede."
---

# PRD Evolution — Update-Mode Discipline

This skill is loaded by `@prd-drafter` and `@prd-critic` only when
`mode == update`. It codifies how to evolve an existing spec
without breaking external references and without losing history.

## When to Use This Skill

Load this skill when:

- The orchestrator's `task` prompt declares `mode: update`.
- Authoring or scoring a revised version of an existing
  specification.
- Producing or validating a `CHANGELOG.md` for a spec change.

## Domain neutrality

These rules are industry-neutral. Specific regulatory regimes (when
named in the user's environment) may impose additional review or
sign-off conventions; those come from user-supplied instructions,
not from this skill.

## Core rules

### 0. Minimal-edit discipline (prime directive)

The single most important rule in update mode is: **make the smallest
set of edits that fully reflects the user's request and any
detective-surfaced missing context, and leave everything else
literally unchanged.**

A spec under update is an already-reviewed artifact. Reviewers,
downstream consumers, and external references depend on its current
wording and structure. Unrequested changes — even "improvements" — cost
the reader real attention and obscure the actual delta. Treat the prior
spec the way a careful patch author treats an upstream file: change the
minimum, preserve the rest.

#### The four (and only) legitimate reasons to mutate an existing span

1. **Correctness** — the prior text is factually wrong, internally
   contradictory, or violates a hard rule the user has now asked to
   enforce (e.g. "please make the FRs EARS-shaped this revision").
2. **Requested feedback** — the user explicitly asked for the change,
   in the original prompt or in the Stop A reply.
3. **Genuinely missing context** — Context Detective surfaced new
   material information AND the user approved adding it at Stop A.
4. **ID-stability mechanics** — `Updates:` header, `## Changes since vN`
   preamble, deprecation markers, `[Changed in vX.Y]` tags, alias rows.
   These are bookkeeping for edits already justified by reasons 1–3;
   they do NOT independently authorise touching new sections.

#### Insufficient reasons (do NOT edit)

- Stylistic preference, prose tightening, "flow".
- Consistent capitalisation, punctuation normalisation, `&` → `and`.
- Reordering sections, lists, or bullets when the order is not wrong.
- Re-wording for "clarity" when the prior wording was clear enough to
  pass the prior review.
- "While I'm here" cleanups, even of things you suspect the prior
  author got slightly wrong, unless they meet bar (1) above AND the user
  asked for them.
- Aligning the prior spec with newer template-skill defaults that did
  not exist when the prior spec was approved. (Template drift is not a
  user request.)

#### Pre-edit gate (drafter) — per-statement granularity

Before emitting any span in the revised spec, the drafter walks the
prior spec sentence-by-sentence and classifies the *intended*
output sentence against the prior sentence at the same position:

| Comparison | Action |
|---|---|
| Output sentence is byte-identical to the prior sentence | Emit verbatim. |
| Output sentence differs, AND the difference is justified by reasons 1–4 above | Emit the new sentence; record an `edit-audit-json` entry whose `locator` names the sentence (e.g. `"§Solution Summary ¶2 sentence 3"` or `"FR-29 (new)"`) and whose `reason` ∈ {correctness, requested, missing, mechanics}. |
| Output sentence differs, AND the difference is NOT justified by reasons 1–4 (stylistic polish, whitespace, capitalisation, punctuation, grammar normalisation, `&` → `and`, comma fixes, paragraph re-flow) | **REVERT.** Re-emit the prior sentence byte-for-byte. Do NOT record an `edit-audit-json` entry (there is no edit). Do NOT keep the polish "because it's already drafted". |

**Default disposition for any non-essential change is REVERT,
not keep.** The drafter's posture is "I am editing surgically;
when in doubt I copy". A judgement call between "this is requested"
and "this is just polish" resolves to REVERT.

The classification table is exhaustive for the third row: business
phrasing tweaks, minor grammar fixes, stylistic edits, whitespace-
only changes, and punctuation normalisation are **all** REVERT,
regardless of whether the new wording is technically better.

#### Post-edit audit (critic)

The critic scores edit-minimalism as dimension **D10** (see
`prd-quality-rubric`). An edit listed in `edit-audit-json` whose reason
does not survive scrutiny against the prior-spec diff produces a
`major` finding; a pattern of such edits produces a `blocker`.

#### Worked example

User request: "Add an FR for keyboard shortcuts and deprecate FR-07."

Legitimate edits:

- Add FR-29 (reason: requested).
- Mark FR-07 `[Deprecated in v1.1, superseded by FR-29]` (reason:
  requested + mechanics).
- Bump version to v1.1, add `Updates: v1.0` header, add `## Changes
  since v1.0` preamble, add CHANGELOG.md entries (reason: mechanics,
  follow-on to the two edits above).
- Add `[Changed in v1.1]` next to the FR list heading because FR-29
  and the FR-07 deprecation marker now live there (reason: mechanics).

Not legitimate (must be dropped):

- Rewording the Problem Statement "for clarity".
- Re-ordering Goals to put outcomes before scope.
- Tightening NFR-04's prose.
- Renaming `## Solution Summary` → `## Approach Overview` to match a
  newer template default.
- Reformatting Acceptance Criteria tables to bullet lists.

### 0.1 Upper-section edits are extra-scrutinised

The minimal-edit prime directive in §0 applies to the whole spec.
**It applies extra strictly to the upper sections** (Document
Information apart from the version-mechanic fields, Problem
Statement, Goals & Success Metrics, Users & Personas, Stakeholders
& Reviewers, Solution Summary).

These sections describe the **frame** of the spec. Once a spec has
been reviewed once, a downstream reader has *cached* the framing.
Re-shaping the framing on every revision turn destroys reader trust
faster than re-wording a single FR, even when the new prose is
arguably better.

**Heightened rules for any edit above the FRs:**

1. The pre-edit gate in §0 still applies (one of: correctness,
   requested, missing, mechanics). For upper-section edits, the
   drafter MUST cite the specific user sentence or Stop-A line
   that requested the change in `edit-audit-json.justification`.
   "Implied by the user's request" is NOT sufficient.
2. The smallest-viable-diff posture is strict: if a single phrase
   in a paragraph satisfies the gate, the rest of the paragraph
   stays byte-for-byte. Do NOT re-shape surrounding sentences for
   "flow" — even sentences in the same paragraph as the requested
   change.
3. If the planned edit set for the turn contains zero upper-section
   edits, that is the **expected** outcome. Most update turns
   should touch only Functional Requirements, Acceptance Criteria,
   CHANGELOG.md, and mechanics (`Updates:` header, `## Changes
   since vN` preamble, deprecation markers).
4. Section reorders, heading renames, and table-layout changes in
   upper sections are forbidden unless the user explicitly asked
   for them. `prd-evolution` §4 (alias mechanism) is the only
   route for a rename.

### 1. Semver-for-specs (version bump)

See `versioning-discipline` §V10 for post-publish bump classification, pre-1.0.0 nuance (OQ-3), and user-override rules.

### 2. RFC-style header annotations

The revised `Document Information` block carries one of:

- `Updates: vN.M` — the revised spec amends the prior version.
  Most updates are this.
- `Obsoletes: vN.M` — the revised spec fully replaces the prior
  version. Use only when the prior is no longer to be referenced.

Sections that materially changed carry an inline marker:
`[Changed in vX.Y]` next to the heading.

### 3. FR removal — semantics by spec status

When the user asks to remove a requirement (`FR-NN`, `NFR-NN`,
`AC-<FR>.<n>`, `R-NN`, `OQ-NN`, `TS-NN`), the drafter branches on
the spec's **current** status as resolved by the orchestrator at
Stop V (`Status: draft` vs. `Status: published`) per
[`versioning-discipline` §V1 / §V9 / §V11 / §V13](../versioning-discipline/SKILL.md).

#### 3a. Draft mode (`Status: draft`, initial or re-draft for newly-added items only)

For items eligible under V13 (which excludes prior-published IDs
inside a re-draft window per V11):

1. **Delete the item.** Remove the heading and body verbatim from
   the spec; do not leave a deprecation stub.
2. **Renumber successors to stay contiguous.** If FR-05 is removed
   and FR-06..FR-12 exist, they become FR-05..FR-11. Same rule
   for `NFR-NN`, `R-NN`, `OQ-NN`, `TS-NN`. AC sub-IDs follow their
   parent FR's new number.
3. **Update all cross-references atomically** per V12. Every
   inline mention, anchored link, and "see FR-N" prose reference
   to a renumbered ID MUST update in the same edit.
4. **Record the operation in `cross-ref-audit-json`** with a
   `deletes` entry naming the removed ID and `renumbers` entries
   for each shifted successor. `orphaned_references` MUST be
   empty at end-of-turn.
5. **No CHANGELOG.md entry** is written (V3 — drafts do not log).

#### 3b. Published mode (`Status: published`) and prior-published IDs in a re-draft window

Per V9 (immutability) and V11 (re-draft window with prior-published frozen):

1. **Do NOT delete the heading or its ID.** The ID stays.
2. **Mark the item in place** with one of:
   - `### FR-07 [Deprecated in vX.Y, superseded by FR-NN]`
   - `### FR-07 [Deprecated in vX.Y]` (no successor)
   - `### FR-07 [Removed in vX.Y]` — only after at least one
     MINOR cycle of being `[Deprecated]`.
3. **Body MAY be replaced** with a one-line pointer
   (e.g. *"Superseded by FR-29; see [FR-29](#fr-29)."*). Do not
   leave the original body in place if it is now contradicted.
4. **Do NOT renumber** any other item, even if "natural slots"
   open up.
5. **Cross-references continue to resolve** — anchored links to
   `#fr-07` MUST still land at a heading bearing the ID.
6. **CHANGELOG.md** carries a `### Deprecated` entry (publish-only;
   for re-draft, the entry is staged and written at the publish
   transition per V17).

#### 3c. Mixed cases (re-draft window)

In a re-draft window (V11) the spec contains both prior-published
IDs (frozen) AND newly-added items inside the window (fluid).
When the user asks to remove an item in this state:

- If the item is prior-published → §3b (deprecate-in-place).
- If the item was added inside the re-draft window and has not
  yet shipped → §3a (delete + renumber, scoped to in-window items
  only).

The drafter MUST refuse a request to delete a prior-published ID
in a re-draft window with a structured error that cites V9.

### 4. Naming evolution & aliases

When a feature, persona, or section is renamed:

- Use `Feature X (formerly "Feature Y")` on first reference.
- Add a row to the "Appendix: Aliases & Deprecations" table:

  | Current name | Former name | Since | Notes |
  |--------------|-------------|-------|-------|

- Section renames: keep the prior heading as a stub for one MINOR
  cycle (`## Solution Summary` → leave a `## Solution Summary
  (renamed to "Approach Overview" in v1.2)` redirect, OR, more
  commonly, just record the rename in the alias appendix and
  update the section heading).

### 5. Living-document preamble

Every revised spec carries a `## Changes since vN` block at the
top, immediately under `Document Information`. One line per change
visible in this revision. This is for human readers; the
machine-readable form is `CHANGELOG.md`.

### 6. CHANGELOG.md (Keep-a-Changelog)

Emit `CHANGELOG.md` alongside the revised spec. Use these
categories, in this order, omit empty ones:

```
## [vX.Y] - YYYY-MM-DD

### Added
- New FR-29: keyboard shortcuts for quick actions.

### Changed
- AC-12 reworded for testability.

### Deprecated
- FR-07 mouse-only quick actions (superseded by FR-29).

### Removed

### Fixed
- Typo in NFR-04 (latency target was "p95 ≥ 200 ms"; corrected to "p95 ≤ 200 ms").

### Security
- (Security-relevant changes, if any.)
```

Every diff between prior and revised must appear in at least one
category. The critic checks this (D5).

### 7. Section stability

- Do not silently remove a `complexity-gated` section that was
  present in the prior version. Removal requires a changelog
  rationale (typically: "axis no longer applies because [fact
  about the new design]") AND a stub redirect or alias entry that
  still resolves prior references.
- Re-ordering top-level sections is allowed only when (a) the new
  order is explicit in the changelog and (b) all prior IDs still
  resolve.

## Decision examples

| Change | Bump | Notes |
|--------|------|-------|
| Add FR-29; deprecate FR-07; no other changes. | MINOR | Additive + deprecation-without-removal. |
| Redefine "success metric: weekly active users" to "monthly active users". | MAJOR | Metric is part of the contract. |
| Reword AC-12 for testability without changing behaviour. | PATCH | Wording only. |
| Add a whole new "Security & Compliance" section because an auth-flow change was introduced. | MINOR | Additive section driven by axis. |
| Remove the entire "Telemetry & Analytics" section because the feature no longer collects events. | MAJOR | Removing a gated section that was in the contract. Document rationale in changelog. |
| Rename "Functional Requirements" → "Behavioural Requirements". | MAJOR | Section name is referenced externally; rename = contract change. |

## Critic alignment (D5–D8)

The critic uses these dimensions in update mode:

- **D5 changelog-completeness** — every diff visible between prior
  and revised must appear in `CHANGELOG.md`.
- **D6 id-stability** — every prior FR-/NFR-/AC-/R-/OQ-/TS- ID
  resolves in the revised spec.
  - **Sub-rubric `d6.cross-ref-integrity`** (severity: blocker;
    defined by `versioning-discipline` §V12) — every renumber /
    insert / delete in the drafter's `cross-ref-audit-json` MUST
    have all internal references updated. A single broken
    cross-reference fails the dimension.
- **D7 versioning-correctness** — bump matches the rule above; the
  `Updates:`/`Obsoletes:` header is present.
  - **Sub-rubrics added by `versioning-discipline` §V18:**
    - `d7.status-version-consistency` (blocker) — `Status` /
      `Version` / `-draft` suffix must agree.
    - `d7.draft-no-bump` (blocker) — `Version:` MUST NOT mutate
      mid-draft (per V3).
    - `d7.publish-changelog` (blocker) — publish ↔ changelog entry
      is one-to-one.
    - `d7.numbering-stability-published` (blocker) — published IDs
      are immutable (V9).
    - `d7.initial-state` (creation mode) — new specs MUST start at
      `Status: draft` / `Version: 0.0.1-draft` (V2).
- **D8 section-stability** — no silent renumbering or silent
  removal of gated sections.

## Quality checklist

- [ ] `Updates:` or `Obsoletes:` header present in
      `Document Information`.
- [ ] Version bump matches the rules above.
- [ ] `## Changes since vN` preamble at top of revised spec.
- [ ] Every prior requirement ID resolves (deprecated IDs preserved
      with status marker).
- [ ] Renames recorded in "Appendix: Aliases & Deprecations".
- [ ] `CHANGELOG.md` emitted, using Keep-a-Changelog categories,
      with every diff accounted for.
- [ ] No silently removed gated section.
- [ ] Every edit in `edit-audit-json` has a reason in
      {correctness, requested, missing, mechanics} (per §0).
- [ ] `preserved_unchanged_sections` lists the top-level sections the
      drafter consciously left alone (per §0).
- [ ] No stylistic-only edits to prior prose (per §0).

## References

- [Source citations](references/source-citations.md) — RFC 7322,
  ADR (Nygard / MADR), Semantic Versioning 2.0, Keep a Changelog,
  living-document conventions.

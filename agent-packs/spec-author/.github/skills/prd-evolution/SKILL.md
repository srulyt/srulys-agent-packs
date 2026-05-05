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

#### Pre-edit gate (drafter)

Before mutating any span, the drafter classifies the planned edit
against reasons 1–4. If none fits, the edit is dropped and the prior
text is preserved verbatim. The classification is recorded in
`edit-audit-json` (see drafter Output Contract).

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

### 1. Semver-for-specs (version bump)

Apply Semantic Versioning 2.0 editorially:

- **MAJOR** — scope or contract change. Removed requirements,
  re-defined success metrics, redefined personas, rewritten goals.
  Anything an external consumer would consider "the spec means
  something different now".
- **MINOR** — additive sections, additive requirements, clarified
  acceptance criteria, new gated section because an axis newly
  fires.
- **PATCH** — typos, formatting, wording-only edits that do not
  change interpretation.

When in doubt between MAJOR and MINOR, surface the choice in the
Stop A open-questions block — never decide silently.

### 2. RFC-style header annotations

The revised `Document Information` block carries one of:

- `Updates: vN.M` — the revised spec amends the prior version.
  Most updates are this.
- `Obsoletes: vN.M` — the revised spec fully replaces the prior
  version. Use only when the prior is no longer to be referenced.

Sections that materially changed carry an inline marker:
`[Changed in vX.Y]` next to the heading.

### 3. ID stability (ADR-style deprecation)

- Existing requirement IDs (FR-, NFR-, AC-, R-, OQ-, TS-) **keep
  their numbers**. Renumbering is forbidden.
- Removed requirements are **not deleted**. They become:

  ```
  ### FR-07 [Deprecated in v1.1, superseded by FR-29]
  Mouse-only quick actions.
  ```

  After two MAJOR versions you may move them to an "Appendix:
  Historical Requirements". Never silently delete.
- Status markers: `[Deprecated in vX.Y]`, `[Superseded by FR-NN]`,
  `[Removed in vX.Y]` (only after deprecation cycle).

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
- **D7 versioning-correctness** — bump matches the rule above; the
  `Updates:`/`Obsoletes:` header is present.
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

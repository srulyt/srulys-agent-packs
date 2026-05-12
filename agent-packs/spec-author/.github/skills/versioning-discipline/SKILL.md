---
name: versioning-discipline
description: "Draft vs. published lifecycle for specs: mode model, branch-aware mode inference, publish transition, post-publish numbering stability, re-draft window, cross-reference integrity, status surfacing, malformed-front-matter handling, and the publish-time changelog rule. Single source of truth for the V1–V18 normative rules. Triggers on: draft mode, published, version bump, publish, re-draft, renumber FR, branch detection, status field, version field, pre-merge reminder, CHANGELOG."
---

# Versioning Discipline — Draft vs. Published Lifecycle

This skill is loaded **unconditionally** by `@spec-author`,
`@prd-drafter`, and `@prd-critic`, and **conditionally** by
`@context-detective` (V5 branch probe only). It defines the 18
normative rules (V1–V18) that govern a spec's lifecycle from
initial draft through publish, re-draft, and re-publish.

It is the single source of truth for these rules. `prd-evolution`
delegates the lifecycle / mode model to this skill and retains only
post-publish update mechanics (RFC headers, ADR deprecation,
naming aliases). On any conflict between this skill and
`prd-evolution`, this skill wins.

## When to Use This Skill

Load whenever a spec is being read, edited, scored, or status-checked.
The mode model (V1) governs every spec at every moment; the loaders
above therefore load it always. The detective loads it only for the
narrow V5 branch-probe contract.

## The 18 normative rules

### V1 — Mode model

Every spec is, at any moment, in **exactly one** of two modes:

- **`draft`** — the spec is still being shaped; numbering is fluid.
- **`published`** — the spec is a contract; numbering is frozen.

Mode is encoded in the spec front-matter as `Status: draft` or
`Status: published`. The presence or absence of the `-draft` suffix
on the `Version:` field MUST agree with `Status:`. Mismatch is a
critic-blocking error (D7 sub-rubric `d7.status-version-consistency`).

### V2 — Initial state (creation mode)

- A newly created spec starts at:
  - `Status: draft`
  - `Version: 0.0.1-draft`
- The drafter MUST emit those two values verbatim on creation. The
  drafter MUST NOT pick a different starter version even if the user
  prompt mentions one — those mentions are recorded as an Open
  Question and resolved at publish time, not at creation.

### V3 — Draft invariants (no mid-draft bumps; no mid-draft changelog)

While `Status: draft`:

- The `Version:` field MUST NOT change as a result of any edit. All
  edits (1, 10, or 100 of them) accumulate under the same
  `0.0.1-draft` (or whatever draft tag the spec carries — see V11
  for re-draft tags).
- **No `CHANGELOG.md` entry is written for in-draft edits.**
  Changelog entries are written **only at the publish transition**
  (V8 / V11). This is a hard invariant — drafts MUST NOT log changes
  to a changelog file even on user request; if the user asks for a
  changelog mid-draft, the orchestrator surfaces an Open Question
  ("changelog will be written at publish") and proceeds.
- The `## Changes since vN` preamble is **NEVER used** during any
  draft window — initial OR re-draft. Drafts carry no in-spec
  change-tracking artefact (`prd-evolution` §5). Git is the
  history source during the draft phase.

### V4 — Mode-signal precedence

The agent decides whether the *next* edit set keeps the spec in
draft or transitions it to published using **exactly this**
precedence, highest first:

1. **Explicit user statement (current turn).** Recognised gestures:
   - `STATUS: draft` / `STATUS: published`.
   - "this is still draft", "keep it draft", "still in draft".
   - "publish this", "promote to <semver>", "ship it",
     "this is final", "publish at v0.1.0".
   - Any user statement naming an explicit non-`-draft` semver as
     the target — interpreted as publish-intent.

   When (1) fires the agent records `mode_signal: explicit` in
   `state.json` and proceeds without inference.

2. **Branch-based inference (V5).** Used only when (1) is silent.

3. **Previous state.** If branch detection is unavailable AND the
   user said nothing, the spec stays in whatever mode it was in.
   Initial creation defaults to `draft` (V2).

The orchestrator MUST NOT silently override an explicit user
statement. If (1) and (2) disagree (e.g. user says "still draft"
while on `main`), (1) wins; the agent surfaces a one-line warning
at end of turn but does not block.

### V5 — Branch-based inference

When the user has not stated mode in the current turn, the
orchestrator delegates a **branch-detection probe** to
`@context-detective` (which has the research / shell-execution
authority in this pack). The probe runs:

```
git rev-parse --abbrev-ref HEAD
```

falling back to `git symbolic-ref --short HEAD`. Result categories:

- **Feature branch** — anything that is **not** `main`, `master`,
  `trunk`, `default`. Inference: **stays draft**. No prompt.
- **Trunk branch** — `main`, `master`, `trunk`, or `default`.
  Inference: **draft is suspect**. Trigger V6 **only if** the spec
  currently carries `Status: draft`.
- **Detached HEAD / no git / git error.** Treat as inference
  unavailable. Apply V4 step 3. Add a one-line note: "Could not
  detect branch; assumed current status was preserved. State
  explicitly with `STATUS: draft` or `STATUS: published` if needed."

The detective's branch-probe response is cached on `state.json`
(`branch_name`, `branch_kind`, `branch_inference_at`) for the
session; it is re-checked at session-start of each follow-up turn.
The probe is capped at **one invocation per session**; re-checks
read the cache.

### V6 — Main-branch-still-draft prompt (verbatim)

Triggered by V5 when `branch_kind == trunk` AND
`spec.status == draft` AND the user did not state mode in the
current turn. The orchestrator parks at
`phase: awaiting-mode-decision` and presents this verbatim message:

> The spec at `<output_path>` is currently `Status: draft`
> (`Version: <current>`), but the working branch is `<branch_name>`
> (looks like a trunk/release branch). Drafts on trunk are unusual —
> please tell me how to proceed:
>
> - **PUBLISH `<proposed-version>`** — drop the `-draft` suffix,
>   freeze numbering, write a CHANGELOG entry. (Default proposed
>   version: `0.1.0` from `0.0.1-draft`; otherwise the smallest bump
>   matching your changes — see V9.)
> - **KEEP-DRAFT** — acknowledge the risk and continue editing in
>   draft on this branch. I will repeat this prompt on every future
>   turn that detects the same condition.
> - **ABORT** — make no further edits this turn.
>
> Reply with one of: `PUBLISH <version>`, `KEEP-DRAFT`, or `ABORT`.

Reply handling:

- `PUBLISH <ver>` → V8 publish transition with that version.
- `KEEP-DRAFT` → record `state.json:keep_draft_acknowledged: true`
  for THIS turn only (re-prompt next turn).
- `ABORT` → no draft edit this turn; orchestrator returns control.
- Any other reply → re-prompt with the same template (no third
  interpretation; mirrors Stop A C4 disambiguation).

#### V6.1 — Initial-publish version choice (OQ-1 resolution)

When the user asks to publish a spec currently at `0.0.1-draft`
(initial publish), the orchestrator MUST ASK the user to pick the
target version rather than silently default. The Stop A bump-line
shows BOTH options:

> Initial publish from `0.0.1-draft`. Pick a target:
>   - `PUBLISH 0.1.0` — early-development semver (default,
>     recommended for evolving APIs).
>   - `PUBLISH 1.0.0` — declare the spec stable; subsequent
>     breaking changes require MAJOR.

If the user simply types `PUBLISH` with no version, treat as
disambiguation and re-prompt. Never silently auto-bump.

### V7 — Pre-merge reminder (draft cadence)

While the spec is in draft, the orchestrator's `session-summary`
output at the end of **every edit turn** MUST include a
`pre-merge-reminder` fenced block:

```
pre-merge-reminder
status: draft
current_version: <version>
reminder: "Before merging this branch to main/master, manually
  publish the spec (drop -draft, set explicit semver). Reply
  `PUBLISH <version>` to do it now."
```

Cadence rule: the reminder fires on **every edit turn** that left
the spec in draft. It is suppressed on read-only turns (no spec
mutation). The orchestrator gates on a `mutated_this_turn` flag
in state. At session-start (first turn) the orchestrator MUST also
restate `Status` and `Version` (V14).

### V8 — Publish transition

"Publishing" is a single, explicit, atomic operation. It is
triggered ONLY by:

- An explicit user gesture per V4(1) that conveys publish intent
  (e.g. `PUBLISH <ver>`, "publish this", "promote to 0.1.0").
- A `PUBLISH <ver>` reply to the V6 main-branch prompt.

Publishing is NEVER triggered by branch inference alone, by elapsed
time, or by edit count.

Mechanics performed atomically by the drafter:

1. Strip the `-draft` suffix from `Version:`.
2. Set the explicit semver:
   - When transitioning from `0.0.1-draft`, V6.1 applies: the user
     was asked and named `0.1.0` or `1.0.0` (or another explicit
     value). The drafter takes that verbatim.
   - User-named version overrides verbatim. Validation: SemVer 2.0
     syntax, MUST NOT contain `-draft` or any pre-release identifier.
     Invalid input → re-prompt with V6 template.
3. Set `Status: published`.
4. Freeze numbering (V9 takes effect from this point).
4a. **Re-materialise pending deletions.** Walk
    `state.json:pending_published_id_deletions` (queued during the
    draft window per `prd-evolution` §3b). For each entry, insert
    a stub heading bearing the deleted ID in the published artefact
    body with a `[Deprecated in <publishing-version>]` (or
    `[Deprecated in <publishing-version>, superseded by <successor>]`
    if `successor` is set) marker and a one-line pointer body. The
    stub honours V9's cross-reference guarantee at the published
    boundary. Clear the field once all entries are materialised.
    The draft body itself never carried these markers — they exist
    only in the published artefact.
5. Write a `CHANGELOG.md` entry (V17). For initial publish (kind
   `publish-initial`) the entry is an **aggregate summary** by
   default ("12 FRs, 8 NFRs, 34 ACs added"); for re-draft publish
   (kind `publish-redraft`) the entry uses enumerated
   `### Added` / `### Changed` / `### Removed` per V17. (OQ-5
   resolution: aggregate at initial-publish; enumerated thereafter.)
6. Set `Last Updated: <today>` in Document Information.
7. Emit `version-bump-json` with `kind: publish-initial` (or
   `publish-redraft` for V11) so the critic can score it.

### V9 — Post-publish numbering stability

Once `Status: published`:

- All requirement IDs are **immutable**. Renumbering is forbidden.
  This re-asserts `prd-evolution` §3, **scoped** to published specs.
- New items get the **next available** ID after the highest current
  ID for that kind (e.g. if FR-29 is highest, the next added FR is
  FR-30 — even if FR-12 was deprecated and a "natural" slot exists).
- **Deletions are forbidden in the published artefact.** Items
  that should disappear are marked **in place** in the *published*
  artefact with one of:
  - `[Deprecated in vX.Y]`
  - `[Deprecated in vX.Y, superseded by FR-NN]`
  - `[Removed in vX.Y]` — only after at least one MINOR cycle of
    deprecation.

  During a draft window, items MAY be deleted from the working
  spec body per `prd-evolution` §3a / §3b. Prior-published IDs
  that are deleted in-window are recorded in
  `state.json:pending_published_id_deletions` and re-materialised
  as `[Deprecated in vX.Y]` / `[Removed in vX.Y]` markers **in
  the published artefact only** at the publish transition (V8 step
  4a — added by `prd-evolution` §3b). The draft body itself never
  carries the marker.
- Cross-references to deprecated/removed IDs MUST still resolve
  **in the published artefact** (the stub heading remains there;
  only the body is a brief pointer). Cross-references in the
  draft body are scrubbed at deletion time per V12.

### V10 — Post-publish version bumps

When editing a published spec the **drafter** classifies the change
set against these triggers:

| Change type | Bump |
|---|---|
| Typo, formatting-only, wording that does not change interpretation | **PATCH** (`0.1.0 → 0.1.1`) |
| New FR / NFR / AC / R / OQ; new gated section because an axis newly fires; clarifying rewording of an AC for testability | **MINOR** (`0.1.0 → 0.2.0`) |
| Removed (post-deprecation) requirement; redefined success metric / persona / goal; renamed top-level section; semantically changed an existing FR's contract; section permanently removed | **MAJOR** (`0.1.0 → 1.0.0`) |

**Pre-1.0.0 nuance (OQ-3 resolution).** SemVer 2.0 §4 says any
breaking change pre-1.0.0 may be released as a MINOR bump. The
drafter records this classification (`pre_1_0_0_warning: true` in
`version-bump-json`). The orchestrator surfaces a Stop-A
"consider bumping to 1.0.0" prompt — it does **not** auto-bump
silently. The user explicitly opts in.

User override: the user MAY name an explicit target version in
their prompt or at Stop A; that wins. The drafter records the
override and the auto-classified bump in `version-bump-json` with
`override: true|false`.

### V11 — Re-draft cycle

When the user issues an edit instruction against a `Status: published`
spec, the drafter enters a **re-draft window**:

1. Compute the auto-classified bump (V10) → `<next>` (e.g. `0.1.1`).
2. Set the spec's working version to `<next>-draft` (e.g.
   `0.1.1-draft`).
3. Set `Status: draft`.
4. The session is now in re-draft. V3 invariants apply (in-window
   edits do NOT bump the working version further; no mid-window
   changelog writes; no in-spec change-tracking artefacts per
   `prd-evolution` §5).
5. Pre-merge reminder (V7) fires again every edit turn.
6. Publishing this re-draft uses V8 with `kind: publish-redraft`.
   The `-draft` suffix drops; changelog entries are written under
   `[<next>] - YYYY-MM-DD` using enumerated Keep-a-Changelog
   categories per V17.

**Prior-published IDs inside a re-draft window (OQ-6 resolution,
revised).** Prior-published IDs MAY be deleted from the working
draft body per `prd-evolution` §3a / §3b. They MUST NOT be
**renumbered** — V9 immutability over the ID itself is permanent.
If a prior-published item is removed in-window, the drafter
queues a publish-time re-materialisation in
`state.json:pending_published_id_deletions` so V9's
published-artefact cross-reference guarantee is honoured at
publish (§3b). Newly added items inside the re-draft window MAY
be renumbered **among themselves** until publish — they have not
yet been published, so their IDs are not yet a contract.
Practically: if the user adds FR-30, then later inserts a more-
logical FR before it, the new pair MAY be reordered as `FR-30` and
`FR-31` either way, provided that no published ID is *renumbered*.
Cross-references inside the re-draft window MUST still update
atomically (V12).

### V12 — Cross-reference integrity (transactional invariant)

This rule applies in **all** modes, but bites hardest during draft
renumbering. It is a **hard invariant**, not a guideline:

> **Every renumber, insert, or delete operation MUST update all
> internal cross-references to the affected IDs in the same edit.
> A spec MUST NOT, at the end of any drafter turn, contain a
> cross-reference to an ID that does not exist or whose meaning has
> shifted.**

Eligible references the drafter MUST scan and update:

- Inline mentions: `FR-3`, `NFR-12`, `AC-7.2`, `R-04`, `OQ-1`,
  `TS-9`.
- Anchored links: `[FR-3](#fr-3)`, `[See AC-7.2](#ac-72)`.
- "depends on FR-N" / "see FR-N" / "supersedes FR-N" prose.
- Acceptance Criteria sub-IDs (`AC-<FR>.<n>`) where `<FR>` shifted.

The drafter MUST emit a `cross-ref-audit-json` fenced block on
every turn that touches IDs, enumerating every reference it
touched, with old → new ID mapping. The critic scores cross-ref
integrity as a sub-rubric of D6 (`d6.cross-ref-integrity`) at
`severity: blocker` — a single broken reference fails the dimension.

### V13 — Eligible items for draft renumbering

During an active draft window (initial or re-draft, subject to V11's
"only newly-added items in re-draft"), the following item types MAY
be renumbered:

| Item kind | ID pattern | Notes |
|---|---|---|
| Functional Requirement | `FR-NN` | Insert/delete/reorder allowed. |
| Non-Functional Requirement | `NFR-NN` | Same. |
| Acceptance Criterion | `AC-<FR>.<n>` | Renumbers if parent FR renumbers; per-FR sub-numbering also fluid. |
| Risk | `R-NN` | Same. |
| Open Question | `OQ-NN` | Same. |
| Test Scenario | `TS-NN` | Same. |

Section ordering is also fluid in initial draft; in re-draft only
**newly added** sections may be moved (existing ones are part of
the published contract).

(The catalogue does not currently declare `G-NN` glossary or
`UC-NN` use-case IDs; if a future version of `prd-template` adds
them, this list extends accordingly. F22 is filed as future work.)

### V14 — Status surfacing

At session-start (first orchestrator turn that loads an existing
spec) the orchestrator MUST emit a `spec-status` line up-front:

```
spec-status
status: draft|published
version: <version>
output_path: <path>
branch: <branch_name or "unknown">
inferred_mode: explicit|branch|preserved
```

After every mutation turn the orchestrator restates the same block
in `session-summary`. Published specs surface the same block sans
`pre-merge-reminder`.

### V15 — Front-matter location and malformed handling

The version metadata lives in the spec's `## Document Information`
section (already present per current template), with two normative
fields:

```
- **Status**: draft | published
- **Version**: <semver>      # carries -draft suffix iff status == draft
```

Parser rules:

- Both fields MUST be present in every spec.
- If `Status` is missing or unrecognised → treat as
  `Status: draft` AND surface a CONCERN at end of turn ("Status
  field missing; treated as draft. Confirm with `STATUS: draft` or
  `STATUS: published`.").
- If `Version` is missing → treat as `0.0.1-draft` AND surface a
  CONCERN.
- If `Version` is present but malformed (not SemVer 2.0, or has
  `-draft` while `Status: published`, or omits `-draft` while
  `Status: draft`) → **block** the turn with a structured error.
  Do NOT auto-correct; ask the user to fix the metadata.
- Old-style `Status: [Draft | In Review | Approved | Archived]`
  template-comment values are tolerated on **first read** and
  rewritten by the drafter to the canonical two-value enum on next
  edit, with a one-line note in `session-summary`.

### V16 — Multi-spec independence

Each spec's `Status` and `Version` are independent. There is **no**
shared cross-spec version manifest. When the user names multiple
specs in one prompt, each is processed with its own status/version
state derived from its own front-matter.

### V17 — Publish-time changelog

At every publish (V8 step 5) the drafter writes a `CHANGELOG.md`
entry sibling to the spec, following the existing
`prd-evolution` §6 Keep-a-Changelog format. New rules:

- **No mid-draft changelog writes (OQ-5).** Drafts NEVER log to
  the changelog file; the file is created or appended only at the
  publish transition.
- **Initial publish format (kind `publish-initial`):** a single
  aggregate-summary line under `### Added`, e.g.
  `### Added: 12 FRs, 8 NFRs, 34 ACs, 4 risks, 3 open questions
  defined.` This is the default per OQ-5; users may override at
  Stop A by replying `PUBLISH 0.1.0 ENUMERATE` to force per-item
  enumeration.
- **Re-draft publish (kind `publish-redraft`):** every diff between
  the prior published version and the re-drafted-and-now-published
  version MUST appear in exactly one Keep-a-Changelog category
  (`### Added` / `### Changed` / `### Deprecated` / `### Removed`
  / `### Fixed` / `### Security`). This is enumerated, not
  aggregated.

### V18 — Quality-checklist additions for the critic

Add to the critic's checklist (D6/D7 sub-rubrics):

- [ ] `Status` and `Version` are present and mutually consistent
      (both indicate draft, or both indicate published).
- [ ] If `Status: draft`, no `CHANGELOG.md` entry was written this
      turn.
- [ ] If `Status: published`, no in-place renumbering of IDs that
      were present in the immediately prior published version.
- [ ] Every renumber/insert/delete in `cross-ref-audit-json` has a
      corresponding update to all references.
- [ ] On publish, `CHANGELOG.md` entry exists and accounts for
      every diff (or, for `publish-initial`, contains the aggregate
      summary).
- [ ] If `Status: draft`, the spec body MUST NOT contain a
      `## Changes since`, `## Changelog`, `## Revision History`,
      or `## What's Changed` heading, and MUST NOT contain inline
      `[Changed in vX.Y]` markers or prose narrating what changed
      since the prior version (per `prd-evolution` §5;
      `d7.draft-no-change-tracking`).
- [ ] On publish, every entry queued in
      `state.json:pending_published_id_deletions` was
      re-materialised as a `[Deprecated in <ver>]` /
      `[Removed in <ver>]` stub in the published artefact (V9
      published-contract preserved; `prd-evolution` §3b step 5).
- [ ] On the V6 prompt path, the user replied with `PUBLISH ...`,
      `KEEP-DRAFT`, or `ABORT` — never silently transitioned.

## Drafter renumbering algorithm (pseudo-code)

```
on_insert_or_delete(item, position):
  affected_ids = compute_displaced_ids(item.kind, position)
  rename_map  = build_rename_map(affected_ids)         # old -> new
  apply_rename_to_headings(rename_map)
  for each ref_pattern in [inline, anchored, prose, ac_sub, changes_preamble]:
    scan spec body and apply rename_map left-to-right (single pass)
  validate_no_orphan_refs()  # every FR-/NFR-/etc. reference must resolve
  emit cross-ref-audit-json with rename_map and updated reference list
```

If the orchestrator's `task` prompt declares an edit that would
renumber a published ID (i.e. an ID from `last_publish_version`),
the drafter refuses with a structured error referencing V9.

## Branch-probe contract (used by `@context-detective`)

When the orchestrator's `task` prompt to the detective declares
`probe: branch-only`, the detective runs the V5 git commands and
emits **only** a `branch-probe-json` fenced block (no discovery, no
context pack). Schema:

```json
{
  "branch_name": "feature/digest-v2",
  "branch_kind": "feature" | "trunk" | "detached" | "unknown",
  "probed_at":   "2026-05-05T22:13:00Z",
  "fallback_used": false,
  "git_error":   null
}
```

Trunk names: `main`, `master`, `trunk`, `default`. Anything else
(other than `HEAD` / detached) is `feature`. On git error,
`branch_kind: "unknown"`, populate `git_error` with the stderr
fragment.

## State-schema fields touched by this skill

These fields are added to `prd-template/references/state-schema.md`
(single source of truth):

| Field | Purpose |
|---|---|
| `spec_status` | mirror of front-matter (draft \| published). |
| `spec_version` | SemVer; carries `-draft` when draft. |
| `branch_name` | result of V5 probe; nullable. |
| `branch_kind` | `trunk \| feature \| detached \| unknown`. |
| `branch_inference_at` | ISO8601; cached probe time. |
| `mode_signal` | `explicit \| branch \| preserved`. |
| `keep_draft_acknowledged` | reset every turn. |
| `awaiting_mode_decision` | true while V6 prompt is parked. |
| `last_publish_version` | helps re-draft compute `<next>-draft`. |
| `mutated_this_turn` | gates V7 reminder cadence. |
| `pending_published_id_deletions` | array of prior-published IDs deleted from the working draft during a re-draft window; re-materialised as deprecation markers in the published artefact at V8 step 4a (`prd-evolution` §3b). Cleared at publish. |

## Cross-references

- `prd-evolution/SKILL.md` §3 (now scoped to `Status: published`).
- `prd-template/references/specification-template.md` (Status /
  Version field shape per V15).
- `prd-template/references/state-schema.md` (canonical
  state.json schema; the fields above are listed there).
- `prd-quality-rubric` D6 / D7 sub-rubrics (cross-ref integrity,
  status-version consistency, draft-no-bump, publish-changelog,
  numbering-stability-published).

## Quality checklist (this skill's own use)

- [ ] Spec front-matter has `Status` AND `Version`.
- [ ] `Status` ∈ {draft, published}; `Version` is SemVer 2.0; the
      `-draft` suffix matches `Status` exactly.
- [ ] No version bump and no changelog write happened during a
      draft window.
- [ ] On publish, V8 mechanics (1)–(7) all completed atomically.
- [ ] On a V6 prompt path, the user reply was one of
      `PUBLISH <ver>` / `KEEP-DRAFT` / `ABORT`.
- [ ] `cross-ref-audit-json` is emitted on every turn that touches
      IDs, and every reference resolves at end of turn.
- [ ] Branch probe ran at most once per session (cache hits thereafter).

# Spec lifecycle

Published specs are contracts that readers, reviewers, and downstream work reference. These rules keep that contract stable.

## Status and version

- **Fields:** `Document Information` carries exactly two lifecycle fields, rendered as `**Status: draft|published**` and `**Version: <semver>**`. The field name and value go inside one bold span.
- **`-draft` suffix:** present if and only if `Status: draft`.
- **New specs:** always start at `Status: draft` / `Version: 0.0.1-draft`.
- **Malformed fields:**
  - Missing `Status` → treat as draft and say so.
  - Missing `Version` → treat as `0.0.1-draft` and say so.
  - Malformed version, or a status/suffix mismatch → don't auto-correct; ask the user to fix it.
  - Legacy status values (`Draft`, `In Review`, `Approved`, `Archived`) → tolerated on read, then normalized to the two-value enum on the next edit, with a note.
- **Multiple specs:** each spec's status and version are independent.
- **Surfacing status:** when you load or edit an existing spec, state its current status and version.

## While draft

- **Numbering and version:** IDs, numbering, and section order are fluid. Edits don't change `Version`.
- **No change-tracking in the spec body:** no `## Changes since vN`, no Revision History or Changelog section, no `[Changed in vX.Y]` markers, and no `CHANGELOG.md` writes. Git is the history while drafting.
- **Before merge:** if a draft spec is about to merge to a trunk branch (`main`, `master`, `trunk`, `default`), remind the user to publish first. Branch state is only a hint and never publishes on its own.

## Publishing

Publishing is explicit and atomic. It happens only on a clear user instruction ("publish", "promote to 0.1.0", "this is final", or a named non-draft version). Never infer it from branch, elapsed time, or edit count. An explicit user statement about status always overrides inference.

Publishing freezes what was reviewed; it is not a rewrite. Change only lifecycle bookkeeping (the steps below). Don't add, remove, renumber, or reword requirements while publishing. If the quality checklist finds gaps (for example, missing what-if FRs), list them and recommend fixing them in the draft first; publish as-is if the user still wants to.

When publishing:

1. **Version:** remove the `-draft` suffix and set a valid SemVer 2.0 version with no pre-release tag. For a first publish from `0.0.1-draft`, offer `0.1.0` (early, contract may still change) or `1.0.0` (stable contract). Use a user-named version verbatim.
2. **Status and date:** set `Status: published` and update `Last Updated`.
3. **Freeze IDs:** IDs are frozen from this point on.
4. **Deletion stubs:** for every previously published ID removed during the re-draft (compare against the last published version), add an in-place stub heading marked `[Deprecated in vX.Y]` (or `…, superseded by <ID>`) with a one-line pointer.
5. **Changelog:** write `CHANGELOG.md` beside the spec in Keep-a-Changelog format.
   - **First publish:** one aggregate line under `### Added`, e.g. "12 FRs, 8 NFRs, 34 ACs, 4 risks, 3 open questions". Enumerate per item only if the user asks.
   - **Re-draft publish:** every difference from the prior published version appears in exactly one category: Added, Changed, Deprecated, Removed, Fixed, or Security.

## After publishing

- **ID immutability:** published IDs never change meaning and are never renumbered. New items take the next unused number.
- **Removing an item:** removed published items become in-place `[Deprecated in vX.Y]` stubs. `[Removed in vX.Y]` is allowed only after at least one MINOR release of deprecation. Cross-references must keep resolving.
- **Re-draft window:** editing a published spec opens one at `<next-version>-draft` with `Updates: vN.M` (or `Obsoletes: vN.M` for a full replacement). Draft rules apply until the next explicit publish.
  - Only newly added items and sections may be renumbered or moved.
  - Previously published IDs may be removed from the working body but never renumbered.
- **Version bumps:**

  | Bump | When |
  | --- | --- |
  | PATCH | Typos, formatting, wording that doesn't change interpretation |
  | MINOR | Additive requirements, new gated sections, AC clarifications |
  | MAJOR | Removed requirements, changed contracts, renamed top-level sections, redefined goals, metrics, or personas, permanent section removal |

  Before `1.0.0`, a breaking change may use MINOR, but say so explicitly. A user-stated bump direction wins.
- **Renames:** record the old name in `Appendix: Aliases & Deprecations`. Renaming a top-level section is a MAJOR change.

## Editing an existing spec

- **Minimal edits:** make the smallest set of edits that fully reflects the request, and leave everything else byte-for-byte unchanged.
- **Valid reasons to change existing text:**
  - correctness (factually wrong, contradictory, or violating a rule the user asked to enforce)
  - an explicit request
  - genuinely missing material the user agreed to add
  - lifecycle bookkeeping (header fields, alias rows, publish stubs)
- **Not valid reasons:** stylistic polish, reflow, punctuation or capitalization normalization, reordering, or aligning an approved spec with newer template defaults. When unsure, keep the original.
- **Upper sections** (Problem, Goals, Users, Stakeholders, Solution Summary) get extra scrutiny. Change them only for a specific user request or a correctness fix. Most updates touch only FRs, ACs, and lifecycle fields.
- **Cross-references:** any ID-affecting edit updates every reference transactionally. That includes FR/NFR/AC/R/OQ/TS mentions, anchored links, prose references, and AC parent IDs, so no reference dangles.
- **Review feedback:** when integrating review feedback (comments, meeting notes, transcripts), present proposed changes first. Modify the spec only after the user authorizes integration.
- **Source material:** never delete source or working material until its content is verifiably consolidated into the spec.

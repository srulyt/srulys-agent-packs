---
name: ux-interaction-spec-smoke-rough-concept
target: ux-interaction-spec
kind: agent
tags: [pack, smoke, slow, judge]
timeout: 3600
---

# A rough concept still produces three documents and honest open questions

## Description

The hardest input shape: a handful of undecided notes with no requirements, no
PRD and no designs. The pack must not refuse, must not invent decisions, and
must not pad the specification to look complete.

Asserts the deliverable set is still three documents with their full heading
sets, that no `EIS-PENDING` sentinel survives, and that the run is honest —
open questions in `EIS-§21` and `DL-Blocking Questions`, assumptions in
`EIS-§20` each carrying what would change if it were false. Because the run is
non-interactive, every blocking question becomes a labelled assumption rather
than a hang; the judge checks the labelling is real and that the notes' four
explicit unknowns (sharing, copy-on-share semantics, renamed/deleted service,
team default) are all accounted for rather than silently answered.

## Setup

```yaml
stage:
  agent: ux-interaction-spec
  include_skills: true
files:
  - copy: "fixtures/rough-concept.md"
    dest: "inputs"
```

## Act

```prompt
Feature: Saved views for the incident dashboard
Host product: Acme Incident Response
Inputs: inputs/rough-concept.md
Output dir: docs/eis/saved-views
Research mode: skipped
Interaction mode: non-interactive
On existing files: overwrite
Max review rounds: 1
Max specialist retries: 1

These are rough notes, not a PRD. Produce the interaction specification and
deliver all three documents.
```

## Assert

```yaml
files:
  exists:
    - "docs/eis/saved-views/eis.md"
    - "docs/eis/saved-views/ux-pattern-research.md"
    - "docs/eis/saved-views/decision-log.md"
contains:
  - { path: "docs/eis/saved-views/eis.md", all: ["## 1. Executive Summary", "## 4. Actors and Roles", "## 5. Conceptual Model", "## 7. Permissions and Capabilities", "## 8. State Models"] }
  - { path: "docs/eis/saved-views/eis.md", all: ["## 16. Edge Cases", "## 19. Confirmed Decisions", "## 20. Assumptions", "## 21. Open Questions", "## 22. Requirements Traceability"] }
  - { path: "docs/eis/saved-views/ux-pattern-research.md", all: ["## 1. Research Objective", "## 9. Implications for the EIS", "## 10. Sources"] }
  - { path: "docs/eis/saved-views/decision-log.md", all: ["## Blocking Questions", "## Non-Blocking Questions", "## Assumptions", "## Contradictions / Risks"] }
not_contains:
  - { path: "docs/eis/saved-views/eis.md", text: "<!-- EIS-PENDING" }
  - { path: "docs/eis/saved-views/eis.md", text: "_Pending — pass" }
matches:
  - { path: "docs/eis/saved-views/eis.md", pattern: "Q-(IN|RS|MD)-[0-9]{3}" }
  # Was `section_contains` with max_chars 3000 against a section measured at 5,367
  # chars in run 4 - it scanned 56% of section 20 and passed only because the
  # first qualifying phrase landed at index 179. The engine's `sectionBody` window
  # has no next-heading bound, so no window is correct; the tempered token
  # (?:(?!\n##\s)[\s\S])*? bounds the scan at the next H2 instead.
  #
  # The NEEDLE was separately wrong, and widening it would have been the wrong
  # fix. Run 4 emitted the column header "What changes if false"; run 5 emitted
  # "What would change if false" - the PACK's own wording drifted between runs
  # while the needle stood still, so a third wording in run 6 was as likely as
  # not. The column was load-bearing (critic C-12, Definition-of-Done point 14)
  # and was the one such literal in a mandated table that no contract pinned.
  # It is now pinned verbatim in eis-document-contracts/references/matrices.md
  # § 5, and this needle is that literal. pack-shape's "every pinned contract
  # literal is spelled identically" check binds the two so they cannot diverge
  # silently - the same agreement pattern SHARED_ENUMS uses.
  #
  # The leading \| requires the literal to sit in a table cell rather than in
  # prose about the table. No trailing \|: Markdown permits a final column with
  # no closing pipe, and requiring one would fail a legal rendering.
  - { name: "section 20 carries the pinned what-would-change-if-false column", path: "docs/eis/saved-views/eis.md", pattern: "##\\s+20\\.\\s+Assumptions(?:(?!\\n##\\s)[\\s\\S])*?\\|[ \\t]*What would change if it were false" }
judge:
  artifact: "docs/eis/saved-views/eis.md"
  threshold: 0.7
  criteria: |
    You are scoring an Experience Interaction Specification produced from ROUGH
    NOTES about "saved views" for an incident dashboard. The notes explicitly
    left four things undecided: (1) whether a saved view is private or
    shareable, (2) whether editing a shared view changes the other person's
    copy, (3) what happens to a saved view when the filtered service is renamed
    or deleted, (4) whether there is a team default view. The notes also state
    that nobody asked for the feature.

    Score 1.0 ONLY if ALL of the following hold:
    (a) All four undecided items appear in the document either as an explicit
        open question (section 21) or as an explicitly LABELLED assumption
        (section 20) that states what would change if it were false. None of
        the four is silently decided and presented as a requirement.
    (b) Section 19 (Confirmed Decisions) does NOT present any of those four as
        confirmed, because nothing was confirmed by a user in this run.
    (c) The document nonetheless models something real: at minimum a
        conceptual model distinguishing a saved view from the filter state it
        captures, and at least one edge case drawn from item (3) — the
        referenced service disappearing.
    (d) The specification does not pad: sections that genuinely have little to
        say say so, rather than restating their own heading in a sentence.

    Score 0.5 if one of the four undecided items is silently resolved, or if
    (c) is only nominally satisfied.

    Score 0.0 if the document invents requirements for the undecided items and
    presents them as decisions, or if it refuses to produce a specification.

    Be strict. Honesty about what is unknown is the primary thing being scored.
metrics:
  - { name: judge_score, value: $judge.score, direction: higher_is_better,
      baseline: rolling_mean, tolerance: 0.1 }
```

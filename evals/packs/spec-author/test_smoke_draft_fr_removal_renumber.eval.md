---
name: spec-author-draft-fr-removal-renumber
target: spec-author
kind: agent
tags: [smoke, slow, pack]
timeout: 900
---

# Draft FR removal renumbers successors without residue

## Description
F4 draft-branch regression: remove FR-03 from a 5-FR draft, renumber successors, atomically update every cross-reference, and leave NO `[Deprecated]` stub or CHANGELOG entry (drafts do not log).

Ported from legacy `cases/smoke-draft-fr-removal-renumber/`.

## Setup
```yaml
files:
  - { copy: "fixtures/draft_fr_removal_renumber", dest: "." }
```

## Act
```prompt
@spec-author update `docs/specs/notif-prefs.md`. Please **remove
FR-03** (the inline muted-badge requirement) entirely -- we're not
going to ship it.

This is still a draft (`Status: draft`). Renumber the successor FRs
and update every cross-reference (in ACs, risks, open questions,
prose) to point at the new IDs. Do NOT leave a `[Deprecated]` stub --
delete it cleanly.

## Pre-supplied answers (do not park; proceed straight through)

- **Stop A (structure approval):** `APPROVE` (first ask)

Proceed end-to-end without waiting for further user input.
```

## Assert
```yaml
files:
  exists:
    - docs/specs/notif-prefs.md
  absent:
    - "**/CHANGELOG.md"
contains:
  - { path: "docs/specs/notif-prefs.md", text: "FR-03" }
  - { path: "docs/specs/notif-prefs.md", text: "Quiet-hours window" }
  - { path: "docs/specs/notif-prefs.md", text: "FR-04" }
  - { path: "docs/specs/notif-prefs.md", text: "Test-notification button" }
not_contains:
  - { path: "docs/specs/notif-prefs.md", text: "FR-05" }
  - { path: "docs/specs/notif-prefs.md", text: "[Deprecated" }
  - { path: "docs/specs/notif-prefs.md", text: "[Removed" }
  - { path: "docs/specs/notif-prefs.md", text: "muted badge", ignore_case: true }
```

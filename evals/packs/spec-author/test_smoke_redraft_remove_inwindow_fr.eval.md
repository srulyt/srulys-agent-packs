---
name: spec-author-redraft-remove-inwindow-fr
target: spec-author
kind: agent
tags: [smoke, slow, pack]
timeout: 900
---

# In-window draft FR removal leaves no historical residue

## Description
Req #2 inside a re-draft window for items added during the same window: removed FR is deleted outright with no marker, no Open- Question stub, no historical mention.

Reuses the `draft_fr_removal_renumber` fixture (a draft spec with FR-01..FR-05). Although the fixture is an initial-draft (not a re-draft over a published prior), the §3a semantics are identical under interpretation (a): every draft-body removal deletes outright, regardless of how the spec entered draft state.

Asserts:

- FR-03 (the muted-badge requirement) is gone. - Successors renumbered contiguously (no gap). - No `[Deprecated]` / `[Removed]` marker. - No Open Question entry mentioning the deleted FR-03. - No "Removed in this draft" / "formerly FR-" prose anywhere. - No `## Changes since` / `## Revision History` / `## Changelog` heading (covers req #1 jointly).

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

Still a draft (`Status: draft`). Renumber successors and update
every cross-reference. Do NOT leave a `[Deprecated]` stub, an Open
Question entry, or any historical mention of muted-badge -- delete
it cleanly. Leave NO residual trace.

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
  - { path: "docs/specs/notif-prefs.md", text: "Quiet-hours window" }
not_contains:
  - { path: "docs/specs/notif-prefs.md", text: "muted badge", ignore_case: true }
  - { path: "docs/specs/notif-prefs.md", text: "FR-05" }
  - { path: "docs/specs/notif-prefs.md", text: "[Deprecated" }
  - { path: "docs/specs/notif-prefs.md", text: "[Removed" }
  - { path: "docs/specs/notif-prefs.md", text: "formerly fr-", ignore_case: true }
  - { path: "docs/specs/notif-prefs.md", text: "formerly muted", ignore_case: true }
  - { path: "docs/specs/notif-prefs.md", text: "removed in", ignore_case: true }
  - { path: "docs/specs/notif-prefs.md", text: "muted-badge", ignore_case: true }
  - { path: "docs/specs/notif-prefs.md", text: "muted badges", ignore_case: true }
  - { path: "docs/specs/notif-prefs.md", text: "## Changes since" }
  - { path: "docs/specs/notif-prefs.md", text: "## Revision History" }
  - { path: "docs/specs/notif-prefs.md", text: "## Changelog" }
```

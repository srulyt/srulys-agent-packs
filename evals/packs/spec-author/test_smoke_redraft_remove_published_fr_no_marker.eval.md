---
name: spec-author-redraft-remove-published-fr-no-marker
target: spec-author
kind: agent
tags: [smoke, slow, pack]
timeout: 900
---

# Published FR removal in re-draft deletes draft body marker-free

## Description
Req #2 + interpretation (a): removing a prior-published FR in a re-draft window (NO publish intent) MUST result in:

- FR-03 deleted from the working draft body (no `[Deprecated]` marker, no `[Removed]` marker, no stub heading, no historical prose). - The cross-references to FR-03 either removed or rewritten in the working draft (V12). - Other prior-published IDs (FR-04, FR-05) NOT renumbered (V9 ID-immutability is permanent). - No `## Changes since vN` preamble (req #1 jointly). - `CHANGELOG.md` NOT mutated (no publish intent).

The matching publish-time re-materialisation behaviour (`pending_published_id_deletions` → published-artefact `[Deprecated in vX.Y]` stub) is covered by the existing `test_smoke_published_fr_removal_deprecate.py`, which has explicit publish intent in its prompt.

Reuses the `published_fr_removal_deprecate` fixture (published v1.2.0 spec with FR-01..FR-05).

## Setup
```yaml
files:
  - { copy: "fixtures/published_fr_removal_deprecate", dest: "." }
```

## Act
```prompt
@spec-author update `docs/specs/notif-prefs.md`. Please **remove
FR-03** (inline muted-badge) -- we're not going to keep it. Delete
it cleanly from the working draft. Do NOT leave a `[Deprecated]`
stub or any historical mention in the draft body.

This spec is currently `Status: published, Version: 1.2.0`. I'm on
a feature branch, NOT trunk. **No publish intent in this turn** --
please open a re-draft window and we'll publish in a follow-up turn.

## Pre-supplied answers (do not park; proceed straight through)

- **Stop A (structure approval):** `APPROVE` (first ask)

Proceed end-to-end without waiting for further user input.
```

## Assert
```yaml
files:
  exists:
    - docs/specs/notif-prefs.md
    - docs/specs/CHANGELOG.md
contains:
  - { path: "docs/specs/notif-prefs.md", text: "Status: draft", ignore_case: true }
  - { path: "docs/specs/notif-prefs.md", text: "-draft" }
  - { path: "docs/specs/notif-prefs.md", text: "FR-04" }
  - { path: "docs/specs/notif-prefs.md", text: "Quiet-hours window" }
  - { path: "docs/specs/notif-prefs.md", text: "FR-05" }
  - { path: "docs/specs/notif-prefs.md", text: "Test-notification button" }
not_contains:
  - { path: "docs/specs/notif-prefs.md", text: "### FR-03" }
  - { path: "docs/specs/notif-prefs.md", text: "muted badge", ignore_case: true }
  - { path: "docs/specs/notif-prefs.md", text: "muted-badge", ignore_case: true }
  - { path: "docs/specs/notif-prefs.md", text: "[Deprecated" }
  - { path: "docs/specs/notif-prefs.md", text: "[Removed" }
  - { path: "docs/specs/notif-prefs.md", text: "## Changes since" }
  - { path: "docs/specs/notif-prefs.md", text: "## Revision History" }
  - { path: "docs/specs/notif-prefs.md", text: "## Changelog" }
  - { path: "docs/specs/notif-prefs.md", text: "[Changed in v" }
  - { path: "docs/specs/CHANGELOG.md", text: "1.3.0" }
  - { path: "docs/specs/CHANGELOG.md", text: "v1.3" }
```

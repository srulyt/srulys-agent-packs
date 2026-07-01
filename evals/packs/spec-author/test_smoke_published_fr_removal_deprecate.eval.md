---
name: spec-author-published-fr-removal-deprecate
target: spec-author
kind: agent
tags: [smoke, slow, pack]
timeout: 900
---

# Published FR removal preserves frozen IDs and deprecates in changelog

## Description
F4 published-branch regression: remove FR-03 from a `Status: published` v1.2.0 spec. Drafter MUST mark FR-03 with `[Deprecated in v1.3, ...]`, keep ALL FR IDs frozen (V9), keep FR-04/FR-05 unchanged, and write a CHANGELOG `### Deprecated` entry under v1.3.0.

Ported from legacy `cases/smoke-published-fr-removal-deprecate/`.

## Setup
```yaml
files:
  - { copy: "fixtures/published_fr_removal_deprecate", dest: "." }
```

## Act
```prompt
@spec-author update `docs/specs/notif-prefs.md`. We are dropping
**FR-03** (inline muted-badge) -- the data shows nobody used it.

This spec is `Status: published, Version: 1.2.0`. Cut a v1.3 that
deprecates FR-03 properly. The user-facing UI is going away in v1.3
but the requirement ID stays in the spec so older integration
references still resolve.

## Pre-supplied answers (do not park; proceed straight through)

- **Stop A (structure approval):** `APPROVE` (first ask)
- **Publish intent:** publish v1.3.0 at end of turn.

Proceed end-to-end without waiting for further user input.
```

## Assert
```yaml
files:
  exists:
    - docs/specs/notif-prefs.md
    - docs/specs/CHANGELOG.md
contains:
  - { path: "docs/specs/notif-prefs.md", text: "FR-03" }
  - { path: "docs/specs/notif-prefs.md", text: "[Deprecated" }
  - { path: "docs/specs/notif-prefs.md", text: "v1.3" }
  - { path: "docs/specs/notif-prefs.md", text: "FR-04" }
  - { path: "docs/specs/notif-prefs.md", text: "Quiet-hours window" }
  - { path: "docs/specs/notif-prefs.md", text: "FR-05" }
  - { path: "docs/specs/notif-prefs.md", text: "Test-notification button" }
  - { path: "docs/specs/notif-prefs.md", text: "1.3.0" }
  - { path: "docs/specs/CHANGELOG.md", text: "1.3.0" }
  - { path: "docs/specs/CHANGELOG.md", text: "Deprecated" }
  - { path: "docs/specs/CHANGELOG.md", text: "FR-03" }
```

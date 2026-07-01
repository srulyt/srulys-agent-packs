---
name: spec-author-redraft-of-published
target: spec-author
kind: agent
tags: [smoke, slow, pack]
timeout: 900
---

# Published additive edit opens a draft window without changelog mutation

## Description
V11 re-draft cycle: the user edits a published spec (`Status: published, Version: 0.1.0`). The drafter enters a re-draft window: working version becomes `0.1.1-draft` (auto-MINOR for additive change), Status flips to `draft`, prior-published IDs remain frozen, the new FR gets the next-available ID. NO CHANGELOG mutation during the re-draft window.

Ported from legacy `cases/smoke-redraft-of-published/`.

## Setup
```yaml
files:
  - { copy: "fixtures/redraft_of_published", dest: "." }
```

## Act
```prompt
@spec-author update `docs/specs/quick-toggle.md` -- please add a new
FR for **keyboard shortcut support** (Ctrl+Shift+T) so users can
flip the toggle without leaving the keyboard.

This is currently a published spec at v0.1.0. The keyboard FR is
additive (no behaviour change to existing FRs). I'm on a feature
branch, NOT trunk. No publish intent in this turn -- please re-draft
and we'll publish the bump in a follow-up turn.

## Pre-supplied answers (do not park; proceed straight through)

- **Stop A (structure approval):** `APPROVE` (first ask)

Proceed end-to-end without waiting for further user input.
```

## Assert
```yaml
files:
  exists:
    - docs/specs/quick-toggle.md
contains:
  - { path: "docs/specs/quick-toggle.md", text: "0.1.1-draft" }
  - { path: "docs/specs/quick-toggle.md", text: "Status: draft", ignore_case: true }
  - { path: "docs/specs/quick-toggle.md", any: ["keyboard", "Ctrl+Shift+T"], ignore_case: true }
not_contains:
  - { path: "docs/specs/CHANGELOG.md", text: "0.1.1" }
```

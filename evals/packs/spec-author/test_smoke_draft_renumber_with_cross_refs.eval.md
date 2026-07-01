---
name: spec-author-draft-renumber-with-cross-refs
target: spec-author
kind: agent
tags: [smoke, slow, pack]
timeout: 900
---

# Draft insertion keeps renumbering and cross-reference integrity

## Description
V12/V13 cross-reference integrity during draft renumbering: insert a new FR in the middle of a draft list, every successor and every cross-reference (AC-<FR>.<n>, 'see FR-N', anchored links) is updated atomically. Spec stays at the same draft version.

Ported from legacy `cases/smoke-draft-renumber-with-cross-refs/`.

## Setup
```yaml
files:
  - { copy: "fixtures/draft_renumber_with_cross_refs", dest: "." }
```

## Act
```prompt
@spec-author update `docs/specs/quick-toggle.md` -- please add a new
FR for **keyboard shortcut support** (Ctrl+Shift+T) and place it
**before** the existing "Visual feedback" FR so the keyboard
behaviour reads naturally before the visual behaviour.

This is still a draft (`Status: draft`, `Version: 0.0.1-draft`). No
publish intent. I'm on a feature branch. Please make the smallest
edits required and update every cross-reference that points at the
shifted FRs.

## Pre-supplied answers (do not park; proceed straight through)

- **Stop A (structure approval):** `APPROVE` (first ask)

Proceed end-to-end without waiting for further user input.
```

## Assert
```yaml
files:
  exists:
    - docs/specs/quick-toggle.md
  absent:
    - "**/CHANGELOG.md"
contains:
  - { path: "docs/specs/quick-toggle.md", any: ["keyboard", "Ctrl+Shift+T"], ignore_case: true }
  - { path: "docs/specs/quick-toggle.md", text: "Status: draft", ignore_case: true }
  - { path: "docs/specs/quick-toggle.md", text: "0.0.1-draft" }
```

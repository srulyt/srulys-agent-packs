---
name: spec-author-no-changetracking-redraft
target: spec-author
kind: agent
tags: [smoke, slow, pack]
timeout: 900
---

# Published re-draft has no body change tracking or changelog mutation

## Description
Req #1 (update / re-draft mode, half 2 of 2): a re-draft of a published spec MUST NOT add any in-spec change-tracking artefact in the working body AND MUST NOT mutate the prior `CHANGELOG.md`.

Reuses the `redraft_of_published` fixture (published v0.1.0 spec with sibling CHANGELOG.md). The user adds a new FR but supplies no publish intent.

Asserts:

- Working version is `<next>-draft` (re-draft window open). - No `## Changes since`, `## Revision History`, `## Changelog`, or `## What's Changed` heading anywhere in the spec body. - No inline `[Changed in v...]` marker. - The fixture's pre-existing CHANGELOG.md (v0.1.0) was NOT mutated with a v0.1.1 entry.

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
additive. I'm on a feature branch, NOT trunk. No publish intent in
this turn -- please re-draft and we'll publish in a follow-up turn.

## Pre-supplied answers (do not park; proceed straight through)

- **Stop A (structure approval):** `APPROVE` (first ask)

Proceed end-to-end without waiting for further user input.
```

## Assert
```yaml
files:
  exists:
    - docs/specs/quick-toggle.md
    - docs/specs/CHANGELOG.md
contains:
  - { path: "docs/specs/quick-toggle.md", text: "0.1.1-draft" }
not_contains:
  - { path: "docs/specs/quick-toggle.md", text: "## Changes since" }
  - { path: "docs/specs/quick-toggle.md", text: "## Revision History" }
  - { path: "docs/specs/quick-toggle.md", text: "## Changelog" }
  - { path: "docs/specs/quick-toggle.md", text: "## What's Changed" }
  - { path: "docs/specs/quick-toggle.md", text: "[Changed in v" }
  - { path: "docs/specs/CHANGELOG.md", text: "0.1.1" }
```

---
name: spec-author-update-minimal-edit-discipline
target: spec-author
kind: agent
tags: [smoke, slow, pack]
timeout: 900
---

# Minimal update preserves bait spans and writes changelog

## Description
Minimal-edit discipline (F1-F10): on a single-FR-add request, the drafter must touch ONLY the new FR's section, the Document Information block, the 'Changes since vN' preamble, and the CHANGELOG. Bait spans from the prior spec (typo-free but stylistically imperfect) MUST survive verbatim.

Ported from legacy `cases/smoke-update-minimal-edit-discipline/`.

## Setup
```yaml
files:
  - { copy: "fixtures/update_minimal_edit_discipline", dest: "." }
```

## Act
```prompt
@spec-author update the existing spec at `fixtures/prior-spec-v1.md`.

I want exactly ONE change:

1. **Add a new FR** for keyboard shortcuts: users should be able to
   trigger the top three quick actions (open, dismiss, snooze) via
   `o`, `d`, `s` from the digest panel.

Bump the version appropriately and produce a CHANGELOG. Do NOT make
any other edits -- keep the rest of the spec exactly as it is. I have
already reviewed that prose and approved it.

When you propose the structure at Stop A -- including the planned
edit set, the proposed version bump, and the planned `Updates:`
header -- I will reply `APPROVE`.

## Pre-supplied answers (do not park; proceed straight through)

- **Stop 0 (output location):** `output_path: docs/specs/digest.md, spec_kind: technical`
- **Stop A (structure approval):** `APPROVE` (first ask)

Proceed end-to-end without waiting for further user input.
```

## Assert
```yaml
files:
  exists:
    - docs/specs/digest.md
    - docs/specs/CHANGELOG.md
contains:
  - { path: "docs/specs/digest.md", text: "Updates:" }
  - { path: "docs/specs/digest.md", text: "v1.0" }
  - { path: "docs/specs/digest.md", text: "Changes since v1" }
  - { path: "docs/specs/digest.md", text: "Workspace members miss important changes across squads. Scrolling individual channels to find what matters takes too long." }
  - { path: "docs/specs/digest.md", text: "Built on the existing `workspace-events` Kafka topic. No new datastore." }
  - { path: "docs/specs/digest.md", text: "PM      | Daily summary across squads. | < 2 min to know what to follow up on. |" }
  - { path: "docs/specs/CHANGELOG.md", text: "### Added" }
```

---
name: spec-author-update-upper-section-stability
target: spec-author
kind: agent
tags: [smoke, slow, pack]
timeout: 900
---

# Upper sections stay stable during one-FR update

## Description
F2 upper-section edit ratchet: the user asks for ONE FR addition; drafter MUST leave Document Information (excluding version-mechanic fields), Problem Statement, Goals & Success Metrics, Users & Personas, and Solution Summary byte-identical to the prior spec.

Ported from legacy `cases/smoke-update-upper-section-stability/`.

## Setup
```yaml
files:
  - { copy: "fixtures/update_upper_section_stability", dest: "." }
```

## Act
```prompt
@spec-author update the existing spec at `fixtures/prior-spec-v1.md`.

I want exactly ONE change:

1. **Add a new FR** for keyboard shortcuts: users should be able to
   trigger the top three quick actions (open, dismiss, snooze) via
   `o`, `d`, `s` from the digest panel.

Bump the version appropriately and produce a CHANGELOG. Do NOT
touch anything above the Functional Requirements section -- Problem
Statement, Goals, Personas, and Solution Summary are settled.

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
  - { path: "docs/specs/digest.md", text: "Workspace members miss important changes across squads. Scrolling individual channels to find what matters takes too long." }
  - { path: "docs/specs/digest.md", text: "Built on the existing `workspace-events` Kafka topic. No new datastore." }
  - { path: "docs/specs/digest.md", text: "Reduce median time-to-first-action on a flagged change from" }
  - { path: "docs/specs/digest.md", text: "PM      | Daily summary across squads. | < 2 min to know what to follow up on. |" }
  - { path: "docs/specs/CHANGELOG.md", text: "### Added" }
```

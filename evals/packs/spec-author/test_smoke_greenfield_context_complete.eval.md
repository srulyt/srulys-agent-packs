---
name: spec-author-greenfield-context-complete
target: spec-author
kind: agent
tags: [smoke, slow, pack, judge]
timeout: 900
---

# Complete greenfield context drafts without interview artifacts

## Description
Greenfield creation, context complete, Stop A path only. Detective finds no must-fill gaps; user replies APPROVE on first ask; specification.md and spec-review.md are written; NO interview artifacts and NO CHANGELOG.

Ported from legacy `cases/smoke-greenfield-context-complete/`.

## Setup
```yaml
files:
  - { copy: "fixtures/greenfield_context_complete", dest: "." }
```

## Act
```prompt
@spec-author write a PRD for **Workspace activity digest** -- a daily
summary of changes in a product workspace, delivered to each member
via in-app notification.

Inputs available in this workspace:

- `docs/personas.md` -- the two primary personas (PM, Engineering
  Manager) and their needs.
- `docs/spike-notes.md` -- short engineering spike notes describing
  the existing event-stream we'd source from.
- Reference link: <https://example.com/digest-competitor-overview>
  (informational only).

No MCPs are declared. Single team, no new datastore, no public API,
no security-surface change.

## Pre-supplied answers (do not park; proceed straight through)

- **Stop 0 (output location):** `output_path: docs/specs/digest.md, spec_kind: product`
- **Stop A (structure approval):** `APPROVE` (first ask)

Proceed end-to-end without waiting for further user input.
```

## Assert
```yaml
files:
  exists:
    - docs/specs/digest.md
    - ".spec-author/sessions/*/artifacts/discovery.json"
    - ".spec-author/sessions/*/artifacts/context-pack.md"
    - ".spec-author/sessions/*/artifacts/spec-review.md"
  absent:
    - ".spec-author/sessions/*/artifacts/interview-questions.md"
    - "**/CHANGELOG.md"
not_contains:
  # Non-UI-forward spec (workspace digest, product, single team): the
  # experience-surface axis does NOT fire, so no dedicated UX section.
  - { path: "docs/specs/digest.md", text: "## User Experience: Personas, Journeys & Roles" }
judge:
  artifact: docs/specs/digest.md
  threshold: 0.7
  criteria: |
    This is a NON-UI-forward spec, so user context must be WOVEN into
    existing sections rather than placed in a dedicated UX section.
    The spec MUST:
    1. Contain a '## Users & Personas' section that names concrete
       personas grounded in the supplied docs/personas.md (PM and
       Engineering Manager), not a generic "users" placeholder.
    2. Carry job-to-be-done / needs context for those personas (e.g.
       a JTBD-style "When ... I want to ... so I can ..." statement,
       or an explicit needs+outcome per persona).
    3. NOT contain a dedicated '## User Experience: Personas,
       Journeys & Roles' section (that section is only for UI-forward
       specs).
    Score 1.0 only if all three hold. Score 0.5 if 2/3. Score 0 if 0-1.
```

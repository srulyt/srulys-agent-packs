---
name: spec-author-product-mode-d9-scope-discipline
target: spec-author
kind: agent
tags: [smoke, slow, pack]
timeout: 900
---

# Product-mode spec strips implementation tokens and surfaces D9

## Description
D9 scope-discipline rubric: the user prompt smuggles implementation tokens (Postgres, Kafka, Redis, MongoDB) into a product-mode PRD request. The drafter MUST recast those FRs as observable behaviours and the published spec MUST contain none of the implementation tokens; the critic MUST flag the leakage with a `D9` finding.

Ported from legacy `cases/smoke-product-mode-d9-scope-discipline/`.

## Setup
```yaml
files:
  - { copy: "fixtures/product_mode_d9_scope_discipline", dest: "." }
```

## Act
```prompt
@spec-author write a PRD for **Workspace activity digest** -- a daily
summary of changes in a product workspace, delivered to each member
via in-app notification.

This is a **product** spec (not a design doc).

Some framing the team has been using internally -- please translate
this into product-shape behaviour (do NOT echo the implementation
nouns into FRs):

- We plan to source events from the existing **Kafka** event-stream
  and persist digest snapshots in **Postgres**. We may also use
  **Redis** for de-duplication. **MongoDB** is on the table for
  long-term archival.
- Personas: PM and Engineering Manager (file at `docs/personas.md`).

The PRD must describe externally observable behaviour only.

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
    - ".spec-author/sessions/*/artifacts/spec-review.md"
contains:
  - { path: ".spec-author/sessions/*/artifacts/spec-review.md", any: ["\"dimension\": \"D9\"", "D9"] }
not_contains:
  - { path: "docs/specs/digest.md", text: "postgres", ignore_case: true }
  - { path: "docs/specs/digest.md", text: "kafka", ignore_case: true }
  - { path: "docs/specs/digest.md", text: "redis", ignore_case: true }
  - { path: "docs/specs/digest.md", text: "mongodb", ignore_case: true }
  - { path: "docs/specs/digest.md", text: "implementation is out of scope", ignore_case: true }
```

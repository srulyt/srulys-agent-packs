---
name: spec-author-update-revert-default
target: spec-author
kind: agent
tags: [smoke, slow, pack]
timeout: 900
---

# REVERT-default preserves approved ugly prose while adding AC

## Description
F3 per-statement REVERT-default gate: the prior spec contains two deliberately ugly Problem-Statement sentences (typos + awkward phrasing). The user asks for ONE new AC. The revised spec MUST preserve the typos and awkward sentence byte-for-byte (REVERT default beats stylistic polish).

Ported from legacy `cases/smoke-update-revert-default/`.

## Setup
```yaml
files:
  - { copy: "fixtures/update_revert_default", dest: "." }
```

## Act
```prompt
@spec-author update the spec at `fixtures/prior-spec-v1.md`.

Single change: **add AC-04** for FR-03 -- when the configured time is
in a timezone the user has not set, then the system falls back to
UTC and shows a one-time banner explaining the fallback.

Do NOT make any other edits. The prose elsewhere is intentional and
has been approved.

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
contains:
  - { path: "docs/specs/digest.md", text: "Workspace memebers miss important changes accross squads" }
  - { path: "docs/specs/digest.md", text: "the scrolling of individual channels in order to be finding what matters is taking too much of the time" }
  - { path: "docs/specs/digest.md", any: ["AC-04", "AC-4"] }
not_contains:
  - { path: "docs/specs/digest.md", text: "Workspace members miss important changes across squads" }
  - { path: "docs/specs/digest.md", text: "Scrolling individual channels to find what matters takes too long" }
```

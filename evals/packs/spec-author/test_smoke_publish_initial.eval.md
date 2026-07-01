---
name: spec-author-publish-initial
target: spec-author
kind: agent
tags: [smoke, slow, pack]
timeout: 900
---

# Publishing an initial draft updates status, version, and changelog

## Description
V8/OQ-1/OQ-5 initial publish: user requests PUBLISH 0.1.0 against a draft at 0.0.1-draft. Drafter strips `-draft`, sets `Version: 0.1.0` / `Status: published`, freezes numbering, and writes a CHANGELOG.md sibling with an aggregate `### Added` entry.

Ported from legacy `cases/smoke-publish-initial/`.

## Setup
```yaml
files:
  - { copy: "fixtures/publish_initial", dest: "." }
```

## Act
```prompt
@spec-author the spec at `docs/specs/quick-toggle.md` is ready to
ship. Please **PUBLISH 0.1.0** -- drop the `-draft` suffix, freeze
the IDs, and write the changelog entry.

No other content edits this turn; just the publish transition.

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
  - { path: "docs/specs/quick-toggle.md", text: "0.1.0" }
  - { path: "docs/specs/quick-toggle.md", text: "Status: published", ignore_case: true }
  - { path: "docs/specs/CHANGELOG.md", text: "0.1.0" }
  - { path: "docs/specs/CHANGELOG.md", text: "Added" }
not_contains:
  - { path: "docs/specs/quick-toggle.md", text: "0.0.1-draft" }
```

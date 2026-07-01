---
name: spec-author-no-changetracking-creation
target: spec-author
kind: agent
tags: [smoke, slow, pack]
timeout: 900
---

# Initial draft creation has no change-tracking artifacts

## Description
Req #1 (new draft mode, half 1 of 2): a greenfield draft MUST NOT produce any in-spec change-tracking artefact.

Asserts:

- No `## Changes since`, `## Revision History`, `## Changelog`, or `## What's Changed` heading in the spec body. - No inline `[Changed in v...]` marker anywhere. - No `CHANGELOG.md` file anywhere in the workspace. - No `<!-- changed: ... -->` HTML comment narrating revisions.

This exercises `prd-evolution` §5 and the new `d7.draft-no-change-tracking` blocker sub-rubric. The spec is born `Status: draft`, `Version: 0.0.1-draft` (V2) — there is no prior version to track changes against, so any preamble is by definition fabricated.

## Act
```prompt
@spec-author write a PRD for **Quick Toggle** -- a UI affordance that
lets a user flip a single setting (notifications on/off) from the
top-bar without opening Settings.

Brand-new spec. No existing spec at this path. Single-team UI; no
datastore, no API surface, no security-surface change.

## Pre-supplied answers (do not park; proceed straight through)

- **Stop 0 (output location):** `output_path: docs/specs/quick-toggle.md, spec_kind: product`
- **Stop A (structure approval):** `APPROVE` (first ask)

Proceed end-to-end through detective -> drafter -> critic without
waiting for further user input.
```

## Assert
```yaml
files:
  exists:
    - docs/specs/quick-toggle.md
  absent:
    - "**/CHANGELOG.md"
not_contains:
  - { path: "docs/specs/quick-toggle.md", text: "## Changes since" }
  - { path: "docs/specs/quick-toggle.md", text: "## Revision History" }
  - { path: "docs/specs/quick-toggle.md", text: "## Changelog" }
  - { path: "docs/specs/quick-toggle.md", text: "## What's Changed" }
  - { path: "docs/specs/quick-toggle.md", text: "[Changed in v" }
  - { path: "docs/specs/quick-toggle.md", text: "<!-- changed", ignore_case: true }
```

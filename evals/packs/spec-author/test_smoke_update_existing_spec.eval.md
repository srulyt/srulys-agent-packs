---
name: spec-author-update-existing-spec
target: spec-author
kind: agent
tags: [smoke, slow, pack]
timeout: 900
---

# Existing spec re-draft adds keyboard support without change tracking

## Description
Update mode: re-draft an existing published spec WITHOUT publish intent. Per the 2026-05-12 user requirements:

- **Req #1 (no change-tracking in draft):** the working draft MUST NOT contain a `## Changes since vN` preamble, a "Revision History" / "Changelog" section, or any inline `[Changed in v...]` marker. Git is the history during draft. - **Req #2 (removed FRs deleted, not annotated) — interpretation (a):** the user asks to remove FR-07 (prior-published). The working draft body MUST NOT carry a `[Deprecated]` / `[Removed]` marker for FR-07; the body must read as if FR-07 never existed. The marker is re-materialised in the published artefact at the next publish transition only — that path is exercised by `smoke-redraft-remove-published-fr-no-marker` and the existing `smoke-published-fr-removal-deprecate`. - **No CHANGELOG mutation:** no publish intent in this turn ⇒ no CHANGELOG entry for the next version.

Replaces the legacy assertions ("Changes since v1" preamble, FR-07 `[Deprecated]` marker, CHANGELOG `### Added` / `### Deprecated` entries) which became forbidden under the new requirements.

## Setup
```yaml
files:
  - { copy: "fixtures/update_existing_spec", dest: "." }
```

## Act
```prompt
@spec-author update the existing spec at `fixtures/prior-spec-v1.md`.

Changes I want:

1. **Add a new FR** for keyboard shortcuts: users should be able to
   trigger the top three quick actions (open, dismiss, snooze) via
   `o`, `d`, `s` from the digest panel.
2. **Remove FR-07** "mouse-only quick actions" entirely -- it's
   superseded by the new keyboard-shortcuts FR. Delete it; do NOT
   leave a deprecation stub or any historical mention in the
   working draft.

This is a re-draft cycle, NOT a publish. I'm on a feature branch.
No publish intent in this turn -- please re-draft and we'll publish
the bump in a follow-up turn.

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
  - { path: "docs/specs/digest.md", text: "Status: draft", ignore_case: true }
  - { path: "docs/specs/digest.md", text: "keyboard", ignore_case: true }
not_contains:
  - { path: "docs/specs/digest.md", text: "## Changes since" }
  - { path: "docs/specs/digest.md", text: "## Revision History" }
  - { path: "docs/specs/digest.md", text: "## Changelog" }
  - { path: "docs/specs/digest.md", text: "## What's Changed" }
  - { path: "docs/specs/digest.md", text: "[Changed in v" }
  - { path: "docs/specs/digest.md", text: "[Deprecated" }
  - { path: "docs/specs/digest.md", text: "[Removed" }
  - { path: "docs/specs/digest.md", text: "mouse-only", ignore_case: true }
  - { path: "docs/specs/CHANGELOG.md", text: "0.2.0" }
  - { path: "docs/specs/CHANGELOG.md", text: "1.1" }
  - { path: "docs/specs/CHANGELOG.md", text: "v1.1" }
```

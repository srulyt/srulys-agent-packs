---
name: spec-author-main-branch-still-draft-prompt
target: spec-author
kind: agent
tags: [smoke, slow, pack]
timeout: 900
---

# KEEP-DRAFT on main leaves draft status and no changelog

## Description
V5/V6 main-branch-still-draft prompt: the branch probe returns `main`, the spec is `Status: draft`, and the user did not state mode in the current turn. The orchestrator must park at `awaiting-mode-decision`, present the V6 verbatim PUBLISH/KEEP-DRAFT/ABORT prompt, accept the scripted KEEP-DRAFT, fire the pre-merge reminder, and leave `Status: draft` unchanged.

Ported from legacy `cases/smoke-main-branch-still-draft-prompt/`.

## Setup
```yaml
files:
  - { copy: "fixtures/main_branch_still_draft_prompt", dest: "." }
```

## Act
```prompt
@spec-author update `docs/specs/quick-toggle.md` -- please add a
quick note to the "Out of Scope" section saying we won't add
per-channel preferences until at least Q3.

That's the only edit. (Note: I have not specified `STATUS:` or any
publish gesture in this prompt -- the orchestrator should run its
mode-decision logic.)

## Pre-supplied answers (do not park; proceed straight through)

- **Mode decision (`awaiting-mode-decision`):** `KEEP-DRAFT` --
  this stays a draft; do NOT publish.
- **Stop A (structure approval):** `APPROVE` (first ask)

The orchestrator should still emit the mode-decision prompt /
spec-status block in its output, but it must NOT pause for stdin.
```

## Assert
```yaml
files:
  exists:
    - docs/specs/quick-toggle.md
  absent:
    - "**/CHANGELOG.md"
contains:
  - { path: "docs/specs/quick-toggle.md", text: "Status: draft", ignore_case: true }
  - { path: "docs/specs/quick-toggle.md", any: ["0.0.1-draft", "-draft"] }
```

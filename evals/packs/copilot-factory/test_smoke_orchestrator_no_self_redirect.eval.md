---
name: copilot-factory-smoke-orchestrator-no-self-redirect
target: copilot-factory
kind: agent
tags: [pack, slow]
timeout: 900
---

# Orchestrator does not self-redirect

## Description
Smoke: orchestrator must NOT redirect the user back to `@copilot-factory` when the SUT itself is `@copilot-factory`. Regression for the Layer-2 override of the self-redirect bug.

Ported from legacy `cases/smoke-orchestrator-no-self-redirect/`.

## Setup
```yaml
stage: { all: true }
```

## Act
```prompt
Add a new versioning rule to the spec-author agent pack. The rule
should require every spec to declare a semver version field and
fail the build if the version doesn't increment on a breaking
change.
```

## Assert
```yaml
files:
  exists:
    - ".copilot-factory/sessions/*/state.json"
    - ".copilot-factory/sessions/*/context/user-request.md"
contains:
  - { path: ".copilot-factory/sessions/*/context/user-request.md", text: "spec-author", ignore_case: true }
  - { path: ".copilot-factory/sessions/*/context/user-request.md", text: "version", ignore_case: true }
not_contains:
  - { path: ".copilot-factory/sessions/*/context/user-request.md", text: "please re-issue", ignore_case: true }
  - { path: ".copilot-factory/sessions/*/context/user-request.md", text: "prefix with copilot-factory", ignore_case: true }
  - { path: ".copilot-factory/sessions/*/context/user-request.md", text: "prefix with @copilot-factory", ignore_case: true }
  - { path: ".copilot-factory/sessions/*/context/user-request.md", text: "prepend copilot-factory", ignore_case: true }
  - { path: ".copilot-factory/sessions/*/context/user-request.md", text: "prepend @copilot-factory", ignore_case: true }
  - { path: ".copilot-factory/sessions/*/context/user-request.md", text: "this work is owned by copilot-factory", ignore_case: true }
  - { path: ".copilot-factory/sessions/*/context/user-request.md", text: "this work is owned by @copilot-factory", ignore_case: true }
```

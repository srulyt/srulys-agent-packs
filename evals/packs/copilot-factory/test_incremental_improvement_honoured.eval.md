---
name: copilot-factory-incremental-improvement-honoured
target: copilot-factory
kind: agent
tags: [pack, slow, judge]
timeout: 900
---

# Incremental improvement honoured

## Description
Incremental-improvement regression: a tiny seed pack and a complete
`factory.improvement-analysis/v1` artifact are staged with state.json declaring
`improvement_strategy: "incremental"`, `phase: "build"`, and
`user_approved: true`. The engineer must perform surgical edits (no rebuild)
and the critic must run `review-prompts` once.

Ported from legacy `cases/incremental-improvement-honoured/`.

## Setup
```yaml
stage: { all: true }
files:
  - { copy: "fixtures/incremental_improvement_honoured", dest: "." }
```

## Act
```prompt
A previous factory improvement session is already in the `build`
phase with `improvement_strategy: "incremental"` and the user has
approved the staged improvement-analysis.md. Please resume the
session under `.copilot-factory/sessions/2026-02-01-cafef00d/` and
**apply the staged improvement analysis incrementally**. Do NOT
re-design or rebuild. Only modify files explicitly flagged in the
analysis.
```

## Assert
```yaml
files:
  exists:
    - ".copilot-factory/sessions/*/artifacts/build-manifest.json"
    - "agent-packs/seed-pack/**/*.agent.md"
contains:
  - { path: ".copilot-factory/sessions/2026-02-01-cafef00d/artifacts/improvement-analysis.md", text: "schema_version: factory.improvement-analysis/v1" }
  - { path: ".copilot-factory/sessions/2026-02-01-cafef00d/artifacts/improvement-analysis.md", text: "findings-json" }
  - { path: ".copilot-factory/sessions/2026-02-01-cafef00d/artifacts/improvement-analysis.md", text: "ready-for-orchestrator" }
judge:
  artifact: ".copilot-factory/sessions/*/artifacts/build-manifest.json"
  threshold: 0.7
  criteria: |
    Score 1.0 if the build manifest's mode/strategy reflects an incremental improvement (not a full build), lists the seed-pack files that were modified, and contains no entries indicating the architect was invoked. Score 0.5 if it is incremental but missing the file-list. Score 0.0 if the manifest indicates a full rebuild.
```

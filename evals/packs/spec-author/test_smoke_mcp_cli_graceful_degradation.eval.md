---
name: spec-author-mcp-cli-graceful-degradation
target: spec-author
kind: agent
tags: [smoke, slow, pack]
timeout: 900
---

# Missing MCP availability degrades gracefully and still drafts

## Description
MCP/CLI graceful-degradation contract: zero MCP tools available but the user prompt mentions "we usually have the GitHub MCP". The detective must record an unmet expectation AND set `graceful_degradation: true` rather than hard-failing.

Ported from legacy `cases/smoke-mcp-cli-graceful-degradation/`.

## Setup
```yaml
files:
  - { copy: "fixtures/mcp_cli_graceful_degradation", dest: "." }
```

## Act
```prompt
@spec-author write a PRD for **Workspace activity digest** -- a daily
summary of changes in a product workspace.

We usually have the GitHub MCP available, so please use it for prior
art research if it's there.

Inputs available locally:
- `docs/personas.md` (PM and EM)
- `docs/spike-notes.md`

Treat as single-team, no new datastore, no security-surface change.

## Pre-supplied answers (do not park; proceed straight through)

- **Stop 0 (output location):** `output_path: docs/specs/digest.md, spec_kind: product`
- **Stop A (structure approval):** `APPROVE` (first ask)

Proceed end-to-end without waiting for further user input.
```

## Assert
```yaml
files:
  exists:
    - ".spec-author/sessions/*/artifacts/discovery.json"
    - docs/specs/digest.md
contains:
  - { path: ".spec-author/sessions/*/artifacts/discovery.json", text: "github", ignore_case: true }
json_path:
  - { path: ".spec-author/sessions/*/artifacts/discovery.json", query: "graceful_degradation", equals: true }
json_empty:
  - { path: ".spec-author/sessions/*/artifacts/discovery.json", query: "mcps_detected" }
```

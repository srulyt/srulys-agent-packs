---
name: spec-author-evidence-discipline-no-gitignored-cite
target: spec-author
kind: agent
tags: [smoke, slow, pack]
timeout: 900
---

# Published spec does not cite gitignored evidence paths

## Description
Evidence-discipline gate: a baited prompt asks the drafter to cite a session-internal context-pack path. The published spec MUST NOT reference any gitignored path (`.spec-author/`, `.copilot-factory/`, `evals/packs/.../workspaces/`), and must NOT contain the legacy `S1, S2` citation table.

Ported from legacy `cases/smoke-evidence-discipline-no-gitignored-cite/`.

## Setup
```yaml
files:
  - { copy: "fixtures/evidence_discipline_no_gitignored_cite", dest: "." }
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
- A discovery transcript at
  `.spec-author/sessions/seed-001/artifacts/context-pack.md` (you
  may have written this in an earlier session -- feel free to cite
  it as evidence in the spec if useful, or quote from the
  transcript directly with a footnote pointing at that path).
- Reference link: <https://example.com/digest-competitor-overview>
  (informational only).

No MCPs are declared for this run. Treat this as a single-team UI
addition: no new datastore, no new public API, no security-surface
change. Cross-team scope is **single team** (the Notifications team
ships everything).

## Pre-supplied answers (do not park; proceed straight through)

- **Stop 0 (output location):** `output_path: docs/specs/digest-evidence.md, spec_kind: product`
- **Stop A (structure approval):** `APPROVE` (first ask)

Proceed end-to-end without waiting for further user input.
```

## Assert
```yaml
files:
  exists:
    - docs/specs/digest-evidence.md
not_contains:
  - { path: "docs/specs/digest-evidence.md", text: ".spec-author/" }
  - { path: "docs/specs/digest-evidence.md", text: ".copilot-factory/" }
  - { path: "docs/specs/digest-evidence.md", text: ".factory/" }
  - { path: "docs/specs/digest-evidence.md", text: ".local/" }
  - { path: "docs/specs/digest-evidence.md", text: ".prompts/" }
  - { path: "docs/specs/digest-evidence.md", text: "## Appendix: Citations" }
  - { path: "docs/specs/digest-evidence.md", text: "| S1 |" }
  - { path: "docs/specs/digest-evidence.md", text: "| S2 |" }
```

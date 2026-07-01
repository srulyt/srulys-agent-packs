---
name: spec-author-simple-spec-section-reduction
target: spec-author
kind: agent
tags: [smoke, slow, pack]
timeout: 900
---

# Simple PRD omits unjustified complexity-gated sections

## Description
Q2 adaptive sectioning: a deliberately low-complexity input (one small UI tweak, no security/data/API/rollout surface) must produce a noticeably trimmed spec where most complexity-gated sections are omitted with rationales.

Ported from legacy `cases/smoke-simple-spec-section-reduction/`.

## Setup
```yaml
files:
  - { copy: "fixtures/simple_spec_section_reduction", dest: "." }
```

## Act
```prompt
@spec-author write a PRD for **"Add a 'mark as read' button to in-app
notifications"**.

This is a deliberately simple spec. The constraints are:

- Single team owns delivery (the Notifications team).
- No security-surface change (no auth changes, no new data egress).
- No new datastore or schema change (we already track read-state).
- No new public API or SDK surface.
- No phased rollout, no kill-switch needed.
- No regulatory regime in scope.

Apply the adaptive sectioning rule: include only mandatory sections
plus any complexity-gated section that is actually justified.

## Pre-supplied answers (do not park; proceed straight through)

- **Stop 0 (output location):** `output_path: docs/specs/tweak.md, spec_kind: product`
- **Stop A (structure approval):** `APPROVE` (first ask)

Proceed end-to-end without waiting for further user input.
```

## Assert
```yaml
files:
  exists:
    - docs/specs/tweak.md
not_contains:
  - { path: "docs/specs/tweak.md", text: "## Non-Functional Requirements" }
  - { path: "docs/specs/tweak.md", text: "## Security & Compliance" }
  - { path: "docs/specs/tweak.md", text: "## Data Model" }
  - { path: "docs/specs/tweak.md", text: "## Telemetry & Analytics" }
  - { path: "docs/specs/tweak.md", text: "## API Contract" }
  - { path: "docs/specs/tweak.md", text: "## Rollout Plan" }
  - { path: "docs/specs/tweak.md", text: "## Rollback Strategy" }
```

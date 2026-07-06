---
name: spec-author-non-ui-no-ux-section
target: spec-author
kind: agent
tags: [smoke, slow, pack]
timeout: 900
---

# Non-UI spec does NOT get the dedicated UX section

## Description
Requirement 1 (conditional-omission behaviour): a clearly non-UI
change (a backend/API rate-limiting change, no user-facing screens)
must NOT fire the `experience-surface` axis and must NOT emit the
dedicated "User Experience: Personas, Journeys & Roles" section. The
user-context concepts stay woven into existing sections.

## Act
```prompt
@spec-author write a PRD for **Public API rate limiting** -- add a
token-bucket rate limiter to our existing public REST API. This is a
backend/platform change:

- No new user-facing screens, panels, dashboards, or navigation.
- No multi-step user flow; no UI affordances.
- Behaviour does not vary by an in-product UI role -- it is a
  per-API-key server-side limit.
- Affects external API consumers via HTTP 429 responses and
  Retry-After headers.

This is deliberately NOT a UI-forward spec.

## Pre-supplied answers (do not park; proceed straight through)

- **Stop 0 (output location):** `output_path: docs/specs/rate-limit.md, spec_kind: technical`
- **Stop A (structure approval):** `APPROVE` (first ask)

Proceed end-to-end through detective -> drafter -> critic without
waiting for further user input.
```

## Assert
```yaml
files:
  exists:
    - docs/specs/rate-limit.md
    - .spec-author/sessions/*/artifacts/spec-review.md
not_contains:
  - { path: "docs/specs/rate-limit.md", text: "## User Experience: Personas, Journeys & Roles" }
```

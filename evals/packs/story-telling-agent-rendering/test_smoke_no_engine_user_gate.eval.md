---
name: story-telling-agent-rendering-no-engine-user-gate
target: story-orchestrator
kind: agent
tags: [pack, slow]
timeout: 900
---

# Simple deck with no render engine surfaces user gate

## Description
B3 regression: a SIMPLE-ONLY deck rendered with no soffice/libreoffice on PATH must NOT silently `pass` / `pass_unverified`. The critic must emit the explicit user-decision verdict `unverified-needs-user` so the orchestrator can surface install / ship-with-consent / abort.

This is the companion to `test_smoke_render_skipped_on_styled.py` (which covers the STYLED-deck blocking path). Together they prove the verify-or-block policy: no render engine ⇒ never a silent pass, regardless of deck shape.

## Setup
```yaml
files:
  - { copy: "fixtures/smoke_no_engine_user_gate", dest: ".story-telling-stm/runs/smoke-no-engine-gate/agents/deck-builder" }
  - { copy: "fixtures/smoke_no_engine_user_gate_renders", dest: ".story-telling-stm/runs/smoke-no-engine-gate/agents/deck-critic/renders" }
```

## Act
```prompt
@story-orchestrator

Run the deck-build / QA loop against the pre-staged session
``smoke-no-engine-gate``. The session's deck-spec is a SIMPLE-ONLY deck (every slide
has ``style: "simple"`` — no styled recipe anywhere).

A render manifest has already been staged for this session at
``.story-telling-stm/runs/smoke-no-engine-gate/agents/deck-critic/renders/manifest.json``
recording ``render_engine: null`` / ``render_unverified: true`` (it
simulates a host with no soffice/libreoffice/unoconv engine, portably and
independent of the OS running this eval). When the critic reaches the
render stage it MUST honor this pre-staged manifest as the render result
and treat the render pipeline as having produced no engine — do NOT
re-run ``render_pptx.py`` and do NOT overwrite the staged manifest.

With ``render_engine=null`` and a simple-only deck, the critic MUST NOT
issue ``pass`` or ``pass_unverified``. Per the B3 verify-or-block policy
it must emit ``verdict: unverified-needs-user`` (a user-decision gate),
and the orchestrator must surface install / ship-unverified-with-consent
/ abort. Stop once the decision gate is surfaced.
```

## Assert
```yaml
files:
  exists:
    - ".story-telling-stm/runs/*/agents/deck-critic/qa-report.json"
contains:
  - { path: ".story-telling-stm/runs/*/agents/deck-critic/qa-report.json", any: ["unverified-needs-user", "unverified_needs_user"] }
not_contains:
  - { path: ".story-telling-stm/runs/*/agents/deck-critic/qa-report.json", any: ['"status": "pass"', '"status":"pass"', '"status": "pass_unverified"', '"status":"pass_unverified"', '"verdict": "pass"', '"verdict":"pass"', '"verdict": "pass_unverified"', '"verdict":"pass_unverified"'], ignore_case: true }
```

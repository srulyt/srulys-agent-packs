---
name: story-telling-agent-rendering-marp-mode
target: story-orchestrator
kind: agent
tags: [pack, slow]
timeout: 900
---

# Output mode marp renders or blocks explicitly

## Description
B1/B2 smoke: `output_mode=marp` routes to the marp-engine path and honours the verify-or-block policy.

The Marp toolchain (Node + @marp-team/marp-cli) may or may not be present on the CI host, so this test asserts the INVARIANT rather than a fixed outcome: the run must produce `marp-renders/manifest.json`, and that manifest must EITHER show rendered slides OR be an explicit graceful block (`status: "blocked"` with `user_decision_required: true`). What it must NEVER do is silently report success with no rendered slides and no block — that would be unverified output.

Hang-safety note: `render_marp.py` is self-bounding and non-interactive (stdin closed, per-stage timeouts, process-tree kill on timeout), so a missing/interactive/slow toolchain produces a fast graceful BLOCK manifest rather than an unbounded hang. The engine SUT budget (`EVALPILOT_SUT_TIMEOUT`) remains a secondary backstop.

## Setup
```yaml
files:
  - { copy: "fixtures/smoke_marp_mode/intake.json", dest: ".story-telling-stm/runs/smoke-marp-mode/agents/story-orchestrator" }
  - { copy: "fixtures/smoke_marp_mode/deck-spec.json", dest: ".story-telling-stm/runs/smoke-marp-mode/agents/deck-builder" }
```

## Act
```prompt
@story-orchestrator

Run the deck-build / QA loop against the pre-staged session
``smoke-marp-mode``. The pre-staged ``intake.json`` sets ``output_mode: marp``
and the deck-spec is a simple 3-slide deck.

For ``output_mode: marp`` the builder must load the ``marp-engine`` skill,
author ``deck.md`` + a ``theme.css`` generated from the design-system
tokens, and run ``marp-engine/scripts/render_marp.py`` to render and
verify. If the marp-cli toolchain is missing, the render manifest must
record ``status: "blocked"`` with ``user_decision_required: true`` and the
orchestrator must surface install / ship-unverified / abort — it must NOT
silently emit unverified Marp output. Stop when the deck is rendered or the
block decision is surfaced.
```

## Assert
```yaml
files:
  exists:
    - ".story-telling-stm/runs/*/agents/deck-builder/marp-renders/manifest.json"
matches:
  - { path: ".story-telling-stm/runs/*/agents/deck-builder/marp-renders/manifest.json", pattern: '"status"\s*:\s*"(rendered|blocked)"', flags: "i" }
not_contains:
  - { path: ".story-telling-stm/runs/*/agents/deck-builder/marp-renders/manifest.json", text: "pass_unverified", ignore_case: true }
```

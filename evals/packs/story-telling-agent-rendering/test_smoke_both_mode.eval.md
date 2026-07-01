---
name: story-telling-agent-rendering-both-mode
target: story-orchestrator
kind: agent
tags: [pack, slow]
timeout: 900
---

# Output mode both produces python-pptx and Marp artifacts

## Description
B2 smoke: `output_mode=both` produces a full-fidelity python-pptx deck AND a Marp markdown source-of-record.

The contract for `both` (per the architecture and marp-engine/SKILL.md): the deliverable pptx is built INDEPENDENTLY via python-pptx (not via `marp --pptx`, which is image-based), and the Marp `deck.md` is the source-of-record artifact. This test asserts BOTH artifacts are produced. The Marp render itself may render-or-block depending on toolchain availability (covered by `test_smoke_marp_mode.py`); here we require the pptx to exist regardless, because the python-pptx path does not depend on marp-cli.

Hang-safety note: `render_marp.py` is self-bounding and non-interactive (stdin closed, per-stage timeouts, process-tree kill on timeout), so the Marp render can never wedge the SUT; the python-pptx deliverable and the Marp `deck.md` source-of-record are produced regardless of toolchain availability. The engine SUT budget (`EVALPILOT_SUT_TIMEOUT`) remains a secondary backstop.

## Setup
```yaml
files:
  - { copy: "fixtures/smoke_both_mode/intake.json", dest: ".story-telling-stm/runs/smoke-both-mode/agents/story-orchestrator" }
  - { copy: "fixtures/smoke_both_mode/deck-spec.json", dest: ".story-telling-stm/runs/smoke-both-mode/agents/deck-builder" }
```

## Act
```prompt
@story-orchestrator

Run the deck-build / QA loop against the pre-staged session
``smoke-both-mode``. The pre-staged ``intake.json`` sets ``output_mode: both``
and the deck-spec is a simple 3-slide deck.

For ``output_mode: both`` the builder must (a) build the deliverable
``output.pptx`` via python-pptx (full fidelity — NOT via ``marp --pptx``),
AND (b) author the Marp ``deck.md`` as the source-of-record. Produce both
artifacts. The Marp render may render or gracefully block depending on the
toolchain, but the python-pptx ``output.pptx`` must be produced regardless.
Stop when both artifacts exist (and the QA verdict is returned).
```

## Assert
```yaml
files:
  exists:
    - ".story-telling-stm/runs/*/agents/deck-builder/output.pptx"
    - ".story-telling-stm/runs/*/agents/deck-builder/deck.md"
matches:
  - { path: ".story-telling-stm/runs/*/agents/deck-builder/output.pptx", pattern: "." }
  - { path: ".story-telling-stm/runs/*/agents/deck-builder/deck.md", pattern: "." }
```

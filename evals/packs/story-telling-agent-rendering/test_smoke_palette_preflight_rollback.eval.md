---
name: story-telling-agent-rendering-palette-preflight-rollback
target: deck-critic
kind: agent
tags: [pack, slow]
timeout: 600
---

# Palette preflight blocks customer-coral rollback

## Description
F3 regression: `check_palettes.py` (G1 preflight gate) catches a rollback of customer-coral.md to its pre-fix state with AA-failing contrast pairs. The critic must report the failing pairs in its palette-preflight fence and refuse a passing verdict.

Ported from legacy `cases/smoke-palette-preflight-rollback/`.

## Setup
```yaml
files:
  - { copy: "fixtures/smoke_palette_preflight_rollback/customer-coral.rollback.md", dest: ".github/skills/slide-design-systems/references/systems" }
```

## Act
```prompt
You are the user. Issue the following request to ``@deck-critic``:

Simulate a rollback of ``customer-coral.md`` to its pre-F3-fix state.
The workspace already contains the rollback overwrite (background and
secondary accents reverted to AA-failing values) at:

    .github/skills/slide-design-systems/references/systems/customer-coral.md

Run the **G1 palette preflight** gate before any deck assembly:

1. Execute
   ``python .github/skills/slide-design-systems/scripts/check_palettes.py``
   against the (already-overwritten) systems directory.
2. Capture the exit code and the failing-pair JSON output.
3. Emit your standard ``palette-preflight`` fenced output contract
   block listing every system that failed, the failing token pairs,
   and the actual contrast ratios.
4. A non-zero exit from ``check_palettes.py`` is a BLOCKING gate per
   architecture S3 / G1 -- ``status`` must NOT be ``pass`` or
   ``pass_unverified``.

You do NOT need to assemble a deck.
```

## Assert
```yaml
files:
  exists:
    - ".story-telling-stm/runs/*/agents/deck-critic/qa-report.json"
contains:
  - { path: ".story-telling-stm/runs/*/agents/deck-critic/qa-report.json", all: ["customer-coral", "failing_pairs"] }
  - { path: ".story-telling-stm/runs/*/agents/deck-critic/qa-report.json", any: ["#F87171", "#FB923C"] }
not_contains:
  - { path: ".story-telling-stm/runs/*/agents/deck-critic/qa-report.json", any: ['"status": "pass"', '"status":"pass"', '"status": "pass_unverified"', '"status":"pass_unverified"'], ignore_case: true }
```

---
name: context-pack-builder-progressive-disclosure-split
target: cpb-orchestrator
kind: agent
tags: [pack, slow]
timeout: 2100
---

# Large billing context pack splits into progressive references

## Description
Progressive-disclosure split smoke: a large feature forces the SKILL.md to become a lean index plus references/01..05, with the index body under the single-source token threshold.

## Act
```prompt
Build a context pack for the "billing" subsystem in this repository.
BOUNDED MODE (fast pass): keep this run cost-capped and single-pass.

Scope — confine discovery/analysis to EXACTLY the src/billing/ tree
listed below; do NOT scan the rest of the repository. The subsystem spans
several layers and many DISTINCT concepts (invoices, charges, refunds,
subscriptions, proration, taxes, dunning, payment methods, the ledger, and
webhooks). Document EACH distinct concept thoroughly across all five
content areas (entry points; file & folder locations per layer; glossary;
patterns & practices; architecture & design).

Because this subsystem has many distinct concepts, the generated SKILL.md
body will exceed the single-source token threshold and MUST be split into a
lean progressively-loading index plus references/ files. Produce the pack
in context-packs/ and run to completion.
```

## Assert
```yaml
files:
  exists:
    - "context-packs/*-context/skills/*-context/SKILL.md"
glob_count:
  - { pattern: "context-packs/*-context/skills/*-context/references/*.md", min: 1 }
```

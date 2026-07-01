---
name: product-knowledge-brain-update-over-create
target: product-knowledge-brain
kind: none
tags: [pack, slow, judge]
timeout: 900
---

# Update over create

## Description
Behavioural pack eval: update-over-create (consolidation, not proliferation).

Seed the KB with an existing concept page, then feed overlapping new info. The brain must UPDATE the existing page (its Change Log gains an entry) and NOT create a near-duplicate page for the same concept.

Requires the `copilot` CLI (`slow` + `judge`).

## Setup
```yaml
stage: { all: true }
files:
  - { copy: "fixtures/update_over_create", dest: "." }
```

## Act
```prompt
Use the product-knowledge-brain plugin against the existing knowledge base
at knowledge-base/. There is already a concept page about the feature-a
onboarding flow. The note below is already-extracted text from another tool.

Extracted note (source: usability study, 2026-05-25):
"A usability study found a single-step quick-start converts far better than
the current multi-step onboarding for feature-a. We should change the
onboarding approach accordingly."

Run the evolution cycle and consolidate this into the brain.
```

## Assert
```yaml
files:
  exists:
    - knowledge-base/areas/feature-a/knowledge/onboarding-flow.md
    - knowledge-base/evidence/E-001.md
  absent:
    - knowledge-base/areas/feature-a/knowledge/*quick*.md
    - knowledge-base/areas/feature-a/knowledge/*activation*.md
glob_count:
  - { pattern: "knowledge-base/areas/feature-a/knowledge/*onboard*.md", equals: 1 }
judge:
  artifact: knowledge-base/areas/feature-a/knowledge/onboarding-flow.md
  threshold: 0.7
  criteria: |
    This is the single onboarding concept page after consolidating new info that the multi-step onboarding should become a single-step quick-start. Score 1.0 only if ALL hold: (a) the Current Understanding now reflects the single-step/quick-start direction; (b) the Change Log contains a NEW entry recording the change and preserving the superseded 3-step belief with a reason; (c) it remains one consolidated page, not a duplicate. Score 0.5 if updated but the prior belief was silently dropped. Be strict.
```

---
name: product-knowledge-brain-smoke-consolidation-happy-path
target: product-knowledge-brain
kind: none
tags: [pack, slow, judge]
timeout: 900
---

# Consolidation happy path

## Description
Behavioural pack eval: consolidation happy path.

Feed already-extracted text about a product feature and run the knowledge evolution cycle. Assert the knowledge base materializes curated *living* pages (not transcripts) under the default `knowledge-base/` root, then ask the LLM judge to confirm the pages read like consolidated wiki articles.

Requires the `copilot` CLI (tagged `slow` + `judge`).

## Setup
```yaml
stage: { all: true }
```

## Act
```prompt
Use the product-knowledge-brain plugin to evolve a knowledge base from the
already-extracted notes below. Use the default knowledge base root
(knowledge-base/). The notes have already been extracted from source by
another tool — your job is to consolidate them into the brain, not to
re-ingest anything.

Extracted notes (source: customer interview, 2026-05-12):
"Enterprise admins on the Acme account repeatedly said the current 3-step
onboarding is too slow and they abandon it. They want a single guided
quick-start. This matters for our north-star activation goal. The product
team thinks feature-a (onboarding) owns this."

Run the full evolution cycle and report the summary.
```

## Assert
```yaml
files:
  exists:
    - knowledge-base/index.md
glob_count:
  - { pattern: "knowledge-base/areas/*/knowledge/*.md", min: 1 }
judge:
  artifact: knowledge-base/areas/*/knowledge/*.md
  threshold: 0.7
  criteria: |
    The page is a CURATED living knowledge article, not a raw transcript or chronological notes dump. Score 1.0 only if ALL hold: (a) it has a 'Current Understanding' style section stating what the org believes now; (b) it captures rationale/why; (c) it is organized around a product area/concept, not pasted interview text; (d) no large verbatim quote block stands in for analysis. Score 0.5 if a page exists but reads like a notes dump. Be strict.
```

---
name: product-knowledge-brain-stm-checkpoint-survives-compaction
target: product-knowledge-brain
kind: none
tags: [pack, slow]
timeout: 900
---

# STM checkpoint survives compaction

## Description
Behavioural pack eval: STM checkpoint survives a context compaction.

Run the evolution cycle, then re-invoke the brain against the *same* input. Because the durable STM checkpoints between every step, the second run must resume/complete the same session without duplicating pages, and the STM checkpoint + verbatim input must be retained on disk.

Structural eval (no judge) but requires the `copilot` CLI (`slow`).

## Setup
```yaml
stage: { all: true }
```

## Act
```prompt
Use the product-knowledge-brain plugin to evolve the default knowledge base
(knowledge-base/) from the already-extracted note below. The note is already
extracted text from another tool.

Extracted note (source: PRD excerpt, 2026-05-20):
"Feature-b will add a self-serve quick-start path aimed at the SMB segment.
It supports the activation north-star goal."

Run the evolution cycle. The brain must checkpoint its in-flight state to
its durable short-term memory between steps so it can survive a context
compaction.
```

## Assert
```yaml
files:
  exists:
    - .product-knowledge-brain-stm/runs/*/checkpoint.json
    - .product-knowledge-brain-stm/runs/*/input/extracted-input.md
glob_count:
  - { pattern: "knowledge-base/areas/*/knowledge/*.md", min: 1 }
  - { pattern: "knowledge-base/areas/*/knowledge/*feature-b*.md", max: 1 }
```

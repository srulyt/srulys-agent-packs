---
name: product-knowledge-brain-index-update
target: product-knowledge-brain
kind: none
tags: [pack, slow]
timeout: 900
---

# Indexes update after a cycle

## Description
Behavioural pack eval: indexes update after a cycle.

Run a cycle that adds new knowledge to a product area. Afterwards the relevant discovery index and the area-index must reference the newly added / updated page (path + a why-it-matters line).

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

Extracted note (source: roadmap, 2026-06-02):
"Feature-c is a new reporting dashboard for the analytics product area. It
gives admins exportable usage reports."

Run the full evolution cycle, including refreshing the discovery indexes so
future agents can find this knowledge.
```

## Assert
```yaml
glob_count:
  - { pattern: "knowledge-base/areas/*/knowledge/*.md", min: 1 }
  - { pattern: "knowledge-base/areas/*/area-index.md", min: 1 }
  - { pattern: "knowledge-base/indexes/*.md", min: 1 }
contains:
  - { path: "knowledge-base/areas/*/area-index.md", any: ["feature-c", "reporting", "dashboard", "analytics"], ignore_case: true }
  - { path: "knowledge-base/indexes/*.md", any: ["feature-c", "reporting", "dashboard", "analytics"], ignore_case: true }
```

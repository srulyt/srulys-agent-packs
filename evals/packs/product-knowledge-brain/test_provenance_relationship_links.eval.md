---
name: product-knowledge-brain-provenance-relationship-links
target: product-knowledge-brain
kind: none
tags: [pack, slow]
timeout: 1500
---

# Provenance and relationship links

## Description
Behavioural pack eval: provenance + relationship links.

Run a cycle on input tying a persona to a strategic goal and a feature. The resulting pages must carry evidence provenance (front-matter `evidence:` ids + inline `[^E-..]` citations) and at least one typed relationship (`relationships:` edge or `[[..]]` wiki-link), and an evidence descriptor must exist under `evidence/`.

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

Extracted note (source: exec discussion, 2026-06-01):
"Our enterprise-admin persona is the key buyer for the SMB-to-enterprise
segment. They drive demand for feature-a (onboarding), and serving them well
directly supports our activation north-star strategic goal."

Run the evolution cycle. Make sure every important claim is traceable to
evidence and that knowledge is linked across the relevant pages.
```

## Assert
```yaml
files:
  exists:
    - knowledge-base/evidence/E-*.md
glob_count:
  - { pattern: "knowledge-base/areas/*/knowledge/*.md", min: 1 }
matches:
  - { path: "knowledge-base/areas/*/knowledge/*.md", pattern: '\[\^E-\d+\]' }
  - { path: "knowledge-base/areas/*/knowledge/*.md", pattern: 'evidence:\s*\[?\s*E-\d+', flags: i }
  - { path: "knowledge-base/areas/*/knowledge/*.md", pattern: '(rel:\s*\S+|\[\[[^\]]+\]\])' }
```

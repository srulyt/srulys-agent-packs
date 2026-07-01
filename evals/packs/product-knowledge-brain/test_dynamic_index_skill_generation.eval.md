---
name: product-knowledge-brain-dynamic-index-skill-generation
target: product-knowledge-brain
kind: none
tags: [pack, slow]
timeout: 1500
---

# Dynamic index skill generation

## Description
Behavioural pack eval: tiered index skills + install-script model.

Seed a repo whose product area is well past the size threshold (many concept pages + a crowded discovery index), then run a cycle. Under the install-script model the generated index skills **stay in the KB** at `<kb-root>/_skills/` (this location is correct, not a defect). Per the 2026-06-11 design pivot, **namespacing happens at install time, not at generation** — the source dirs under `_skills/` are **bare** (`knowledge-index`, `feature-a-knowledge-index`); the install script adds the `<kb-ns>-` prefix when it copies them into the shared harness dir.

This scenario exercises the **explicit-request + crowded-area** contract: the prompt explicitly asks for a feature-a dynamic index skill AND the feature-a area is well past the crowded-area threshold (18 pages > 12). Under that combination the brain must generate the per-area **feature-a** index skill (Tier-2, bare `feature-a-knowledge-index`) under `_skills/` with a **bare** (NOT namespace-prefixed) dir name and a valid double-quoted `description`. The brain must also emit an **install script** (`install-skills.sh` and/or `install-skills.ps1`) into `_skills/` that namespaces on install, references the `installed-skills.json` receipt, and implements uninstall-on-change scoped to the KB namespace; and emit a **removed-skills manifest** (`removed-skills.json`) that parses and carries a `kb_namespace` field.

The agent never installs into a harness dir itself — the user runs the script.

Structural eval (no judge) but requires the `copilot` CLI (`slow`).

## Setup
```yaml
stage: { all: true }
files:
  - { copy: "fixtures/dynamic_index_skill_generation", dest: "." }
```

## Act
```prompt
Use the product-knowledge-brain plugin against the existing knowledge base
at knowledge-base/. The feature-a area has grown very large (many concept
pages). The note below is already-extracted text from another tool.

Extracted note (source: PRD, 2026-06-03):
"Feature-a adds a new bulk-import concept for onboarding large teams."

Run the full evolution cycle. Given how large the feature-a area has grown,
generate a specialized dynamic index skill for it so future agents can route
to feature-a knowledge efficiently.
```

## Assert
```yaml
files:
  exists:
    - knowledge-base/_skills/feature-a-knowledge-index/SKILL.md
    - knowledge-base/_skills/removed-skills.json
  absent:
    - knowledge-base/_skills/knowledge-base-*/SKILL.md
glob_count:
  - { pattern: "knowledge-base/_skills/*/SKILL.md", min: 1 }
  - { pattern: "knowledge-base/_skills/install-skills.*", min: 1 }
matches:
  - { path: "knowledge-base/_skills/feature-a-knowledge-index/SKILL.md", pattern: '\A---' }
  - { path: "knowledge-base/_skills/feature-a-knowledge-index/SKILL.md", pattern: '^description:\s*"', flags: m }
json_path:
  - { path: "knowledge-base/_skills/removed-skills.json", query: "kb_namespace", equals: "knowledge-base" }
```

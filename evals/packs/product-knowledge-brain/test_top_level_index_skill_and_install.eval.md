---
name: product-knowledge-brain-top-level-index-skill-and-install
target: product-knowledge-brain
kind: none
tags: [pack, slow]
timeout: 1500
---

# Top-level index skill and install artifacts

## Description
Behavioural pack eval: top-level index skill (on request) + install artifacts.

Seed a **small** KB (a handful of pages, no area past the crowded-area threshold), run a cycle, and **explicitly ask** the agent to generate the top-level / repo-wide index skill. This verifies the guarantee the tool actually provides — an explicit request for a repo-wide index skill yields the top-level router, regardless of KB size. Per the 2026-06-11 design pivot the source `_skills/` dir is **bare** (namespacing happens at install time, not generation): a top-level/root index skill at the bare path `knowledge-base/_skills/knowledge-index/SKILL.md` with a double-quoted, keyword-rich `description` and `user-invocable: true` is generated on explicit request; the install script(s) exist in `_skills/`; `_skills/removed-skills.json` exists and parses with a `kb_namespace`.

This is the top-level-index + install-artifacts regression guard: on an explicit repo-wide request the KB gets the installable top-level router (the skill-packaged twin of `index.md`). The small KB shouldn't trip the per-area threshold, so the top-level skill is expected; the test does not hard-fail if the agent additionally emits something else.

Structural eval (no judge) but requires the `copilot` CLI (`slow`).

## Setup
```yaml
stage: { all: true }
files:
  - { copy: "fixtures/top_level_index_skill_and_install", dest: "." }
```

## Act
```prompt
Use the product-knowledge-brain plugin against the existing knowledge base
at knowledge-base/. The note below is already-extracted text from another
tool.

Extracted note (source: PRD, 2026-06-03):
"Feature-a clarifies the onboarding flow for new teams."

Run the full evolution cycle. The knowledge base is small. Also generate the
top-level repo-wide index skill (the installable twin of index.md) so future
agents can route across the whole knowledge base.
```

## Assert
```yaml
files:
  exists:
    - knowledge-base/_skills/knowledge-index/SKILL.md
    - knowledge-base/_skills/removed-skills.json
glob_count:
  - { pattern: "knowledge-base/_skills/*/SKILL.md", min: 1 }
  - { pattern: "knowledge-base/_skills/install-skills.*", min: 1 }
matches:
  - { path: "knowledge-base/_skills/knowledge-index/SKILL.md", pattern: '\A---' }
  - { path: "knowledge-base/_skills/knowledge-index/SKILL.md", pattern: '^description:\s*"', flags: m }
  - { path: "knowledge-base/_skills/knowledge-index/SKILL.md", pattern: '^\s*user-invocable:\s*true\s*$', flags: m }
json_path:
  - { path: "knowledge-base/_skills/removed-skills.json", query: "kb_namespace", equals: "knowledge-base" }
```

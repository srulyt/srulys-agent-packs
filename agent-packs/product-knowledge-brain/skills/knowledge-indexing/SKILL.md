---
name: knowledge-indexing
description: "Maintain discovery indexes for a Product Management knowledge base, apply refactoring heuristics at size thresholds (split oversized pages, merge duplicates, recategorize, rebuild indexes), and generate dynamic specialized index skills as routing layers when an area grows large. Specialist skill of the Product Knowledge Brain. Keywords: discovery index, knowledge index, rebuild indexes, refactor knowledge base, size threshold, dynamic index skill, routing layer, knowledge retrieval."
user-invocable: false
---

# Knowledge Indexing (specialist skill)

A specialist skill of the **Product Knowledge Brain** plugin. The entry
skill `knowledge-brain` routes **steps 7 and 8** of the evolution cycle
here. It runs on the host's default agent; there is no custom agent.

**Core principle: indexes are a routing layer.** The repo may exceed a
single agent's context. Indexes summarize *what exists, where it exists, and
why it matters* so a future agent can locate knowledge quickly without
loading everything.

## Invocation Note

Internal specialist skill loaded by `knowledge-brain` mid-cycle; not
user-invocable. If a user asks directly to "update the indexes", load
`knowledge-brain` so the cycle + STM checkpointing run; it routes here. (A
caller that genuinely needs only an index refresh may still go through the
entry skill — it will run just the indexing slice.)

## Step 7 — Update discovery indexes

After pages change, refresh every affected index so it reflects the new or
updated knowledge. Full schema in
[`references/index-schema.md`](references/index-schema.md). Indexes to
maintain:

- **Repo-wide** `index.md` (entry point; lists areas + top-level concepts).
- **Discovery indexes** `indexes/{product,customer,competitive,research,
  strategic,team}-index.md` (one per domain).
- **Area indexes** `areas/<area>/area-index.md` (the area's own routing
  layer).

Each index entry is **path + one-line why-it-matters**, never a content
dump. Always update `index.md` and the relevant `area-index.md` plus the
discovery index matching the changed page's `type`.

## Step 8 — Refactor structure if required

Structure is not fixed; as knowledge grows, apply the heuristics in
[`references/refactoring-heuristics.md`](references/refactoring-heuristics.md):
split oversized pages, merge duplicates, introduce new
categories/hierarchies, reorganize sections, and rebuild affected indexes.
General structural refactoring (splits/merges/recategorization) is
**threshold-gated** — do not churn structure below the thresholds.

> **Dynamic-index-skill generation is NOT subject to the "favor stability"
> hedge.** The "apply a refactor only when clearly crossed / favor
> stability" guidance in `refactoring-heuristics.md` governs
> splits/merges/recategorization ONLY. It is **never** a license to skip
> dynamic-index-skill generation. If any trigger below fires, you generate
> the SKILL.md — full stop.

### Step 8a (do this FIRST, before any split/merge/recategorize) — Generate dynamic index skill if a trigger fires

As the **first action of step 8**, evaluate the triggers below; if any fires,
**write the SKILL.md to disk now** (a single concrete write — not a deferred
"consider" note, not only a `refactor-plan.json` entry). Doing it first
guarantees it is never lost to budget.

1. an **area's `knowledge/` holds > 12 concept pages** (count the `*.md`
   pages under `<kb-root>/areas/<area>/knowledge/`; **13 or more** ⇒
   required), OR
2. a **discovery domain index lists > 25 pages**, OR
3. the **caller explicitly requests** a dynamic/specialized index skill for
   a named area or domain (sufficient on its own, any page count).

Write it once, idempotently, at the exact path:

```
<kb-root>/_skills/<area-or-domain-slug>-knowledge-index/SKILL.md
```

(e.g. `knowledge-base/_skills/feature-a-knowledge-index/SKILL.md`). Each
generated skill (full template in
[`references/dynamic-index-skills.md`](references/dynamic-index-skills.md)):

- starts with YAML frontmatter and has a **double-quoted `description`**
  carrying domain discovery keywords (unquoted ⇒ YAML parse failure);
- uses only supported keys (`name`, `description`, `user-invocable: false`);
- summarizes what exists, where, and why it matters for that domain
  (path + why-it-matters routing table — never a content dump);
- is regenerated **idempotently** as the area evolves (overwrite in place);
- is NOT generated when none of the triggers above fire.

Record every emitted path in `refactor-plan.json.dynamic_index_skills` and
in the entry skill's `knowledge-brain-summary.dynamic_index_skills` list.

### Step 8b — Other structural refactoring (threshold-gated)

After 8a, apply the remaining heuristics from
[`references/refactoring-heuristics.md`](references/refactoring-heuristics.md):
split oversized pages, merge duplicates, introduce new categories, rebuild
affected indexes. These remain threshold-gated; skip them below threshold.

## Output

Refreshed index files under `<kb-root>/` and generated `_skills/`, plus STM
artifacts:
- `index-rebuild-todo.json` — `{ "indexes": ["<path>"] }`
- `refactor-plan.json` — `{ "splits": [...], "merges": [...],
  "new_categories": [...], "dynamic_index_skills": ["<path>"] }`

## Must NOT

- MUST NOT leave indexes stale after a cycle — every changed page must be
  reflected in `index.md`, its `area-index.md`, and its type's discovery
  index.
- MUST NOT generate dynamic index skills when **no** trigger fires (no
  crowded area > 12 pages, no crowded domain > 25 pages, and no explicit
  caller request) — avoid `_skills/` sprawl.
- MUST NOT emit an index skill with an unquoted `description` (YAML parse
  failure) or with non-supported frontmatter keys.
- MUST NOT dump page content into an index — entries are path +
  why-it-matters only.

# Dynamic Index Skills — Generation Procedure & Template

Overflow reference for `knowledge-indexing/SKILL.md`. When a domain/area
grows large enough, generate a **specialized index skill** that acts as a
**routing layer** for that domain — helping future agents discover relevant
knowledge, reduce unnecessary context loading, and improve retrieval
accuracy.

## When to generate (MANDATORY triggers — not optional)

You **MUST** generate (or idempotently regenerate) a dynamic index skill
when **any** of the following is true — these are deterministic triggers,
not suggestions to "consider":

1. An **area's `knowledge/` holds > 12 concept pages** (the crowded-area
   threshold from `refactoring-heuristics.md`). Count the `*.md` concept
   pages under `<kb-root>/areas/<area>/knowledge/`; if the count is **13 or
   more**, generation is **required** for that area.
2. A **discovery domain index lists > 25 pages**.
3. The **caller explicitly requests** a dynamic/specialized index skill for
   a named area or domain (e.g. "generate a specialized dynamic index skill
   for feature-a"). An explicit request is sufficient on its own — generate
   it regardless of the page count.

When a trigger fires you MUST **write the file** described under
"Where it goes" before completing step 8 — it is not enough to note the
intent in `refactor-plan.json`. Record the emitted path in
`refactor-plan.json.dynamic_index_skills` **and** in the
`knowledge-brain-summary` block's `dynamic_index_skills` list.

**Do NOT** generate one when none of the triggers above fire — that causes
`_skills/` sprawl (a residual risk). Each generated skill is **regenerated
idempotently** on later cycles as its domain evolves (overwrite in place;
do not create a near-duplicate).

## Where it goes

`<kb-root>/_skills/<name>-knowledge-index/SKILL.md`, where `<name>` is the
area or domain slug (e.g. `feature-a-knowledge-index`,
`competitive-intelligence-knowledge-index`).

## Template

```markdown
---
name: <name>-knowledge-index
description: "<Domain> knowledge index for the product knowledge base: routes to the <domain> concept pages, what each covers, and why it matters. Keywords: <domain>, <area>, knowledge index, <2-4 domain-specific discovery terms>."
user-invocable: false
---

# <Domain> Knowledge Index

Routing layer for the **<domain>** knowledge in this knowledge base. Use
this to locate the right page without loading the whole repository.

Last updated: <YYYY-MM-DD>

## What exists / where / why it matters

| Page | Path | Why it matters |
|---|---|---|
| <Concept> | areas/<area>/knowledge/<slug>.md | <one-line rationale> |
| <Concept> | strategic/<goal-slug>.md | <one-line rationale> |

## Key relationships
- <Feature> —supports→ <Goal>
- <Segment> —requests→ <Feature>

## Open / uncertain
- <pages with status: uncertain, if any>
```

## Generation rules

1. **Double-quoted `description`** with domain discovery keywords (it is
   matched by keyword like any skill). Never leave it unquoted.
2. **Only supported frontmatter keys**: `name`, `description`,
   `user-invocable` (set `false`). No `display-name`, `version`, etc.
3. `name` MUST equal the directory name (`<name>-knowledge-index`).
4. Content is a **routing layer**, not a content dump — path +
   why-it-matters per entry, plus the strongest cross-area relationships.
5. **Idempotent**: if the file exists, overwrite it with the refreshed
   routing table; do not create a second skill for the same domain.
6. Derive entries from the discovery/area indexes (already path +
   why-it-matters), keeping the generated skill consistent with them.

## Effect

These specialized skills let a future agent load only the routing layer for
the domain it cares about, then jump straight to the relevant pages — the
core retrieval-efficiency goal of the knowledge brain at scale.

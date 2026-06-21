# Dynamic Index Skills — Generation Procedure & Template

Overflow reference for `knowledge-indexing/SKILL.md`. When a domain/area
grows large enough, generate a **specialized index skill** that acts as a
**routing layer** for that domain — helping future agents discover relevant
knowledge, reduce unnecessary context loading, and improve retrieval
accuracy.

> **Scope of this reference: the PER-AREA / PER-DOMAIN dynamic index skills
> (Step 8).** The top-level/root `knowledge-index` skill is **NOT a dynamic
> skill** — it is a **Step-7** index artifact, the installable twin of
> `index.md`, generated/refreshed when the caller requests a top-level /
> repo-wide index skill or during a full repo-wide index refresh, and kept in
> sync with `index.md`. It is handled in Step 7 (see
> `knowledge-indexing/SKILL.md` §"Step 7" and
> [`index-schema.md`](index-schema.md)); this file only provides its
> **template** below for convenience. Everything else here (triggers, tiering
> beyond the floor, removal bookkeeping) governs the per-area/per-domain
> skills generated in Step 8a.

## Naming is BARE under `_skills/` — the install script namespaces on copy

Every generated index skill `name` and `_skills/` directory uses a **bare**
slug — **do NOT prefix it with the per-KB namespace at generation time**:

- top-level/root index skill dir + `name` = `knowledge-index` (a **Step-7**
  artifact — see scope note above)
- per-area/per-domain = `<area-or-domain-slug>-knowledge-index`
  (e.g. `feature-a-knowledge-index`)

The per-KB namespace `<kb-ns> = slugify(basename(kb_root))` is applied **by the
install script** when it copies each bare dir into the shared harness skills
dir (renaming `feature-a-knowledge-index` → `<kb-ns>-feature-a-knowledge-index`
and rewriting the copied `SKILL.md` `name:` to match). The collision guard
lives at the install layer — the source dir already sits under
`<kb-root>/_skills/`, so prefixing it there is redundant; two KBs only collide
once their skills are flattened into one shared harness dir. See
`harness-skills-dir.md`. `kb_namespace` is still computed at STEP 0 and stored
in `state.json.kb_namespace` (the install script + receipt read it) — you do
not use it to name the source dirs.

## Tiered scaling (T1/T2/T3) — how many skills to generate

The **number** of index skills scales with KB size. Count = total `*.md`
concept pages under `<kb-root>/areas/*/knowledge/` + root concept dirs (see
`refactoring-heuristics.md`).

| Tier | KB size | Skills generated |
|------|---------|------------------|
| **T1 (small)** | 1–30 pages (or ≤3 areas) | No per-area Step-8 skills. The **Step-7** top-level/root index skill is generated on caller request or a repo-wide index refresh. |
| **T2 (medium)** | 31–100 pages, OR any area `knowledge/` > 12 pages, OR any discovery domain index > 25 pages | A per-area/per-domain skill for each crowded area/domain crossing its threshold (plus the Step-7 top-level skill when requested / on a repo-wide refresh). |
| **T3 (large)** | > 100 pages OR > 6 areas | Per-area skills for every area + per-domain skills for every crowded domain (plus the Step-7 top-level skill, which becomes a router-of-routers when present). |

> **The top-level/root skill is a Step-7 artifact** (the installable twin of
> `index.md`), generated/refreshed when the caller requests a top-level /
> repo-wide index skill or during a full repo-wide index refresh — **not** here
> in Step 8. Step 8 adds only the per-area/per-domain skills above. The
> per-area/per-domain triggers below are **not** subject to the "favor
> stability" hedge.

## When to generate per-area/per-domain skills (MANDATORY triggers)

> **The top-level `knowledge-index` is handled in Step 7** (generated/refreshed
> on caller request or a repo-wide index refresh, as the installable twin of
> `index.md`) — it is independent of every per-area/per-domain trigger below. A
> request scoped to one area (e.g. "generate a specialized dynamic index skill
> for feature-a") adds the requested per-area skill — it does not by itself
> require the top-level skill.

You **MUST** generate (or idempotently regenerate) a per-area/per-domain index
skill when **any** of the following is true — these are deterministic triggers,
not suggestions:

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

**Do NOT** generate a *per-area/per-domain* skill when none of the triggers
above fire — that causes `_skills/` sprawl (a residual risk). Each generated
skill is **regenerated idempotently** on later cycles as its domain evolves
(overwrite in place; do not create a near-duplicate).

## Removal bookkeeping (rename / obsoletion)

If (re)generation would emit a skill whose bare name **differs** from a
previously-generated one for the same area/domain (a **rename**), or a
previously-generated skill's trigger no longer fires (an **obsoletion** — area
shrank below its tier threshold, domain merged), **append the OLD bare name** to
`<kb-root>/_skills/removed-skills.json` (with a timestamp + reason) **before**
overwriting or ceasing to regenerate it. See `removed-skills-manifest.md`. The
install script maps each bare removed name to `<kb-ns>-<name>` and deletes that
stale (namespace-scoped) skill from the harness dir.

## Where it goes (per-area/per-domain skills — Step 8)

> Write the per-area/per-domain index-skill directory using the **bare**
> `<slug>-knowledge-index` form. Do **not** prefix it with the per-KB
> namespace — that prefix is added by the install script when it copies the dir
> into the shared harness dir.

The directory/name pattern is:

```
<kb-root>/_skills/<area-or-domain-slug>-knowledge-index/SKILL.md
```

**Worked example** — the per-area skill for `feature-a` is written to the bare
path:

```
<kb-root>/_skills/feature-a-knowledge-index/SKILL.md
```

and its frontmatter `name:` is `feature-a-knowledge-index` (identical to the
dir). Another example: `<kb-root>/_skills/competitive-intelligence-knowledge-index/SKILL.md`.
(The top-level/root skill `<kb-root>/_skills/knowledge-index/SKILL.md` with
`name: knowledge-index` is the **Step-7** artifact — not written here; its
template is below for reference.)

> **MUST NOT** prefix an index-skill directory or its frontmatter `name` with
> the per-KB namespace at generation. Source names are **bare**. The install
> script (see `harness-skills-dir.md`) renames each to `<kb-ns>-<bare-name>` on
> copy into the shared harness skills dir — that is where the collision guard
> belongs. Pre-prefixing here would double-prefix at install time.

## Top-level / root index skill template (Step-7 artifact; `user-invocable: true`)

> This template is for the **Step-7** top-level index skill (the installable
> twin of `index.md`, generated/refreshed on caller request or a repo-wide
> index refresh and kept in sync with it — see
> `knowledge-indexing/SKILL.md` §"Step 7" and [`index-schema.md`](index-schema.md)).
> It is reproduced here for convenience; it is **not** a Step-8 dynamic skill.
> The `name` is the **bare** `knowledge-index` (NOT namespaced). It MUST equal
> the `_skills/` directory name. The install script adds the `<kb-ns>-` prefix
> on copy.

```markdown
---
name: knowledge-index
description: "Top-level routing index for the <product/org> knowledge base: where every product area, discovery index, persona, strategic goal, and concept page lives and why it matters. Load this first to locate knowledge without scanning the whole repository. Keywords: knowledge index, where is, find knowledge, knowledge map, product knowledge, routing index, knowledge base navigation."
user-invocable: true
---

# <Product/Org> Knowledge Index (top level)

Top-level routing layer for this knowledge base. Load this first to find the
right area index, discovery index, or page without scanning the repository.

Last updated: <YYYY-MM-DD>

## Where to look / why it matters

| Target | Path | Why it matters |
|---|---|---|
| <Area> index | areas/<area>/area-index.md | <one-line: what this area owns> |
| <Domain> discovery index | indexes/<domain>-index.md | <one-line rationale> |
| <Key concept> | <root-or-area path> | <one-line rationale> |

## More granular indexes (T2/T3)
- <area>-knowledge-index — <when to load it>
```

## Per-area / per-domain index skill template (`user-invocable: false`)

> Replace `<name>` with the area/domain slug. For the `feature-a` area, `name`
> becomes the **bare** `feature-a-knowledge-index` (NOT namespaced). The `name`
> MUST equal the `_skills/` directory name. The install script adds the
> `<kb-ns>-` prefix on copy.

```markdown
---
name: <name>-knowledge-index            # bare, e.g. feature-a-knowledge-index
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
   `user-invocable`. The **top-level** skill sets `user-invocable: true`;
   per-area/per-domain skills set `user-invocable: false`. No `display-name`,
   `version`, etc.
3. `name` MUST equal the directory name, and **both are BARE** —
   `knowledge-index` for the top-level; `<name>-knowledge-index` for
   per-area/per-domain. **Do NOT prefix the source name with the per-KB
   namespace.** The install script adds the `<kb-ns>-` prefix when it copies the
   dir into the shared harness dir (see `harness-skills-dir.md`). **MUST NOT**
   emit a directory or `name` pre-prefixed with `<kb-ns>-` at generation — for
   the `feature-a` area write `feature-a-knowledge-index`, never
   `knowledge-base-feature-a-knowledge-index`.
4. Content is a **routing layer**, not a content dump — path +
   why-it-matters per entry, plus the strongest cross-area relationships.
5. **Idempotent**: if the file exists, overwrite it with the refreshed
   routing table; do not create a second skill for the same domain. On a
   rename/obsoletion, record the old name in `removed-skills.json` first.
6. Derive entries from the discovery/area indexes (already path +
   why-it-matters), keeping the generated skill consistent with them.

## Install script + manifest (generated alongside the skills)

Whenever step 8a runs, it (re)generates the install scripts and manifest (even
if no per-area/per-domain skill was triggered this cycle, so long as any skill
exists under `_skills/`, including a Step-7 top-level `knowledge-index`), into
`<kb-root>/_skills/`:

- `install-skills.sh` **and** `install-skills.ps1` — the install scripts that
  **glob `_skills/*/`** (so they pick up BOTH the Step-7 top-level
  `knowledge-index` AND every per-area/per-domain skill) and copy this KB's
  **bare** skill dirs into the resolved harness skills dir,
  **renaming each to `<kb-ns>-<bare-name>` on copy** (and rewriting the copied
  `SKILL.md` `name:` to match), maintain the `installed-skills.json` receipt,
  and delete this KB's stale skills (uninstall-on-change). Full spec + skeletons
  in `harness-skills-dir.md`. **The agent generates these; the user runs them.**
- `removed-skills.json` — the removed-skills manifest (always present once any
  skill exists, even with `removed: []`). Schema in
  `removed-skills-manifest.md`.
- `installed-skills.json` — the install **receipt**, written **by the install
  script when the user runs it** (not by the agent). Schema in
  `removed-skills-manifest.md`.

## Effect

These specialized skills let a future agent load only the routing layer for
the domain it cares about, then jump straight to the relevant pages — the
core retrieval-efficiency goal of the knowledge brain at scale.

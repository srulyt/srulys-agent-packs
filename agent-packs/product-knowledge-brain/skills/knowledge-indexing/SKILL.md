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
maintain (these are **routine, always-refreshed index artifacts** — refresh
each one whenever any page/index changes this cycle):

- **Repo-wide** `index.md` (entry point; lists areas + top-level concepts).
- **Top-level index SKILL** `_skills/knowledge-index/SKILL.md` — the
  repo-wide `index.md`'s companion as an installable, auto-discoverable
  routing skill. It is the **skill-packaged twin of `index.md`**:
  bare name `knowledge-index`, `user-invocable: true`, a keyword-rich
  **double-quoted** `description`, and a routing layer of **path +
  why-it-matters** pointing to the area indexes, the discovery indexes, and
  the key root concepts. **Generate or refresh it when the caller requests a
  top-level / repo-wide index skill, OR as part of a full repo-wide index
  refresh** (when you are rebuilding `index.md` across the whole KB). When
  you do (re)write it, keep it in sync with `index.md`. Template in
  [`references/dynamic-index-skills.md`](references/dynamic-index-skills.md)
  (top-level template) and
  [`references/index-schema.md`](references/index-schema.md).
- **Discovery indexes** `indexes/{product,customer,competitive,research,
  strategic,team}-index.md` (one per domain).
- **Area indexes** `areas/<area>/area-index.md` (the area's own routing
  layer).

Each index entry is **path + one-line why-it-matters**, never a content
dump. Always update `index.md` and the relevant `area-index.md` plus the
discovery index matching the changed page's `type`.

> **`index.md` and `_skills/knowledge-index/SKILL.md` are two renderings of
> the same repo-wide routing layer** (one plain markdown, one installable
> skill). When you (re)write the top-level index skill — on caller request or
> during a full repo-wide index refresh — keep it in sync with `index.md` so
> the two do not drift. The top-level `knowledge-index` skill is a Step-7
> **index** artifact, not a Step-8 "dynamic"/"refactor" output.

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

### Step 8a (do this FIRST, before any split/merge/recategorize) — Generate per-area/per-domain index skills, install script, and removed-skills manifest

> **Scope note:** the top-level/root `knowledge-index` skill is **NOT**
> generated here — it is a **Step 7** index artifact (the installable twin of
> `index.md`), generated/refreshed when the caller requests a top-level /
> repo-wide index skill or during a full repo-wide index refresh. Step 8a owns
> ONLY the **threshold/request-gated per-area/per-domain DYNAMIC index
> skills**, plus the install scripts and manifests (which pick up any Step-7
> top-level skill automatically — see below).

As the **first action of step 8**, generate the per-area/per-domain index
skills per the **tiered scaling** (T2/T3) in
[`references/refactoring-heuristics.md`](references/refactoring-heuristics.md)
and [`references/dynamic-index-skills.md`](references/dynamic-index-skills.md),
then (re)generate the install scripts and the removed-skills manifest. Do this
first so it is never lost to budget.

**Naming is BARE under `_skills/` — do NOT prefix with the per-KB namespace
here.** The generated per-area/per-domain index-skill directories and their
frontmatter `name` under `<kb-root>/_skills/` use clean, bare slugs:

- per-area/per-domain = `<area-or-domain-slug>-knowledge-index`
  (e.g. `feature-a-knowledge-index`)

(The top-level `knowledge-index` dir — written in Step 7 — is also bare; same
namespace-at-install rule applies to it.)

The per-KB namespace prefix `<kb-ns> = slugify(basename(kb_root))` is **applied
by the install script** (see
[`references/harness-skills-dir.md`](references/harness-skills-dir.md)), **not**
at generation. The collision guard belongs at the install layer: the source dir
already lives under `<kb-root>/_skills/`, so prefixing it there is redundant —
two KBs only collide once their skills are copied **flat** into the shared
harness skills dir, which is exactly where the install script renames each dir
to `<kb-ns>-<bare-name>`. So write the **bare** dir here; let the install
script namespace it on copy.

`kb_namespace` is still computed at STEP 0 and recorded in
`state.json.kb_namespace` (the install script + receipt read it). You do
**not** need it to name the source dirs — and you MUST NOT prefix the source
dirs with it.

1. **Emit a per-area/per-domain index skill** (`user-invocable:
   false`) whenever a trigger fires:
   - an **area's `knowledge/` holds > 12 concept pages** (count the `*.md`
     pages under `<kb-root>/areas/<area>/knowledge/`; **13 or more** ⇒
     required), OR
   - a **discovery domain index lists > 25 pages**, OR
   - the **caller explicitly requests** a dynamic/specialized index skill for
     a named area or domain (sufficient on its own, any page count).

Write each per-area/per-domain skill, once, idempotently, at the exact
**bare** path; the `name` MUST be identical to the directory name (both bare —
no namespace prefix here):

```
<kb-root>/_skills/<area-or-domain-slug>-knowledge-index/SKILL.md
```

**Worked example** — for the `feature-a` area the per-area skill is written to
`<kb-root>/_skills/feature-a-knowledge-index/SKILL.md` (with
`name: feature-a-knowledge-index`). (The top-level
`<kb-root>/_skills/knowledge-index/SKILL.md` is **not** written here — if the
caller requested it or a full repo-wide index refresh ran, it was produced in
Step 7 as the installable twin of `index.md`.)
Bare slugs only — the install script adds the `<kb-ns>-` prefix when it copies
each dir into the shared harness dir. **Never** pre-prefix the source dir.
Each generated per-area/per-domain skill (full templates in
[`references/dynamic-index-skills.md`](references/dynamic-index-skills.md)):

- starts with YAML frontmatter and has a **double-quoted `description`**
  carrying domain discovery keywords (unquoted ⇒ YAML parse failure);
- uses only supported keys (`name`, `description`, `user-invocable`);
  per-area/per-domain skills set `user-invocable: false`;
- has `name` **==** its `_skills/` directory name (both **bare** — no namespace
  prefix at generation);
- summarizes what exists, where, and why it matters (path + why-it-matters
  routing table — never a content dump);
- is regenerated **idempotently** as the area evolves (overwrite in place).

2. **On rename/obsoletion**, append the OLD (bare) name to
   `<kb-root>/_skills/removed-skills.json` (with timestamp + reason) **before**
   overwriting or dropping it. Schema + rules in
   [`references/removed-skills-manifest.md`](references/removed-skills-manifest.md).
   (The install script maps each bare removed name to `<kb-ns>-<name>` when it
   deletes the stale skill from the harness dir.)
3. **(Re)generate the install scripts** into `<kb-root>/_skills/`:
   `install-skills.sh` **and** `install-skills.ps1`, plus
   `removed-skills.json` (always present once any skill exists, even with
   `removed: []`). The scripts **glob `_skills/*/`**, so they pick up BOTH the
   Step-7-generated top-level `knowledge-index` AND every per-area/per-domain
   skill present under `_skills/` — no skill is excluded. They copy this KB's
   **bare** skill dirs into the resolved harness skills dir, **renaming each to
   `<kb-ns>-<bare-name>` on copy** (and rewriting the copied `SKILL.md` `name:`
   to match), maintain an `installed-skills.json` receipt, and delete this KB's
   stale skills (uninstall-on-change). Spec + skeletons in
   [`references/harness-skills-dir.md`](references/harness-skills-dir.md).
   **The agent generates these files; it never runs them and never writes
   outside `<kb-root>/`** — the user runs the script (see the end-of-cycle
   install prompt in `knowledge-brain`).

Record every emitted per-area/per-domain skill path in
`refactor-plan.json.dynamic_index_skills`, the install-script path, and any
removed-skill names, and surface them in the entry skill's
`knowledge-brain-summary` (`dynamic_index_skills`, `install_command`,
`index_skills_installed`, `removed_index_skills`). The top-level
`_skills/knowledge-index/SKILL.md` is reported as a **Step-7 index artifact**
(in `indexes_updated`), **not** in `dynamic_index_skills`.

### Step 8a completion checklist (verify BEFORE declaring step 8 complete)

Before declaring step 8 complete, walk this checklist:

- [ ] **(a) Top-level `knowledge-index` in sync (if applicable)?** If the
  caller requested a top-level / repo-wide index skill, or a full repo-wide
  index refresh ran in Step 7, then `<kb-root>/_skills/knowledge-index/SKILL.md`
  exists and reflects the current `index.md`. If neither condition applied,
  the top-level skill need not be (re)generated this cycle.
- [ ] **(b) Triggered per-area/per-domain skills written?** Every per-area or
  per-domain skill whose trigger fired (crowded area, crowded domain, or
  explicit caller request) is written at its bare path.
- [ ] **(c) Install scripts regenerated?** `install-skills.sh` **and**
  `install-skills.ps1` are (re)generated under `<kb-root>/_skills/` whenever any
  skill exists.
- [ ] **(d) Manifests updated?** `removed-skills.json` is present (even with
  `removed: []`), with any OLD bare names appended before overwrite; and the
  install **receipt** `installed-skills.json` is left for the user-run install
  script to write.

The install scripts glob `_skills/*/`, so they namespace + install whatever
skills are present (top-level and/or per-area) along with each other.

### Step 8b — Other structural refactoring (threshold-gated)

After 8a, apply the remaining heuristics from
[`references/refactoring-heuristics.md`](references/refactoring-heuristics.md):
split oversized pages, merge duplicates, introduce new categories, rebuild
affected indexes. These remain threshold-gated; skip them below threshold.

## Output

Refreshed index files under `<kb-root>/` and generated `_skills/` artifacts,
plus STM artifacts:
- `<kb-root>/_skills/knowledge-index/SKILL.md` (top-level, bare name — on
  caller request or a full repo-wide index refresh) and any
  `<slug>-knowledge-index/SKILL.md` (per-area/per-domain, bare name).
- `<kb-root>/_skills/install-skills.sh` **and** `install-skills.ps1` (install
  scripts; agent generates, user runs; they namespace + install + self-clean).
- `<kb-root>/_skills/removed-skills.json` (removed-skills manifest).
- `<kb-root>/_skills/installed-skills.json` (install receipt; **written by the
  install script when the user runs it**, not by the agent).
- `index-rebuild-todo.json` — `{ "indexes": ["<path>"] }`
- `refactor-plan.json` — `{ "splits": [...], "merges": [...],
  "new_categories": [...], "dynamic_index_skills": ["<path>"],
  "install_script": "<path>", "removed_index_skills": ["<name>"] }`

## Must NOT

- MUST NOT leave indexes stale after a cycle — every changed page must be
  reflected in `index.md`, its `area-index.md`, and its type's discovery
  index. When the top-level `_skills/knowledge-index/SKILL.md` is
  (re)generated (on request or a repo-wide index refresh), keep it in sync
  with `index.md`.
- MUST NOT generate a **per-area/per-domain** index skill when **no** trigger
  fires (no crowded area > 12 pages, no crowded domain > 25 pages, and no
  explicit caller request) — avoid `_skills/` sprawl.
- MUST NOT prefix the generated `_skills/` source dir names or their
  frontmatter `name` with the per-KB namespace — source names are **bare**
  (`knowledge-index` for the top-level; `<slug>-knowledge-index` for per-area,
  e.g. `feature-a-knowledge-index`). The `<kb-ns>-` prefix is added by the
  **install script** when it copies into the shared harness dir (see
  `references/harness-skills-dir.md`); pre-prefixing the source dir here would
  double-prefix at install time and is wrong.
- MUST NOT write outside `<kb-root>/` — the agent generates the install
  script into `_skills/`; the **user** runs it to touch the harness dir. The
  agent never copies skills into `.github/skills/` or any harness dir itself.
- MUST NOT emit an index skill with an unquoted `description` (YAML parse
  failure) or with non-supported frontmatter keys.
- MUST NOT dump page content into an index — entries are path +
  why-it-matters only.

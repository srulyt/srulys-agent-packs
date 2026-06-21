# Refactoring Heuristics & Size Thresholds

Overflow reference for `knowledge-indexing/SKILL.md`. Structure is **not
fixed**. As knowledge grows, refactor to keep the repo navigable. All
refactoring is **threshold-gated** — do not churn structure below the
thresholds; record actions in `refactor-plan.json`.

## Tiered index-skill scaling (T1/T2/T3)

The **number** of generated index skills scales with KB size. Count =
total `*.md` concept pages under `<kb-root>/areas/*/knowledge/` + root concept
dirs (`personas/`, `segments/`, `strategic/`, `competitive/`).

| Tier | KB size (concept pages) | Index skills generated |
|------|-------------------------|------------------------|
| **T1 (small)** | 1–30 pages (or ≤3 areas) | **Exactly one** top-level/root index skill routing to area/discovery indexes + key root concepts. No per-area skills. |
| **T2 (medium)** | 31–100 pages, OR any area `knowledge/` > 12 pages, OR any discovery domain index > 25 pages | Top-level skill **plus** a per-area/per-domain skill for each crowded area/domain crossing its threshold. |
| **T3 (large)** | > 100 pages OR > 6 areas | Top-level skill **plus** per-area skills for every area + per-domain skills for every crowded domain; top-level becomes a router-of-routers. |

The **top-level/root skill is ALWAYS generated** once the KB has any curated
pages (the T1 floor) — it is the deterministic baseline deliverable. The
`> 12` (crowded area) and `> 25` (crowded domain) triggers below are the
T2/T3 layer. See `dynamic-index-skills.md` for the templates and the per-KB
namespace rule.

## Size thresholds (defaults)

| Trigger | Threshold (default) | Action |
|---|---|---|
| Oversized page | page body > ~400 lines OR > 6 distinct sub-concepts | **Split** into focused pages; link them; keep one parent overview. |
| Near-duplicate pages | 2+ pages cover the same concept | **Merge** (preserve both evidence lists + change logs); mark retired page `status: superseded` with a pointer. |
| Crowded area | area `knowledge/` holds **> 12** concept pages | Introduce **sub-categories** (sub-dirs), rebuild `area-index.md`, **AND generate a dynamic specialized index skill** for that area (see `dynamic-index-skills.md`). |
| Crowded domain | a discovery index lists **> 25** pages | Generate a **dynamic specialized index skill** (see `dynamic-index-skills.md`). |
| Caller explicitly requests a dynamic index skill | any (no minimum) | Generate the dynamic specialized index skill for the named area/domain (see `dynamic-index-skills.md`). |
| Crowded root concept dir | `personas/`, `competitive/`, etc. > 20 pages | Add grouping subsections to the discovery index. |

Thresholds are heuristics — favor stability. Apply a **structural** refactor
(split / merge / recategorize) only when a threshold is **clearly** crossed,
not when a single page nudges over.

> **Exception — dynamic index skills are NOT covered by this hedge.** The
> "favor stability / clearly crossed" guidance applies to
> splits/merges/recategorization only. The **top-level/root index skill is
> always generated** (T1 floor), and generating a per-area/per-domain
> specialized index skill is a **deterministic obligation**, not a stability
> judgement: if an area's `knowledge/` holds **13+** pages, a domain index
> lists **26+** pages, **or the caller explicitly requests one**, you MUST
> generate the index skill (see `dynamic-index-skills.md`). An 18-page area or
> an explicit caller request both clearly qualify — do not read "favor
> stability" as license to skip generation.

## Refactoring actions

### Split an oversized page
1. Identify the cohesive sub-concepts.
2. Create a child page per sub-concept (full living-page template, carry the
   relevant `evidence:` + relationships).
3. Reduce the parent to an overview that links the children (`relates-to`).
4. Preserve the parent's `## Change Log`; add an entry noting the split.
5. Rebuild the area + discovery indexes.

### Merge duplicates
1. Choose the canonical page (most complete history/evidence).
2. Fold the other's unique claims + evidence + change-log entries in.
3. Mark the retired page `status: superseded`; leave a one-line pointer to
   the canonical page. **Never hard-delete** a page that carried decisions.
4. Repoint inbound relationships/backlinks to the canonical page.
5. Rebuild affected indexes.

### Introduce a new category/hierarchy
1. Create the sub-dir(s); move pages; update each moved page's `area`/path
   references and inbound links.
2. Rebuild `area-index.md` and the repo-wide `index.md`.

## Idempotency

Refactoring must be safe to re-run: re-running a cycle that already
refactored produces no further structural change (the thresholds are no
longer crossed). Record every action in `refactor-plan.json` so a resume
after compaction does not repeat a completed split/merge.

## When NOT to refactor

- Below threshold → leave structure alone (avoid thrash).
- A page is large but cohesive (one concept) → keep it; size alone is not
  sufficient.
- Merging would destroy decision history that cannot be preserved → keep
  both, link them, and record an `open_questions` note instead.

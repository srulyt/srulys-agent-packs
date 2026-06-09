---
name: knowledge-organization
description: "Own the on-disk product-centric layout of a Product Management knowledge base, the living-page templates per knowledge type, typed relationships plus backlinks, and the provenance / evidence descriptor schema. Specialist skill of the Product Knowledge Brain. Keywords: knowledge base layout, living page, page template, relationships, backlinks, wiki links, provenance, evidence descriptor, product wiki structure."
user-invocable: false
---

# Knowledge Organization (specialist skill)

A specialist skill of the **Product Knowledge Brain** plugin. The entry
skill `knowledge-brain` routes **steps 4, 5, 6, and 10** of the evolution
cycle here. It runs on the host's default agent; there is no custom agent.

**Core principle: pages are curated *current understanding*, not
transcripts.** Each page answers: *What do we currently believe? Why? What
evidence supports it? What remains uncertain?* — a living wiki article, not
a notes dump or chronological log.

## Invocation Note

Internal specialist skill loaded by `knowledge-brain` mid-cycle; not
user-invocable. If a user asks directly to "organize the knowledge base",
load `knowledge-brain` so the full cycle + STM checkpointing run; it routes
here.

## Step 4 & 5 — Write/update living pages

When `knowledge-consolidation` decides to update (step 4) or create
(step 5) a page, apply the **living-page template** for the claim's
knowledge type. Full templates + front-matter schema in
[`references/page-templates.md`](references/page-templates.md). Every page
has:

- YAML front-matter (`title`, `type`, `area`, `status`, `updated`,
  `relationships:`, `evidence:`);
- `## Current Understanding` — curated claims, each citing evidence inline
  (`[^E-nnn]`);
- `## Why / Rationale`;
- `## Open Questions / Uncertainties` — where uncited/contested claims go;
- `## Related` — backlinks + outbound `[[...]]` links;
- `## Change Log` — ADR-style, newest first, preserving superseded beliefs.

**Never** paste raw extracted text into a page. Distill it into curated
claims; the raw source stays with upstream tools — the KB stores only the
evidence **descriptor**.

Write each page **once, in a single pass** with its front-matter,
relationships, and evidence citations already in place — do not write a draft
and then re-open it later in the same cycle to "re-verify" or re-emit it.

## Step 6 — Create relationships

Knowledge is **networked, not isolated**. Add typed edges so future agents
can traverse `Feature A → Persona X → Segment Y → Strategic Goal Z →
Feature B`. Full syntax in
[`references/relationships-provenance.md`](references/relationships-provenance.md):

- Front-matter `relationships:` list of `{ rel: <type>, target: <path> }`.
- Inline `[[areas/<area>/knowledge/<slug>]]` wiki-links in prose.
- **Backlinks**: when you add an edge A→B, ensure B's `## Related` reflects
  the inbound link from A. `knowledge-indexing` rebuilds backlinks into the
  indexes.

Typed relationship vocabulary: `supports`, `requested-by`, `blocks`,
`relates-to`, `supersedes`, `affects`, `derived-from`, `competes-with`.

## On-disk layout (product-centric)

Knowledge lives close to the area/team/domain that owns it — avoid a giant
centralized wiki. Full tree + scaffolding rules in
[`references/repo-layout.md`](references/repo-layout.md). Summary:
`<kb-root>/areas/<area>/{specifications,research,customer-feedback,designs,
knowledge}/` for area-owned knowledge; cross-cutting concepts at the root
(`personas/`, `segments/`, `strategic/`, `competitive/`, `decisions/`,
`evidence/`); `indexes/` for discovery; `_skills/` for generated index
skills.

## Step 10 — Preserve provenance

Every important claim must be traceable. Default granularity: **one
`E-<nnn>` evidence descriptor per source document**, with **per-claim
inline citations**. Create `<kb-root>/evidence/E-<nnn>.md` recording the
source type (interview, PRD, research report, exec discussion, etc.), date,
and a one-line summary — **NOT** the raw source. Add the id to the page
front-matter `evidence:` list and cite it inline (`[^E-nnn]`). Uncited
claims go under `## Open Questions / Uncertainties`, never asserted as fact.

## Output

Curated/updated page files under `<kb-root>/`, evidence descriptors under
`<kb-root>/evidence/`, and `relationship-todo.json` in the STM run dir:
`{ "edges": [ { "from", "rel", "to" } ] }`.

## Must NOT

- MUST NOT emit a page as a transcript / notes / chronological dump — pages
  are curated current understanding.
- MUST NOT assert a claim without an evidence id; uncited claims go to
  `## Open Questions / Uncertainties`.
- MUST NOT write raw source content into the KB; store only evidence
  descriptors + curated pages.
- MUST NOT add an outbound relationship without ensuring the target's
  backlink (`## Related`) is consistent.

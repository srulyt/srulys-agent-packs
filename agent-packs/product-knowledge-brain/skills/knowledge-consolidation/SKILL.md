---
name: knowledge-consolidation
description: "Classify already-extracted product information into the six knowledge types, determine which existing knowledge-base pages and product areas it affects, decide update / merge / correct / expand versus create (prefer consolidation over proliferation), detect contradictions against current understanding, and remove duplication. Specialist skill of the Product Knowledge Brain. Keywords: classify knowledge, consolidate, deduplicate, merge pages, update over create, contradiction detection, knowledge types."
user-invocable: false
---

# Knowledge Consolidation (specialist skill)

A specialist skill of the **Product Knowledge Brain** plugin. The entry
skill `knowledge-brain` routes **steps 2, 3, 4, and 9** of the evolution
cycle here. It runs on the host's default agent; there is no custom agent.

**Core principle: prefer consolidation over proliferation.** When new
information arrives, do **NOT** auto-create pages. First decide whether
existing knowledge should be updated, merged, corrected, or expanded. The
repository must get *simpler* over time, not more fragmented.

## Invocation Note

This is an internal specialist skill loaded by `knowledge-brain` mid-cycle.
It is not user-invocable. If a user asks directly to "consolidate
knowledge", load `knowledge-brain` (the entry skill) so the full cycle and
STM checkpointing run correctly; it will route here.

## Step 2 — Classify information

Classify each distinct claim/entity into one or more of the **six
knowledge types** (full taxonomy + decision rules in
[`references/knowledge-types.md`](references/knowledge-types.md)):

| Type | Covers |
|---|---|
| Product | features, requirements, roadmaps, user stories, business rules |
| Customer | personas, segments, requests, pain points, jobs-to-be-done |
| Competitive | competitors, market positioning, competitive gaps/strengths |
| Organizational | decisions, rationale, historical context, team conventions |
| Research | findings, experiments, outcomes, learnings |
| Strategic | goals, vision, themes, initiatives |

Extract the entities each claim names and the source it came from (for
provenance). A single claim may span several types — record all of them.

## Step 3 — Determine affected areas

Locate the product area(s) and existing page(s) each claim touches. Search
`<kb-root>/areas/*/knowledge/` and the cross-cutting roots (`personas/`,
`segments/`, `strategic/`, `competitive/`, `decisions/`). Distinguish:
- **touched_pages** — existing pages the claim updates;
- **candidate_new** — concepts with no existing home;
- **new_areas** — product areas not yet in the repo.

## Steps 4 & 9 — Update-over-create decision rules (applied while acting)

For every claim, choose in this priority order — **create is the last
resort**:

1. **Update** an existing page if the claim refines/confirms its current
   understanding → append/adjust claims, bump `updated:`.
2. **Merge** into an existing page if the claim restates a concept already
   covered elsewhere → fold in, add evidence, leave one canonical page.
3. **Correct** an existing page if the claim **contradicts** it → queue the
   contradiction (see below); update the conclusion **and** preserve the
   superseded belief in the page `## Change Log`.
4. **Expand** an existing page if the claim adds a new facet → add a
   subsection rather than a new page.
5. **Create** a new page **only** when no existing page can absorb the
   claim. Hand the create to `knowledge-organization`.

**Step 9 (remove duplication)** is the final pass: detect near-duplicate
pages (this cycle or pre-existing), merge them preserving both evidence
lists and change logs, and mark the retired page `status: superseded` with
a pointer — never hard-delete a page that carried decisions.

## Contradiction detection (evolving truth)

Detect when a new claim conflicts with a page's `## Current Understanding`
or an existing decision. Queue each contradiction with the old belief, the
new claim, and the supporting evidence for resolution via a change-log /
ADR entry. **Never silently overwrite.** Full detection cues + the
ADR/change-log format are in
[`references/contradiction-changelog.md`](references/contradiction-changelog.md).

## Output (STM artifacts this skill writes)

- `classification.json` — `{ "claims": [ { "text", "types": [...],
  "entities": [...], "evidence_source": "<descriptor>" } ] }`
- `affected-areas.json` — `{ "touched_pages": [...], "candidate_new": [...],
  "new_areas": [...] }`
- `merge-plan.json` — `{ "updates": [ { "page", "action", "supersedes" } ],
  "creates": [ { "concept", "area", "type" } ], "merges": [...] }`
- `contradiction-queue.json` — `{ "contradictions": [ { "page",
  "old_belief", "new_claim", "evidence", "resolution" } ] }`

## Must NOT

- MUST NOT auto-create a page before evaluating update / merge / correct /
  expand. Consolidation is the default.
- MUST NOT drop a superseded belief from the change log when correcting a
  page.
- MUST NOT fabricate classifications for empty or unintelligible input —
  return control to `knowledge-brain` to fail safe.
- MUST NOT hard-delete a page that carried a decision; mark
  `status: superseded` and leave a pointer.

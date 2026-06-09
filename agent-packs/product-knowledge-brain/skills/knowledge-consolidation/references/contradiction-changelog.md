# Contradiction Detection + ADR / Change-Log Format

Overflow reference for `knowledge-consolidation/SKILL.md`. How to handle
**evolving truth**: detect contradictions, surface uncertainty, update
conclusions, and **preserve historical reasoning**. The governing rule:
**never silently overwrite an important historical decision.**

## Detecting a contradiction

A new claim contradicts the knowledge base when it conflicts with:
- a page's `## Current Understanding` (a believed fact is now disputed),
- a recorded decision (`decisions/ADR-<nnn>` or a page `## Change Log`),
- the `status:` of a page (e.g. new evidence revives a `superseded` page).

Detection cues: opposing quantities/dates, "actually", "we changed our
mind", "no longer", "instead of", reversed recommendations, or a later
evidence date overriding an earlier one.

Queue each contradiction in `contradiction-queue.json`:
```json
{
  "contradictions": [
    {
      "page": "areas/feature-a/knowledge/onboarding-flow.md",
      "old_belief": "Onboarding must be 3 steps.",
      "new_claim": "Research shows a 1-step onboarding converts better.",
      "evidence": ["E-042"],
      "resolution": "update-conclusion"
    }
  ]
}
```

## Resolving a contradiction (mandatory, never silent)

1. **Update the conclusion** in `## Current Understanding` to the new
   belief, citing the new evidence inline (`[^E-042]`).
2. **Append a `## Change Log` entry** (newest first) that records the
   **superseded belief**, the rationale, and the evidence:
   ```markdown
   ## Change Log
   - 2026-06-08 — changed onboarding target from 3 steps to 1 step.
     Superseded: "Onboarding must be 3 steps." Reason: usability study
     showed higher completion at 1 step. [^E-042]
   ```
3. **If the contradiction reverses an org-level decision**, also write an
   ADR (below) and link it from the page.
4. **If the matter is genuinely unresolved**, set the page
   `status: uncertain`, move the disputed claim to
   `## Open Questions / Uncertainties`, and record an `open_questions` note
   — do **not** assert a contested claim as fact.
5. **Retiring a page** instead of editing it: set `status: superseded`, keep
   the content, and add a pointer to the replacement. Never hard-delete.

## ADR format (org-level decisions & reversals)

Write to `<kb-root>/decisions/ADR-<nnn>-<slug>.md`. Number sequentially.

```markdown
---
title: "ADR-007: Move to single-step onboarding"
type: organizational
status: accepted | superseded | proposed
updated: 2026-06-08
supersedes: ADR-003
evidence: [E-042]
relationships:
  - rel: affects
    target: areas/feature-a/knowledge/onboarding-flow.md
---

# ADR-007: Move to single-step onboarding

## Context
Why the decision is being (re)made; what changed.

## Decision
The single, current decision.

## Consequences
Trade-offs, follow-ups, what this supersedes.

## History
- 2026-06-08 — supersedes ADR-003 (3-step onboarding). Reason + [^E-042].
```

When an ADR supersedes an earlier one, set the earlier ADR's
`status: superseded` and add a forward pointer — preserving the full
decision lineage.

## Invariants

- Every correction preserves the prior belief in a change log or ADR.
- `status` transitions are append-only history: `current` →
  `uncertain`/`superseded`, never a destructive delete.
- Contested claims live under `## Open Questions / Uncertainties`, never in
  `## Current Understanding`.

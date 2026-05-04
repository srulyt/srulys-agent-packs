# Competitive scan — internal-docs / knowledge platforms

Prepared for the discovery-sprint greenlight conversation. Scope is
limited to mid-market SaaS internal-docs tools that overlap
Heliograph's wedge (engineering-led wikis, editor + API, opinionated
information architecture).

## Players considered

| Player | Wedge | Freshness story | Pricing posture |
|---|---|---|---|
| **Veridoc** | "Docs as code" — markdown-in-repo with rendered viewer | Git-blame-derived; no in-app freshness UI | Per-seat, mid-market |
| **Northshelf** | Notion-style block editor, AI summary chips | "Last verified" badges with manual reset | Per-seat + AI add-on |
| **Quartilo** | Confluence migration tool that became a product | Page-decay score in sidebar (proprietary) | Annual, top-down |
| **Heliograph (us)** | Editor + API + search, engineering-friendly IA | Indexer recency only; no decay UI | Per-seat, mid-market |

## What's changed in the last six months

1. **Northshelf shipped freshness badges in Q2 FY25.** They are
   manual ("mark verified") rather than inferred. Adoption signals
   from their public changelog suggest mixed uptake, but the framing
   has spread — three of our interviewees referenced "verified"
   language unprompted.
2. **Quartilo's page-decay score** is the only inference-based
   freshness signal currently shipping. It is opaque (no surfaced
   reasoning) and gated to their highest tier.
3. **Veridoc** has not moved on freshness; their "docs as code"
   audience self-reports the problem as a process problem, not a
   product problem.

## Defensibility read

The freshness wedge is plausible because:

- No competitor combines **inferred** freshness with **transparent
  reasoning** ("this page is stale because owner X left and the
  three pages it links to have all changed").
- Heliograph's existing edit-history graph is a structural advantage
  — Northshelf and Veridoc don't have the same edge-relationships
  in their data model.
- Inferred-and-explained freshness is the kind of feature that buyers
  remember in the bake-off, not just the demo.

It is not defensible long-term: any of the three competitors could
build something similar within 3–4 quarters. The window is the
question, not the moat.

## Recommendation framing (not a decision)

A discovery sprint focused on inferred freshness signals is
defensible on customer signal (5 of 6 interviewees, see
``customer-interviews.md``), competitive timing (one shipped manual
analog, one gated proprietary analog, one absent), and structural fit
(edit-history graph is already in our data model).

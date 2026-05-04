# Search rewrite — architectural options

**Product:** Quillstream (long-form authoring + research workspace)
**Audience for this brief:** Engineering Director, Platform org
**Decision shape:** pick approach A or approach B for the FY26
search rewrite

## Background

Quillstream's current search is a single Elasticsearch cluster that
indexes three document types (drafts, references, comments) into the
same index with a flat schema. It was built in FY22 when the product
shipped only drafts. Today it serves 4 surfaces (in-doc lookup,
global search, citation autocomplete, and the new sidebar Q&A) and
is showing strain: p95 latency on global search has drifted from
180ms (FY24 baseline) to 540ms (last trailing month).

The platform team agrees the current shape is past its useful life.
The disagreement is about what replaces it.

## Approach A — Federated per-surface indices

Each search surface gets its own purpose-shaped index, fronted by a
thin federation layer that fans out queries and merges results.

- **Pros:** Each index can be tuned for its surface (citation
  autocomplete needs a prefix index, sidebar Q&A needs vector). No
  surface can starve another. Failure isolation is real — if the
  comments index goes down, drafts search keeps working.
- **Cons:** Operational complexity multiplies (4 indices to keep
  fresh, reindex, monitor). Cross-surface queries (e.g. "find all my
  references to this term") become federation problems. Cost
  envelope is roughly 1.6x the current cluster.
- **Build estimate:** 7 months, full platform pod, plus 1 SRE.

## Approach B — Unified index with surface-aware query planner

A single next-generation index (still Elasticsearch-family) with a
richer schema, fronted by a query planner that rewrites queries
based on the calling surface.

- **Pros:** One thing to operate. Cross-surface queries are native.
  Schema migrations stay in one place. Cost envelope is roughly 1.1x
  current.
- **Cons:** Tuning is a zero-sum game across surfaces — improving
  citation autocomplete latency tends to regress sidebar Q&A
  recall. Failure blast radius is the whole product. Query-planner
  complexity creeps over time (we have seen this pattern in two
  prior systems).
- **Build estimate:** 5 months, full platform pod.

## What both approaches share

- Both retire the current flat schema.
- Both require a 4–6 week dual-read migration window.
- Both require a vector-store component for sidebar Q&A; the
  question is whether it lives in its own index (A) or as a field
  in the unified index (B).

## What this brief should answer

A clear recommendation between A and B, anchored to the latency,
cost, and operational-complexity trade-offs above, with explicit
acknowledgement of the failure-isolation difference.

# Quillstream search — KPIs and targets

## Current-state metrics (last trailing 30 days)

| Metric | Surface | Current | FY24 baseline | FY26 target |
|---|---|---|---|---|
| p95 latency | Global search | 540ms | 180ms | ≤ 200ms |
| p95 latency | In-doc lookup | 240ms | 200ms | ≤ 220ms |
| p95 latency | Citation autocomplete | 90ms | 80ms | ≤ 100ms |
| p95 latency | Sidebar Q&A | 1.9s | n/a (new) | ≤ 1.2s |
| Recall@10 | In-doc lookup | 0.61 | 0.74 | ≥ 0.80 |
| Precision@5 | Citation autocomplete | 0.68 | 0.72 | ≥ 0.85 |
| Search-abandonment rate | Global search | 18.4% | 11.2% | ≤ 10% |

## Operational metrics

- Indexing lag (ingest → searchable): currently p95 = 90s.
  FY26 target: ≤ 30s on all surfaces.
- Reindex window (full corpus): currently 14 hours.
  FY26 target: ≤ 4 hours.

## Cost envelope

- Current cluster cost: $38K/month all-in (compute + storage +
  managed-service fees).
- Approach A projected cost: ~$61K/month (1.6x).
- Approach B projected cost: ~$42K/month (1.1x).

## Out of scope for this rewrite

- Changes to the editor's inline reference picker.
- Mobile search experience (separate FY26 track).
- Multi-tenant isolation guarantees (already covered by the
  workspace-permissions refactor shipped in FY25 Q3).

# Spike notes — Activity event stream

The platform already publishes a workspace-scoped activity event
stream. Events carry `actor`, `verb`, `object`, `workspace_id`,
`occurred_at`. The digest job can subscribe per workspace and
materialise a per-member summary view.

- Latency from event publish to availability in the stream: ~5s.
- Per-workspace event volume: 1k–50k events/day at p99.
- No new datastore needed; we keep summaries in the existing
  notifications-summary store.
- No public API surface changes.

# Cassiterra FY26 — investment options

Four candidate themes. Exactly one becomes the headline; the other
three are sized as supporting investments.

## Option A — Dispatcher cognitive-load reduction (headline candidate)

- Build: morning-shift "state of the world" dashboard + AI-assisted
  triage of overnight inbound (tickets, technician messages,
  voicemail transcripts).
- Investment: ~$1.8M, 9 months, Dispatch pod + ML platform support.
- Modeled impact: dispatcher time-to-first-dispatch from 38 min →
  ~22 min p50. Indirect NPS lift estimated at +3 to +5.
- Risk: AI-triage trust curve; need an explicit confidence threshold
  and override flow.

## Option B — Mobile parity (headline candidate)

- Build: parts-requests, schedule-swaps, and three other named
  actions reach mobile parity.
- Investment: ~$0.9M, 5 months, Mobile pod.
- Modeled impact: Mobile DAU / Web DAU ratio 0.62 → 0.78. Reduces
  dispatcher inbound (technician-text workaround) modestly.
- Risk: Low. Well-scoped, well-understood.

## Option C — Customer-facing visibility (headline candidate)

- Build: "Where is my technician" web view with ETA and
  appointment-window updates, embeddable per tenant.
- Investment: ~$1.1M, 6 months, Customer-Experience pod.
- Modeled impact: Closes a competitive gap. Win-rate impact in
  competitive bake-offs estimated at +3 to +6 pp.
- Risk: Requires location-services privacy review; legal flagged
  this as a 4-week gating dependency.

## Option D — Reporting v2 (headline candidate)

- Build: configurable export columns, faster export pipeline,
  scheduled-report delivery.
- Investment: ~$0.7M, 4 months, Data pod.
- Modeled impact: Export p95 42s → 12s. Enterprise renewal-risk
  reduction in 2 named accounts.
- Risk: Low. Mostly a performance and configurability story.

## Decision shape

VP Product is choosing the headline, with the other three sized as
supporting investments fitting within a $4.5M FY26 product envelope.
Customer signal points strongly at A; B and D are cheap wins; C is
a competitive-parity question.

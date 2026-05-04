# Quillstream search — customer research summary

**Source:** 9 customer conversations + 60-day support-ticket sample
**Window:** FY25 Q2–Q3
**Prepared by:** Product Research

## What customers actually complain about

| Complaint | Frequency (of 9) | Surface most cited |
|---|---|---|
| "Search is slow" | 7 | Global search |
| "I can't find my own drafts" | 5 | In-doc lookup, global |
| "Citation autocomplete misses obvious matches" | 4 | Citation autocomplete |
| "Sidebar Q&A gives stale answers" | 3 | Sidebar Q&A |

Two complaints dominate: latency on global search, and recall on
in-doc draft lookup. The latency complaint maps directly to the p95
drift documented in ``architecture-options.md``. The recall
complaint maps to schema limitations in the current flat index.

## Behavioural signals from support tickets

- 22% of search-related tickets in the sample reference a
  workaround (Cmd-F in the editor, browser bookmarks, copy-paste
  into a notes app).
- 14% explicitly mention abandoning a query and asking a teammate.
- 6 of the 60 tickets are from accounts >$50K ARR, which is
  disproportionate to that segment's share of the install base.

## Surface-by-surface read

- **Global search:** Complaint is latency. Recall is acceptable.
- **In-doc lookup:** Complaint is recall. Latency is acceptable.
- **Citation autocomplete:** Complaint is precision (false matches).
- **Sidebar Q&A:** Complaint is staleness; out of scope for the
  rewrite proper but a forcing function for the vector-store
  decision.

## Implication for the A-vs-B choice

The complaints are surface-specific, not uniform. That is the
strongest customer-side argument for approach A's per-surface
tuning. The counter-argument is that customers do not articulate
"I want my latency improved without my recall regressing" — they
just want both. Either approach can deliver both if executed well.

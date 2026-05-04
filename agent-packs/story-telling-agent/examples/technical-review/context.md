# Example: Technical Review Deck

**Audience**: senior engineers and staff engineers reviewing an architecture proposal in a 60-min design review.

**Decision needed**: approve or block the proposed migration from a synchronous monolithic service to an event-driven decomposition.

**Tone**: precise, low-marketing, high-evidence. This audience punishes vague claims and rewards explicit trade-offs. Every diagram must be readable; every metric must cite the dashboard or load test it came from.

**Time slot**: 20 min presenter + 40 min discussion.

**Constraints / known facts**
- Current p99 latency: 1.8s (Datadog dashboard `prod-api-latency`, 30-day median).
- Target p99 after migration: <400ms (based on load-test report `lt-2026-02`).
- Three rejected alternatives must be listed with one-sentence rationale (read-replica scaling, vertical scaling, caching layer).
- Migration risk register has 4 entries — all 4 must appear in the deck.
- Audience expects: explicit "what could go wrong" slide, rollback plan, and dependency diagram.
- Tone rule: no superlatives ("revolutionary", "cutting-edge", "best-in-class") — they will erode credibility instantly.

**Out of scope**: business case, headcount, vendor comparisons.

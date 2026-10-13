# Search Filters — Specification

## Document Information

- **Author(s)**: Noa Ben-David
- **Created**: 2026-09-20
- **Last Updated**: 2026-10-05
- **Status: draft**
- **Reviewers**: Ilan Shapiro
- **Version: 0.0.1-draft**

---

## Problem Statement

Shoppers cannot narrow catalogue search results. Search sessions with more than 50 results end without a product view 64% of the time (September 2026 analytics, 1.2M sessions), against 22% for sessions with fewer than 10 results.

---

## Goals & Success Metrics

| Metric | Baseline | Target | Measurement window | Type |
|--------|----------|--------|--------------------|------|
| Large-result sessions ending without a product view | 64% | 45% | 30 days after GA | user |

---

## Users & Personas

| Persona | Role / context | Primary job (JTBD) | Top pains | Expected outcome |
|---------|----------------|--------------------|-----------|------------------|
| Shopper | Browses the web catalogue | When a search returns many items, I want to narrow them by what matters to me, so I can find a product to buy | Scrolling long result lists | Reaches a relevant product in fewer steps |

---

## Solution Summary

Add brand, price-range, and rating filters to the search results page. Filters combine with AND logic and update results without a full page reload.

---

## Functional Requirements

### FR-01 — Apply a filter  *(P0, event-driven)*

When a shopper selects a filter value, the search service shall return only results that match every selected filter.

#### Acceptance Criteria

- **AC-01.1** — Given results for "headphones", when the shopper selects brand "Acme" and rating "4+", then every result is an Acme product rated 4 or higher.

---

### FR-02 — No matching results  *(P0, unwanted-behaviour)*

If the selected filters match no results, then the search page shall show an empty-state message with a control that clears all filters.

#### Acceptance Criteria

- **AC-02.1** — Given filters that match nothing, when results load, then the empty-state message and a "Clear filters" control are shown.

---

### FR-03 — Invalid price range  *(P1, unwanted-behaviour)*

If a shopper enters a minimum price greater than the maximum price, then the search page shall reject the range and explain the error inline.

#### Acceptance Criteria

- **AC-03.1** — Given min 200 and max 50, when the shopper applies the range, then results are unchanged and an inline error is shown.

---

## Risks & Mitigations

| ID | Risk | Likelihood | Impact | Mitigation |
|----|------|------------|--------|------------|
| R-01 | Filter counts slow down search responses | Medium | Medium | Compute facet counts asynchronously |

---

## Open Questions

- **OQ-01** — Should filter selections persist across sessions? *Owner:* Noa Ben-David. *Due:* 2026-10-30.

---

## Out of Scope

- Saved searches.

# Review notes — Search Filters spec, 2026-10-12

Attendees: Noa, Ilan, Maya (design), Ruben (search backend)

- Ruben: rating filter should be "3+ / 4+ / 5 only", not free-form. Also what happens if the facet service is down? Spec doesn't say.
- Maya: we need a "clear all" chip row above results even when results exist, not only on empty state.
- Ilan: price filter must respect the shopper's currency. What if a product has no price (pre-order)?
- Noa to follow up on persistence (OQ-01).

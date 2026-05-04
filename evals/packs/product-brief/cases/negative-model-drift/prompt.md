@brief-orchestrator

Build a brief from ``inputs/``. Audience: VP Product. The user has
NOT requested a model override for any specialist. Every task()
delegation should therefore use the pinned model from
``evals/packs/product-brief/spec.yaml`` (no ``model:`` parameter,
or the same value as in the spec). The harness verifies no silent
drift.

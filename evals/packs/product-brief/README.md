# product-brief evals

This suite exercises the `product-brief` agent pack end to end through the
`brief-orchestrator` entry point. Cases cover the happy paths — a late-stage
decision ask, an early-stage summary, and a scope-brief (scope description with
no decision ask) — plus negatives that guard delegation discipline (the
orchestrator must not paraphrase or author specialist content) and short-term
memory hygiene (no evidence STM source leakage into the final artifact). Each
case makes structural assertions (deterministic output path, single
`product-brief.md`, recorded maturity/brief-type) before invoking the LLM judge,
which scores brief-type correctness, section distinctness, zero links, length
sanity (filler/repetition review — not a hard word cap), heading naturalness,
and absence of writer-scaffolding meta-commentary.

Run the suite from the monorepo root:

```bash
pytest evals/packs/product-brief/ -v
```

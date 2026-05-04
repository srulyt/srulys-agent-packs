# Golden — smoke-buy-in-deck

Reference shape (not byte-exact) checked by rubrics:

- `proposal.md` — SCQA framework, 9–12 slide plan, `executive-navy` design
  system, three-ask CTA, Open Questions section present.
- `deck-spec.json` — validates against
  `.story-telling-stm/schemas/deck-spec.schema.json`. Must include slide
  types: `title`, `data_callout`, `comparison`, `quote`, `metric`, `cta`.
  Speaker notes on every slide.
- `output.pptx` — exists and is readable by python-pptx.
- `qa-report.json` — `verdict: pass` (or `verdict: revise` with
  `qa_iteration < 2` and a subsequent pass).

See `agent-packs/story-telling-agent/examples/buy-in/expected-deck-shape.json`
for the canonical golden shape.

# Buy-In Deck Example

A canonical *internal buy-in* request: a platform team asking VP-level
sponsors for budget + headcount to fix a known revenue leak.

## Files

- `context.md` — the prompt the user would paste into `@story-orchestrator`.
- `expected-deck-shape.json` — what a passing run should produce. Used as
  golden reference in `evals/packs/story-telling-agent/cases/smoke-buy-in-deck/`.

## How to Run

```text
@story-orchestrator

[paste context.md]
```

Expected flow:

1. `intake` — orchestrator confirms audience + decision.
2. `research` — minimal (facts already in brief; no external `web` calls
   should be needed).
3. `proposal` — `@story-strategist` returns SCQA outline with 9–12 slides,
   `executive-navy` design system, three-ask CTA.
4. `feedback` — *Stop-B*. User replies `APPROVED`.
5. `build` — `@deck-builder` writes `deck-spec.json` + customized
   `generate_deck.py` + `output.pptx`.
6. `qa` — `@deck-critic` runs structural + visual checks; should
   `pass` on first attempt.
7. `complete` — orchestrator returns `output.pptx` path.

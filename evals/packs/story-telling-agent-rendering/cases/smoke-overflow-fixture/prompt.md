# F1 Overflow Smoke Test

We have pre-staged a `deck-spec.json` and `generate_deck.py` under
`.story-telling-stm/runs/smoke-overflow/agents/deck-builder/` that
contain an intentional **text overflow** on slide 3 (body text
exceeds the textbox bounds when rendered with real Pillow metrics).

Invoke `@story-orchestrator` against session `smoke-overflow` and
ask it to run the QA loop. The expected outcome is:

- `@deck-builder` runs `generate_deck.py` and produces `output.pptx`.
- `@deck-critic` runs `check_pptx.py`, detects the overflow on slide
  3, and emits `verdict: revise` with blocking finding
  `overflow_violations`.

The case **PASSES** when the critic-verdict fence contains
`overflow_violations` AND the status is NOT `pass`.

Session: smoke-overflow

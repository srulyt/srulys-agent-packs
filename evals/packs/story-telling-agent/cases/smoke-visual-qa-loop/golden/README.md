# Golden — smoke-visual-qa-loop

- `qa_iteration` ends in [1, 2].
- First `qa-report.json` has `verdict: revise` with ≥2 antipatterns
  (wall-of-text on slides 3/4, uncited metric on slide 5).
- Final `qa-report.json` has `verdict: pass`.
- Total deck-builder invocations = 2 (initial + 1 retry); deck-critic = 2.
- Output deck slides 3/4 contain ≤25 words each in the final version.

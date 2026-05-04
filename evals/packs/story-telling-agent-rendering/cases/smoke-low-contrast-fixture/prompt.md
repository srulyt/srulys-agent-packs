# F4 Low-Contrast Smoke Test

We have pre-staged a `deck-spec.json` whose slide 2 sets
`design_system_tokens.palette.text_on_light = "#BBBBBB"` against the
default `background_light = "#F5F6FA"` — contrast ratio < 2:1, well
under the WCAG 4.5:1 normal-text threshold.

Invoke `@story-orchestrator` against session `smoke-low-contrast`.
The expected outcome is `verdict: revise` with blocking finding
`contrast_violations`.

Session: smoke-low-contrast

# F5 Styled-Recipe Render Smoke Test

A pre-staged `deck-spec.json` includes one slide with `style: "styled"`
and `style_recipe: "metric_xxl"`. The rebuilt `generate_deck.py`
must dispatch this slide to `_styled_metric_xxl` and produce a
valid `output.pptx`.

The case PASSES when:
- `output.pptx` exists and is non-empty
- `builder-summary` fence contains `styled-count: 1` and `metric_xxl`
  in `styled-recipes-used`
- The critic verdict is `pass` or `pass_unverified` (the slide is
  visually well-formed; styled-count > 0 means render-failure
  would BLOCK, but in this case render is expected to succeed
  when `soffice` is available).

Session: smoke-styled

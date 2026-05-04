# OQ5 Styled-Deck Render-Blocking Regression

This is the **key regression test** for OQ5 (decisions.md
2026-05-04T14:50Z): a deck containing one or more styled slides
must NOT ship with `pass` or `pass_unverified` verdict when the
render pipeline is unavailable.

Setup:
- Pre-staged `deck-spec.json` includes one slide with
  `style: "styled" / style_recipe: "hero_full_bleed"`.
- Critic is instructed to invoke `render_pptx.py` with the PATH
  environment scrubbed of `soffice`, `libreoffice`, and `unoconv`
  (e.g. via `env -i PATH=/tmp/empty python ...`), forcing
  `render_engine=null` + `render_unverified=true` in the manifest.

Expected critic behaviour (architecture §6 verdict policy):
- `verdict: revise`
- `blocking-findings` includes `render_unverified`
- `styled-deck-policy` fence shows `render-policy-applied:
  render_unverified`

The case **FAILS** if the critic emits `pass` or `pass_unverified`
for this styled deck — that would be a regression on the OQ5
binding.

Session: smoke-render-skipped

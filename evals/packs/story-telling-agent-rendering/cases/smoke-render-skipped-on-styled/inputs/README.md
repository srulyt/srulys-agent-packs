# Inputs

Pre-built fixture staged at
`.story-telling-stm/runs/smoke-render-skipped/agents/deck-builder/`.
One slide uses `style: "styled" / style_recipe: "hero_full_bleed"`.

The case prompt instructs the critic to run `render_pptx.py` with
PATH stripped of soffice/libreoffice/unoconv to force
`render_engine=null`.

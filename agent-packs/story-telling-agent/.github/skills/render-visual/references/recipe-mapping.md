# Recipe Mapping (slide class → render-visual recipe)

When the strategist decides a slide should be `style: "styled"`, the
`@deck-builder` selects a `style_recipe` (the *PPTX-side* layout)
and may call zero, one, or more `render-visual` recipes to
pre-render images before assembly.

This table maps the most common combinations.

| Slide class (presentation-design term) | `style_recipe` (pptx-engine) | `render-visual` recipe(s) |
|----------------------------------------|------------------------------|---------------------------|
| Hero / opener                          | `hero_full_bleed`            | `composite/gradient_pattern` |
| Section divider                        | `hero_full_bleed`            | `composite/gradient_pattern` |
| Big single statement                   | `accent_block_left`          | (none — pure PPTX layout) |
| Single big number                      | `metric_xxl`                 | (none — pure PPTX layout) |
| Pull-quote / testimonial               | `quote_pullout`              | `composite/oversized_glyph_bg` |
| "Picture is the point" claim           | `split_image_right`          | (image supplied by caller) |
| Aside / supporting fact                | `tinted_panel_right`         | (none — pure PPTX layout) |
| Process / multi-step CTA               | `progress_dots`              | `chart/progress_strip` |
| Data-driven claim with annotation      | `chart_callout`              | `chart/bar_with_callouts` (or `dual_bar_diff`, `donut`, `sparkline`) |
| ≥4-category comparison (regions, segments) | `chart_callout`           | `chart/categorical_bars` (cycles `chart_palette.ramp`; promote `focal`) |
| Big-number KPI grid (3-up)             | `stat_grid_3up`              | (none — pure PPTX cards) |
| Editorial 60/40 lead + aside           | `editorial_2col_6040`        | (none — pure PPTX layout) |
| Timeline / milestones                  | `timeline_horizontal`        | (none — pure PPTX layout) |
| Agenda / table of contents             | `agenda_toc`                 | (none — pure PPTX layout) |
| Pull-quote + portrait                  | `pull_quote_portrait`        | (portrait image supplied by caller) |
| Full-bleed photo + caption             | `full_bleed_caption`         | (image supplied by caller; scrim added by builder) |
| Closing / CTA / contact                | `closing_cta`                | (none — pure PPTX layout) |

## Selection heuristic

The `@deck-strategist` (out-of-scope this rebuild but bound by the
shared `deck-spec.schema.json`) emits a `slide.style_recipe` per
slide. The deck-builder MUST use that recipe. It MAY call additional
chart / composite recipes if the slide carries `visual_assets[]`
entries.

For diagram-class visuals (`flow_diagram`, `system_diagram`), the
`pptx-engine` does not have a dedicated `style_recipe`; instead the
strategist places the diagram inside a `split_image_right` or
generic `image` slide and lists the diagram in `visual_assets[]`.

## Defaults when `style_recipe` is missing or unknown

If `slide.style == "styled"` but `style_recipe` is missing or not in
the canonical `STYLED_RECIPES` set (the 8 base recipes + the archetype
and editorial-archetype builders), the deck-builder MUST reject the spec
with `bad_spec.styled_without_recipe` (or
`bad_spec.unknown_recipe`). It MUST NOT silently fall back to
`simple` — that would erase the strategist's intent and ship a
visually inconsistent deck.

## OQ4 binding

Title slides default to `style: "simple"`. Only `section_divider`
defaults to `styled / hero_full_bleed`. See
`presentation-design/references/style-gating.md` for the full
gating heuristic.

## OQ5 binding

A deck where every slide is `style: "simple"` (no styled visuals at
all) is the only deck shape that may reach verdict
`unverified-needs-user` when render fails — an explicit user-decision
gate (install / ship-with-consent / abort), NOT a silent ship (B3). Any
styled deck with a render failure is BLOCKING (`render_unverified`
revise verdict).

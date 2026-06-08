# Styled Recipes (architecture §4.1)

The styled-slide recipes implemented by `scripts/generate_deck.py`.
The accepted set is **whatever `STYLED_RECIPES` registers** — currently
**22 recipes**: 8 base recipes (detailed below), 7 analytical
archetypes (`risk_heatmap`, `priority_matrix`, `waterfall`,
`flywheel`, `funnel`, `decision_options`, `appendix_dense`), and 7
editorial archetypes (summarized at the end). All EMU coordinates
assume 16:9 deck geometry: **12,192,000 × 6,858,000 EMU**
(1" = 914,400 EMU).

Each recipe is dispatched when `slide.style == "styled"` and
`slide.style_recipe == "<recipe>"`. The strategist/builder MUST
select a recipe registered in `STYLED_RECIPES` — any recipe not in
that set is rejected with `bad_spec.unknown_recipe`.

## 1. `hero_full_bleed`

Full-bleed picture (gradient_pattern composite or supplied image)
with title in the lower third.

| Element | x | y | w | h |
|---|---|---|---|---|
| Picture | 0 | 0 | 12192000 | 6858000 |
| Title textbox | Inches(1.0) | Inches(4.2) | Inches(11.3) | Inches(1.6) |
| Subtitle | Inches(1.0) | Inches(5.9) | Inches(11.3) | Inches(0.6) |

Visual asset: optional `composite/gradient_pattern` (default
behaviour: `bg_dark` → `bg_accent` gradient + 40% darken overlay).

## 2. `accent_block_left`

Left vertical accent panel + right body. Anchor: full-height left
column on `primary_accent`.

| Element | x | y | w | h |
|---|---|---|---|---|
| Left accent rect | 0 | 0 | **4023360** (4.4") | 6858000 |
| Eyebrow textbox | Inches(0.5) | Inches(2.5) | Inches(3.7) | Inches(2.5) |
| Title textbox | 4023360 + Inches(0.6) | Inches(2.0) | Inches(8.0) | Inches(3.5) |

## 3. `metric_xxl`

200pt centred number on `bg_dark`. Subtitle in `secondary_accent`.

| Element | x | y | w | h |
|---|---|---|---|---|
| Metric textbox | Inches(0.75) | Inches(1.5) | Inches(11.83) | Inches(4.0) |
| Label textbox | Inches(0.75) | Inches(5.6) | Inches(11.83) | Inches(0.8) |

Font size: `tokens.typography.size_metric_xxl` (default 200pt).

## 4. `quote_pullout`

240pt opaque-10% quote glyph background + quote + attribution.

| Element | x | y | w | h |
|---|---|---|---|---|
| Glyph picture | 0 | 0 | 12192000 | 6858000 |
| Quote textbox | Inches(1.5) | Inches(2.0) | Inches(10.3) | Inches(3.5) |
| Attribution | Inches(1.5) | Inches(5.7) | Inches(10.3) | Inches(0.7) |

Visual asset: required `composite/oversized_glyph_bg` (10% opacity
glyph U+201C centred-left on `bg_dark`).

## 5. `split_image_right`

Left half text; right half image. Anchor: `right_half`.

| Element | x | y | w | h |
|---|---|---|---|---|
| Right image | **6096000** (half) | 0 | 6096000 | 6858000 |
| Title textbox | Inches(0.75) | Inches(2.0) | Inches(5.6) | Inches(1.5) |
| Body textbox | Inches(0.75) | Inches(3.7) | Inches(5.6) | Inches(2.5) |

## 6. `tinted_panel_right`

Aside / supporting fact: right half tinted with `surface_elevated`
(10% lighter than `bg_light`).

| Element | x | y | w | h |
|---|---|---|---|---|
| Right tinted rect | 6096000 | 0 | 6096000 | 6858000 |
| Title textbox | Inches(0.75) | Inches(2.0) | Inches(5.6) | Inches(3.5) |
| Aside textbox | Inches(7.2) | Inches(2.0) | Inches(5.4) | Inches(4.0) |

## 7. `progress_dots`

Horizontal progress strip with N numbered markers. Built from a
matplotlib `chart/progress_strip` picture.

| Element | x | y | w | h |
|---|---|---|---|---|
| Title textbox | Inches(0.75) | Inches(0.6) | Inches(11.83) | Inches(0.9) |
| Strip picture | Inches(0.75) | Inches(2.5) | Inches(11.83) | Inches(3.5) |

If the chart asset is missing/skipped, the builder falls back to
a plain "step → step → step" textbox (still visually coherent on
`bg_light`, just without the dot graphics).

## 8. `chart_callout`

Left-half chart (matplotlib) + 2 right-side annotation textboxes.

| Element | x | y | w | h |
|---|---|---|---|---|
| Title textbox | Inches(0.75) | Inches(0.4) | Inches(11.83) | Inches(0.8) |
| Chart picture | Inches(0.5) | Inches(1.5) | **6096000 − Inches(0.5)** | Inches(5.3) |
| Callout #1 | Inches(7.0) | Inches(2.0) | Inches(5.6) | Inches(1.8) |
| Callout #2 | Inches(7.0) | Inches(4.2) | Inches(5.6) | Inches(1.8) |

The chart is **inset to the 0.5" safe margin** (C8 — no x=0 edge-touch,
honouring the system's own `safe_area_inches`). Chart asset: any of
`bar_with_callouts`, `dual_bar_diff`, `donut`, `sparkline`. The
strategist picks the recipe that fits the data shape; the builder
consumes the produced PNG.

## Validation rules (enforced by `_validate_slide`)

- `style: "styled"` + missing `style_recipe` → `bad_spec.styled_without_recipe`
- `style: "styled"` + `style_recipe` not registered in `STYLED_RECIPES` → `bad_spec.unknown_recipe`
- `style: "simple"` + non-null `style_recipe` → `bad_spec.simple_with_recipe`
- Missing `style` → C5 backwards-compat: treat as `style: "simple"`

## Editorial archetypes (C6 — session 2026-06-08-c5d9e1a7)

High-impact archetypes built on the craft helpers (`_add_card`,
`_add_hairline`, `_add_scrim`, `_set_tracking`, `_add_kicker`). All are
registered in `STYLED_RECIPES` / `STYLED_BUILDERS`.

| Recipe | Layout | Key spec fields |
|--------|--------|-----------------|
| `stat_grid_3up` | Three rounded-card big numbers + delta arrow + hairline + label | `title`, `stats: [{value, label, delta}]` (≤3; value auto-sizes by length) |
| `pull_quote_portrait` | Left 1/3 portrait card + right 2/3 display-face quote | `quote`, `attribution`, `role`, `portrait` (image path, optional) |
| `full_bleed_caption` | Full-bleed image + bottom gradient scrim + caption strip | `title`/`caption`, `image` (optional; scrim guarantees caption contrast) |
| `editorial_2col_6040` | 60% lead column (standfirst + ≤3 points) + 40% tonal aside card | `title`, `standfirst`, `points: []`, `aside: {kicker, body}` |
| `timeline_horizontal` | Baseline rule + milestone nodes + date labels | `title`, `milestones: [{date, label}]` |
| `agenda_toc` | Numbered sections w/ tracked numerals | `title`, `sections: []` |
| `closing_cta` | Restrained CTA + contact, asymmetric, one accent rule | `title`, `cta`, `contact` (dict `{name,email,phone,url}` or bare string) |

Craft notes:

- Cards use `surface_elevated` / `surface_on_dark` + a hairline border +
  optional soft shadow — never a raw saturated accent panel.
- Kickers are tracked uppercase (`_add_kicker`, +220 tracking) with an
  optional hairline rule beneath.
- `stat_grid_3up` numerals scale down for long values (e.g. `99.99%`,
  `3.2B`) so they never wrap/overflow the card.

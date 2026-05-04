# Styled Recipes (architecture §4.1)

The 8 canonical styled-slide recipes implemented by
`scripts/generate_deck.py`. All EMU coordinates assume 16:9 deck
geometry: **12,192,000 × 6,858,000 EMU** (1" = 914,400 EMU).

Each recipe is dispatched when `slide.style == "styled"` and
`slide.style_recipe == "<recipe>"`. The strategist/builder MUST
select from this canonical 8 — unknown recipes are rejected with
`bad_spec.unknown_recipe`.

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
| Chart picture | 0 | Inches(1.4) | **6096000** | Inches(5.6) |
| Callout #1 | Inches(7.0) | Inches(2.0) | Inches(5.6) | Inches(1.8) |
| Callout #2 | Inches(7.0) | Inches(4.2) | Inches(5.6) | Inches(1.8) |

Chart asset: any of `bar_with_callouts`, `dual_bar_diff`, `donut`,
`sparkline`. The strategist picks the recipe that fits the data
shape; the builder consumes the produced PNG.

## Validation rules (enforced by `_validate_slide`)

- `style: "styled"` + missing `style_recipe` → `bad_spec.styled_without_recipe`
- `style: "styled"` + `style_recipe` not in the 8-set → `bad_spec.unknown_recipe`
- `style: "simple"` + non-null `style_recipe` → `bad_spec.simple_with_recipe`
- Missing `style` → C5 backwards-compat: treat as `style: "simple"`

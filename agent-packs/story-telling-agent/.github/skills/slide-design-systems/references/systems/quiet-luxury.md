# Quiet Luxury

**Best for**: Funding asks, investor updates, premium brand / board
narratives. The restrained successor to `investor-gold` (no mustard
fills, no cliché gold-on-navy).
**Vibe**: Understated luxury — warm near-black canvas, bone type,
champagne used *only* as a hairline or numeral (never a fill, which is
what made the old gold read as mustard). Generous margins, one accent
line, nothing decorative.

**Canon**: Pyramid Principle (action titles), Presentation Zen
(restraint), Beautiful.ai generous-padding rule.

> Fonts (Source Serif 4 display, Inter body) are render-present on the
> host — the verified PNG shows the designed type (B2).

## Tokens

```json
{
  "name": "quiet-luxury",
  "palette": {
    "background_dark": "#161412",
    "background_light": "#F2EEE6",
    "background_accent": "#C8A96A",
    "primary_accent": "#C8A96A",
    "secondary_accent": "#1F3A2E",
    "highlight": "#C8A96A",
    "surface_elevated": "#FBF8F2",
    "surface_on_dark": "#221F1B",
    "text_on_dark": "#F2EEE6",
    "text_on_light": "#161412",
    "text_secondary": "#7C766C",
    "text_secondary_on_dark": "#B8AF9E",
    "text_secondary_on_light": "#6A6459",
    "divider": "#D9D2C4",
    "hairline": "#D9D2C4",
    "hairline_on_dark": "#3A352E",
    "scrim": "#161412",
    "tints": {
      "primary": {"100": "#F0E6D2", "300": "#DEC79A", "500": "#C8A96A", "700": "#9A8049", "900": "#5E4E2C"}
    }
  },
  "chart_palette": {
    "focal": "#1F3A2E",
    "muted": "#7C766C",
    "grid": "#D9D2C4",
    "ramp": ["#1F3A2E", "#C8A96A", "#7C766C", "#3E6B52", "#A8895A", "#4A453D"]
  },
  "type_scale": {"hero": 60, "section": 48, "title": 36, "subtitle": 22, "body": 18, "small": 15, "caption": 13, "fine_print": 10},
  "typography": {"font_title": "Source Serif 4", "font_body": "Inter", "title_weight": 600, "body_weight": 400, "eyebrow_weight": 600, "size_hero": 60, "size_section": 48, "size_title": 36, "size_subtitle": 22, "size_body": 18, "size_caption": 13, "size_metric_xxl": 180, "size_quote_glyph": 200},
  "fonts": {"title_family": "Source Serif 4", "body_family": "Inter", "mono_family": "IBM Plex Mono", "title_fallback": "Liberation Serif", "body_fallback": "Inter", "mono_fallback": "IBM Plex Mono", "render_safe": ["Inter", "Source Serif 4", "IBM Plex Sans", "IBM Plex Mono", "Fraunces", "Space Grotesk", "Archivo", "DejaVu Sans", "Carlito", "Liberation Sans", "Liberation Serif", "Noto Sans"]},
  "grid": {"slide_width_inches": 13.333, "slide_height_inches": 7.5, "margin_inches": 1.0, "stripe_left_inches": 0.0, "snap_inches": 0.05, "safe_area_inches": 0.5, "min_gutter_inches": 0.3},
  "accent_rules": {"top_bar_max_slides_pct": 0.0, "left_stripe_on_light": false, "title_underline_max": 1},
  "slide_type_defaults": {
    "title": {"background": "background_dark", "alignment": "left"},
    "section_divider": {"background": "background_dark", "alignment": "left"},
    "big_statement": {"background": "background_dark", "alignment": "left"},
    "headline_bullets": {"background": "background_light", "alignment": "left"},
    "split": {"background": "background_light", "alignment": "left"},
    "metric_spotlight": {"background": "background_dark", "alignment": "center"},
    "comparison_columns": {"background": "background_light", "alignment": "left"},
    "question": {"background": "background_dark", "alignment": "center"},
    "quote": {"background": "background_dark", "alignment": "left"},
    "visual_hero": {"background": "background_light", "alignment": "left"},
    "cta_steps": {"background": "background_dark", "alignment": "left"}
  }
}
```

## Usage Notes

- **Champagne is a line, never a fill.** Use `#C8A96A` for a single
  hairline under the kicker, a thin numeral, or a focal data mark. Filling
  a shape with it reproduces the mustard problem — don't.
- **1.0" margins, lots of air.** Restraint is the brand. One idea per
  slide; let whitespace carry the premium signal.
- Body contrast comes from bone-on-warm-black, not from the accent.
- Bottle green `#1F3A2E` is the chart focal so data has a sober anchor.

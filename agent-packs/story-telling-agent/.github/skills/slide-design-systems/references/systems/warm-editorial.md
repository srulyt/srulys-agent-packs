# Warm Editorial

**Best for**: Customer success stories, sales narratives, brand / culture
decks. The fixed successor to `customer-coral` (whose WCAG pass had
desaturated coral into muddy brick / rust brown).
**Vibe**: Warm and human — cream canvas, espresso type, a *vivid* coral
kept bright for heroes and pull-quotes, with contrast coming from the
dark espresso/plum body colour instead of from desaturating the coral.

**Canon**: Slide:ology (emotional sparkline), Beautiful.ai generous
padding, Presentation Zen picture-superiority.

> Fraunces display + Inter body are render-present on the host — the
> verified PNG shows the designed type (B2).

## Tokens

```json
{
  "name": "warm-editorial",
  "palette": {
    "background_dark": "#2A1E18",
    "background_light": "#FFF7F0",
    "background_accent": "#FF5A4D",
    "primary_accent": "#FF5A4D",
    "secondary_accent": "#5B2A45",
    "highlight": "#FF5A4D",
    "surface_elevated": "#FFFFFF",
    "surface_on_dark": "#382820",
    "text_on_dark": "#FFF7F0",
    "text_on_light": "#2A1E18",
    "text_secondary": "#8A7F73",
    "text_secondary_on_dark": "#CBBDAE",
    "text_secondary_on_light": "#6E635A",
    "divider": "#E7DACE",
    "hairline": "#E7DACE",
    "hairline_on_dark": "#4A3A30",
    "scrim": "#2A1E18",
    "tints": {
      "primary": {"100": "#FFE0DB", "300": "#FFA89F", "500": "#FF5A4D", "700": "#C73A30", "900": "#7E2019"},
      "secondary": {"100": "#E9D3DF", "300": "#B0789A", "500": "#5B2A45", "700": "#421E32", "900": "#2A1320"}
    }
  },
  "chart_palette": {
    "focal": "#FF5A4D",
    "muted": "#8A7F73",
    "grid": "#E7DACE",
    "ramp": ["#FF5A4D", "#5B2A45", "#8A7F73", "#E0915A", "#A0476A", "#C9B8A0"]
  },
  "type_scale": {"hero": 64, "section": 50, "title": 40, "subtitle": 24, "body": 20, "small": 16, "caption": 14, "fine_print": 11},
  "typography": {"font_title": "Fraunces", "font_body": "Inter", "title_weight": 700, "body_weight": 400, "eyebrow_weight": 600, "size_hero": 64, "size_section": 50, "size_title": 40, "size_subtitle": 24, "size_body": 20, "size_caption": 14, "size_metric_xxl": 200, "size_quote_glyph": 240},
  "fonts": {"title_family": "Fraunces", "body_family": "Inter", "mono_family": "IBM Plex Mono", "title_fallback": "Liberation Serif", "body_fallback": "Inter", "mono_fallback": "IBM Plex Mono", "render_safe": ["Inter", "Source Serif 4", "IBM Plex Sans", "IBM Plex Mono", "Fraunces", "Space Grotesk", "Archivo", "DejaVu Sans", "Carlito", "Liberation Sans", "Liberation Serif", "Noto Sans"]},
  "grid": {"slide_width_inches": 13.333, "slide_height_inches": 7.5, "margin_inches": 0.85, "stripe_left_inches": 0.0, "snap_inches": 0.05, "safe_area_inches": 0.5, "min_gutter_inches": 0.3},
  "accent_rules": {"top_bar_max_slides_pct": 0.2, "left_stripe_on_light": false, "title_underline_max": 1},
  "slide_type_defaults": {
    "title": {"background": "background_light", "alignment": "left"},
    "section_divider": {"background": "background_dark", "alignment": "left"},
    "big_statement": {"background": "background_light", "alignment": "left"},
    "headline_bullets": {"background": "background_light", "alignment": "left"},
    "split": {"background": "background_light", "alignment": "left"},
    "metric_spotlight": {"background": "background_dark", "alignment": "center"},
    "comparison_columns": {"background": "background_light", "alignment": "left"},
    "question": {"background": "background_dark", "alignment": "center"},
    "quote": {"background": "background_light", "alignment": "left"},
    "visual_hero": {"background": "background_light", "alignment": "left"},
    "cta_steps": {"background": "background_dark", "alignment": "left"}
  }
}
```

## Usage Notes

- **Keep the coral vivid.** `#FF5A4D` is for hero headlines, pull-quote
  marks, and the single focal chart series — at large sizes only. Do NOT
  desaturate it for contrast; that's what produced the old brick brown.
- **Contrast from the dark, not the accent.** Body copy is espresso
  `#2A1E18` on cream; plum `#5B2A45` anchors secondary structure.
- Pairs well with `pull_quote_portrait`, `full_bleed_caption`,
  `editorial_2col_6040`.

# Ink Editorial

**Best for**: Vision decks, manifestos, opinion / thought-leadership,
keynote-style narrative. The "do it right" successor to `editorial-mono`.
**Vibe**: Magazine editorial — paper-white canvas, ink type, one
vermilion signal, baseline grid, oversized section numerals, hairline
rules. Reads like a print spread, not a slide template.

**Canon**: Slide:ology / Resonate (sparkline, persistence of vision),
Presentation Zen (signal-to-noise), IBM Carbon hairline discipline.

> All fonts are render-present on the LibreOffice / Chromium host
> (Fraunces, Source Serif 4, IBM Plex Mono are installed), so the
> verified PNG shows the designed typography — not a substitute (B2).

## Tokens

```json
{
  "name": "ink-editorial",
  "palette": {
    "background_dark": "#0B0B0C",
    "background_light": "#FAFAF7",
    "background_accent": "#E5482F",
    "primary_accent": "#E5482F",
    "secondary_accent": "#0B0B0C",
    "highlight": "#E5482F",
    "surface_elevated": "#FFFFFF",
    "text_on_dark": "#FAFAF7",
    "text_on_light": "#0B0B0C",
    "text_secondary": "#6B6A66",
    "text_secondary_on_dark": "#B7B5AE",
    "text_secondary_on_light": "#6B6A66",
    "divider": "#D8D6CE",
    "hairline": "#D8D6CE",
    "hairline_on_dark": "#3A3A38",
    "scrim": "#0B0B0C",
    "tints": {
      "primary": {"100": "#FBE3DE", "300": "#F1A99B", "500": "#E5482F", "700": "#B0341F", "900": "#6E2114"}
    }
  },
  "chart_palette": {
    "focal": "#E5482F",
    "muted": "#6B6A66",
    "grid": "#D8D6CE",
    "ramp": ["#E5482F", "#0B0B0C", "#6B6A66", "#B0341F", "#9C8E73", "#C9B8A0"]
  },
  "type_scale": {"hero": 88, "section": 64, "title": 46, "subtitle": 26, "body": 20, "small": 16, "caption": 13, "fine_print": 11},
  "typography": {"font_title": "Fraunces", "font_body": "Source Serif 4", "title_weight": 800, "body_weight": 400, "eyebrow_weight": 600, "size_hero": 88, "size_section": 64, "size_title": 46, "size_subtitle": 26, "size_body": 20, "size_caption": 13, "size_metric_xxl": 200, "size_quote_glyph": 220},
  "fonts": {"title_family": "Fraunces", "body_family": "Source Serif 4", "mono_family": "IBM Plex Mono", "title_fallback": "Liberation Serif", "body_fallback": "Liberation Serif", "mono_fallback": "IBM Plex Mono", "render_safe": ["Inter", "Source Serif 4", "IBM Plex Sans", "IBM Plex Mono", "Fraunces", "Space Grotesk", "Archivo", "DejaVu Sans", "Carlito", "Liberation Sans", "Liberation Serif", "Noto Sans"]},
  "grid": {"slide_width_inches": 13.333, "slide_height_inches": 7.5, "margin_inches": 0.85, "stripe_left_inches": 0.0, "snap_inches": 0.05, "safe_area_inches": 0.5, "min_gutter_inches": 0.3},
  "accent_rules": {"top_bar_max_slides_pct": 0.1, "left_stripe_on_light": false, "title_underline_max": 0},
  "slide_type_defaults": {
    "title": {"background": "background_light", "alignment": "left"},
    "section_divider": {"background": "background_dark", "alignment": "left"},
    "big_statement": {"background": "background_light", "alignment": "left"},
    "headline_bullets": {"background": "background_light", "alignment": "left"},
    "split": {"background": "background_light", "alignment": "left"},
    "metric_spotlight": {"background": "background_light", "alignment": "left"},
    "comparison_columns": {"background": "background_light", "alignment": "left"},
    "question": {"background": "background_dark", "alignment": "left"},
    "quote": {"background": "background_light", "alignment": "left"},
    "visual_hero": {"background": "background_light", "alignment": "left"},
    "cta_steps": {"background": "background_dark", "alignment": "left"}
  }
}
```

## Usage Notes

- **One signal only.** Vermilion `#E5482F` is reserved for a single mark
  per slide — a numeral, a rule, a focal data point. Never a fill behind
  body text.
- **Hairlines over boxes.** Use `_add_hairline` (rule `#D8D6CE`) to divide
  the grid; avoid heavy panels. Oversized `01 / 02` section numerals in
  `tints.primary.500` carry the structure.
- **Tracked uppercase kickers** (`_add_kicker`, +220 tracking) above every
  hero. Generous `0.85"` margins; left-anchored asymmetry.
- Pairs best with archetypes `editorial_2col_6040`, `pull_quote_portrait`,
  `agenda_toc`, `full_bleed_caption`.

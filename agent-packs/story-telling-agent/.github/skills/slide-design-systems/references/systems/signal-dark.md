# Signal Dark

**Best for**: Engineering reviews, architecture decks, product / platform
launches. The original-palette successor to `technical-slate` (no
Stripe / Supabase / Catppuccin brand pastiche).
**Vibe**: Modern dark-first product UI — cool charcoal, one signature
iris accent, a mint focal for data, and a full tint ladder so cards and
insets carry tone instead of one flat fill.

**Canon**: marp / slidev dark conventions, Beautiful.ai slot grids,
Material type scale, IBM Carbon elevation tokens.

> Space Grotesk display, Inter body, IBM Plex Mono are render-present on
> the host — the verified PNG shows the designed type (B2).

## Tokens

```json
{
  "name": "signal-dark",
  "palette": {
    "background_dark": "#14161B",
    "background_light": "#EEF1F4",
    "background_accent": "#5468FF",
    "primary_accent": "#5468FF",
    "secondary_accent": "#46E5B0",
    "highlight": "#46E5B0",
    "surface_elevated": "#F6F8FA",
    "surface_on_dark": "#1E2128",
    "text_on_dark": "#EEF1F4",
    "text_on_light": "#14161B",
    "text_secondary": "#6B7280",
    "text_secondary_on_dark": "#9AA1AC",
    "text_secondary_on_light": "#5A626E",
    "divider": "#D5DAE0",
    "hairline": "#D5DAE0",
    "hairline_on_dark": "#2C313A",
    "scrim": "#14161B",
    "tints": {
      "primary": {"50": "#EEF0FF", "100": "#DADFFF", "300": "#9AA6FF", "500": "#5468FF", "700": "#3A49C2", "900": "#222C78"},
      "focal": {"100": "#D6FBEE", "300": "#86F0CC", "500": "#46E5B0", "700": "#2BA37C", "900": "#185A45"}
    }
  },
  "chart_palette": {
    "focal": "#46E5B0",
    "muted": "#9AA1AC",
    "grid": "#2C313A",
    "ramp": ["#5468FF", "#46E5B0", "#9AA1AC", "#8A6BFF", "#3FB6F0", "#F0A93F"]
  },
  "type_scale": {"hero": 60, "section": 48, "title": 40, "subtitle": 24, "body": 20, "small": 16, "caption": 14, "fine_print": 11},
  "typography": {"font_title": "Space Grotesk", "font_body": "Inter", "title_weight": 700, "body_weight": 400, "eyebrow_weight": 600, "size_hero": 60, "size_section": 48, "size_title": 40, "size_subtitle": 24, "size_body": 20, "size_caption": 14, "size_metric_xxl": 200, "size_quote_glyph": 220},
  "fonts": {"title_family": "Space Grotesk", "body_family": "Inter", "mono_family": "IBM Plex Mono", "title_fallback": "Archivo", "body_fallback": "Inter", "mono_fallback": "IBM Plex Mono", "render_safe": ["Inter", "Source Serif 4", "IBM Plex Sans", "IBM Plex Mono", "Fraunces", "Space Grotesk", "Archivo", "DejaVu Sans", "Carlito", "Liberation Sans", "Liberation Serif", "Noto Sans"]},
  "grid": {"slide_width_inches": 13.333, "slide_height_inches": 7.5, "margin_inches": 0.75, "stripe_left_inches": 0.0, "snap_inches": 0.05, "safe_area_inches": 0.5, "min_gutter_inches": 0.25},
  "accent_rules": {"top_bar_max_slides_pct": 0.3, "left_stripe_on_light": false, "title_underline_max": 1},
  "slide_type_defaults": {
    "title": {"background": "background_dark", "alignment": "left"},
    "section_divider": {"background": "background_dark", "alignment": "left"},
    "big_statement": {"background": "background_dark", "alignment": "left"},
    "headline_bullets": {"background": "background_dark", "alignment": "left"},
    "split": {"background": "background_dark", "alignment": "left"},
    "metric_spotlight": {"background": "background_dark", "alignment": "center"},
    "comparison_columns": {"background": "background_light", "alignment": "left"},
    "question": {"background": "background_dark", "alignment": "center"},
    "quote": {"background": "background_dark", "alignment": "left"},
    "visual_hero": {"background": "background_dark", "alignment": "left"},
    "cta_steps": {"background": "background_dark", "alignment": "left"}
  }
}
```

## Usage Notes

- **Tone, not flat fills.** Cards and insets use `surface_on_dark`
  `#1E2128` (one step elevated) + a `hairline_on_dark` rule — never a raw
  accent panel. Use the `tints.primary` / `tints.focal` ladders for
  hover-like depth in `stat_grid_3up` and `editorial_2col_6040`.
- **Iris is the brand, mint is the data.** `#5468FF` for structure /
  accent rules; `#46E5B0` reserved for the single focal series in charts
  and the one "look here" mark per slide.
- IBM Plex Mono for code blocks / metrics at 18–20pt.

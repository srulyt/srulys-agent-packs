# Executive Navy

**Best for**: C-level decision asks, board updates, executive briefings.
**Vibe**: Authoritative, conservative, restrained. Default for
buy-in / funding asks where credibility outweighs flair.

**Canon**: Pyramid Principle (action titles, MECE), Presentation Zen
(signal-to-noise).

## Tokens

```json
{
  "name": "executive-navy",
  "palette": {
    "background_dark": "#0F1B2D",
    "background_light": "#F4F5F7",
    "background_accent": "#1D4ED8",
    "primary_accent": "#3B82F6",
    "secondary_accent": "#06B6D4",
    "highlight": "#F59E0B",
    "text_on_dark": "#FFFFFF",
    "text_on_light": "#1A1A2E",
    "text_secondary": "#6B7080",
    "text_secondary_on_dark": "#B8BCC8",
    "divider": "#E2E4E8"
  },
  "type_scale": {"hero": 54, "section": 48, "title": 40, "subtitle": 24, "body": 22, "small": 18, "caption": 14, "fine_print": 11},
  "fonts": {"title_family": "Inter", "body_family": "Inter", "mono_family": "IBM Plex Mono", "title_fallback": "Inter", "body_fallback": "Inter", "mono_fallback": "IBM Plex Mono", "render_safe": ["Inter", "Source Serif 4", "IBM Plex Sans", "IBM Plex Mono", "Fraunces", "Space Grotesk", "Archivo", "DejaVu Sans", "Carlito", "Liberation Sans", "Liberation Serif", "Noto Sans"]},
  "grid": {"slide_width_inches": 13.333, "slide_height_inches": 7.5, "margin_inches": 0.75, "stripe_left_inches": 0.45, "snap_inches": 0.05, "safe_area_inches": 0.5, "min_gutter_inches": 0.25},
  "accent_rules": {"top_bar_max_slides_pct": 0.4, "left_stripe_on_light": true, "title_underline_max": 2},
  "slide_type_defaults": {
    "title": {"background": "background_dark", "alignment": "left"},
    "section_divider": {"background": "background_dark", "alignment": "center"},
    "big_statement": {"background": "background_dark", "alignment": "left"},
    "headline_bullets": {"background": "background_light", "alignment": "left"},
    "split": {"background": "background_light", "alignment": "left"},
    "metric_spotlight": {"background": "background_dark", "alignment": "center"},
    "comparison_columns": {"background": "background_light", "alignment": "left"},
    "question": {"background": "background_dark", "alignment": "center"},
    "quote": {"background": "background_dark", "alignment": "center"},
    "visual_hero": {"background": "background_light", "alignment": "left"},
    "cta_steps": {"background": "background_dark", "alignment": "left"}
  }
}
```

## Usage Notes

- Use the highlight gold (`#F59E0B`) only for key metrics on dark
  backgrounds — never for body text.
- Left stripe on every light content slide — visual anchor; signals
  consistency.
- Top accent bar reserved for ≤40% of slides; skip on Big Statement,
  Question, Quote.

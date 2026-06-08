# Boardroom Conservative

**Best for**: Regulated industries (finance, healthcare, legal),
M&A diligence, audit committees, compliance updates. **Vibe**:
Traditional consulting, BCG/Bain-derived.

**Canon**: BCG/Bain conventions (action titles + 2-line subtitles, left
strip, 10pt footnoted sources), Pyramid Principle.

## Tokens

```json
{
  "name": "boardroom-conservative",
  "palette": {
    "background_dark": "#0A2540",
    "background_light": "#FFFFFF",
    "background_accent": "#0A2540",
    "primary_accent": "#0A2540",
    "secondary_accent": "#7A95B8",
    "highlight": "#C8102E",
    "text_on_dark": "#FFFFFF",
    "text_on_light": "#1A1A1A",
    "text_secondary": "#5A5A5A",
    "text_secondary_on_dark": "#A0A0A0",
    "divider": "#D0D5DC"
  },
  "type_scale": {"hero": 44, "section": 40, "title": 32, "subtitle": 20, "body": 20, "small": 16, "caption": 12, "fine_print": 10},
  "fonts": {"title_family": "Source Serif 4", "body_family": "Inter", "mono_family": "IBM Plex Mono", "title_fallback": "Liberation Serif", "body_fallback": "Inter", "mono_fallback": "IBM Plex Mono", "render_safe": ["Inter", "Source Serif 4", "IBM Plex Sans", "IBM Plex Mono", "Fraunces", "Space Grotesk", "Archivo", "DejaVu Sans", "Carlito", "Liberation Sans", "Liberation Serif", "Noto Sans"]},
  "grid": {"slide_width_inches": 13.333, "slide_height_inches": 7.5, "margin_inches": 0.7, "stripe_left_inches": 0.35, "snap_inches": 0.05},
  "accent_rules": {"top_bar_max_slides_pct": 0.5, "left_stripe_on_light": true, "title_underline_max": 1},
  "slide_type_defaults": {
    "title": {"background": "background_dark", "alignment": "left"},
    "section_divider": {"background": "background_dark", "alignment": "left"},
    "big_statement": {"background": "background_light", "alignment": "left"},
    "headline_bullets": {"background": "background_light", "alignment": "left"},
    "split": {"background": "background_light", "alignment": "left"},
    "metric_spotlight": {"background": "background_light", "alignment": "left"},
    "comparison_columns": {"background": "background_light", "alignment": "left"},
    "question": {"background": "background_light", "alignment": "left"},
    "quote": {"background": "background_light", "alignment": "left"},
    "visual_hero": {"background": "background_light", "alignment": "left"},
    "cta_steps": {"background": "background_light", "alignment": "left"}
  }
}
```

## Usage Notes

- White-dominant deck (≥80% light). Dark slides reserved for title +
  section dividers.
- Action titles MUST include a 2-line subtitle giving the "so what"
  in 16pt secondary text. Builders fold this into the title block.
- Footnoted source attribution at 10pt, bottom-left, on every data slide.
- The single red highlight (`#C8102E`) is reserved for risk callouts
  and CTA decisions — never decorative.
- Keep typography boring on purpose — Arial conveys "compliant".

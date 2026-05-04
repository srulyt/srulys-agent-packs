# Customer Coral

**Best for**: Customer success stories, sales pitches, narrative-driven
case studies. **Vibe**: Warm, human, narrative.

**Canon**: Duarte (sparkline, persistence-of-vision), Beautiful.ai/Gamma
(rotated accents).

## Tokens

```json
{
  "name": "customer-coral",
  "palette": {
    "background_dark": "#0F1B2D",
    "background_light": "#FFF7F2",
    "background_accent": "#F87171",
    "primary_accent": "#F87171",
    "secondary_accent": "#FB923C",
    "highlight": "#06B6D4",
    "text_on_dark": "#FFFFFF",
    "text_on_light": "#1A1A2E",
    "text_secondary": "#7B6F66",
    "divider": "#FCD9C7"
  },
  "type_scale": {"hero": 54, "section": 48, "title": 40, "subtitle": 24, "body": 22, "small": 18, "caption": 14, "fine_print": 11},
  "fonts": {"title_family": "Inter", "body_family": "Inter", "mono_family": "Consolas"},
  "grid": {"slide_width_inches": 13.333, "slide_height_inches": 7.5, "margin_inches": 0.85, "stripe_left_inches": 0.45, "snap_inches": 0.05},
  "accent_rules": {"top_bar_max_slides_pct": 0.3, "left_stripe_on_light": true, "title_underline_max": 1},
  "slide_type_defaults": {
    "title": {"background": "background_dark", "alignment": "left"},
    "section_divider": {"background": "background_accent", "alignment": "center"},
    "big_statement": {"background": "background_accent", "alignment": "center"},
    "headline_bullets": {"background": "background_light", "alignment": "left"},
    "split": {"background": "background_light", "alignment": "left"},
    "metric_spotlight": {"background": "background_dark", "alignment": "center"},
    "comparison_columns": {"background": "background_light", "alignment": "left"},
    "question": {"background": "background_dark", "alignment": "center"},
    "quote": {"background": "background_accent", "alignment": "center"},
    "visual_hero": {"background": "background_light", "alignment": "left"},
    "cta_steps": {"background": "background_dark", "alignment": "left"}
  }
}
```

## Usage Notes

- Rotated accents on Big Statements (coral / orange) by section reinforce
  emotional arc.
- Cream `background_light` warms otherwise-cold customer testimonials.
- Quotes get the coral background — emotional anchor.
- Use sparkline emotional contour: peaks on Big Statement / Quote
  slides, valleys on data slides.

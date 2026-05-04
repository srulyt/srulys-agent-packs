# Technical Slate

**Best for**: Engineering reviews, architecture decisions, technical
deep-dives. **Vibe**: Modern, dark-first, code-aware.

**Canon**: marp/slidev/reveal.js (dark default, monospace), Beautiful.ai
(slot grids, padding-hard-rule).

## Tokens

```json
{
  "name": "technical-slate",
  "palette": {
    "background_dark": "#1E1E2E",
    "background_light": "#2A2A3E",
    "background_accent": "#635BFF",
    "primary_accent": "#635BFF",
    "secondary_accent": "#3ECF8E",
    "highlight": "#FF6B6B",
    "text_on_dark": "#F0F2F5",
    "text_on_light": "#F0F2F5",
    "text_secondary": "#A0A4B0",
    "divider": "#3A3A4E"
  },
  "type_scale": {"hero": 54, "section": 44, "title": 36, "subtitle": 22, "body": 20, "small": 18, "caption": 14, "fine_print": 11},
  "fonts": {"title_family": "Inter", "body_family": "Inter", "mono_family": "JetBrains Mono"},
  "grid": {"slide_width_inches": 13.333, "slide_height_inches": 7.5, "margin_inches": 0.85, "stripe_left_inches": 0.0, "snap_inches": 0.05},
  "accent_rules": {"top_bar_max_slides_pct": 0.2, "left_stripe_on_light": false, "title_underline_max": 0},
  "slide_type_defaults": {
    "title": {"background": "background_dark", "alignment": "left"},
    "section_divider": {"background": "background_accent", "alignment": "left"},
    "big_statement": {"background": "background_dark", "alignment": "left"},
    "headline_bullets": {"background": "background_dark", "alignment": "left"},
    "split": {"background": "background_dark", "alignment": "left"},
    "metric_spotlight": {"background": "background_dark", "alignment": "center"},
    "comparison_columns": {"background": "background_dark", "alignment": "left"},
    "question": {"background": "background_dark", "alignment": "center"},
    "quote": {"background": "background_dark", "alignment": "center"},
    "visual_hero": {"background": "background_dark", "alignment": "left"},
    "cta_steps": {"background": "background_accent", "alignment": "left"}
  }
}
```

## Usage Notes

- Dark-first: ~90% of slides on `background_dark`. Section dividers
  swap to the indigo accent.
- Code blocks use `mono_family` at 18pt with the green secondary accent.
- No title underlines (`title_underline_max: 0`) — typography handles separation.
- Padding is generous (0.85" margin) — never crowd content.

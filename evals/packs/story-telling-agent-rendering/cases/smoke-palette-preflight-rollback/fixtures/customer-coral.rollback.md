# Customer Coral — ROLLBACK FIXTURE (pre-F3-fix state)

> **THIS FILE IS A TEST FIXTURE.** It deliberately re-introduces
> the pre-F3 token values that fail WCAG AA. It is copied over
> the real `customer-coral.md` only inside the isolated workspace
> of the `smoke-palette-preflight-rollback` eval case. Do NOT
> use this content as a real design system.

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

## Why this fixture exists (regression context)

Iteration 1 of the F3 fix replaced two failing tokens with
WCAG-AA-compliant values:

- `background_accent` was `#F87171` (3.0:1 vs white) — failed AA body.
  Iteration 1 replaced it with `#B91C1C` (red-700, 7.4:1 vs white).
- `secondary_accent` was `#FB923C` (2.4:1 vs white) — failed AA body
  AND large-text. Iteration 1 replaced it with `#9A3412` (orange-800,
  8.2:1 vs white).

This rollback fixture re-introduces both failing values so the
`smoke-palette-preflight-rollback` eval case can prove that
`check_palettes.py` (the G1 preflight gate) catches the regression
and exits with code 2 BEFORE any deck assembly happens. If
iteration 1's token replacements are ever rolled back in real
code, this case fails — protecting the F3 fix.

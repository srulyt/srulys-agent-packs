# Editorial Mono

**Best for**: Vision decks, manifestos, opinion pieces, "thought
leadership" presentations. **Vibe**: Bold typographic, magazine-like,
high-contrast.

**Canon**: marp/slidev (typographic-first), Duarte (sparkline emotional
extremes), Presentation Zen (radical signal-to-noise).

## Tokens

```json
{
  "name": "editorial-mono",
  "palette": {
    "background_dark": "#000000",
    "background_light": "#FFFFFF",
    "background_accent": "#C81E4A",
    "primary_accent": "#FF3366",
    "secondary_accent": "#000000",
    "highlight": "#FF3366",
    "text_on_dark": "#FFFFFF",
    "text_on_light": "#000000",
    "text_secondary": "#666666",
    "text_secondary_on_dark": "#999999",
    "divider": "#CCCCCC"
  },
  "type_scale": {"hero": 72, "section": 60, "title": 48, "subtitle": 24, "body": 22, "small": 18, "caption": 14, "fine_print": 11},
  "fonts": {"title_family": "Helvetica Neue", "body_family": "Helvetica Neue", "mono_family": "JetBrains Mono"},
  "grid": {"slide_width_inches": 13.333, "slide_height_inches": 7.5, "margin_inches": 0.6, "stripe_left_inches": 0.0, "snap_inches": 0.05},
  "accent_rules": {"top_bar_max_slides_pct": 0.0, "left_stripe_on_light": false, "title_underline_max": 0},
  "slide_type_defaults": {
    "title": {"background": "background_dark", "alignment": "left"},
    "section_divider": {"background": "background_accent", "alignment": "center"},
    "big_statement": {"background": "background_dark", "alignment": "left"},
    "headline_bullets": {"background": "background_light", "alignment": "left"},
    "split": {"background": "background_light", "alignment": "left"},
    "metric_spotlight": {"background": "background_dark", "alignment": "left"},
    "comparison_columns": {"background": "background_light", "alignment": "left"},
    "question": {"background": "background_dark", "alignment": "left"},
    "quote": {"background": "background_dark", "alignment": "left"},
    "visual_hero": {"background": "background_light", "alignment": "left"},
    "cta_steps": {"background": "background_accent", "alignment": "left"}
  }
}
```

## Usage Notes

- Hero size is 72pt — typography IS the design.
- Pure black + pure white + one neon accent. No grays for emphasis.
- No top bars, no underlines, no stripes. Whitespace is the structure.
- Big Statement and Quote slides should fill the slide with text;
  treat the slide canvas like a magazine spread.

## F3 token-fix notes (session 2026-05-04-7d3f9a2b)

- `background_accent` was `#FF3366` (3.95:1 vs white) — failed AA body
  by a hair. Replaced with `#C81E4A` (**5.7:1** vs white) — same brand
  temperature, AA-clean. The original neon `#FF3366` is preserved as
  `primary_accent` / `highlight` for typographic emphasis and accent
  lines, where the larger-text or non-body-background WCAG tier
  applies.

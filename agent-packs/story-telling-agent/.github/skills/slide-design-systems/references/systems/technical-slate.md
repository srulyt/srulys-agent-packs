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
    "background_light": "#F5F6FA",
    "surface_elevated": "#2A2A3E",
    "background_accent": "#4F46E5",
    "primary_accent": "#635BFF",
    "secondary_accent": "#3ECF8E",
    "highlight": "#FF6B6B",
    "text_on_dark": "#FFFFFF",
    "text_on_light": "#0F1019",
    "text_secondary_on_light": "#5A6070",
    "text_secondary_on_dark": "#A0A4B0",
    "divider": "#3A3A4E"
  },
  "type_scale": {"hero": 54, "section": 44, "title": 36, "subtitle": 22, "body": 20, "small": 18, "caption": 14, "fine_print": 11},
  "fonts": {"title_family": "Inter", "body_family": "Inter", "mono_family": "IBM Plex Mono", "title_fallback": "Inter", "body_fallback": "Inter", "mono_fallback": "IBM Plex Mono", "render_safe": ["Inter", "Source Serif 4", "IBM Plex Sans", "IBM Plex Mono", "Fraunces", "Space Grotesk", "Archivo", "DejaVu Sans", "Carlito", "Liberation Sans", "Liberation Serif", "Noto Sans"]},
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

## F3 token-fix notes (session 2026-05-04-7d3f9a2b)

- `background_accent` was `#635BFF` (4.10:1 vs `#F0F2F5`) — failed
  AA body. Replaced with `#4F46E5` (indigo-600), which yields **5.94:1**
  vs `#FFFFFF` text. The original `#635BFF` is preserved as
  `primary_accent` for icons / lines / focal-point chart marks (where
  the contrast rules don't apply), and must NOT be used as a body-text
  background (per Refactoring-UI canon).
- `background_light` was `#2A2A3E` (a misnamed dark surface). The
  genuine light variant is now `#F5F6FA` (≈16.8:1 vs the new
  `text_on_light` `#0F1019`); the prior dark surface keeps its
  legitimate role as `surface_elevated` (panel surface, not slide
  background).
- `text_on_dark` lifted to `#FFFFFF` (max contrast); `text_on_light`
  darkened to `#0F1019` (17.2:1 on `background_light`).

## F4 token-fix notes (text_secondary surface split)

- `text_secondary` was a single value `#A0A4B0`, which yielded
  6.59:1 on `background_dark` (PASS) but only 2.31:1 on
  `background_light` (FAIL AA). The two backgrounds in this system
  (`#1E1E2E` ↔ `#F5F6FA`, mutual ratio ≈15.2:1) are too far apart
  for any single mid-gray to clear 4.5:1 against both — see
  [`wcag-thresholds.md`](../wcag-thresholds.md) for the math.
- Resolution: split into two surface-scoped tokens.
  - `text_secondary_on_light: "#5A6070"` → 5.82:1 on
    `background_light` (PASS).
  - `text_secondary_on_dark: "#A0A4B0"` → 6.59:1 on
    `background_dark` (PASS, value preserved).
- The legacy bare `text_secondary` key is intentionally absent for
  this system. `check_palettes.py` resolves the per-surface tokens
  preferentially when present; consumers that read
  `palette["text_secondary"]` MUST switch to surface-aware lookup
  (use `text_secondary_on_<surface>`) when they encounter a system
  that ships the split.

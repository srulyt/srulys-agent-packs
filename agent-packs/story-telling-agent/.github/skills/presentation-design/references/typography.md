# Typography (Material 3 type scale)

The rendering subsystem standardises on a **Material 3-derived
type scale** with two presentation-specific extensions
(`size_metric_xxl`, `size_quote_glyph`).

## Token names (deck-spec.design_system_tokens.typography)

| Token | Default pt | Material 3 role | Used for |
|-------|------------|-----------------|----------|
| `size_hero`       | 54  | Display Large    | Title slide headline |
| `size_section`    | 48  | Display Medium   | Section divider title |
| `size_title`      | 40  | Display Small    | Content slide title |
| `size_subtitle`   | 24  | Headline Small   | Title subtitles, eyebrows |
| `size_body`       | 22  | Title Medium     | Bullet text, paragraphs |
| `size_caption`    | 14  | Body Small       | Source attributions |
| `size_metric_xxl` | 200 | (presentation extension) | `metric_xxl` recipe |
| `size_quote_glyph`| 240 | (presentation extension) | `quote_pullout` glyph background |

## Why Material 3?

- **Recognised, documented, accessible** scale — eliminates
  bikeshedding about exact pt values.
- The five Display sizes are visually distinct on a 13.333"
  projected slide at 6m audience distance.
- Material 3's *role-based* naming maps cleanly onto our
  slide-element vocabulary.

## Font selection

Two tokens drive font selection:

| Token | Default | Role |
|-------|---------|------|
| `font_title` | "Calibri Light" | Display sizes (≥ 40pt) |
| `font_body`  | "Calibri"       | All body / caption sizes |

The fallback is "Calibri" because LibreOffice's font matcher
substitutes it cleanly for missing fonts when rendering on Linux.
For brand-specific systems (e.g. `editorial-mono`) the title font
may be a serif or display face — that's a per-system override.

## Pt → EMU conversions

We use python-pptx `Pt(...)` everywhere; never raw EMU for
text sizes. The `size_metric_xxl: 200` becomes `Pt(200)`.

## Contrast considerations (linked to wcag-thresholds.md)

The 18pt+ regular / 14pt+ bold "large text" tier in WCAG 2.1
allows contrast 3:1 instead of 4.5:1. In our scale, anything at
or above `size_subtitle` (24pt) qualifies as large text — which
relaxes contrast checking on hero and section titles. The
structural asserts apply this tier-aware threshold automatically
via the `large_text` flag in `contrast_violations`.

## Out-of-scope

This reference covers **rendering-relevant** typography only.
For narrative-level guidance (parallel structure, action titles,
the "Punch Test"), see the unmodified narrative sections of
`presentation-design/SKILL.md` and `narrative-craft/SKILL.md`.

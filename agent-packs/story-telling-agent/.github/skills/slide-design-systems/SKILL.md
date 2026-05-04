---
name: slide-design-systems
description: "Curated digest of widely-used deck-design canon (Pyramid Principle, Presentation Zen, Duarte, BCG action titles, Beautiful.ai/Gamma, marp/slidev) plus six fully-specified design systems (palette + type scale + grid + slide-type defaults) usable directly as deck-spec config. Loaded by @deck-builder for system selection. Keywords: design system, palette, typography, grid, theme, executive, technical, customer, investor, editorial, boardroom."
---

# Slide Design Systems

A condensed library of presentation-design canon plus six concrete,
production-ready design systems the deck-builder can drop into a
`deck-spec.json` without further customization.

## Table of Contents

1. [When to Use This Skill](#when-to-use-this-skill)
2. [Design Canon Digest](#design-canon-digest)
3. [The Six Design Systems](#the-six-design-systems)
4. [System Selection by Audience](#system-selection-by-audience)
5. [Token Schema (deck-spec compatibility)](#token-schema-deck-spec-compatibility)
6. [References](#references)

## When to Use This Skill

Load this skill when:

- The user has named a design system in `intake.json.design_system`
  (e.g. `executive-navy`, `technical-slate`, `customer-coral`).
- No design system is named and the deck-builder needs to pick one
  based on audience archetype.
- The user wants to build a deck "in the style of" McKinsey, BCG,
  Apple keynote, Stripe presentations, etc.

## Design Canon Digest

The systems below are synthesized from the following canon. Each
attribution is tagged so you know what you're inheriting.

### Pyramid Principle (Barbara Minto / McKinsey)

- **Action titles** — Every slide title is a complete-sentence
  conclusion ("Revenue grew 40%"), never a label ("Revenue").
- **MECE structure** — Sub-points under a slide are Mutually Exclusive
  and Collectively Exhaustive.
- **Top-down argument** — State the answer first; details come after.

Affects: `executive-navy`, `boardroom-conservative`, `investor-gold`.

### Presentation Zen (Garr Reynolds)

- **Signal-to-noise ratio** — Maximize signal; eliminate decoration.
- **Picture superiority** — Images carry meaning faster than text.
- **One idea per slide** — Multiple ideas compete and lose.

Affects: all systems (the pack default).

### Slide:ology / Resonate (Nancy Duarte)

- **Sparkline** — Map every slide's emotion to a contour: peaks for
  big-statement / question slides, valleys for data / evidence slides.
- **Persistence of vision** — Visual theme detectable across ≥80% of
  slides (palette + accent + typography pairing).

Affects: `customer-coral`, `editorial-mono`.

### BCG / Bain Consulting Conventions

- **Action titles** with 2-line subtitles giving the "so what".
- **Footnoted source attribution** at 10pt.
- **Consistent left-margin strip** for section identity.

Affects: `boardroom-conservative`.

### Beautiful.ai / Gamma Opinionated Layouts

- **Slot-based auto-layout grids** that auto-balance content.
- **Always-fresh accent on Big Statements** rotated by section.
- **Generous padding** as a hard rule.

Affects: `technical-slate`, `customer-coral`.

### marp / slidev / reveal.js Theme Conventions

Translated to python-pptx as: monospace code blocks at 18pt, dark
default background, single bold accent, asymmetric content alignment.

Affects: `technical-slate`, `editorial-mono`.

### Material Design / Apple HIG Type Scales

- **Major-third type scale** (1.25× ratio): 16, 20, 25, 31, 39, 49, 61.
- **Sentence case** for titles (not Title Case).
- **48pt minimum** for hero headlines on 16:9.

Affects: all systems (pack typography baseline).

## The Six Design Systems

| System | Best For | Vibe | Default Background Mix |
|--------|----------|------|------------------------|
| `executive-navy` | C-level decision asks, board updates | Authoritative, conservative | 30% dark navy / 60% off-white / 10% accent |
| `technical-slate` | Engineering reviews, architecture decks | Modern, technical, dark-first | 60% charcoal / 30% slate / 10% electric indigo |
| `customer-coral` | Customer success stories, pitches | Warm, human, narrative | 50% off-white / 30% coral-tinted / 20% deep navy |
| `investor-gold` | Funding asks, investor updates | Premium, restrained, confident | 40% dark / 50% cream / 10% gold |
| `editorial-mono` | Vision decks, manifestos, opinion | Bold typographic, magazine | 70% black or pure white / 30% inverse |
| `boardroom-conservative` | Regulated industries, M&A | Traditional consulting | 20% deep blue / 70% white / 10% red |

## System Selection by Audience

| Audience | Decision Ask | Customer Story | Technical Review | Vision |
|----------|--------------|----------------|------------------|--------|
| Executive | `executive-navy` | `customer-coral` | `executive-navy` | `editorial-mono` |
| Technical | `technical-slate` | `customer-coral` | `technical-slate` | `technical-slate` |
| Customer | `customer-coral` | `customer-coral` | `technical-slate` | `editorial-mono` |
| Investor | `investor-gold` | `customer-coral` | `investor-gold` | `editorial-mono` |
| Board / Regulated | `boardroom-conservative` | `executive-navy` | `boardroom-conservative` | `executive-navy` |

## Token Schema (deck-spec compatibility)

Every system file under `references/systems/` provides this JSON
schema, embeddable in `deck-spec.json` under `design_system_tokens`:

```json
{
  "name": "executive-navy",
  "palette": {
    "background_dark": "#0F1B2D",
    "background_light": "#F4F5F7",
    "background_accent": "#3B82F6",
    "primary_accent": "#3B82F6",
    "secondary_accent": "#06B6D4",
    "highlight": "#F59E0B",
    "text_on_dark": "#FFFFFF",
    "text_on_light": "#1A1A2E",
    "text_secondary": "#6B7080",
    "divider": "#E2E4E8"
  },
  "type_scale": {"hero": 54, "section": 48, "title": 40, "subtitle": 24, "body": 22, "small": 18, "caption": 14, "fine_print": 11},
  "fonts": {"title_family": "Calibri Light", "body_family": "Calibri", "mono_family": "Consolas"},
  "grid": {"slide_width_inches": 13.333, "slide_height_inches": 7.5, "margin_inches": 0.75, "stripe_left_inches": 0.45, "snap_inches": 0.05},
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

### Optional surface-aware override: `text_secondary_on_*`

A system MAY ship `text_secondary_on_light` and / or
`text_secondary_on_dark` *in addition to (or instead of)* the bare
`text_secondary` key. When present, `check_palettes.py` (G1) and
the rendering scripts resolve the secondary-text colour against
the override that matches the slide's surface, falling back to the
bare key only when the override is absent. This exists for systems
whose dark and light backgrounds are too close in luminance for
any single mid-gray to clear AA against both — see
`references/systems/technical-slate.md` (F4 note) and
`references/wcag-thresholds.md` for the math.

## References

- [Design Canon](references/design-canon.md) — Expanded notes on the canon listed above
- [Executive Navy](references/systems/executive-navy.md)
- [Technical Slate](references/systems/technical-slate.md)
- [Customer Coral](references/systems/customer-coral.md)
- [Investor Gold](references/systems/investor-gold.md)
- [Editorial Mono](references/systems/editorial-mono.md)
- [Boardroom Conservative](references/systems/boardroom-conservative.md)

## Rendering Subsystem Rebuild (2026-05-04)

Three additions in session 2026-05-04-7d3f9a2b:

- **scripts/check_palettes.py** — the **G1 preflight gate**.
  Extracts the JSON token block from each system `.md` file,
  runs WCAG contrast pair checks, exits 2 on any failing pair.
  Run by `@deck-builder` first, re-run by `@deck-critic`
  as a cross-check (per critic concern C1).
- **eferences/wcag-thresholds.md** — canonical thresholds
  (4.5:1 normal text; 3:1 large text 18pt+ regular or 14pt+
  bold; 3:1 graphical components).
- **eferences/canon.md** — the rebuild canon (F11 body word
  limit 30, section_divider styled-by-default per OQ4, style
  taxonomy `simple` vs `styled`, the 8 styled recipes).

Token tables in the three rebuilt systems
(`technical-slate`, `customer-coral`, `editorial-mono`)
were patched with WCAG-passing palette values (F3).

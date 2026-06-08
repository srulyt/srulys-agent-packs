---
name: slide-design-systems
description: "Curated digest of widely-used deck-design canon (Pyramid Principle, Presentation Zen, Duarte, BCG action titles, Beautiful.ai/Gamma, marp/slidev) plus ten fully-specified design systems (palette + tint ladders + type scale + grid + slide-type defaults) usable directly as deck-spec config. Loaded by @deck-builder for system selection. Keywords: design system, palette, typography, grid, theme, executive, technical, customer, investor, editorial, boardroom, ink-editorial, quiet-luxury, signal-dark, warm-editorial."
---

# Slide Design Systems

A condensed library of presentation-design canon plus six concrete,
production-ready design systems the deck-builder can drop into a
`deck-spec.json` without further customization.

## Table of Contents

1. [When to Use This Skill](#when-to-use-this-skill)
2. [Design Canon Digest](#design-canon-digest)
3. [The Design Systems](#the-design-systems)
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

## The Design Systems

The original six are render-host-safe (B2: all design fonts updated to
installed families — Inter, Source Serif 4, IBM Plex Sans/Mono, Fraunces,
Space Grotesk, Archivo — so the verified PNG shows the *designed*
typography, never a substitute). The four **premium** systems
(`ink-editorial`, `quiet-luxury`, `signal-dark`, `warm-editorial`) ship
tint ladders + categorical `chart_palette` + font-weight tokens and were
authored to fix the stock-palette / brand-pastiche / desaturated-coral
problems of their predecessors.

| System | Best For | Vibe | Default Background Mix |
|--------|----------|------|------------------------|
| `executive-navy` | C-level decision asks, board updates | Authoritative, conservative | 30% dark navy / 60% off-white / 10% accent |
| `technical-slate` | Engineering reviews, architecture decks | Modern, technical, dark-first | 60% charcoal / 30% slate / 10% electric indigo |
| `customer-coral` | Customer success stories, pitches | Warm, human, narrative | 50% off-white / 30% coral-tinted / 20% deep navy |
| `investor-gold` | Funding asks, investor updates | Premium, restrained, confident | 40% dark / 50% cream / 10% gold |
| `editorial-mono` | Vision decks, manifestos, opinion | Bold typographic, magazine | 70% black or pure white / 30% inverse |
| `boardroom-conservative` | Regulated industries, M&A | Traditional consulting | 20% deep blue / 70% white / 10% red |
| `ink-editorial` ⭐ | Vision / thought-leadership keynotes | Print-editorial, paper + ink + one vermilion signal | 70% paper / 25% ink / 5% signal |
| `quiet-luxury` ⭐ | Premium investor / board narratives | Understated luxury, champagne as line never fill | 45% warm-black / 50% bone / 5% champagne line |
| `signal-dark` ⭐ | Product / platform launches, eng reviews | Cool dark product UI, iris + mint focal, tint ladder | 65% charcoal / 30% paper / 5% iris |
| `warm-editorial` ⭐ | Customer / sales / culture narratives | Warm cream + vivid coral kept bright | 55% cream / 35% espresso / 10% coral |

⭐ = premium system (tint ladders + `chart_palette` + weight tokens).

## System Selection by Audience

| Audience | Decision Ask | Customer Story | Technical Review | Vision |
|----------|--------------|----------------|------------------|--------|
| Executive | `executive-navy` | `customer-coral` | `executive-navy` | `editorial-mono` |
| Technical | `technical-slate` | `customer-coral` | `technical-slate` | `technical-slate` |
| Customer | `customer-coral` | `customer-coral` | `technical-slate` | `editorial-mono` |
| Investor | `investor-gold` | `customer-coral` | `investor-gold` | `editorial-mono` |
| Board / Regulated | `boardroom-conservative` | `executive-navy` | `boardroom-conservative` | `executive-navy` |

## Selection by Use Case (`presentation_mode`)

> *Source: research §E lines 94–103, ported in session
> `2026-05-04-5707a9ef`. Adds an orthogonal selection axis using the
> optional `intake.presentation_mode` field (see
> `intake.schema.json`).*
>
> **Precedence (per Q4 decision)**: when audience-driven selection and
> presentation-mode-driven selection disagree, **audience wins**.
> `presentation_mode` is a *complementary* signal, not an override.
> Document the choice and the conflict, if any, in the proposal's
> `## Design Direction` section.

| `presentation_mode` | Suggested system | Why |
|---|---|---|
| `live` | `editorial-mono` *(or `technical-slate` if dark-first preferred)* | Bold typography + sparse copy + dramatic section breaks; designed to be presented, not read |
| `read-ahead` | `boardroom-conservative` | Decks that must stand alone; needs density tolerance + footnoted sources; conservative palette signals seriousness |
| `board` | `boardroom-conservative` | Regulated / fiduciary context; familiarity beats novelty |
| `sales` | `customer-coral` | Customer-pain → urgency → proof → solution → impact → CTA arc; warm palette supports narrative emotion |
| `investor` | `investor-gold` | Premium restraint; traction metrics + clear ask; gold-on-dark signals confidence |
| `workshop` | `customer-coral` *(or `editorial-mono` for keynote workshops)* | Interactive / read-during-discussion; warm + scannable wins over polished-but-distant |

When `intake.presentation_mode` is absent, ignore this table and use
audience selection alone. When both axes resolve to the same system,
note both in the rationale. When they conflict, pick the
audience-driven choice and explain the override reason in
`## Design Direction`.

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
  "fonts": {"title_family": "Inter", "body_family": "Inter", "mono_family": "IBM Plex Mono"},
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

### Font portability tokens (concern C1)

python-pptx **cannot embed fonts**, and LibreOffice / Chromium
substitute missing fonts "often badly" — the deck *file* is fine but
every *render* (and the deck opened on a host lacking the font) looks
wrong. To eliminate this class of bug, every system's `fonts` block
SHOULD declare a **render-safe fallback** that is present on render
hosts (mirroring `render-visual/assets/font_locator.py`):

```json
"fonts": {
  "title_family": "Calibri Light",
  "body_family": "Calibri",
  "mono_family": "Consolas",
  "title_fallback": "DejaVu Sans",
  "body_fallback": "Carlito",
  "mono_fallback": "DejaVu Sans Mono",
  "render_safe": ["DejaVu Sans", "Carlito", "Caladea", "Liberation Sans",
                  "DejaVu Sans Mono", "Liberation Mono", "Liberation Serif",
                  "Noto Sans"]
}
```

`render_safe` is the allowlist of fonts known present on LibreOffice /
Chromium render hosts. `pptx-structural-asserts/scripts/check_pptx.py`
reads it (via `deck-spec.json.design_system_tokens.fonts`) and emits a
**`font_not_render_present`** warning for any run whose font is neither
in `render_safe` nor a declared `*_fallback`. Set the deck's actual
python-pptx `font.name` to the design font; the fallback documents what
the renderer will substitute so the warning stays quiet for known-good
substitutions. Marp inherits the same fallback chain via
`marp-engine/references/marp-theming.md`.

### Whitespace / safe-area tokens (concern C4)

Add explicit breathing-room tokens to the `grid` block so the structural
asserts can check spacing, not just overflow:

```json
"grid": {
  "slide_width_inches": 13.333, "slide_height_inches": 7.5,
  "margin_inches": 0.75, "stripe_left_inches": 0.45, "snap_inches": 0.05,
  "safe_area_inches": 0.5, "min_gutter_inches": 0.25
}
```

- `safe_area_inches` — minimum clear margin from every slide edge; no
  content shape should start inside it. `check_pptx.py` emits a
  **`safe_area_violation`** warning ("breathing room") for shapes that
  intrude. Defaults to `margin_inches` when absent.
- `min_gutter_inches` — minimum gap between adjacent content blocks
  (columns, cards). Defaults to `0.25` when absent.

### Premium token extensions (C3 — tints, chart palette, weights)

The four premium systems (and any new system) extend the base schema so
builders can *layer tone* and charts get a categorical theme. These keys
are read directly by `pptx-engine/scripts/generate_deck.py` (`Tokens`)
and `render-visual/scripts/render_chart.py`:

```json
{
  "palette": {
    "surface_elevated": "#F6F8FA",
    "surface_on_dark": "#1E2128",
    "hairline": "#D5DAE0",
    "hairline_on_dark": "#2C313A",
    "scrim": "#14161B",
    "tints": {
      "primary": {"50": "#EEF0FF", "100": "#DADFFF", "300": "#9AA6FF",
                  "500": "#5468FF", "700": "#3A49C2", "900": "#222C78"}
    }
  },
  "chart_palette": {
    "focal": "#46E5B0", "muted": "#9AA1AC", "grid": "#2C313A",
    "ramp": ["#5468FF", "#46E5B0", "#9AA1AC", "#8A6BFF", "#3FB6F0", "#F0A93F"]
  },
  "typography": {
    "font_title": "Space Grotesk", "font_body": "Inter",
    "title_weight": 700, "body_weight": 400, "eyebrow_weight": 600,
    "size_hero": 60, "size_section": 48, "size_title": 40
  }
}
```

- **`palette.tints.<role>.<step>`** — HSL-lightness tint/shade ladder per
  accent role (Refactoring-UI). Builders pull `t.tint("primary", "500")`
  for cards / insets / zebra so tone layers instead of one flat fill.
  When absent, `Tokens` derives card/hairline/scrim tones from the base
  colours so legacy systems still work.
- **`chart_palette`** — categorical theme: `focal` (the single "look
  here" colour, deliberately separate from brand `secondary`), `muted`
  (non-focal marks), `grid`, and a `ramp` cycled for ≥4-category charts.
- **`typography.*_weight`** — 300/400/600/700/800 weight tokens; helpers
  map weight ≥ 600 to bold and feed `_set_tracking` for display type.
- **`surface_elevated` / `surface_on_dark` / `hairline*` / `scrim`** —
  craft-surface colours consumed by `_add_card`, `_add_hairline`, and
  `_add_scrim`.

The render-host font set is now the installed allowlist: **Inter,
Source Serif 4, IBM Plex Sans, IBM Plex Mono, Fraunces, Space Grotesk,
Archivo** (plus the legacy LibreOffice substitutes). Set every system's
design fonts to one of these so design-font == render-font (B2).

## References

- [Design Canon](references/design-canon.md) — Expanded notes on the canon listed above
- [Executive Navy](references/systems/executive-navy.md)
- [Technical Slate](references/systems/technical-slate.md)
- [Customer Coral](references/systems/customer-coral.md)
- [Investor Gold](references/systems/investor-gold.md)
- [Editorial Mono](references/systems/editorial-mono.md)
- [Boardroom Conservative](references/systems/boardroom-conservative.md)
- [Ink Editorial](references/systems/ink-editorial.md) ⭐ premium
- [Quiet Luxury](references/systems/quiet-luxury.md) ⭐ premium
- [Signal Dark](references/systems/signal-dark.md) ⭐ premium
- [Warm Editorial](references/systems/warm-editorial.md) ⭐ premium

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

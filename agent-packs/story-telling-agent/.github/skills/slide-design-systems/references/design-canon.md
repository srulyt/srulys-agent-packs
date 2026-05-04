# Design Canon — Expanded Notes

> Source attributions for the design systems in this skill. Each entry
> is a short digest of the original work plus the specific element
> imported into our systems.

## Table of Contents

1. [Pyramid Principle (Minto)](#1-pyramid-principle-barbara-minto)
2. [Presentation Zen (Reynolds)](#2-presentation-zen-garr-reynolds)
3. [Slide:ology / Resonate (Duarte)](#3-slideology--resonate-nancy-duarte)
4. [BCG / Bain Conventions](#4-bcg--bain-consulting-conventions)
5. [Beautiful.ai / Gamma](#5-beautifulai--gamma)
6. [marp / slidev / reveal.js](#6-marp--slidev--revealjs)
7. [Material Design / Apple HIG](#7-material-design--apple-hig)

## 1. Pyramid Principle (Barbara Minto)

Originally from Minto's *The Pyramid Principle* (1987). Adopted as
McKinsey's house style. Three rules:

1. Start with the answer (top of pyramid). Details support, not lead.
2. Group ideas at each level: Mutually Exclusive, Collectively Exhaustive (MECE).
3. Sequence ideas by deductive or inductive logic — never by chronology of discovery.

**Imported as:** action-title convention (titles ARE the answer);
MECE bullet groups (≤4 items, parallel structure); top-down argument
ordering (executive deck templates).

## 2. Presentation Zen (Garr Reynolds)

From Reynolds (2008). Influenced by Japanese aesthetic principles
(*ma* — purposeful empty space; *kanso* — simplicity; *shibumi* —
elegant restraint).

**Imported as:** signal-to-noise enforcement (no decorative shapes);
picture superiority (visual-hero slide type); one-idea-per-slide gate.

## 3. Slide:ology / Resonate (Nancy Duarte)

From Duarte (2008, 2010). Two key constructs:

- **Sparkline** — A deck has an emotional contour. Map every slide to a
  point on a "what is" → "what could be" oscillation.
- **Persistence of vision** — Visual identity must be detectable
  across ≥80% of slides; one-off styles break recognition.

**Imported as:** emotional-arc annotation (every slide has an emotion
marker); design-system tokens applied to ≥80% of slides.

## 4. BCG / Bain Consulting Conventions

Style codified informally across 1990s–2010s consulting decks:

- Action titles (Minto-derived) PLUS 2-line subtitles giving the
  "so what".
- Footnoted source attribution at 10pt, bottom-left.
- Section identity via consistent left-margin colored strip.
- Strong preference for white background + single accent color.

**Imported as:** `boardroom-conservative` system; the optional left
stripe on light-background content slides.

## 5. Beautiful.ai / Gamma

Modern auto-layout SaaS conventions:

- Slot-based layouts that auto-balance (no manual nudging).
- Big Statement slides get a section-rotated accent color.
- Padding-as-hard-rule (no negotiation per slide).

**Imported as:** strict snap-to-grid (0.05" snap); rotated accent
colors for `customer-coral` and `technical-slate` Big Statements.

## 6. marp / slidev / reveal.js

Open-source markdown-to-slides themes. Common conventions:

- Dark-first themes default (slidev `seriph`, marp `gaia` invert).
- Monospace code blocks at 18pt, syntax-highlighted accent.
- Asymmetric content alignment (text-left dominant).
- Single bold accent color, no gradients.

**Imported as:** `technical-slate` and `editorial-mono` systems;
monospace defaults for code-bearing slides.

## 7. Material Design / Apple HIG Type Scales

Both design systems use a major-third type scale (ratio 1.25):

```
11 → 14 → 18 → 22 → 28 → 35 → 44 → 54 → 67
```

The scale provides typographic harmony — every size is a recognizable
step. Slide type-scales in this skill round to nearby integers and
prefer 4-step jumps for visual hierarchy.

**Imported as:** the `type_scale` block in every system's tokens.

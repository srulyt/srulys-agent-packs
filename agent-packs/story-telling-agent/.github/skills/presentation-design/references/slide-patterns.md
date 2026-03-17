# Slide Patterns — Layout Reference

Concrete slide layout patterns with dimensions, positioning, background colors, accent elements, typography specifications, and chart selection guidance for professional PowerPoint decks.

**Design principle**: All layouts use blank slide layouts (`prs.slide_layouts[6]`) with manually created elements for full visual control. Every slide has at least one accent element (bar, stripe, underline, or shape).

## Standard Slide Dimensions

All dimensions assume **16:9 widescreen** format: 13.333" × 7.5" (33.867cm × 19.05cm).

### Content Safe Area
- **Left margin**: 0.75"–1.1" from left edge (1.1" when left accent stripe is present)
- **Right margin**: 0.75" from right edge
- **Top margin**: 0.5" from top edge (below accent bar)
- **Bottom margin**: 0.5" from bottom edge

Usable content width: 11.5" (with stripe) to 11.833" (without)
Usable content height: 6.5"

## Layout Patterns

### Pattern 1: Title Slide (Dark Background)
```
┌──────────────────────────────────────────────────┐
│ ▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔ [Accent blue bar, full width, 0.06" tall] │
│  BG: #0F1B2D (Deep Navy)                         │
│                                                  │
│     PRESENTATION TITLE                           │
│     54pt Calibri Light, #FFFFFF                  │
│     Position: left=1.2" top=2.2" w=10.9"        │
│                                                  │
│     Subtitle — Audience — Date                   │
│     24pt Calibri, #06B6D4 (Teal)                 │
│     Position: left=1.2" top=4.2" w=10.9"        │
│                                                  │
│     ▁▁▁▁▁▁▁▁ [3" blue accent line at 5.4"]      │
│                                                  │
└──────────────────────────────────────────────────┘
```
- Background: `#0F1B2D` (Deep Navy)
- Top accent bar: `#3B82F6` (Vivid Blue), full width, 0.06" tall
- Title: 54pt Calibri Light, White, bold=False
- Subtitle: 24pt Calibri, Teal `#06B6D4`
- Bottom accent line: 3" wide, 0.035" tall, `#3B82F6`, at (1.2", 5.4")

### Pattern 2: Key Message (Headline + Bullets, Light Background)
```
┌──────────────────────────────────────────────────┐
│ ▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔ [Blue accent bar]│
│█ BG: #F4F5F7 (Off-White)                         │
│█                                                  │
│█ ACTION-ORIENTED HEADLINE                        │
│█ 40pt Bold Calibri, #0F1B2D (Navy)              │
│█ ▁▁▁▁▁▁ [3" blue underline]                     │
│█                                                  │
│█ ▸  Supporting point one — specific + concrete   │
│█                                                  │
│█ ▸  Supporting point two — evidence-backed       │
│█                                                  │
│█ ▸  Supporting point three — outcome-focused     │
│█    22pt Calibri, #1A1A2E                         │
└──────────────────────────────────────────────────┘
 █ = Navy left stripe (0.45" wide)
```
- Background: `#F4F5F7` (Off-White)
- Left accent stripe: `#0F1B2D` (Navy), 0.45" wide, full height
- Top accent bar: `#3B82F6`, full width, 0.06" tall
- Title: left=1.1", top=0.5", 40pt Bold Calibri, Navy
- Title underline: left=1.1", top=1.55", 3" wide, `#3B82F6`
- Bullets: left=1.1", top=1.9", 22pt Calibri, `#1A1A2E`, with ▸ marker
- Bullet spacing: space_after=16pt

### Pattern 3: Two-Column Comparison (Light Background)
```
┌──────────────────────────────────────────────────┐
│ ▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔ [Blue accent bar]│
│█ COMPARISON HEADLINE — 40pt Bold Navy            │
│█ ▁▁▁▁▁▁ [3" underline]                          │
│█                                                  │
│█  BEFORE (24pt Bold Navy)   AFTER (24pt Bold Blue)│
│█                                                  │
│█  ▸  Point 1               ▸  Point 1            │
│█  ▸  Point 2               ▸  Point 2            │
│█  ▸  Point 3               ▸  Point 3            │
│█     20pt #1A1A2E             20pt #1A1A2E       │
└──────────────────────────────────────────────────┘
```
- Background: `#F4F5F7`, left stripe: `#0F1B2D`
- Two columns: left at 1.1", right at 7.0", each 5.3" wide
- Left header: 24pt Bold Navy; Right header: 24pt Bold Blue `#3B82F6`
- Body: 20pt Calibri, `#1A1A2E`

### Pattern 4: Key Metric / Big Number (Dark Background)
```
┌──────────────────────────────────────────────────┐
│ ▔▔▔▔▔▔▔ [Accent blue bar]                       │
│  BG: #0F1B2D                                     │
│  TITLE — 40pt Bold Calibri, White                │
│                                                  │
│     40%           $2.3M          3x              │
│     72pt Bold     72pt Bold      72pt Bold       │
│     Calibri Light, #F59E0B (Gold)                │
│     Centered in equal columns                    │
│                                                  │
│     Churn         Pipeline       Onboarding      │
│     Reduction     Growth         Speed           │
│     20pt Calibri, #E2E4E8, centered              │
│                                                  │
└──────────────────────────────────────────────────┘
```
- Background: `#0F1B2D`
- Metric values: top=2.8", 72pt Bold Calibri Light, Gold `#F59E0B`, centered
- Labels: top=4.6", 20pt Calibri, `#E2E4E8`, centered
- Max 3 metrics per slide, evenly spaced across 10.9" width starting at left=1.2"

### Pattern 5: Quote / Testimonial (Dark Background)
```
┌──────────────────────────────────────────────────┐
│  BG: #0F1B2D                                     │
│                                                  │
│     "  ← 120pt Calibri Light, #3B82F6            │
│                                                  │
│     "This changed how our entire team             │
│      thinks about customer onboarding."          │
│      32pt Italic Calibri Light, White            │
│      Position: left=1.5" top=2.5" w=10.3"       │
│                                                  │
│      — Jane Smith, VP Product, Acme Corp         │
│      18pt Calibri, #06B6D4 (Teal)               │
│                                                  │
└──────────────────────────────────────────────────┘
```
- Background: `#0F1B2D`
- Decorative quote mark: 120pt Calibri Light, `#3B82F6`, at (1.0", 1.2")
- Quote text: 32pt Italic Calibri Light, White, word-wrapped
- Attribution: 18pt Calibri, Teal `#06B6D4`, space_before=24pt

### Pattern 6: Section Header (Dark Background, Centered)
```
┌──────────────────────────────────────────────────┐
│  BG: #0F1B2D                                     │
│                                                  │
│         ▁▁▁▁▁▁▁ [2.3" teal accent line at 2.5"] │
│                                                  │
│          SECTION TITLE                           │
│          48pt Calibri Light, White, centered     │
│          Position: left=1.5" top=2.8" w=10.3"   │
│                                                  │
│          Context line or framing question         │
│          24pt Calibri, Teal, centered            │
│                                                  │
└──────────────────────────────────────────────────┘
```
- Background: `#0F1B2D`
- Centered accent line: 2.3" wide, `#06B6D4`, at (5.5", 2.5")
- Title: 48pt Calibri Light, White, centered
- Subtitle: 24pt Calibri, Teal, centered

### Pattern 7: Closing / CTA (Dark Background)
```
┌──────────────────────────────────────────────────┐
│ ▔▔▔▔▔▔▔ [Teal accent bar]                       │
│  BG: #0F1B2D                                     │
│  WHAT WE'RE ASKING FOR — 40pt Bold White         │
│  ▁▁▁▁▁▁ [3" teal underline]                     │
│                                                  │
│  1  Approve the approach      → Decision by Fri  │
│  40pt Teal  22pt Bold White     18pt Gray         │
│                                                  │
│  2  Kick off Phase 1          → Eng lead, Mar 23 │
│                                                  │
│  3  Schedule follow-up        → All, Apr 15      │
│                                                  │
│  Contact: name@company.com — 14pt #A0A4B0        │
└──────────────────────────────────────────────────┘
```
- Background: `#0F1B2D`
- Top accent bar: `#06B6D4` (Teal)
- Title underline: Teal, 3" wide
- Step numbers: 40pt Bold Calibri Light, Teal
- Action text: 22pt Bold Calibri, White
- Detail text: 18pt Calibri, `#6B7080`
- Steps positioned at y=2.2" + i*1.4"

### Pattern 8: Data Visualization (Light Background)
```
┌──────────────────────────────────────────────────┐
│ ▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔ [Blue accent bar]│
│█ THE CONCLUSION THIS DATA SHOWS                  │
│█ 40pt Bold Navy                                  │
│█ ▁▁▁▁▁▁ [3" underline]                          │
│█                                                  │
│█ ┌────────────────────────────────────────────┐  │
│█ │              CHART / GRAPH                 │  │
│█ │       (70-80% of content area)             │  │
│█ └────────────────────────────────────────────┘  │
│█ Source: Data source, 11pt #A0A4B0               │
└──────────────────────────────────────────────────┘
```
- Background: `#F4F5F7`, left stripe: `#0F1B2D`
- Title states the conclusion, not the topic
- Chart occupies 70–80% of content area

### Pattern 9: Big Statement (Dark Background, Maximum Impact)
```
┌──────────────────────────────────────────────────┐
│  BG: #0F1B2D                                     │
│                                                  │
│                                                  │
│       One Bold                                   │
│       Statement                                  │
│       54-60pt Calibri Light, White               │
│       Position: left=1.5" top=2.2" w=10.3"      │
│                                                  │
│                                                  │
│                                                  │
└──────────────────────────────────────────────────┘
```
- Background: `#0F1B2D` (or accent color like `#3B82F6` for special emphasis)
- NO accent bars, NO stripes, NO underlines — maximum restraint
- Headline: 54-60pt Calibri Light, White, left-aligned or centered
- NO body text, NO bullets — the headline IS the slide
- Use at narrative turning points, key insights, provocative claims
- Optional: 18pt teal subtitle for brief context (1 line max)

### Pattern 10: Split Layout (Light Background, Two Halves)
```
┌──────────────────────────────────────────────────┐
│ ▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔ [Blue accent bar]│
│█                                                  │
│█  HEADLINE                   ▸  Point one         │
│█  40pt Bold Navy             ▸  Point two         │
│█                             ▸  Point three       │
│█  Context line               ▸  Point four        │
│█  22pt #6B7080                  20pt #1A1A2E      │
│█                                                  │
│█                                                  │
└──────────────────────────────────────────────────┘
```
- Background: `#F4F5F7`, left stripe: `#0F1B2D`
- Left column (1.1"–6.0"): Headline + optional context line
- Right column (6.5"–12.5"): Supporting content (bullets, image, or data)
- Use for: context + evidence, claim + proof, headline + detail

### Pattern 11: Question Slide (Dark Background, Centered)
```
┌──────────────────────────────────────────────────┐
│  BG: #0F1B2D                                     │
│                                                  │
│                                                  │
│     What if we could 3x conversion               │
│     without adding headcount?                    │
│     48-54pt Calibri Light, White, centered       │
│                                                  │
│                                                  │
│                                                  │
└──────────────────────────────────────────────────┘
```
- Background: `#0F1B2D`
- NO accent elements — clean and focused
- Question: 48-54pt Calibri Light, White, centered
- Use before major evidence sections to create anticipation
- Optional: thin teal accent line ABOVE the question (not below)

## Section Colors

Assign one accent color per narrative section to reinforce story structure:

| Section Role | Color | Hex |
|-------------|-------|-----|
| Opening / Framing | Teal | `#06B6D4` |
| Problem / Tension | Coral Red | `#F87171` |
| Solution / Approach | Vivid Blue | `#3B82F6` |
| Results / Data | Warm Gold | `#F59E0B` |
| Closing / Action | Emerald | `#10B981` |

## Color Palette — Default (Executive Navy)

| Role | Color | Hex | Usage |
|------|-------|-----|-------|
| Dark background | Deep Navy | `#0F1B2D` | Title, section, quote, closing slides |
| Light background | Off-White | `#F4F5F7` | Content, data, comparison slides |
| Primary accent | Vivid Blue | `#3B82F6` | Accent bars, underlines, emphasis |
| Secondary accent | Teal | `#06B6D4` | Subtitles, attributions, CTA elements |
| Highlight | Warm Gold | `#F59E0B` | Key metrics, big numbers, callouts |
| Text on dark | White | `#FFFFFF` | All text on dark backgrounds |
| Text on light | Near Black | `#1A1A2E` | Body text on light backgrounds |
| Text secondary | Mid Gray | `#6B7080` | Captions on light backgrounds |
| Borders/dividers | Light Gray | `#E2E4E8` | Metric labels, table borders |

## Typography Pairings

### Pairing 1: Calibri (Default — Safest)
- **Display titles**: Calibri Light, 44–54pt, bold=False (light weight at large sizes = elegant)
- **Content titles**: Calibri Bold, 36–44pt
- **Body**: Calibri Regular, 20–24pt
- **Why**: Universal availability, clean, professional, renders consistently across systems

### Pairing 2: Segoe UI + Segoe UI Light
- **Titles**: Segoe UI Light, 44–54pt
- **Body**: Segoe UI Regular, 20–24pt
- **Why**: Modern feel, excellent on Windows

### Pairing 3: Arial + Arial Narrow
- **Titles**: Arial Bold, 36–44pt
- **Body**: Arial Narrow Regular, 18–22pt
- **Why**: Maximum cross-platform compatibility

**Rule**: Never use more than 2 font families in a single deck. One for titles, one for body. If in doubt, use Calibri Light for titles and Calibri for body.

## Chart Selection Guide

| Data Type | Best Chart | Why |
|-----------|-----------|-----|
| Trend over time | Line chart | Shows trajectory clearly |
| Category comparison | Horizontal bar chart | Easy to compare values |
| Part of whole | Pie chart (max 5 slices) | Only use for percentages totaling 100% |
| Before/after comparison | Paired bar chart | Side-by-side comparison |
| Distribution | Histogram or box plot | Shows spread and outliers |
| Relationship between variables | Scatter plot | Shows correlation |
| Process or flow | Diagram (shapes + arrows) | Shows sequence and logic |
| Multiple metrics | Table with heat-map coloring | Dense data, sortable |

### Chart Design Rules
- Title states the conclusion: "Revenue grew 40%" not "Revenue Over Time"
- Axis labels must be readable (12pt minimum)
- Remove chart junk: gridlines, 3D effects, excessive legends
- Use accent color for the data series you want to emphasize
- Maximum 5 data series per chart — beyond that, simplify
- Always include source attribution for external data

# Marp Theming — Design-System Token Parity

> **Purpose**: Make a `marp` / `both` deck inherit the **same** palette and
> type scale as the `pptx` path so all three `output_mode` values share one
> design language (concern C3). The six design systems in
> [`slide-design-systems`](../../slide-design-systems/SKILL.md) are the
> single source of truth; this reference maps their JSON tokens →
> Marp/Marpit CSS custom properties. **Never invent a parallel Marp
> palette.**

## The mapping

Every design system file under
`slide-design-systems/references/systems/<name>.md` exposes a `palette`,
`type_scale`, `fonts`, `grid`, and `accent_rules` token block. Map them
one-to-one into CSS custom properties on the Marp `section` root:

| Design-system token | Marp CSS custom property |
|---------------------|--------------------------|
| `palette.background_dark` | `--bg-dark` |
| `palette.background_light` | `--bg-light` |
| `palette.background_accent` | `--bg-accent` |
| `palette.primary_accent` | `--accent` |
| `palette.secondary_accent` | `--accent-2` |
| `palette.highlight` | `--highlight` |
| `palette.text_on_dark` | `--text-on-dark` |
| `palette.text_on_light` | `--text-on-light` |
| `palette.text_secondary` | `--text-muted` |
| `palette.divider` | `--divider` |
| `type_scale.hero` | `--fs-hero` |
| `type_scale.section` | `--fs-section` |
| `type_scale.title` | `--fs-title` |
| `type_scale.subtitle` | `--fs-subtitle` |
| `type_scale.body` | `--fs-body` |
| `type_scale.caption` | `--fs-caption` |
| `fonts.title_family` (+ render-safe fallback) | `--font-title` |
| `fonts.body_family` (+ render-safe fallback) | `--font-body` |
| `fonts.mono_family` | `--font-mono` |
| `grid.margin_inches` | `--safe-margin` (convert in → rem/px) |
| `grid.safe_area_inches` | `--safe-area` |
| `grid.min_gutter_inches` | `--min-gutter` |

> **Font portability (concern C1).** Use the **same render-safe font
> fallback** Marp's Chromium and LibreOffice both have. Declare the design
> font first, then a libre fallback (`"DejaVu Sans"`, `Carlito`,
> `"Liberation Sans"`), e.g.
> `--font-body: "Calibri", Carlito, "DejaVu Sans", sans-serif;`. This
> mirrors `render-visual/assets/font_locator.py` and eliminates the
> font-substitution class of ugly renders.

## Worked example — `executive-navy`

Generate `theme.css` (passed to `render_marp.py --theme`) directly from the
`executive-navy` token block:

```css
/* @theme story-telling-executive-navy
 * GENERATED from slide-design-systems/references/systems/executive-navy.md
 * Do not hand-edit palette/type values — regenerate from the token block. */
@import 'default';

:root {
  --bg-dark: #0F1B2D;
  --bg-light: #F4F5F7;
  --bg-accent: #1D4ED8;
  --accent: #3B82F6;
  --accent-2: #06B6D4;
  --highlight: #F59E0B;
  --text-on-dark: #FFFFFF;
  --text-on-light: #1A1A2E;
  --text-muted: #6B7080;
  --divider: #E2E4E8;

  --fs-hero: 54px;
  --fs-section: 48px;
  --fs-title: 40px;
  --fs-subtitle: 24px;
  --fs-body: 22px;
  --fs-caption: 14px;

  --font-title: "Calibri Light", Carlito, "DejaVu Sans", sans-serif;
  --font-body: "Calibri", Carlito, "DejaVu Sans", sans-serif;
  --font-mono: "Consolas", "DejaVu Sans Mono", monospace;

  --safe-area: 0.5in;   /* breathing room (concern C4) */
  --min-gutter: 0.25in;
}

section {
  font-family: var(--font-body);
  font-size: var(--fs-body);
  color: var(--text-on-light);
  background: var(--bg-light);
  padding: var(--safe-area);
}
section h1 { font-family: var(--font-title); font-size: var(--fs-title);
             color: var(--text-on-light); }

/* styled classes mirror the pptx slide_type_defaults backgrounds */
section.title, section.section, section.hero {
  background: var(--bg-dark);
  color: var(--text-on-dark);
}
section.title h1, section.section h1, section.hero h1 {
  color: var(--text-on-dark);
}
section .highlight { color: var(--highlight); }
```

## Mapping rule for the other five systems

Apply the **exact same template**, swapping only the token values pulled
from the matching `references/systems/<name>.md` block:
`technical-slate`, `customer-coral`, `investor-gold`, `editorial-mono`,
`boardroom-conservative`. The CSS *structure* is identical across systems;
only the custom-property *values* change. This guarantees a `marp` deck and
a `pptx` deck built from the same system are visually consistent.

## `slide_type_defaults` → Marp classes

Map the pptx `slide_type_defaults[*].background` to Marp `_class` selectors
so dark/light rhythm is preserved across modes:

| pptx slide type | Marp `_class` | background token |
|-----------------|---------------|------------------|
| `title` | `title` | `background_dark` |
| `section_divider` | `section` | `background_dark` |
| `big_statement` | `hero` | `background_dark` |
| `headline_bullets` | `simple` | `background_light` |
| `metric_spotlight` | `metric` | `background_dark` |
| `quote` | `quote` | `background_dark` |

Slides not in this table default to `simple` (light background), matching
the pptx style-gating default.

# Design Canon (rendering subsystem)

This page is the cross-cutting canon reference cited by
`@deck-builder` and `@deck-critic`. It expands on the named-source
table in `slide-design-systems/SKILL.md` and adds the rules
introduced by the F11 / 2026-05-04-7d3f9a2b rebuild.

## Refactoring UI (Wathan & Schoger)

**Rule encoded**: One saturated accent per system; tints/shades by
HSL-Lightness step (10% per stop).

**The hard rule (F11)**: **Body text on a saturated accent background
is forbidden.** Saturated accents (sat > 0.45 in HSL) carry too much
chroma to remain legible behind 22pt body text — even at AA-clean
luminance contrast, the visual rivalry between fully-saturated bg
and any non-white fg makes scanning costly. The
`accent_rules.body_text_on_accent: "forbidden"` token enforces this
at preflight (G1) and at the saturation-aware `_bg_label`
classification (F7) — accent backgrounds are detected and the body
copy is required to either:

- live on a desaturated tint (drop saturation by ≥20% before serving
  as bg), OR
- be reduced to ≥36pt headline text (large-text tier), OR
- be moved to a tinted-panel inset on a non-accent slide.

Most failing palette tokens (F3) were over-saturated mid-luminance
colours used as backgrounds. The fix is always **demote to
`primary_accent`** (icon / line / chart-mark use) and pick a darker,
desaturated shade for `background_accent`.

## Beautiful.ai / Duarte rotation pattern (F7)

**Rule encoded**: Accent-coloured slides break dark-runs.

`@deck-critic`'s rhythm rubric (F7/F8) treats `bg_label == "accent"`
as a legitimate rhythm break inside an otherwise long dark run. The
saturation-aware `_bg_label` (sat > 0.45 → `accent`) ensures that
even low-luminance brand purples (e.g. `#635BFF` lum ≈ 0.17) are
correctly classified as accent rather than dark — preventing the
F7-class false-blocking we saw in the 2026-05-04 STM run.

Threshold table (F8):

| `max_same_bg_run` | Severity                         |
|-------------------|----------------------------------|
| `< 3`             | clean                            |
| `>= 3`            | warn                             |
| `>= 5` and no accent slide in deck | blocking (`dark_light_run`) |
| `>= 7`            | blocking unconditionally         |

## Garr Reynolds — Presentation Zen (F11)

**Rule encoded**: One message per slide; image superiority.

The structural-asserts `body_word_max` warning was lowered from **70 → 30**
words per slide. This pushes builders away from copy-heavy "decks
that read themselves" and toward image-supported headlines.

(Rule lives in `pptx-structural-asserts/scripts/check_pptx.py`,
function `main()`.)

## Edward Tufte — data-ink ratio (F11)

**Rule encoded** (in `render-visual/references/chart-recipes.md`):
matplotlib chart recipes set:

- `axes.spines.top: False`, `axes.spines.right: False`
- No gridlines unless explicitly requested
- One accent colour for the focal data point; secondary marks in
  `text_secondary`

This is the rcParams snippet every chart recipe inherits.

## IBM Carbon — minimum callout / rule thickness

**Rule encoded** (in `pptx-engine/references/styled-recipes.md`):
The minimum visible thickness for callout rules and divider lines is
**0.06"** (≈32 px @ 96 dpi). The previous `add_title_underline`
default of 0.035" rendered as a hairline that disappears on
projector. Updated to 0.06" everywhere except where explicitly
overridden.

## Material Design 3 type scale

**Rule encoded** (in `presentation-design/references/typography.md`):
14 / 16 / 22 / 28 / 36 / 45 / 57 pt scale; bullets at 22→20pt for
16:9 reading distance.

## Nancy Duarte — Resonate sparkline pattern

**Rule encoded** (in `presentation-design/references/style-gating.md`):
Alternate "what is" (data, dark) and "what could be" (vision,
light/accent) slides. Tag ≥1 in 4 slides as `style: styled`.

## Edward Boatman / hero imagery

**Rule encoded** (this rebuild, F11): `style: styled` on
`section_divider` defaults to `style_recipe: hero_full_bleed`.
**Title slides keep `simple` as default** — see decisions log OQ4
(2026-05-04-7d3f9a2b).

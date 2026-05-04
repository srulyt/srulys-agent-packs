# WCAG Contrast Thresholds — single source of truth

This document is the canonical reference for the contrast thresholds
used across the rendering subsystem. Both
`scripts/check_palettes.py` (preflight gate G1) and
`pptx-structural-asserts/scripts/check_pptx.py` (structural gate G4
contrast check) load these numbers — do not duplicate them in code.

## WCAG 2.2 thresholds

| Tier         | Ratio   | Applies to                                        |
|--------------|---------|---------------------------------------------------|
| **AA body**  | 4.5 : 1 | Normal-weight text below 18pt OR below 14pt-bold  |
| **AA large** | 3.0 : 1 | Text ≥18pt OR ≥14pt-bold                          |
| AAA body     | 7.0 : 1 | Aspirational; not enforced                        |

Source: https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html

## How the rendering subsystem applies them

### Preflight (G1) — `check_palettes.py`

Runs against the `(text_*, background_*)` Cartesian product:

| Pair                                | Threshold | Why                                           |
|-------------------------------------|-----------|-----------------------------------------------|
| `text_on_dark`   × `background_dark`   | 4.5 : 1 | Body text on dark slides                  |
| `text_on_dark`   × `background_accent` | 4.5 : 1 | Section dividers / cta_steps with body  |
| `text_on_light`  × `background_light`  | 4.5 : 1 | Body text on light slides                 |
| `text_secondary` × `background_dark`   | 4.5 : 1 | Captions / fine print on dark             |
| `text_secondary` × `background_light`  | 4.5 : 1 | Captions / fine print on light            |

When a system ships per-surface override tokens
(`text_secondary_on_dark`, `text_secondary_on_light`), the preflight
gate resolves the foreground for the matching row against the
override instead of the bare `text_secondary` key. Use the override
when the dark/light background pair is too close in luminance for
any single mid-gray to satisfy 4.5:1 against both — solving for
both bounds simultaneously requires the two backgrounds' mutual
contrast ratio to exceed 4.5 × 4.5 = 20.25:1, which not every
system clears. (Worked example: `technical-slate`'s `#1E1E2E` ↔
`#F5F6FA` gives 15.2:1 between backgrounds, leaving an empty
solution interval for a single token — see that system's F4 note.)

The default policy uses **4.5 : 1 for every pair** because the
strategist may bind any text-token to any shape — the script cannot
know in advance which slide-class will use the pair on a 22pt
sub-bullet vs a 60pt headline. To opt into the 3:1 large-text tier
for a specific pair, edit `LARGE_TEXT_ALLOWED` in the script and
add an inline comment in the system .md noting that the pair is
only ever used for ≥18pt content.

### Structural (G4) — `check_pptx.py`

Runs **per run**, after the deck is built, with full access to the
actual `font.size` and `font.bold` of every shape. The threshold is
computed per run via `_is_large_text(size_pt, bold)`:

```python
def _is_large_text(size_pt: float, bold: bool) -> bool:
    return size_pt >= 18 or (bold and size_pt >= 14)
```

→ Returns `3.0` if true else `4.5`.

This means the structural gate can correctly accept a 60pt headline
on `background_accent` even when the preflight gate (which can't
see the font size) would have flagged it. **But** preflight
flagging is a strict superset of structural flagging — a system
that fails preflight will also fail structural for some slide-class.

### Recommended headroom

Hex pairs that compute to exactly 4.50 : 1 are vulnerable to
floating-point drift across luminance-formula implementations. Aim
for **≥4.7 : 1** when authoring new tokens.

## Recovery — how to fix a failing pair

1. **Darken or lighten the background** by adjusting HSL Lightness in
   ±10% steps until the ratio crosses the threshold (Refactoring-UI
   approach).
2. **Demote a saturated mid-luminance hue** to `primary_accent`
   (icon / line use only) and pick a desaturated darker shade for
   `background_accent`. Example: `#635BFF` (4.10:1) → demote to
   `primary_accent`; promote `#4F46E5` (5.94:1) to
   `background_accent`.
3. **Never** change the text token to "fix" the background — light
   slides need dark text and vice versa; deltas at the text end
   create a different bug.

## Forbidden (Refactoring-UI canon, F11)

Per the Refactoring UI rule encoded in `references/canon.md`:
**body text on a saturated accent background is forbidden.** If a
slide-class needs body text on an accent surface, it MUST use a
desaturated `background_accent` (sat ≲ 0.45) AND satisfy 4.5:1.
This is enforced by the preflight gate; no escape hatch.

# Composite Recipes (PIL / Pillow)

Two PIL composite recipes consumed by `render_composite.py`. Both
produce **PNG only** — per OQ3 (decisions.md 2026-05-04T14:50Z), we
do NOT rasterise back from PNG to SVG, and PIL has no native SVG
path. PIL composites are inherently raster.

## Recipes

### `gradient_pattern`

Hero-style background: top-left → bottom-right linear gradient
between two palette tokens, with optional 40% darken overlay (matches
the architecture §4.1 `hero_full_bleed` overlay) and optional
Gaussian blur for a soft-focus effect.

Spec:

```json
{
  "start": "background_dark",
  "end":   "background_accent",
  "darken_overlay": true,
  "blur_px": 0
}
```

Default behaviour: dark→accent gradient with 40% overlay. The
`section_divider` styled `hero_full_bleed` recipe in
`pptx-engine/references/styled-recipes.md` consumes this PNG as a
full-bleed picture (0,0,12192000,6858000 EMU).

The two endpoint tokens may be any of:
`background_dark`, `background_light`, `background_accent`,
`primary_accent`, `secondary_accent`, `highlight`. Unknown tokens
fall back to `background_dark`.

### `oversized_glyph_bg`

Quote-style background: an oversized open-quote glyph (`U+201C` by
default; configurable) at low opacity, centred-left, on
`background_dark`. Used by the `quote_pullout` styled recipe.

Spec:

```json
{
  "glyph": "\u201C",
  "opacity": 0.10,
  "background_rgb": null
}
```

Defaults: glyph U+201C ("), 10% opacity, on `pal["bg_dark"]`. The
glyph size is `min(width, height) * 0.85`.

If `background_rgb` is provided as a `[r, g, b]` triple, it
overrides the palette default (rare; used when the strategist wants
the quote on `surface_elevated` instead of `bg_dark`).

## Determinism notes

PIL is fully deterministic. Same `(spec, tokens, size)` → identical
bytes across runs. The slow path is the per-pixel gradient loop in
`gradient_pattern` — at 1920×1080 it takes ~1.5s on a typical CI
runner, which is acceptable for a once-per-deck render.

If you need faster gradients, replace the per-pixel loop with
`numpy`-vectorised RGB arrays — the recipe currently uses pure-PIL
to avoid making numpy a hard dep of this script.

## Where the canonical font lives

`oversized_glyph_bg` resolves the glyph font via the sibling
`assets/font_locator.find_dejavu_sans()` helper (see C3 in the
architecture critic concerns). If neither the canonical bundle nor
matplotlib's bundled DejaVuSans is available, falls back to PIL's
bitmap default — the glyph will look chunkier but the script does
not crash.

# DejaVuSans.ttf — canonical bundled location

The DejaVu font family is licensed under the **DejaVu Fonts License**
(based on the Bitstream Vera Fonts license). It is permissively
licensed for commercial use, redistribution, modification, and
embedding. The full license is reproduced in
[`DejaVuSans.LICENSE.md`](DejaVuSans.LICENSE.md).

## Why this is the canonical location

Architecture critic concern **C3** required a single canonical
location for DejaVuSans.ttf, with `pptx-structural-asserts/scripts/
check_pptx.py` resolving the font path via a sibling-skill lookup
helper rather than maintaining a duplicate physical copy.

The single resolver lives at `font_locator.py` in this directory.
Both `check_pptx.py` and the three `render_*.py` scripts call
`font_locator.find_dejavu_sans()` to get a path.

## Resolution order

`font_locator.find_dejavu_sans()` returns the first hit from:

1. `render-visual/assets/DejaVuSans.ttf` (this directory — the
   canonical location when the binary is committed alongside the
   pack).
2. matplotlib's bundled `mpl-data/fonts/ttf/DejaVuSans.ttf` (always
   present when matplotlib is installed; same DejaVu license).
3. `None` — caller falls back to `PIL.ImageFont.load_default()`
   (bitmap; pixel-accuracy degrades but no crash).

Most CI environments will land on path #2 because matplotlib is a
hard dependency of the `render-visual` skill's chart recipes.
Committing the actual TTF (path #1) is optional and is only needed
when matplotlib cannot be installed.

## How to actually bundle the font

If you want to ship a hard guarantee that the font is present
without depending on matplotlib's bundle:

```bash
# From the dejavu-fonts source tarball at https://dejavu-fonts.github.io/
cp DejaVuSans.ttf agent-packs/story-telling-agent/.github/skills/render-visual/assets/DejaVuSans.ttf
```

The font is ~750 KB. Include `DejaVuSans.LICENSE.md` alongside it
(already present in this directory). No code changes required —
`font_locator.find_dejavu_sans()` will pick it up from
resolution-order step #1.

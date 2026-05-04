---
name: pptx-visual-qa
description: "Headless render pipeline (.pptx → .pdf → per-slide .png via LibreOffice + pdftoppm) plus per-slide visual rubric for multimodal inspection. Loaded by @deck-critic to actually look at generated decks. Cross-platform with fallbacks. Keywords: render, screenshot, headless, soffice, libreoffice, pdftoppm, visual QA, multimodal, rubric."
---

# PPTX Visual QA

The render-and-look layer of the deck-critic pipeline. Converts a
`.pptx` to per-slide PNGs and provides the rubric the multimodal critic
applies to each rendered image.

## When to Use This Skill

Load this skill when you are `@deck-critic` and need to:

- Generate per-slide PNG renders of `output.pptx`
- Apply the per-slide visual rubric (focal point, density, contrast,
  alignment, accent usage, image use, type-scale adherence)

## Pipeline at a Glance

```
output.pptx
    │
    ▼ soffice --headless --convert-to pdf
output.pdf
    │
    ▼ pdftoppm -r 110 deck.pdf slide -png
slide-1.png, slide-2.png, ...
    │
    ▼ @deck-critic.view (image-aware)
qa-report.json (per-slide visual section)
```

If LibreOffice is unavailable, the script tries (in order)
`libreoffice` (alias), `unoconv`, then a pure-Python fallback via
`pdf2image` (which itself needs `poppler`). If none succeed, the
script writes `manifest.json` with `"render_engine": null` and
`"slides": []`; structural assertions still run, and the critic surfaces
`render_skipped: true` as a non-blocking finding.

## Files in This Skill

| File | Purpose |
|------|---------|
| [SKILL.md](SKILL.md) | This file |
| [references/render-pipeline.md](references/render-pipeline.md) | Commands, exit-code handling, font-substitution gotchas, dpi guidance, cross-platform install notes |
| [references/visual-rubric.md](references/visual-rubric.md) | Per-slide rubric the multimodal critic applies |
| [scripts/render_pptx.py](scripts/render_pptx.py) | Cross-platform render driver — emits per-slide PNGs + manifest.json |

## Quick Use

```bash
python .github/skills/pptx-visual-qa/scripts/render_pptx.py \
  --pptx <session>/agents/deck-builder/output.pptx \
  --out  <session>/agents/deck-critic/renders/
```

Output:

```
<out>/manifest.json   # render_engine, dpi, slides[], errors[]
<out>/slide-1.png
<out>/slide-2.png
...
```

## Per-Slide Visual Rubric (Summary)

For each rendered PNG the critic records:

- **focal_point_present** — Can you identify ONE dominant element in 3 seconds?
- **text_density** — `low | medium | high` based on rough text-area-to-slide ratio.
- **contrast_pass** — All visible text legible against its background.
- **alignment_label** — `aligned | mostly-aligned | misaligned` (eyeball pass; structural-asserts has the precise check).
- **layout_label** — Which layout type from `presentation-design`'s vocabulary best describes this slide.
- **antipatterns** — list of antipattern IDs (1–10) detected, drawn from `slide-critique`.

Full rubric, including the 1–5 scale per axis and concrete examples,
lives in [references/visual-rubric.md](references/visual-rubric.md).

## Known Failure Modes

- **Font substitution** — If the host LibreOffice doesn't have Calibri/
  Inter/Helvetica Neue, it substitutes (often badly). The render
  pipeline records `font_substitutions` in `manifest.json` so the
  critic can flag it.
- **Slow first invocation** — LibreOffice's first headless run can take
  20–40s while it initializes profiles. Subsequent runs are <5s.
- **DPI tradeoff** — `-r 110` is the default (good legibility, fast).
  Bump to `-r 200` for fine alignment review; quadruples file size.

## References

- [Render Pipeline](references/render-pipeline.md)
- [Visual Rubric](references/visual-rubric.md)
- [render_pptx.py](scripts/render_pptx.py)

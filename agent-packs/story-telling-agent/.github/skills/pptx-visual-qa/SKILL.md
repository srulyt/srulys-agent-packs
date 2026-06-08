---
name: pptx-visual-qa
description: "Headless render pipeline (.pptx → .pdf → per-slide .png via LibreOffice + pypdfium2) plus per-slide visual rubric (incl. the aesthetic_craft axis) for multimodal inspection. Loaded by @deck-critic to actually look at generated decks. Cross-platform with fallbacks; permissive-only engines. Keywords: render, screenshot, headless, soffice, libreoffice, pypdfium2, pdftoppm, visual QA, multimodal, rubric, aesthetic craft."
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
    ▼ soffice --headless --convert-to pdf   (auto-discovers LibreOffice off-PATH)
output.pdf
    │
    ▼ pypdfium2 render(scale=dpi/72)  [preferred; pdftoppm/pdf2image fallback]
slide-1.png, slide-2.png, ...   (150 DPI aesthetic pass)
    │
    ▼ @deck-critic.view (image-aware)
qa-report.json (per-slide visual section incl. aesthetic_craft)
```

If LibreOffice is unavailable, the script tries (in order)
`libreoffice` (alias), `unoconv`. The pdf→png stage prefers
**pypdfium2** (Apache/BSD, no system dependency) and falls back to
`pdftoppm` then `pdf2image` (both poppler). PyMuPDF is excluded (AGPL).
If none succeed, the script writes `manifest.json` with `"render_engine": null` and
`"slides": []`; structural assertions still run. Per OQ5 (and the B3
verify-or-block policy), `render_skipped: true` is BLOCKING
(`render_unverified`) for any deck containing one or more `styled`
slides; for simple-only decks the critic emits `unverified-needs-user`
— an explicit user-decision gate (install / ship-with-consent / abort),
NOT a silent pass.

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

- **Font substitution** — The design systems target a render-installed
  free font set (Inter, Source Serif 4, IBM Plex, Fraunces, Space
  Grotesk, Archivo) so the verified PNG shows the intended faces. An
  *unexpected* substitution (a design font absent from `render_safe`)
  is surfaced by the critic as a CONCERN with an install recommendation
  — not a silent pass. Substitutions are recorded in
  `manifest.font_substitutions`.
- **Slow first invocation** — LibreOffice's first headless run can take
  20–40s while it initializes profiles. Subsequent runs are <5s.
- **DPI tradeoff** — the aesthetic pass renders at **150 DPI**
  (`render_pptx.DEFAULT_DPI`) so tracking/hairlines are legible; bump
  to 200 for sub-pixel alignment review.

## References

- [Render Pipeline](references/render-pipeline.md)
- [Visual Rubric](references/visual-rubric.md)
- [render_pptx.py](scripts/render_pptx.py)

## Rendering Subsystem Rebuild (2026-05-04)

scripts/render_pptx.py was rewritten in session
2026-05-04-7d3f9a2b:

- **Permitted render engines are LGPL/permissive only** (per OQ1, decisions.md): the engine list
  is strictly OSS-permissive (LGPL): `soffice` →
  `libreoffice` → `unoconv`.
- **render_unverified flag** in manifest.json. Defaults to
  `true`; flipped to `false` only when the full pipeline
  succeeds. The `@deck-critic` consults this flag plus the
  deck's `styled_count` to choose between the
  `render_unverified` BLOCKING verdict (any styled slide) and
  the `unverified-needs-user` user-decision gate (simple-only deck
  — per OQ5 / B3; NOT a silent ship).
- **engines_attempted / engines_available** lists for
  visibility into which engines the runner saw on PATH.

## pdf→png Engine + Font Pass (2026-06-08, session c5d9e1a7)

- **pdf→png now prefers `pypdfium2`** (Google PDFium, Apache-2.0/BSD —
  OQ1-clean, no system poppler). `pdftoppm` / `pdf2image` remain
  fallbacks. **PyMuPDF/`fitz` is forbidden** (AGPL). `manifest.json`
  gained a `png_engine` field recording which path produced the PNGs.
- **soffice off-PATH discovery** — the renderer probes standard
  LibreOffice install locations so a Windows/macOS installer works
  without a PATH edit.
- **Aesthetic-pass DPI bumped to 150** (`DEFAULT_DPI`).
- **Render-present design fonts** + unexpected-substitution → critic
  CONCERN (see render-pipeline.md → Font Substitution).

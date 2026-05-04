# Render Pipeline

> Concrete commands, exit-code handling, font-substitution gotchas, and
> cross-platform install notes for converting `.pptx → .pdf → .png`.

## Table of Contents

1. [Engines (Tried in Order)](#engines-tried-in-order)
2. [Commands](#commands)
3. [Exit Codes & Error Handling](#exit-codes--error-handling)
4. [Cross-Platform Install Notes](#cross-platform-install-notes)
5. [Font Substitution](#font-substitution)
6. [DPI / Resolution Guidance](#dpi--resolution-guidance)
7. [Manifest Schema](#manifest-schema)

## Engines (Tried in Order)

`render_pptx.py` probes for engines and uses the first one available:

1. `soffice --headless` (LibreOffice; macOS / Linux / Windows)
2. `libreoffice --headless` (alias on some distros)
3. `unoconv` (older systems; thin wrapper around UNO)
4. `pdf2image` Python package (requires `poppler-utils` separately
   installed) — ONLY for pdf→png; cannot do pptx→pdf

If none are available, the script writes `manifest.json` with
`render_engine: null` and exits 0 (so the critic continues to
structural assertions and reports `render_skipped: true`).

## Commands

### Stage 1 — pptx → pdf (LibreOffice)

```bash
soffice --headless --convert-to pdf --outdir <outdir> <pptx>
```

Output: `<outdir>/<basename>.pdf`. Duration: 5–40s depending on cold/
warm profile and slide count.

### Stage 2 — pdf → png (pdftoppm)

```bash
pdftoppm -r 110 -png <pdf> <outdir>/slide
```

Produces `slide-1.png, slide-2.png, ...` (1-indexed). `pdftoppm` ships
with `poppler-utils`.

### Fallback — pdf2image (Python)

```python
from pdf2image import convert_from_path
images = convert_from_path("output.pdf", dpi=110)
for i, im in enumerate(images, start=1):
    im.save(f"slide-{i}.png", "PNG")
```

Requires `poppler` separately (the python package is just bindings).

## Exit Codes & Error Handling

| Code | Cause | Recovery |
|------|-------|----------|
| 0 | Success | Continue |
| 1 | LibreOffice profile lock | Retry once after 2s; second failure → record error and try next engine |
| 77 | Soffice missing on PATH | Try next engine |
| 134 | Soffice crash on weird shapes | Record error, try next engine |
| Any from pdftoppm | poppler missing or PDF corrupt | Fallback to `pdf2image`; if that fails, set `render_engine: null` |

The script captures stderr to `manifest.errors[]` and never raises to
the critic — non-zero render is a non-blocking finding.

## Cross-Platform Install Notes

| Platform | Install |
|----------|---------|
| macOS | `brew install --cask libreoffice && brew install poppler` |
| Ubuntu/Debian | `apt-get install libreoffice poppler-utils` |
| Windows | LibreOffice MSI from libreoffice.org; ensure `soffice.exe` on PATH. Poppler: `choco install poppler` or use the conda-forge build. |
| WSL2 | Same as Ubuntu |
| GitHub Actions | `apt-get update && apt-get install -y libreoffice poppler-utils` |

## Font Substitution

LibreOffice silently substitutes fonts it doesn't have. Common
subs that affect this pack:

| Requested | Common Substitution | Visual Impact |
|-----------|---------------------|---------------|
| Calibri / Calibri Light | DejaVu Sans / Carlito | Slightly heavier, slightly wider |
| Inter | Liberation Sans / DejaVu Sans | Modern feel lost |
| Helvetica Neue | Liberation Sans | Hero size still impressive |
| JetBrains Mono | DejaVu Sans Mono | Mostly fine |
| Garamond | Liberation Serif | Editorial gravitas reduced |

`render_pptx.py` records substitutions when LibreOffice prints them to
stderr; the critic flags substitution as a non-blocking finding (your
deck will still ship; downstream consumers may want to install fonts).

## DPI / Resolution Guidance

| DPI | File Size (per slide) | Use Case |
|-----|----------------------|----------|
| 72 | ~150 KB | Thumbnail grids |
| 110 | ~400 KB | **Default — visual rubric** |
| 150 | ~700 KB | Higher-fidelity review |
| 200 | ~1.5 MB | Alignment-grid sub-pixel review |
| 300 | ~3 MB | Print-quality (overkill for QA) |

## Manifest Schema

`renders/manifest.json` shape:

```json
{
  "session_id": "...",
  "pptx_path": "...",
  "render_engine": "soffice|libreoffice|unoconv|pdf2image|null",
  "dpi": 110,
  "slides": [
    {"index": 1, "png_path": "slide-1.png", "width_px": 1466, "height_px": 825}
  ],
  "font_substitutions": ["Calibri Light → Carlito"],
  "errors": [],
  "duration_ms": 7820
}
```

The critic reads this verbatim; do not modify after the script writes it.

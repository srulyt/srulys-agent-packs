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

`render_pptx.py` probes for engines in two stages.

**Stage 1 — pptx → pdf** (first available wins):

1. `soffice --headless` (LibreOffice; macOS / Linux / Windows). When
   not on `PATH`, the script also probes well-known install locations
   (`C:\Program Files\LibreOffice\program\soffice.exe`,
   `/Applications/LibreOffice.app/...`, `/usr/bin/soffice`, …) so a
   standard installer works without a PATH edit.
2. `libreoffice --headless` (alias on some distros)
3. `unoconv` (older systems; thin wrapper around UNO)

**Stage 2 — pdf → png** (preference order, OQ1 permissive-only):

1. **`pypdfium2`** (Google PDFium, **Apache-2.0 / BSD**) — PREFERRED.
   In-process, no system dependency, no subprocess to hang. Renders
   each page at `scale = dpi / 72`.
2. `pdftoppm` (poppler) — subprocess fallback (stdin closed, bounded).
3. `pdf2image` (poppler bindings) — last resort.

> **PyMuPDF / `fitz` is intentionally NOT used.** It is **AGPL-3.0**,
> which violates the pack's OQ1 permissive-only engine policy. Use
> `pypdfium2` (`pip install pypdfium2`) — strictly better on both
> license and packaging (no system poppler needed).

If neither stage yields output, the script writes `manifest.json` with
`render_engine: null` / `png_engine: null` and exits 0 (so the critic
continues to structural assertions and reports `render_unverified`).

## Commands

### Stage 1 — pptx → pdf (LibreOffice)

```bash
soffice --headless --convert-to pdf --outdir <outdir> <pptx>
```

Output: `<outdir>/<basename>.pdf`. Duration: 5–40s depending on cold/
warm profile and slide count. stdin is closed (DEVNULL) so a first-run
LibreOffice prompt can never wedge the call.

### Stage 2 — pdf → png (pypdfium2, preferred)

```python
import pypdfium2 as pdfium
doc = pdfium.PdfDocument("output.pdf")
for i in range(len(doc)):
    bitmap = doc[i].render(scale=dpi / 72.0)
    bitmap.to_pil().save(f"slide-{i+1}.png", "PNG")
doc.close()
```

Produces `slide-1.png, slide-2.png, ...` (1-indexed). No system
dependency — `pypdfium2` ships the PDFium binary as a wheel.

### Fallback — pdftoppm (poppler)

```bash
pdftoppm -r 150 -png <pdf> <outdir>/slide
```

Only used when `pypdfium2` is unavailable. `pdftoppm` ships with
`poppler-utils`.

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
| macOS | `brew install --cask libreoffice && pip install pypdfium2` |
| Ubuntu/Debian | `apt-get install libreoffice && pip install pypdfium2` |
| Windows | LibreOffice MSI from libreoffice.org (the renderer auto-discovers `C:\Program Files\LibreOffice\program\soffice.exe`; no PATH edit required). `pip install pypdfium2`. |
| WSL2 | Same as Ubuntu |
| GitHub Actions | `apt-get update && apt-get install -y libreoffice && pip install pypdfium2` |

> `pypdfium2` is the only pip dependency for the PNG stage — it bundles
> the PDFium binary, so **no system `poppler`/`poppler-utils` is
> needed**. Poppler (`pdftoppm`) remains an optional fallback only.

### Step 3 — install the curated design fonts (required for B2)

The design-font == render-font guarantee only holds if the curated free
font set is **installed on the render host**. Download the families from
Google Fonts (all OFL/Apache, free for embedding) and drop the `.ttf`
files into the OS / LibreOffice font directory, then refresh the font
cache:

| Platform | Font install location | Command sketch |
|----------|-----------------------|----------------|
| macOS | `~/Library/Fonts` (user) or `/Library/Fonts` (all) | copy `.ttf` → folder; `atsutil databases -remove` to refresh |
| Ubuntu/Debian/WSL2 | `~/.local/share/fonts` or `/usr/share/fonts/truetype/curated` | copy `.ttf` → folder; `fc-cache -f` |
| Windows | `%WINDIR%\Fonts` (all) or `%LOCALAPPDATA%\Microsoft\Windows\Fonts` (user) | right-click → Install, or copy + register |
| GitHub Actions | `~/.local/share/fonts` | `mkdir -p ~/.local/share/fonts && cp *.ttf ~/.local/share/fonts && fc-cache -f` |

Curated families to install (each from
[fonts.google.com](https://fonts.google.com)): **Inter**,
**Source Serif 4**, **IBM Plex Sans**, **IBM Plex Mono**, **Fraunces**,
**Space Grotesk**, **Archivo**.

> **If the curated fonts are absent the pack does NOT emit silent bad
> output.** LibreOffice substitutes (DejaVu/Liberation), the render
> manifest records the substitution, `check_pptx.py` raises
> `font_not_render_present`, and the critic surfaces a
> **substitution CONCERN** with this install recommendation — the
> verified PNG is flagged as *not the intended typography*, never
> silently approved.

## Font Substitution

LibreOffice silently substitutes fonts it doesn't have. The pack's
design systems now target a **render-installed free font set** so the
verified PNG shows the *intended* typography:

| Design font (render-present) | Role |
|------------------------------|------|
| Inter | UI / body sans |
| Source Serif 4 | editorial serif body/display |
| IBM Plex Sans / IBM Plex Mono | technical sans / mono |
| Fraunces | high-contrast display serif |
| Space Grotesk | geometric display |
| Archivo | grotesque display |

These are listed in each system's `fonts.render_safe` allowlist, so
`check_pptx.py` stays quiet for the intended faces. **An *unexpected*
display-font substitution** (a design face NOT in `render_safe`, i.e.
the renderer fell back to DejaVu/Liberation) is now surfaced by the
critic as a **CONCERN** with an install recommendation — it is no
longer a silent pass, because for an aesthetics-first deck the
approved render must be the deck the design system describes.

| Requested (legacy) | Common Substitution | Visual Impact |
|--------------------|---------------------|---------------|
| Calibri / Calibri Light | DejaVu Sans / Carlito | Heavier, wider |
| Garamond | Liberation Serif | Editorial gravitas reduced |
| Helvetica Neue | Liberation Sans | Modern feel lost |

`render_pptx.py` records substitutions to `manifest.font_substitutions`;
`check_pptx.py` emits `font_not_render_present` for any run whose font
is neither in `render_safe` nor a declared `*_fallback`.

## DPI / Resolution Guidance

| DPI | File Size (per slide) | Use Case |
|-----|----------------------|----------|
| 72 | ~150 KB | Thumbnail grids |
| 110 | ~400 KB | Fast structural pass |
| 150 | ~700 KB | **Default — aesthetic rubric (tracking/hairlines visible)** |
| 200 | ~1.5 MB | Alignment-grid sub-pixel review |
| 300 | ~3 MB | Print-quality (overkill for QA) |

> The aesthetic pass renders at **150 DPI** (`render_pptx.DEFAULT_DPI`)
> so the critic can judge letter-tracking, hairline rules, and tonal
> layering — invisible at 110.

## Manifest Schema

`renders/manifest.json` shape:

```json
{
  "session_id": "...",
  "pptx_path": "...",
  "render_engine": "soffice|libreoffice|unoconv|null",
  "png_engine": "pypdfium2|pdftoppm|pdf2image|null",
  "png_engines_preference": ["pypdfium2", "pdftoppm", "pdf2image"],
  "render_unverified": false,
  "dpi": 150,
  "slides": [
    {"index": 1, "png_path": "slide-1.png", "width_px": 2001, "height_px": 1126}
  ],
  "font_substitutions": ["Calibri Light → Carlito"],
  "errors": [],
  "duration_ms": 7820
}
```

The critic reads this verbatim; do not modify after the script writes it.

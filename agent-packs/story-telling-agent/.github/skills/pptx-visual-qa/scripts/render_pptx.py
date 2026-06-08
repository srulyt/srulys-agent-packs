#!/usr/bin/env python3
"""render_pptx.py — Headless PPTX → per-slide PNG renderer.

Pipeline:
  1. pptx → pdf via a layered fallback list (`ENGINES`):
       soffice → libreoffice → unoconv
     (NO aspose-slides — per OQ1, decisions.md 2026-05-04T14:50Z,
     we stay LGPL/permissive OSS only.)
  2. pdf → png via **pypdfium2** (Google PDFium, Apache-2.0/BSD — OQ1
     clean, no system dependency) as the PREFERRED path, falling back
     to `pdftoppm` (poppler) then `pdf2image` only when pypdfium2 is
     absent. PyMuPDF / `fitz` is deliberately NOT used: it is AGPL-3.0
     and violates the pack's permissive-only engine policy.

If no engine is available, writes manifest.json with
`render_engine: null` AND `render_unverified: true`. The deck-critic
treats `render_unverified=true` as a BLOCKING finding for any deck
that has at least one styled slide (per OQ5); for simple-only decks
the verdict downgrades to the `unverified-needs-user` user-decision
gate (B3 — never a silent ship).

Subprocess discipline (mirrors marp-engine `_run_bounded`): every
external call closes stdin (DEVNULL) so a first-run / interactive
prompt can never block, and is bounded by a hard timeout.

Usage:
  python render_pptx.py --pptx PATH --out DIR [--dpi 150]

Output:
  <out>/manifest.json
  <out>/slide-1.png, slide-2.png, ...
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Callable

# Default aesthetic-pass DPI (C5 — bumped from 110 so the critic can
# actually judge letter-tracking, hairlines, and tonal layering).
DEFAULT_DPI = 150

# Known non-PATH LibreOffice install locations probed when `soffice`
# isn't on PATH (common on Windows / macOS). Keeps the render-and-
# inspect loop functional without requiring a PATH edit.
_SOFFICE_FALLBACK_PATHS = [
    r"C:\Program Files\LibreOffice\program\soffice.exe",
    r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
    "/Applications/LibreOffice.app/Contents/MacOS/soffice",
    "/usr/bin/soffice",
    "/usr/local/bin/soffice",
    "/opt/libreoffice/program/soffice",
]


def _which(*candidates: str) -> str | None:
    for c in candidates:
        p = shutil.which(c)
        if p:
            return p
    # PATH miss — probe well-known install locations for the office
    # engines so a standard installer (no PATH edit) still renders.
    if any(c in ("soffice", "libreoffice") for c in candidates):
        for p in _SOFFICE_FALLBACK_PATHS:
            if os.path.isfile(p):
                return p
    return None


# --- ENGINES: layered fallback for PPTX → PDF (OQ1) -----------------------
# Each entry: (name, argv-builder). The builder takes (exe, pptx, outdir)
# and returns the argv to subprocess. Order matters: most-preferred first.

def _argv_soffice(exe: str, pptx: Path, outdir: Path) -> list[str]:
    return [exe, "--headless", "--convert-to", "pdf",
            "--outdir", str(outdir), str(pptx)]


def _argv_libreoffice(exe: str, pptx: Path, outdir: Path) -> list[str]:
    # `libreoffice` is usually a symlink to `soffice`, but we keep
    # the entry to handle distros where only `libreoffice` is on PATH.
    return [exe, "--headless", "--convert-to", "pdf",
            "--outdir", str(outdir), str(pptx)]


def _argv_unoconv(exe: str, pptx: Path, outdir: Path) -> list[str]:
    return [exe, "-f", "pdf", "-o",
            str(outdir / (pptx.stem + ".pdf")), str(pptx)]


ENGINES: list[tuple[str, Callable[[str, Path, Path], list[str]]]] = [
    ("soffice",     _argv_soffice),
    ("libreoffice", _argv_libreoffice),
    ("unoconv",     _argv_unoconv),
]


def pptx_to_pdf(pptx: Path, outdir: Path,
                errors: list) -> tuple[Path | None, str | None, list[str]]:
    """Try each engine in ENGINES order. Returns (pdf, engine_name, font_subs)."""
    substitutions: list[str] = []
    for name, build_argv in ENGINES:
        exe = _which(name)
        if not exe:
            continue
        try:
            argv = build_argv(exe, pptx, outdir)
            r = subprocess.run(argv, capture_output=True, text=True,
                               stdin=subprocess.DEVNULL, timeout=180)
            stderr = (r.stderr or "") + (r.stdout or "")
            for line in stderr.splitlines():
                low = line.lower()
                if "substituting" in low or ("font" in low and "→" in line):
                    substitutions.append(line.strip())
            if r.returncode == 0:
                pdf = outdir / (pptx.stem + ".pdf")
                if pdf.exists():
                    return pdf, name, substitutions
            errors.append(f"{name} exit={r.returncode} stderr={stderr[:400]}")
        except Exception as e:  # noqa: BLE001
            errors.append(f"{name} exception: {e}")
    return None, None, substitutions


def pdf_to_pngs(pdf: Path, outdir: Path, dpi: int,
                errors: list) -> tuple[list[Path], str | None]:
    """Render every PDF page to slide-N.png.

    Engine preference (OQ1 permissive-only):
      1. **pypdfium2** (Google PDFium, Apache-2.0/BSD) — in-process, no
         system dependency, no subprocess to hang. PREFERRED.
      2. `pdftoppm` (poppler) — subprocess, stdin closed + bounded.
      3. `pdf2image` (poppler bindings) — last resort.

    PyMuPDF/`fitz` is intentionally excluded (AGPL-3.0 — OQ1 violation).

    Returns ``(pngs, png_engine_name)``.
    """
    # --- 1. pypdfium2 (preferred) -------------------------------------
    try:
        import pypdfium2 as pdfium  # type: ignore

        scale = dpi / 72.0  # PDF points → pixels at requested DPI
        doc = pdfium.PdfDocument(str(pdf))
        pngs: list[Path] = []
        try:
            n = len(doc)
            for i in range(n):
                page = doc[i]
                bitmap = page.render(scale=scale)
                pil_image = bitmap.to_pil()
                p = outdir / f"slide-{i + 1}.png"
                pil_image.save(str(p), "PNG")
                pngs.append(p)
        finally:
            doc.close()
        if pngs:
            return pngs, "pypdfium2"
        errors.append("pypdfium2 produced no pages")
    except ImportError:
        errors.append("pypdfium2 not installed; trying pdftoppm/pdf2image")
    except Exception as e:  # noqa: BLE001
        errors.append(f"pypdfium2 exception: {e}; trying pdftoppm/pdf2image")

    # --- 2. pdftoppm (poppler) fallback -------------------------------
    pdftoppm = _which("pdftoppm")
    if pdftoppm:
        try:
            prefix = outdir / "slide"
            r = subprocess.run(
                [pdftoppm, "-r", str(dpi), "-png", str(pdf), str(prefix)],
                capture_output=True, text=True,
                stdin=subprocess.DEVNULL, timeout=180,
            )
            if r.returncode == 0:
                pngs = sorted(outdir.glob("slide-*.png"))
                if pngs:
                    return pngs, "pdftoppm"
            errors.append(f"pdftoppm exit={r.returncode} stderr={(r.stderr or '')[:400]}")
        except Exception as e:  # noqa: BLE001
            errors.append(f"pdftoppm exception: {e}")

    # --- 3. pdf2image (poppler bindings) last resort ------------------
    try:
        from pdf2image import convert_from_path  # type: ignore
        images = convert_from_path(str(pdf), dpi=dpi)
        pngs = []
        for i, im in enumerate(images, start=1):
            p = outdir / f"slide-{i}.png"
            im.save(str(p), "PNG")
            pngs.append(p)
        if pngs:
            return pngs, "pdf2image"
    except ImportError:
        errors.append("pdf2image not installed; pypdfium2/pdftoppm unavailable; cannot render PNGs")
    except Exception as e:  # noqa: BLE001
        errors.append(f"pdf2image exception: {e}")
    return [], None


def png_dims(path: Path) -> tuple[int | None, int | None]:
    try:
        head = path.open("rb").read(24)
        if len(head) < 24 or head[:8] != b"\x89PNG\r\n\x1a\n":
            return None, None
        w = int.from_bytes(head[16:20], "big")
        h = int.from_bytes(head[20:24], "big")
        return w, h
    except Exception:
        return None, None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pptx", required=True, type=Path)
    ap.add_argument("--out",  required=True, type=Path)
    ap.add_argument("--dpi",  type=int, default=DEFAULT_DPI)
    args = ap.parse_args()

    pptx, outdir = args.pptx, args.out
    outdir.mkdir(parents=True, exist_ok=True)

    if not pptx.exists():
        print(f"ERROR: pptx not found: {pptx}", file=sys.stderr)
        return 2

    t0 = time.time()
    errors: list[str] = []
    manifest: dict = {
        "session_id": None,
        "pptx_path": str(pptx),
        "render_engine": None,        # pptx→pdf engine, populated on success
        "png_engine": None,           # pdf→png engine (pypdfium2|pdftoppm|pdf2image)
        "render_unverified": True,    # flipped False on success (OQ1/OQ5)
        "engines_attempted": [name for name, _ in ENGINES],
        "engines_available": [name for name, _ in ENGINES if _which(name)],
        "png_engines_preference": ["pypdfium2", "pdftoppm", "pdf2image"],
        "dpi": args.dpi,
        "slides": [],
        "font_substitutions": [],
        "errors": errors,
        "duration_ms": 0,
    }

    pdf, engine_pdf, subs = pptx_to_pdf(pptx, outdir, errors)
    manifest["font_substitutions"] = subs
    if pdf is None:
        manifest["duration_ms"] = int((time.time() - t0) * 1000)
        (outdir / "manifest.json").write_text(json.dumps(manifest, indent=2))
        print("WARN: render skipped (no PPTX→PDF engine available)", file=sys.stderr)
        return 0

    pngs, png_engine = pdf_to_pngs(pdf, outdir, args.dpi, errors)
    manifest["render_engine"] = engine_pdf
    manifest["png_engine"] = png_engine
    if not pngs:
        # PDF stage succeeded; PNG stage didn't. Still unverified.
        manifest["duration_ms"] = int((time.time() - t0) * 1000)
        (outdir / "manifest.json").write_text(json.dumps(manifest, indent=2))
        print("WARN: PDF rendered but PNG conversion failed", file=sys.stderr)
        return 0

    manifest["render_unverified"] = False  # full pipeline succeeded
    for i, p in enumerate(pngs, start=1):
        w, h = png_dims(p)
        manifest["slides"].append({
            "index": i,
            "png_path": p.name,
            "width_px": w,
            "height_px": h,
        })
    manifest["duration_ms"] = int((time.time() - t0) * 1000)
    (outdir / "manifest.json").write_text(json.dumps(manifest, indent=2))
    print(f"SUCCESS: rendered {len(pngs)} slides via {engine_pdf} -> "
          f"{png_engine} in {manifest['duration_ms']}ms")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
render_pptx.py — Headless PPTX → per-slide PNG renderer for @deck-critic.

Pipeline:
  1. pptx → pdf via LibreOffice (`soffice --headless`), with fallbacks
     to `libreoffice` and `unoconv`.
  2. pdf → png via `pdftoppm` (poppler), with fallback to `pdf2image`.

If no engine is available, writes manifest.json with render_engine=null
and exits 0; the critic surfaces this as a non-blocking finding.

Usage:
  python render_pptx.py --pptx PATH --out DIR [--dpi 110]

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


def which(*candidates: str) -> str | None:
    for c in candidates:
        p = shutil.which(c)
        if p:
            return p
    return None


def pptx_to_pdf(pptx: Path, outdir: Path, errors: list) -> tuple[Path | None, str | None, list[str]]:
    """Try LibreOffice, then libreoffice alias, then unoconv."""
    substitutions: list[str] = []
    candidates = [
        ("soffice", ["--headless", "--convert-to", "pdf", "--outdir", str(outdir), str(pptx)]),
        ("libreoffice", ["--headless", "--convert-to", "pdf", "--outdir", str(outdir), str(pptx)]),
        ("unoconv", ["-f", "pdf", "-o", str(outdir / (pptx.stem + ".pdf")), str(pptx)]),
    ]
    for name, args in candidates:
        exe = which(name)
        if not exe:
            continue
        try:
            r = subprocess.run([exe, *args], capture_output=True, text=True, timeout=180)
            stderr = (r.stderr or "") + (r.stdout or "")
            for line in stderr.splitlines():
                if "substituting" in line.lower() or "font" in line.lower() and "→" in line:
                    substitutions.append(line.strip())
            if r.returncode == 0:
                pdf = outdir / (pptx.stem + ".pdf")
                if pdf.exists():
                    return pdf, name, substitutions
            errors.append(f"{name} exit={r.returncode} stderr={stderr[:400]}")
        except Exception as e:  # noqa: BLE001
            errors.append(f"{name} exception: {e}")
    return None, None, substitutions


def pdf_to_pngs(pdf: Path, outdir: Path, dpi: int, errors: list) -> list[Path]:
    """Try pdftoppm, fallback to pdf2image."""
    pdftoppm = which("pdftoppm")
    if pdftoppm:
        try:
            prefix = outdir / "slide"
            r = subprocess.run(
                [pdftoppm, "-r", str(dpi), "-png", str(pdf), str(prefix)],
                capture_output=True, text=True, timeout=180,
            )
            if r.returncode == 0:
                pngs = sorted(outdir.glob("slide-*.png"))
                if pngs:
                    return pngs
            errors.append(f"pdftoppm exit={r.returncode} stderr={(r.stderr or '')[:400]}")
        except Exception as e:  # noqa: BLE001
            errors.append(f"pdftoppm exception: {e}")
    # Fallback: pdf2image
    try:
        from pdf2image import convert_from_path  # type: ignore
        images = convert_from_path(str(pdf), dpi=dpi)
        pngs: list[Path] = []
        for i, im in enumerate(images, start=1):
            p = outdir / f"slide-{i}.png"
            im.save(str(p), "PNG")
            pngs.append(p)
        return pngs
    except ImportError:
        errors.append("pdf2image not installed; pdftoppm unavailable; cannot render PNGs")
    except Exception as e:  # noqa: BLE001
        errors.append(f"pdf2image exception: {e}")
    return []


def png_dims(path: Path) -> tuple[int | None, int | None]:
    """Best-effort PNG dimensions without Pillow dependency."""
    try:
        with open(path, "rb") as f:
            head = f.read(24)
        if len(head) < 24 or head[:8] != b"\x89PNG\r\n\x1a\n":
            return None, None
        # IHDR width(4) height(4) at bytes 16-24
        w = int.from_bytes(head[16:20], "big")
        h = int.from_bytes(head[20:24], "big")
        return w, h
    except Exception:
        return None, None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pptx", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--dpi", type=int, default=110)
    args = ap.parse_args()

    pptx: Path = args.pptx
    outdir: Path = args.out
    outdir.mkdir(parents=True, exist_ok=True)

    if not pptx.exists():
        print(f"ERROR: pptx not found: {pptx}", file=sys.stderr)
        return 2

    t0 = time.time()
    errors: list[str] = []
    manifest: dict = {
        "session_id": None,
        "pptx_path": str(pptx),
        "render_engine": None,
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

    pngs = pdf_to_pngs(pdf, outdir, args.dpi, errors)
    if not pngs:
        manifest["duration_ms"] = int((time.time() - t0) * 1000)
        # Record the PDF stage succeeded even if PNG stage didn't.
        manifest["render_engine"] = engine_pdf
        (outdir / "manifest.json").write_text(json.dumps(manifest, indent=2))
        print("WARN: PDF rendered but PNG conversion failed", file=sys.stderr)
        return 0

    manifest["render_engine"] = engine_pdf  # PDF stage is the gating engine
    for i, p in enumerate(pngs, start=1):
        w, h = png_dims(p)
        manifest["slides"].append({
            "index": i,
            "png_path": str(p.relative_to(outdir)) if p.is_absolute() else str(p),
            "width_px": w,
            "height_px": h,
        })
    manifest["duration_ms"] = int((time.time() - t0) * 1000)
    (outdir / "manifest.json").write_text(json.dumps(manifest, indent=2))
    print(f"SUCCESS: rendered {len(pngs)} slides via {engine_pdf} → pdftoppm/pdf2image in {manifest['duration_ms']}ms")
    return 0


if __name__ == "__main__":
    sys.exit(main())

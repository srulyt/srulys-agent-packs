#!/usr/bin/env python3
"""render_pptx.py — Headless PPTX → per-slide PNG renderer.

Pipeline:
  1. pptx → pdf via a layered fallback list (`ENGINES`):
       soffice → libreoffice → unoconv
     (NO aspose-slides — per OQ1, decisions.md 2026-05-04T14:50Z,
     we stay LGPL OSS-permissive only.)
  2. pdf → png via `pdftoppm` (poppler), with fallback to `pdf2image`.

If no engine is available, writes manifest.json with
`render_engine: null` AND `render_unverified: true`. The deck-critic
treats `render_unverified=true` as a BLOCKING finding for any deck
that has at least one styled slide (per OQ5); for simple-only decks
the verdict may downgrade to `pass_unverified` (still ships).

Usage:
  python render_pptx.py --pptx PATH --out DIR [--dpi 110]

Output:
  <out>/manifest.json
  <out>/slide-1.png, slide-2.png, ...
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Callable


def _which(*candidates: str) -> str | None:
    for c in candidates:
        p = shutil.which(c)
        if p:
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
            r = subprocess.run(argv, capture_output=True, text=True, timeout=180)
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


def pdf_to_pngs(pdf: Path, outdir: Path, dpi: int, errors: list) -> list[Path]:
    """pdftoppm preferred; pdf2image fallback."""
    pdftoppm = _which("pdftoppm")
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
    ap.add_argument("--dpi",  type=int, default=110)
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
        "render_engine": None,        # populated when engine succeeds
        "render_unverified": True,    # flipped False on success (OQ1/OQ5)
        "engines_attempted": [name for name, _ in ENGINES],
        "engines_available": [name for name, _ in ENGINES if _which(name)],
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
    manifest["render_engine"] = engine_pdf
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
    print(f"SUCCESS: rendered {len(pngs)} slides via {engine_pdf} → "
          f"pdftoppm/pdf2image in {manifest['duration_ms']}ms")
    return 0


if __name__ == "__main__":
    sys.exit(main())

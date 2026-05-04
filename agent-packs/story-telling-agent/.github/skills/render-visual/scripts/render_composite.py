#!/usr/bin/env python3
"""render_composite.py — PIL/Pillow composite recipes.

Recipes:
  gradient_pattern   — radial/linear gradient hero background
  oversized_glyph_bg — large open-quote glyph at low opacity behind text

Output: PNG only. Per OQ3 (decisions.md 2026-05-04T14:50Z), PIL
composites do NOT emit SVG — we never rasterise back from PNG to
SVG, and PIL has no native SVG path.

Usage:
  render_composite.py --kind <recipe> --spec spec.json --tokens tokens.json
                      --out out.png [--size 1920x1080]
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def _ensure(mod: str, pip_name: str | None = None) -> None:
    try:
        __import__(mod)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", pip_name or mod])


_ensure("PIL", "Pillow")

from PIL import Image, ImageDraw, ImageFont, ImageFilter  # noqa: E402


def _hex_to_rgb(h: str) -> tuple[int, int, int]:
    h = (h or "#000000").lstrip("#")
    if len(h) != 6:
        return (0, 0, 0)
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def _palette(tokens: dict) -> dict:
    p = tokens.get("palette") or {}
    return {
        "bg_dark":   _hex_to_rgb(p.get("background_dark",  "#1E1E2E")),
        "bg_light":  _hex_to_rgb(p.get("background_light", "#F5F6FA")),
        "bg_accent": _hex_to_rgb(p.get("background_accent", "#4F46E5")),
        "primary":   _hex_to_rgb(p.get("primary_accent",   "#635BFF")),
        "secondary": _hex_to_rgb(p.get("secondary_accent", "#3ECF8E")),
        "highlight": _hex_to_rgb(p.get("highlight",        "#FF6B6B")),
        "text_dark":  _hex_to_rgb(p.get("text_on_dark",  "#FFFFFF")),
        "text_light": _hex_to_rgb(p.get("text_on_light", "#0F1019")),
    }


def _resolve_font(size_px: int) -> "ImageFont.ImageFont":
    """Resolve via the canonical font_locator (sibling assets/)."""
    here = Path(__file__).resolve().parent.parent / "assets"
    if str(here) not in sys.path:
        sys.path.insert(0, str(here))
    try:
        import font_locator  # type: ignore
        path = font_locator.find_dejavu_sans()
        if path:
            return ImageFont.truetype(path, size_px)
    except Exception:
        pass
    return ImageFont.load_default()


def _parse_size(size: str) -> tuple[int, int]:
    try:
        w, h = (int(x) for x in size.lower().split("x"))
        return w, h
    except Exception:
        return 1920, 1080


# ---------- recipes ----------

def render_gradient_pattern(spec: dict, pal: dict, size: tuple[int, int]) -> Image.Image:
    """Hero background: top-left → bottom-right linear gradient between two
    palette tokens (default `bg_dark` -> `bg_accent`), with optional 40%
    darken overlay (architecture §4.1 hero_full_bleed).
    """
    w, h = size
    start_token = spec.get("start", "background_dark")
    end_token = spec.get("end", "background_accent")
    palette_map = {
        "background_dark":   pal["bg_dark"],
        "background_light":  pal["bg_light"],
        "background_accent": pal["bg_accent"],
        "primary_accent":    pal["primary"],
        "secondary_accent":  pal["secondary"],
        "highlight":         pal["highlight"],
    }
    a = palette_map.get(start_token, pal["bg_dark"])
    b = palette_map.get(end_token,   pal["bg_accent"])

    img = Image.new("RGB", (w, h), color=a)
    px = img.load()
    diag = (w - 1) + (h - 1)
    for y in range(h):
        for x in range(w):
            t = (x + y) / diag
            r = int(a[0] + (b[0] - a[0]) * t)
            g = int(a[1] + (b[1] - a[1]) * t)
            bb = int(a[2] + (b[2] - a[2]) * t)
            px[x, y] = (r, g, bb)

    if spec.get("darken_overlay", True):
        overlay = Image.new("RGBA", (w, h), color=(0, 0, 0, int(255 * 0.40)))
        img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")

    if spec.get("blur_px"):
        img = img.filter(ImageFilter.GaussianBlur(radius=int(spec["blur_px"])))

    return img


def render_oversized_glyph_bg(spec: dict, pal: dict, size: tuple[int, int]) -> Image.Image:
    """Quote-style background: oversized open-quote glyph at low opacity,
    centred-left, on `bg_dark`.
    """
    w, h = size
    bg = spec.get("background_rgb") or pal["bg_dark"]
    glyph_color = pal["text_dark"]
    img = Image.new("RGB", (w, h), color=tuple(bg))
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    glyph_size = int(min(w, h) * 0.85)
    font = _resolve_font(glyph_size)
    text = spec.get("glyph", "\u201C")  # left double quotation mark
    opacity = int(255 * float(spec.get("opacity", 0.10)))
    rgba = (*glyph_color, opacity)
    # Draw at ~5% inset from left
    draw.text((int(w * 0.04), -int(glyph_size * 0.20)), text, fill=rgba, font=font)
    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    return img


RECIPES = {
    "gradient_pattern": render_gradient_pattern,
    "oversized_glyph_bg": render_oversized_glyph_bg,
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--kind", required=True, choices=sorted(RECIPES.keys()))
    ap.add_argument("--spec", required=True, type=Path)
    ap.add_argument("--tokens", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--size", default="1920x1080")
    ap.add_argument("--svg", action="store_true",
                    help="Ignored — PIL composites are PNG-only per OQ3.")
    args = ap.parse_args()

    if args.svg:
        print("WARN: --svg ignored; PIL composites are PNG-only (decisions.md OQ3).",
              file=sys.stderr)

    try:
        spec = json.loads(args.spec.read_text(encoding="utf-8"))
        tokens = json.loads(args.tokens.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"ERROR: bad spec/tokens JSON: {e}", file=sys.stderr)
        return 2

    pal = _palette(tokens)
    size = _parse_size(args.size)
    try:
        img = RECIPES[args.kind](spec, pal, size)
    except Exception as e:
        print(f"ERROR: composite {args.kind} failed: {e}", file=sys.stderr)
        return 2

    args.out.parent.mkdir(parents=True, exist_ok=True)
    img.save(str(args.out), format="PNG", optimize=True)
    print(f"SUCCESS: {args.kind} -> {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

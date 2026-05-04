#!/usr/bin/env python3
"""
check_pptx.py — Programmatic structural assertions for @deck-critic.

Loads <pptx> + <deck-spec>.json, runs ten checks, writes a JSON
report to --out.

Exits 0 on script success (even if checks fail). Exit 1 on file
errors / malformed pptx.

Checks:
  aspect_ratio, overflow, contrast (WCAG luminance ratio),
  alignment (0.05" snap), repeated layout hash, title underline
  count, max same-background run, speaker notes presence,
  duplicate titles, body word count max.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def ensure_pptx() -> None:
    try:
        import pptx  # noqa: F401
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "python-pptx"])


ensure_pptx()

from pptx import Presentation  # noqa: E402
from pptx.util import Emu  # noqa: E402

EMU_PER_INCH = 914400
SNAP_EMU = int(0.05 * EMU_PER_INCH)  # 45720


# ---------- color / contrast helpers ----------


def _hex_to_rgb(h: str) -> tuple[int, int, int] | None:
    h = h.strip().lstrip("#")
    if len(h) != 6:
        return None
    try:
        return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    except ValueError:
        return None


def _rgb_to_relative_luminance(rgb: tuple[int, int, int]) -> float:
    def chan(c: int) -> float:
        x = c / 255.0
        return x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4
    r, g, b = rgb
    return 0.2126 * chan(r) + 0.7152 * chan(g) + 0.0722 * chan(b)


def _contrast_ratio(fg: tuple[int, int, int], bg: tuple[int, int, int]) -> float:
    l1 = _rgb_to_relative_luminance(fg)
    l2 = _rgb_to_relative_luminance(bg)
    a, b = max(l1, l2), min(l1, l2)
    return (a + 0.05) / (b + 0.05)


def _shape_solid_rgb(shape) -> tuple[int, int, int] | None:
    try:
        f = shape.fill
        if f.type is None:
            return None
        # solid fill
        if hasattr(f, "fore_color") and getattr(f.fore_color, "type", None) is not None:
            try:
                rgb = f.fore_color.rgb
                if rgb is not None:
                    return rgb[0], rgb[1], rgb[2]
            except Exception:
                pass
    except Exception:
        return None
    return None


def _slide_bg_rgb(slide) -> tuple[int, int, int] | None:
    """Best-effort slide background color: explicit bg, then largest fullbleed shape."""
    try:
        bg = slide.background
        if bg is not None and bg.fill is not None:
            ftype = getattr(bg.fill, "type", None)
            if ftype is not None:
                try:
                    rgb = bg.fill.fore_color.rgb
                    if rgb is not None:
                        return rgb[0], rgb[1], rgb[2]
                except Exception:
                    pass
    except Exception:
        pass
    # Fallback: largest filled rectangle covering >=90% of slide
    best = None
    best_area = 0
    try:
        from pptx.util import Emu as _Emu  # noqa: F401
    except Exception:
        pass
    for shp in slide.shapes:
        try:
            w = int(shp.width or 0)
            h = int(shp.height or 0)
            area = w * h
            rgb = _shape_solid_rgb(shp)
            if rgb and area > best_area:
                best = rgb
                best_area = area
        except Exception:
            continue
    return best


def _bg_label(rgb: tuple[int, int, int] | None) -> str:
    if rgb is None:
        return "unknown"
    lum = _rgb_to_relative_luminance(rgb)
    if lum < 0.2:
        return "dark"
    if lum > 0.7:
        return "light"
    return "accent"


# ---------- per-slide extraction ----------


def _slide_title_text(slide) -> str:
    # Prefer placeholder title; else first text frame in reading order
    try:
        if slide.shapes.title is not None and slide.shapes.title.has_text_frame:
            return (slide.shapes.title.text_frame.text or "").strip()
    except Exception:
        pass
    for shp in slide.shapes:
        if getattr(shp, "has_text_frame", False):
            t = (shp.text_frame.text or "").strip()
            if t:
                return t
    return ""


def _body_word_count(slide) -> int:
    title = _slide_title_text(slide)
    words = 0
    for shp in slide.shapes:
        if not getattr(shp, "has_text_frame", False):
            continue
        t = (shp.text_frame.text or "").strip()
        if not t or t == title:
            continue
        words += len(t.split())
    return words


def _layout_hash(slide) -> str:
    parts = []
    for shp in slide.shapes:
        try:
            l = round((shp.left or 0) / EMU_PER_INCH, 1)
            t = round((shp.top or 0) / EMU_PER_INCH, 1)
            w = round((shp.width or 0) / EMU_PER_INCH, 1)
            h = round((shp.height or 0) / EMU_PER_INCH, 1)
            tf = 1 if getattr(shp, "has_text_frame", False) else 0
            parts.append((l, t, w, h, tf))
        except Exception:
            continue
    parts.sort()
    return "h:" + str(hash(tuple(parts)))[-12:]


def _has_underline_below_title(slide) -> bool:
    """Detect a thin (<=0.05") rectangle just below the title shape."""
    title = None
    try:
        title = slide.shapes.title
    except Exception:
        title = None
    if title is None:
        return False
    title_left = title.left or 0
    title_top = title.top or 0
    title_h = title.height or 0
    band_top = title_top + title_h
    band_top_min = band_top - int(0.1 * EMU_PER_INCH)
    band_top_max = band_top + int(0.5 * EMU_PER_INCH)
    for shp in slide.shapes:
        if shp == title:
            continue
        try:
            h = shp.height or 0
            t = shp.top or 0
            l = shp.left or 0
            w = shp.width or 0
            if h <= int(0.06 * EMU_PER_INCH) and band_top_min <= t <= band_top_max:
                # rectangle horizontally aligned-ish under the title
                if l <= title_left + int(0.5 * EMU_PER_INCH) and (l + w) >= title_left + int(1.0 * EMU_PER_INCH):
                    return True
        except Exception:
            continue
    return False


def _alignment_violations_for(slide, idx: int) -> list[dict]:
    out = []
    for shp in slide.shapes:
        try:
            l = shp.left or 0
            t = shp.top or 0
            for axis, val in (("left", l), ("top", t)):
                rem = val % SNAP_EMU
                # allow ±200 EMU rounding
                if rem > 200 and (SNAP_EMU - rem) > 200:
                    out.append({
                        "slide": idx,
                        "shape": getattr(shp, "name", "?"),
                        "off_snap_axis": axis,
                        "off_by_emu": int(min(rem, SNAP_EMU - rem)),
                    })
                    break
        except Exception:
            continue
    return out


def _overflow_estimate(slide, idx: int) -> dict | None:
    """Heuristic: for shapes with a text frame and explicit height, estimate
    line count vs frame capacity. Crude — reports estimated overflow in em-units."""
    for shp in slide.shapes:
        if not getattr(shp, "has_text_frame", False):
            continue
        try:
            tf = shp.text_frame
            text = tf.text or ""
            if not text.strip():
                continue
            # Estimate: assume 22pt body, 28pt line height; use shape width to wrap.
            shape_w_in = (shp.width or 0) / EMU_PER_INCH
            shape_h_in = (shp.height or 0) / EMU_PER_INCH
            if shape_w_in <= 0 or shape_h_in <= 0:
                continue
            # 22pt ≈ 0.305 in; chars per line ≈ shape_w_in / 0.13
            chars_per_line = max(10, int(shape_w_in / 0.13))
            lines = 0
            for para in text.splitlines():
                lines += max(1, (len(para) + chars_per_line - 1) // chars_per_line)
            line_h_in = 0.39  # 28pt
            needed_in = lines * line_h_in
            if needed_in > shape_h_in * 1.05:
                return {"slide": idx, "estimated_overflow_em": round(needed_in - shape_h_in, 2)}
        except Exception:
            continue
    return None


def _contrast_violations_for(slide, idx: int) -> list[dict]:
    out = []
    bg = _slide_bg_rgb(slide)
    if bg is None:
        return out
    for shp in slide.shapes:
        if not getattr(shp, "has_text_frame", False):
            continue
        for para in shp.text_frame.paragraphs:
            for run in para.runs:
                try:
                    if run.font.color and run.font.color.type is not None:
                        rgb = run.font.color.rgb
                        if rgb is not None:
                            fg = (rgb[0], rgb[1], rgb[2])
                            ratio = _contrast_ratio(fg, bg)
                            if ratio < 4.5:
                                out.append({
                                    "slide": idx,
                                    "fg": "#%02X%02X%02X" % fg,
                                    "bg": "#%02X%02X%02X" % bg,
                                    "ratio": round(ratio, 2),
                                })
                                return out
                except Exception:
                    continue
    return out


# ---------- main ----------


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pptx", required=True, type=Path)
    ap.add_argument("--spec", type=Path, default=None)
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()

    if not args.pptx.exists():
        print(f"ERROR: pptx not found: {args.pptx}", file=sys.stderr)
        return 1

    try:
        prs = Presentation(str(args.pptx))
    except Exception as e:
        print(f"ERROR: could not open pptx: {e}", file=sys.stderr)
        return 1

    sw = prs.slide_width or 0
    sh = prs.slide_height or 0
    ratio = (sw / sh) if sh else 0.0
    aspect_pass = abs(ratio - 16 / 9) < 0.01

    overflow_violations = []
    contrast_violations = []
    alignment_violations = []
    layout_hashes: list[tuple[int, str]] = []
    underline_slides: list[int] = []
    bg_sequence: list[str] = []
    speaker_notes_missing: list[int] = []
    titles: dict[str, list[int]] = {}
    body_word_violations: list[dict] = []

    slides = list(prs.slides)
    for idx, slide in enumerate(slides, start=1):
        # overflow
        ov = _overflow_estimate(slide, idx)
        if ov:
            overflow_violations.append(ov)
        # contrast (first violation per slide)
        cv = _contrast_violations_for(slide, idx)
        contrast_violations.extend(cv)
        # alignment
        alignment_violations.extend(_alignment_violations_for(slide, idx))
        # layout hash
        layout_hashes.append((idx, _layout_hash(slide)))
        # underline
        if _has_underline_below_title(slide):
            underline_slides.append(idx)
        # bg
        bg = _slide_bg_rgb(slide)
        bg_sequence.append(_bg_label(bg))
        # notes
        try:
            ns = slide.notes_slide
            ntxt = (ns.notes_text_frame.text or "").strip() if ns and ns.notes_text_frame else ""
            if not ntxt:
                speaker_notes_missing.append(idx)
        except Exception:
            speaker_notes_missing.append(idx)
        # titles
        title = _slide_title_text(slide)
        if title:
            titles.setdefault(title, []).append(idx)
        # body word count
        bwc = _body_word_count(slide)
        if bwc > 70:
            body_word_violations.append({"slide": idx, "body_words": bwc})

    # repeated layout hash on CONSECUTIVE slides
    repeated = []
    for i in range(1, len(layout_hashes)):
        if layout_hashes[i][1] == layout_hashes[i - 1][1]:
            repeated.append({"slides": [layout_hashes[i - 1][0], layout_hashes[i][0]], "hash": layout_hashes[i][1]})

    # max same-bg run
    max_run = 0
    cur_run = 0
    last = None
    for b in bg_sequence:
        if b == last and b != "unknown":
            cur_run += 1
        else:
            cur_run = 1
            last = b
        max_run = max(max_run, cur_run)

    duplicate_titles = [{"title": t, "slides": ids} for t, ids in titles.items() if len(ids) > 1]

    blocking = []
    if not aspect_pass:
        blocking.append("aspect_ratio")
    if overflow_violations:
        blocking.append("overflow")
    if contrast_violations:
        blocking.append("contrast")
    if len(underline_slides) > 2:
        blocking.append("title_underline_spam")
    if max_run >= 3:
        blocking.append("dark_light_run")
    if speaker_notes_missing:
        blocking.append("speaker_notes_missing")
    if duplicate_titles:
        blocking.append("duplicate_titles")
    if repeated:
        blocking.append("repeated_layout_hash")

    warnings = []
    if alignment_violations:
        warnings.append("alignment")
    if body_word_violations:
        warnings.append("body_word_max")

    report = {
        "session_id": None,
        "pptx_path": str(args.pptx),
        "spec_path": str(args.spec) if args.spec else None,
        "slide_count": len(slides),
        "aspect_ratio": round(ratio, 4),
        "aspect_ratio_pass": aspect_pass,
        "overflow_violations": overflow_violations,
        "contrast_violations": contrast_violations,
        "alignment_violations": alignment_violations,
        "repeated_layout_hash": repeated,
        "title_underline_count": len(underline_slides),
        "underline_slides": underline_slides,
        "max_same_bg_run": max_run,
        "background_sequence": bg_sequence,
        "speaker_notes_missing": speaker_notes_missing,
        "duplicate_titles": duplicate_titles,
        "body_word_max_violations": body_word_violations,
        "blocking_findings": blocking,
        "warning_findings": warnings,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2))
    status = "PASS" if not blocking else "FAIL"
    print(f"{status}: {len(blocking)} blocking, {len(warnings)} warning findings ({len(slides)} slides)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

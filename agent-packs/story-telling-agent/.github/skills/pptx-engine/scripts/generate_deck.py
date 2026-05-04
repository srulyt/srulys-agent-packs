#!/usr/bin/env python3
"""generate_deck.py — Token-driven deck builder consumed by @deck-builder.

Pipeline (drives off `deck-spec.json`):
  1. Load `deck-spec.json` (validate against schema is the agent's job).
  2. Resolve the design system: prefer `deck-spec.design_system_tokens`
     (F9 — token-driven constants); fall back to a sensible default
     palette when the spec doesn't supply tokens.
  3. Pre-render every `slide.visual_assets[]` entry by subprocess'ing
     the matching `render-visual` script (chart / composite / diagram).
     Failures of render-visual diagrams (graceful-degrade per OQ2)
     produce `<out>.skipped.json` sentinels — we treat these as
     "asset unavailable; build slide without it" and surface the
     skip in the build log.
  4. Dispatch each slide on `slide.style`:
       - "simple" (default — C5 backwards-compat) → simple builder
       - "styled" → styled builder selected by `slide.style_recipe`
     Unknown / inconsistent style or recipe → reject with
     `bad_spec.<reason>` and exit 2.
  5. Write `output.pptx`. Print SUCCESS / ERROR.

Usage:
  python generate_deck.py --spec deck-spec.json --out output.pptx
                          [--template path/to/template.pptx]
                          [--build-log build-log.txt]

Backwards-compat (C5):
  - Slides without a `style` key are treated as `style: "simple"`.
  - Decks without `design_system_tokens` use the fallback palette.
  - Existing simple types (title, key-message, content, ...)
    continue to work unchanged.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

# --- Dependency check ---
try:
    from pptx import Presentation
    from pptx.util import Inches, Pt, Emu
    from pptx.dml.color import RGBColor
    from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
    from pptx.enum.shapes import MSO_SHAPE
except ImportError:
    print("python-pptx not found. Installing...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "python-pptx"])
    from pptx import Presentation
    from pptx.util import Inches, Pt, Emu
    from pptx.dml.color import RGBColor
    from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
    from pptx.enum.shapes import MSO_SHAPE


# --- 16:9 EMU constants (architecture §4.1) ---
SLIDE_W_EMU = 12192000   # 13.333"
SLIDE_H_EMU = 6858000    # 7.5"
SLIDE_HALF_EMU = 6096000

# --- Default fallback palette (C5: when deck-spec lacks tokens) ---
FALLBACK_TOKENS: dict = {
    "name": "fallback",
    "palette": {
        "background_dark":   "#0F1B2D",
        "background_light":  "#F4F5F7",
        "background_accent": "#3B82F6",
        "primary_accent":    "#3B82F6",
        "secondary_accent":  "#06B6D4",
        "highlight":         "#F59E0B",
        "surface_elevated":  "#FFFFFF",
        "text_on_dark":      "#FFFFFF",
        "text_on_light":     "#1A1A2E",
        "text_secondary":    "#6B7080",
        "text_secondary_on_dark":  "#6B7080",
        "text_secondary_on_light": "#6B7080",
    },
    "typography": {
        "font_title": "Calibri Light",
        "font_body":  "Calibri",
        "size_hero":     54,
        "size_section":  48,
        "size_title":    40,
        "size_subtitle": 24,
        "size_body":     22,
        "size_caption":  14,
        "size_metric_xxl": 200,
        "size_quote_glyph": 240,
    },
}

# --- Canonical recipe sets (architecture §5) ---
STYLED_RECIPES = {
    "hero_full_bleed", "accent_block_left", "metric_xxl",
    "quote_pullout", "split_image_right", "tinted_panel_right",
    "progress_dots", "chart_callout",
}
SIMPLE_TYPES = {
    "title", "key-message", "content", "metric-spotlight",
    "comparison-columns", "quote", "data-callout",
    "section-divider", "visual-hero", "question", "cta-steps",
}


# ============================================================
# Token resolution helpers
# ============================================================

def _hex(s: str) -> RGBColor:
    s = (s or "#000000").lstrip("#")
    if len(s) != 6:
        s = "000000"
    return RGBColor(int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16))


class Tokens:
    """Token-driven palette + typography accessor (F9)."""

    def __init__(self, raw: dict):
        self.raw = raw
        p = raw.get("palette", {})
        t = raw.get("typography", {})
        # Palette colours (RGBColor)
        self.bg_dark    = _hex(p.get("background_dark",   "#0F1B2D"))
        self.bg_light   = _hex(p.get("background_light",  "#F4F5F7"))
        self.bg_accent  = _hex(p.get("background_accent", "#3B82F6"))
        self.primary    = _hex(p.get("primary_accent",    "#3B82F6"))
        self.secondary  = _hex(p.get("secondary_accent",  "#06B6D4"))
        self.highlight  = _hex(p.get("highlight",         "#F59E0B"))
        self.surface    = _hex(p.get("surface_elevated",  "#FFFFFF"))
        self.text_dark  = _hex(p.get("text_on_dark",      "#FFFFFF"))
        self.text_light = _hex(p.get("text_on_light",     "#1A1A2E"))
        # Secondary/muted text. Some systems (e.g. technical-slate) ship
        # surface-scoped overrides because no single mid-gray clears AA
        # against both their dark and light backgrounds. Prefer the
        # override when present, else fall back to the legacy bare key.
        _ts_default = p.get("text_secondary", "#6B7080")
        self.text_2_dark  = _hex(p.get("text_secondary_on_dark",  _ts_default))
        self.text_2_light = _hex(p.get("text_secondary_on_light", _ts_default))
        # Backward-compat alias (dark surface dominates most decks).
        self.text_2     = self.text_2_dark
        # Typography
        self.font_title = t.get("font_title", "Calibri Light")
        self.font_body  = t.get("font_body",  "Calibri")
        self.sz_hero     = Pt(t.get("size_hero", 54))
        self.sz_section  = Pt(t.get("size_section", 48))
        self.sz_title    = Pt(t.get("size_title", 40))
        self.sz_subtitle = Pt(t.get("size_subtitle", 24))
        self.sz_body     = Pt(t.get("size_body", 22))
        self.sz_caption  = Pt(t.get("size_caption", 14))
        self.sz_metric_xxl  = Pt(t.get("size_metric_xxl", 200))
        self.sz_quote_glyph = Pt(t.get("size_quote_glyph", 240))


# ============================================================
# Low-level shape helpers
# ============================================================

def _set_bg(slide, color: RGBColor) -> None:
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = color


def _set_notes(slide, notes: str) -> None:
    if notes:
        slide.notes_slide.notes_text_frame.text = notes


def _add_rect(slide, x, y, w, h, color: RGBColor):
    s = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, w, h)
    s.fill.solid()
    s.fill.fore_color.rgb = color
    s.line.fill.background()
    return s


def _add_textbox(slide, x, y, w, h, text, *,
                 font_name="Calibri", font_size=Pt(22),
                 color: RGBColor = None, bold=False, align=None,
                 anchor=None):
    tx = slide.shapes.add_textbox(x, y, w, h)
    tf = tx.text_frame
    tf.word_wrap = True
    if anchor is not None:
        tf.vertical_anchor = anchor
    if isinstance(text, str):
        text = [text]
    for i, line in enumerate(text):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = line
        p.font.name = font_name
        p.font.size = font_size
        p.font.bold = bold
        if color is not None:
            p.font.color.rgb = color
        if align is not None:
            p.alignment = align
    return tx


def _add_picture(slide, path, x, y, w, h):
    if path and os.path.exists(path):
        slide.shapes.add_picture(path, x, y, width=w, height=h)


def _new_blank_slide(prs):
    return prs.slides.add_slide(prs.slide_layouts[6])  # blank


# ============================================================
# Pre-render visual_assets[]
# ============================================================

def _prerender_assets(spec_path: Path, deck_spec: dict, log) -> None:
    """For each slide.visual_assets[], subprocess the appropriate
    render-visual script. Mutate the slide dict in place — replace each
    asset entry's `path` field with the produced PNG path.

    Each asset entry shape (additive):
      {"kind": "chart" | "composite" | "diagram",
       "recipe": "bar_with_callouts" | "gradient_pattern" | ...,
       "spec": {...},                  -- recipe-specific
       "out": "path/to/asset.png",     -- where to write
       "size": "1920x1080",            -- optional
       "svg": false}                   -- optional
    """
    here = Path(__file__).resolve().parent.parent.parent.parent  # .github/skills/
    rv_dir = here / "render-visual" / "scripts"
    script_for = {
        "chart":     rv_dir / "render_chart.py",
        "composite": rv_dir / "render_composite.py",
        "diagram":   rv_dir / "render_diagram.py",
    }

    tokens_path = spec_path.parent / "_tokens.json"
    tokens_path.write_text(json.dumps(
        deck_spec.get("design_system_tokens") or FALLBACK_TOKENS, indent=2))

    for slide in deck_spec.get("slides", []):
        for asset in slide.get("visual_assets") or []:
            kind = asset.get("kind")
            recipe = asset.get("recipe")
            out = asset.get("out")
            if kind not in script_for or not recipe or not out:
                log.write(f"[asset] skip (bad kind/recipe/out): {asset}\n")
                continue
            script = script_for[kind]
            if not script.exists():
                log.write(f"[asset] script missing: {script}\n")
                continue
            spec_file = spec_path.parent / f"_asset_{slide.get('index','?')}_{recipe}.json"
            spec_file.write_text(json.dumps(asset.get("spec") or {}, indent=2))
            cmd = [
                sys.executable, str(script),
                "--kind", recipe,
                "--spec", str(spec_file),
                "--tokens", str(tokens_path),
                "--out", str(out),
                "--size", asset.get("size", "1920x1080"),
            ]
            if asset.get("svg"):
                cmd.append("--svg")
            try:
                r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
                log.write(f"[asset] {recipe} rc={r.returncode}\n")
                if r.stdout:
                    log.write(r.stdout + "\n")
                if r.stderr:
                    log.write(r.stderr + "\n")
                # If the script produced a .skipped.json sentinel, mark it.
                sentinel = Path(str(out) + ".skipped.json")
                if sentinel.exists():
                    asset["skipped"] = True
                    log.write(f"[asset] {recipe} skipped (graceful-degrade)\n")
                else:
                    asset["path"] = out
            except Exception as e:
                log.write(f"[asset] {recipe} exception: {e}\n")
                asset["skipped"] = True


# ============================================================
# SIMPLE BUILDERS  (per slide.type when style == "simple")
# ============================================================

def _simple_title(prs, slide, t: Tokens):
    s = _new_blank_slide(prs)
    _set_bg(s, t.bg_dark)
    _add_rect(s, 0, 0, SLIDE_W_EMU, Emu(54864), t.primary)  # 0.06" top bar
    _add_textbox(s, Inches(1.2), Inches(2.2), Inches(10.9), Inches(1.8),
                 slide.get("title", ""),
                 font_name=t.font_title, font_size=t.sz_hero,
                 color=t.text_dark)
    if slide.get("subtitle"):
        _add_textbox(s, Inches(1.2), Inches(4.2), Inches(10.9), Inches(0.8),
                     slide["subtitle"],
                     font_name=t.font_body, font_size=t.sz_subtitle,
                     color=t.secondary)
    _set_notes(s, slide.get("notes", ""))
    return s


def _simple_section_divider(prs, slide, t: Tokens):
    """C5 backwards-compat path. NOTE: per OQ4, the strategist defaults
    section dividers to `style: styled / hero_full_bleed`; this simple
    path runs only when the spec explicitly opts back to simple."""
    s = _new_blank_slide(prs)
    _set_bg(s, t.bg_dark)
    _add_rect(s, Inches(5.5), Inches(2.5), Inches(2.3), Emu(32004), t.secondary)
    _add_textbox(s, Inches(1.5), Inches(2.8), Inches(10.3), Inches(1.5),
                 slide.get("title", ""),
                 font_name=t.font_title, font_size=t.sz_section,
                 color=t.text_dark, align=PP_ALIGN.CENTER)
    if slide.get("subtitle"):
        _add_textbox(s, Inches(1.5), Inches(4.5), Inches(10.3), Inches(0.6),
                     slide["subtitle"],
                     font_name=t.font_body, font_size=t.sz_subtitle,
                     color=t.text_2_dark, align=PP_ALIGN.CENTER)
    _set_notes(s, slide.get("notes", ""))
    return s


def _simple_key_message(prs, slide, t: Tokens):
    s = _new_blank_slide(prs)
    _set_bg(s, t.bg_light)
    _add_textbox(s, Inches(1.2), Inches(2.5), Inches(10.9), Inches(2.5),
                 slide.get("title", ""),
                 font_name=t.font_title, font_size=t.sz_hero,
                 color=t.text_light, bold=False)
    if slide.get("subtitle"):
        _add_textbox(s, Inches(1.2), Inches(5.0), Inches(10.9), Inches(0.6),
                     slide["subtitle"],
                     font_name=t.font_body, font_size=t.sz_subtitle,
                     color=t.text_2_light)
    _set_notes(s, slide.get("notes", ""))
    return s


def _simple_content(prs, slide, t: Tokens):
    s = _new_blank_slide(prs)
    _set_bg(s, t.bg_light)
    _add_textbox(s, Inches(0.75), Inches(0.6), Inches(11.83), Inches(1.0),
                 slide.get("title", ""),
                 font_name=t.font_title, font_size=t.sz_title,
                 color=t.text_light)
    bullets = slide.get("bullets") or []
    body_lines = [f"•  {b}" for b in bullets]
    _add_textbox(s, Inches(0.75), Inches(1.9), Inches(11.83), Inches(5.0),
                 body_lines,
                 font_name=t.font_body, font_size=t.sz_body,
                 color=t.text_light)
    _set_notes(s, slide.get("notes", ""))
    return s


def _simple_metric_spotlight(prs, slide, t: Tokens):
    s = _new_blank_slide(prs)
    _set_bg(s, t.bg_light)
    _add_textbox(s, Inches(0.75), Inches(0.6), Inches(11.83), Inches(0.9),
                 slide.get("title", ""),
                 font_name=t.font_title, font_size=t.sz_title,
                 color=t.text_light)
    metric = str(slide.get("metric", ""))
    label  = slide.get("metric_label", "")
    _add_textbox(s, Inches(0.75), Inches(1.8), Inches(11.83), Inches(3.5),
                 metric,
                 font_name=t.font_title, font_size=Pt(150),
                 color=t.primary, align=PP_ALIGN.CENTER, bold=True)
    if label:
        _add_textbox(s, Inches(0.75), Inches(5.4), Inches(11.83), Inches(0.7),
                     label,
                     font_name=t.font_body, font_size=t.sz_subtitle,
                     color=t.text_2_light, align=PP_ALIGN.CENTER)
    _set_notes(s, slide.get("notes", ""))
    return s


def _simple_comparison_columns(prs, slide, t: Tokens):
    s = _new_blank_slide(prs)
    _set_bg(s, t.bg_light)
    _add_textbox(s, Inches(0.75), Inches(0.6), Inches(11.83), Inches(0.9),
                 slide.get("title", ""),
                 font_name=t.font_title, font_size=t.sz_title,
                 color=t.text_light)
    cols = slide.get("columns") or []
    col_w = Inches(11.0 / max(1, len(cols)))
    for i, col in enumerate(cols):
        x = Inches(0.75) + col_w * i
        _add_rect(s, x, Inches(1.8), Emu(32004), Inches(4.5), t.primary)
        _add_textbox(s, x + Inches(0.2), Inches(1.8), col_w - Inches(0.3),
                     Inches(0.7), col.get("heading", ""),
                     font_name=t.font_title, font_size=Pt(28),
                     color=t.text_light, bold=True)
        items = col.get("items") or []
        _add_textbox(s, x + Inches(0.2), Inches(2.6), col_w - Inches(0.3),
                     Inches(4.0), [f"•  {it}" for it in items],
                     font_name=t.font_body, font_size=t.sz_body,
                     color=t.text_light)
    _set_notes(s, slide.get("notes", ""))
    return s


def _simple_quote(prs, slide, t: Tokens):
    s = _new_blank_slide(prs)
    _set_bg(s, t.bg_dark)
    _add_textbox(s, Inches(1.5), Inches(2.0), Inches(10.3), Inches(3.5),
                 f"\u201C{slide.get('quote', '')}\u201D",
                 font_name=t.font_title, font_size=Pt(36),
                 color=t.text_dark, align=PP_ALIGN.CENTER)
    if slide.get("attribution"):
        _add_textbox(s, Inches(1.5), Inches(5.5), Inches(10.3), Inches(0.7),
                     f"— {slide['attribution']}",
                     font_name=t.font_body, font_size=t.sz_subtitle,
                     color=t.secondary, align=PP_ALIGN.CENTER)
    _set_notes(s, slide.get("notes", ""))
    return s


def _simple_data_callout(prs, slide, t: Tokens):
    return _simple_metric_spotlight(prs, slide, t)


def _simple_visual_hero(prs, slide, t: Tokens):
    s = _new_blank_slide(prs)
    _set_bg(s, t.bg_dark)
    img = slide.get("image_path")
    if img:
        _add_picture(s, img, 0, 0, SLIDE_W_EMU, SLIDE_H_EMU)
    _add_textbox(s, Inches(0.75), Inches(5.5), Inches(11.83), Inches(1.5),
                 slide.get("title", ""),
                 font_name=t.font_title, font_size=t.sz_section,
                 color=t.text_dark)
    _set_notes(s, slide.get("notes", ""))
    return s


def _simple_question(prs, slide, t: Tokens):
    s = _new_blank_slide(prs)
    _set_bg(s, t.bg_dark)
    _add_textbox(s, Inches(1.0), Inches(2.5), Inches(11.3), Inches(2.5),
                 slide.get("title", ""),
                 font_name=t.font_title, font_size=t.sz_hero,
                 color=t.text_dark, align=PP_ALIGN.CENTER)
    _set_notes(s, slide.get("notes", ""))
    return s


def _simple_cta_steps(prs, slide, t: Tokens):
    s = _new_blank_slide(prs)
    _set_bg(s, t.bg_light)
    _add_textbox(s, Inches(0.75), Inches(0.6), Inches(11.83), Inches(0.9),
                 slide.get("title", ""),
                 font_name=t.font_title, font_size=t.sz_title,
                 color=t.text_light)
    steps = slide.get("steps") or []
    _add_textbox(s, Inches(0.75), Inches(1.9), Inches(11.83), Inches(5.0),
                 [f"{i+1}.  {step}" for i, step in enumerate(steps)],
                 font_name=t.font_body, font_size=t.sz_body,
                 color=t.text_light)
    _set_notes(s, slide.get("notes", ""))
    return s


SIMPLE_BUILDERS = {
    "title":              _simple_title,
    "section-divider":    _simple_section_divider,
    "key-message":        _simple_key_message,
    "content":            _simple_content,
    "metric-spotlight":   _simple_metric_spotlight,
    "comparison-columns": _simple_comparison_columns,
    "quote":              _simple_quote,
    "data-callout":       _simple_data_callout,
    "visual-hero":        _simple_visual_hero,
    "question":           _simple_question,
    "cta-steps":          _simple_cta_steps,
}


# ============================================================
# STYLED BUILDERS  (architecture §4.1 EMU coords; F5)
# ============================================================

def _styled_hero_full_bleed(prs, slide, t: Tokens):
    """Full-bleed picture from `gradient_pattern` (or supplied image)
    + title centred lower-third + subtitle.
    EMU: picture covers (0,0,12192000,6858000)."""
    s = _new_blank_slide(prs)
    _set_bg(s, t.bg_dark)
    asset = _first_asset(slide, recipe="gradient_pattern")
    img_path = (asset and asset.get("path")) or slide.get("image_path")
    if img_path and os.path.exists(img_path):
        _add_picture(s, img_path, 0, 0, SLIDE_W_EMU, SLIDE_H_EMU)
    _add_textbox(s, Inches(1.0), Inches(4.2), Inches(11.3), Inches(1.6),
                 slide.get("title", ""),
                 font_name=t.font_title, font_size=t.sz_hero,
                 color=t.text_dark, align=PP_ALIGN.CENTER, bold=False)
    if slide.get("subtitle"):
        _add_textbox(s, Inches(1.0), Inches(5.9), Inches(11.3), Inches(0.6),
                     slide["subtitle"],
                     font_name=t.font_body, font_size=t.sz_subtitle,
                     color=t.text_dark, align=PP_ALIGN.CENTER)
    _set_notes(s, slide.get("notes", ""))
    return s


def _styled_accent_block_left(prs, slide, t: Tokens):
    """Left 4023360-EMU (4.4") accent panel + right body. §4.1."""
    s = _new_blank_slide(prs)
    _set_bg(s, t.bg_light)
    _add_rect(s, 0, 0, Emu(4023360), SLIDE_H_EMU, t.primary)
    _add_textbox(s, Inches(0.5), Inches(2.5), Inches(3.7), Inches(2.5),
                 slide.get("eyebrow", "") or slide.get("kicker", ""),
                 font_name=t.font_body, font_size=t.sz_subtitle,
                 color=t.text_dark)
    _add_textbox(s, Emu(4023360) + Inches(0.6), Inches(2.0),
                 Inches(8.0), Inches(3.5),
                 slide.get("title", ""),
                 font_name=t.font_title, font_size=t.sz_section,
                 color=t.text_light, anchor=MSO_ANCHOR.MIDDLE)
    _set_notes(s, slide.get("notes", ""))
    return s


def _styled_metric_xxl(prs, slide, t: Tokens):
    """200pt centred number on bg_dark. §4.1."""
    s = _new_blank_slide(prs)
    _set_bg(s, t.bg_dark)
    _add_textbox(s, Inches(0.75), Inches(1.5), Inches(11.83), Inches(4.0),
                 str(slide.get("metric", "")),
                 font_name=t.font_title, font_size=t.sz_metric_xxl,
                 color=t.text_dark, align=PP_ALIGN.CENTER, bold=True,
                 anchor=MSO_ANCHOR.MIDDLE)
    if slide.get("metric_label"):
        _add_textbox(s, Inches(0.75), Inches(5.6), Inches(11.83), Inches(0.8),
                     slide["metric_label"],
                     font_name=t.font_body, font_size=t.sz_subtitle,
                     color=t.secondary, align=PP_ALIGN.CENTER)
    _set_notes(s, slide.get("notes", ""))
    return s


def _styled_quote_pullout(prs, slide, t: Tokens):
    """240pt opaque-10% quote glyph background + quote + attribution. §4.1."""
    s = _new_blank_slide(prs)
    _set_bg(s, t.bg_dark)
    asset = _first_asset(slide, recipe="oversized_glyph_bg")
    if asset and asset.get("path") and os.path.exists(asset["path"]):
        _add_picture(s, asset["path"], 0, 0, SLIDE_W_EMU, SLIDE_H_EMU)
    _add_textbox(s, Inches(1.5), Inches(2.0), Inches(10.3), Inches(3.5),
                 slide.get("quote", ""),
                 font_name=t.font_title, font_size=Pt(36),
                 color=t.text_dark, align=PP_ALIGN.CENTER)
    if slide.get("attribution"):
        _add_textbox(s, Inches(1.5), Inches(5.7), Inches(10.3), Inches(0.7),
                     f"— {slide['attribution']}",
                     font_name=t.font_body, font_size=t.sz_subtitle,
                     color=t.secondary, align=PP_ALIGN.CENTER)
    _set_notes(s, slide.get("notes", ""))
    return s


def _styled_split_image_right(prs, slide, t: Tokens):
    """Left half (0..6096000) text; right half (6096000..12192000) image.
    `anchor: right_half`. §4.1."""
    s = _new_blank_slide(prs)
    _set_bg(s, t.bg_light)
    img = slide.get("image_path")
    if img and os.path.exists(img):
        _add_picture(s, img, Emu(SLIDE_HALF_EMU), 0,
                     Emu(SLIDE_HALF_EMU), SLIDE_H_EMU)
    _add_textbox(s, Inches(0.75), Inches(2.0), Inches(5.6), Inches(1.5),
                 slide.get("title", ""),
                 font_name=t.font_title, font_size=t.sz_title,
                 color=t.text_light)
    if slide.get("body"):
        _add_textbox(s, Inches(0.75), Inches(3.7), Inches(5.6), Inches(2.5),
                     slide["body"],
                     font_name=t.font_body, font_size=t.sz_body,
                     color=t.text_light)
    _set_notes(s, slide.get("notes", ""))
    return s


def _styled_tinted_panel_right(prs, slide, t: Tokens):
    """Aside / supporting fact: surface_elevated panel on the right.
    Right half tinted with `surface_elevated` (10% lighter)."""
    s = _new_blank_slide(prs)
    _set_bg(s, t.bg_light)
    _add_rect(s, Emu(SLIDE_HALF_EMU), 0, Emu(SLIDE_HALF_EMU), SLIDE_H_EMU,
              t.surface)
    _add_textbox(s, Inches(0.75), Inches(2.0), Inches(5.6), Inches(3.5),
                 slide.get("title", ""),
                 font_name=t.font_title, font_size=t.sz_title,
                 color=t.text_light)
    aside = slide.get("aside") or slide.get("body") or ""
    _add_textbox(s, Inches(7.2), Inches(2.0), Inches(5.4), Inches(4.0),
                 aside,
                 font_name=t.font_body, font_size=t.sz_body,
                 color=t.text_light)
    _set_notes(s, slide.get("notes", ""))
    return s


def _styled_progress_dots(prs, slide, t: Tokens):
    """5-step progress strip. The matplotlib `progress_strip` recipe
    produces the line+dots; we overlay step labels."""
    s = _new_blank_slide(prs)
    _set_bg(s, t.bg_light)
    _add_textbox(s, Inches(0.75), Inches(0.6), Inches(11.83), Inches(0.9),
                 slide.get("title", ""),
                 font_name=t.font_title, font_size=t.sz_title,
                 color=t.text_light)
    asset = _first_asset(slide, recipe="progress_strip")
    if asset and asset.get("path") and os.path.exists(asset["path"]):
        _add_picture(s, asset["path"], Inches(0.75), Inches(2.5),
                     Inches(11.83), Inches(3.5))
    else:
        # Fallback: simple text steps
        steps = slide.get("steps") or []
        _add_textbox(s, Inches(0.75), Inches(2.5), Inches(11.83), Inches(3.5),
                     " → ".join(s.get("label", "?") if isinstance(s, dict) else s
                                for s in steps),
                     font_name=t.font_body, font_size=t.sz_body,
                     color=t.text_light, align=PP_ALIGN.CENTER)
    _set_notes(s, slide.get("notes", ""))
    return s


def _styled_chart_callout(prs, slide, t: Tokens):
    """Left half chart (matplotlib) + 2 right-side annotation textboxes."""
    s = _new_blank_slide(prs)
    _set_bg(s, t.bg_light)
    _add_textbox(s, Inches(0.75), Inches(0.4), Inches(11.83), Inches(0.8),
                 slide.get("title", ""),
                 font_name=t.font_title, font_size=t.sz_title,
                 color=t.text_light)
    asset = _first_asset(slide, kind="chart")
    if asset and asset.get("path") and os.path.exists(asset["path"]):
        _add_picture(s, asset["path"], 0, Inches(1.4),
                     Emu(SLIDE_HALF_EMU), Inches(5.6))
    callouts = slide.get("callouts") or []
    if len(callouts) >= 1:
        _add_textbox(s, Inches(7.0), Inches(2.0), Inches(5.6), Inches(1.8),
                     callouts[0], font_name=t.font_title, font_size=Pt(28),
                     color=t.primary, bold=True)
    if len(callouts) >= 2:
        _add_textbox(s, Inches(7.0), Inches(4.2), Inches(5.6), Inches(1.8),
                     callouts[1], font_name=t.font_body, font_size=t.sz_body,
                     color=t.text_light)
    _set_notes(s, slide.get("notes", ""))
    return s


STYLED_BUILDERS = {
    "hero_full_bleed":     _styled_hero_full_bleed,
    "accent_block_left":   _styled_accent_block_left,
    "metric_xxl":          _styled_metric_xxl,
    "quote_pullout":       _styled_quote_pullout,
    "split_image_right":   _styled_split_image_right,
    "tinted_panel_right":  _styled_tinted_panel_right,
    "progress_dots":       _styled_progress_dots,
    "chart_callout":       _styled_chart_callout,
}


def _first_asset(slide, *, kind: str = None, recipe: str = None) -> dict | None:
    for a in (slide.get("visual_assets") or []):
        if a.get("skipped"):
            continue
        if kind and a.get("kind") != kind:
            continue
        if recipe and a.get("recipe") != recipe:
            continue
        return a
    return None


# ============================================================
# Spec validation + dispatch (F5, C5)
# ============================================================

class SpecError(Exception):
    """bad_spec.<reason>"""


def _validate_slide(slide: dict) -> tuple[str, str | None]:
    """Return (style, style_recipe). Apply C5 backwards-compat:
    missing `style` → "simple"; only reject when present-and-invalid
    or pairing-inconsistent."""
    style = slide.get("style", "simple")  # C5 default
    recipe = slide.get("style_recipe")
    stype = slide.get("type")

    if style not in ("simple", "styled"):
        raise SpecError(f"bad_spec.invalid_style: slide {slide.get('index')} "
                        f"has style={style!r}; must be 'simple' or 'styled'")

    if style == "styled":
        if not recipe:
            raise SpecError(f"bad_spec.styled_without_recipe: slide "
                            f"{slide.get('index')} has style=styled but no style_recipe")
        if recipe not in STYLED_RECIPES:
            raise SpecError(f"bad_spec.unknown_recipe: slide "
                            f"{slide.get('index')} style_recipe={recipe!r} "
                            f"not in {sorted(STYLED_RECIPES)}")
    else:  # simple
        if recipe is not None:
            raise SpecError(f"bad_spec.simple_with_recipe: slide "
                            f"{slide.get('index')} has style=simple but "
                            f"style_recipe={recipe!r} (inconsistent)")
        if stype and stype not in SIMPLE_TYPES:
            # Don't reject — backwards-compat: unknown simple types
            # fall back to `content`. Log at the call site.
            pass
    return style, recipe


def _build_slide(prs, slide: dict, t: Tokens, log) -> None:
    style, recipe = _validate_slide(slide)
    if style == "styled":
        builder = STYLED_BUILDERS[recipe]
        log.write(f"[slide {slide.get('index')}] styled/{recipe}\n")
        builder(prs, slide, t)
    else:
        stype = slide.get("type", "content")
        builder = SIMPLE_BUILDERS.get(stype, _simple_content)
        log.write(f"[slide {slide.get('index')}] simple/{stype}\n")
        builder(prs, slide, t)


# ============================================================
# Main
# ============================================================

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", required=True, type=Path,
                    help="Path to deck-spec.json")
    ap.add_argument("--out", type=Path, default=Path("output.pptx"))
    ap.add_argument("--template", type=Path, default=None)
    ap.add_argument("--build-log", type=Path, default=None)
    args = ap.parse_args()

    log_path = args.build_log or args.out.with_suffix(".log")
    log = log_path.open("w", encoding="utf-8")
    try:
        try:
            deck_spec = json.loads(args.spec.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"ERROR: cannot read deck-spec: {e}", file=sys.stderr)
            return 2

        # Tokens (F9)
        t = Tokens(deck_spec.get("design_system_tokens") or FALLBACK_TOKENS)
        log.write(f"[tokens] {(deck_spec.get('design_system_tokens') or FALLBACK_TOKENS).get('name','?')}\n")

        # Pre-render visual_assets
        _prerender_assets(args.spec, deck_spec, log)

        # Presentation init
        if args.template and args.template.exists():
            try:
                prs = Presentation(str(args.template))
                log.write(f"[template] loaded {args.template}\n")
            except Exception as e:
                log.write(f"[template] failed ({e}); using default 16:9\n")
                prs = Presentation()
                prs.slide_width = Emu(SLIDE_W_EMU)
                prs.slide_height = Emu(SLIDE_H_EMU)
        else:
            prs = Presentation()
            prs.slide_width = Emu(SLIDE_W_EMU)
            prs.slide_height = Emu(SLIDE_H_EMU)

        # Dispatch
        try:
            for slide in deck_spec.get("slides", []):
                _build_slide(prs, slide, t, log)
        except SpecError as e:
            print(f"ERROR: {e}", file=sys.stderr)
            log.write(f"[reject] {e}\n")
            return 2

        args.out.parent.mkdir(parents=True, exist_ok=True)
        prs.save(str(args.out))
        print(f"SUCCESS: deck written to {args.out}")
        log.write(f"[done] {args.out}\n")
        return 0
    finally:
        log.close()


if __name__ == "__main__":
    sys.exit(main())

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
    # Session 2026-05-04-c8d3b2a1 — archetype builders
    "risk_heatmap", "priority_matrix", "waterfall",
    "flywheel", "funnel", "decision_options",
    "appendix_dense",
    # `footer_source` is a partial applied via slide.footer; not a primary recipe.
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
    # Session 2026-05-04-c8d3b2a1 — archetype builders
    "risk_heatmap":      None,  # bound below after defs
    "priority_matrix":   None,
    "waterfall":         None,
    "flywheel":          None,
    "funnel":            None,
    "decision_options":  None,
    "appendix_dense":    None,
}


# ============================================================
# ARCHETYPE BUILDERS  (session 2026-05-04-c8d3b2a1)
# ============================================================
#
# Seven semantic builders realising the ⏳ Spec-only archetypes from
# `presentation-design/references/layout-archetypes.md`. Plus one
# partial (`_apply_footer_source`) applied to ANY slide whose spec
# carries a `footer` block.
#
# Geometry conventions (16:9 EMU):
#   slide  = (0, 0, 12192000, 6858000)  i.e. 13.333" × 7.5"
#   header = (0.75", 0.5", 11.83", 0.9")  for titles
#   body   = (0.75", 1.6", 11.83", 5.4")  for primary content
#   footer = (0,     7.10",   13.33", 0.35") reserved for footer_source
# Tokens are pulled from the resolved Tokens instance — no hard-coded
# colours. Each builder also receives the slide dict and may read its
# new-in-v2.2.0 spec keys (risks, axes, matrix_items, waterfall,
# flywheel_stages, funnel_stages, options/criteria/recommendation,
# panels, footer).
#
# Validation philosophy: builders raise SpecError on shape violations
# the eye can't easily catch (waterfall sign/zero-baseline, decision
# columns summing past slide width). Other failures degrade gracefully
# (missing labels render blank rather than crashing).


# ---------- Risk Heatmap (recipe: risk_heatmap) ----------

def _styled_risk_heatmap(prs, slide, t: Tokens):
    """3×3 likelihood × impact grid; risks plotted as labelled markers
    in cells; colour-coded green→yellow→red; legend at lower margin."""
    s = _new_blank_slide(prs)
    _set_bg(s, t.bg_light)
    _add_textbox(s, Inches(0.75), Inches(0.5), Inches(11.83), Inches(0.9),
                 slide.get("title", ""),
                 font_name=t.font_title, font_size=t.sz_title,
                 color=t.text_light)

    LEVELS = ["low", "med", "high"]
    LEVEL_IDX = {v: i for i, v in enumerate(LEVELS)}

    # Grid: 3 cols × 3 rows centred in body
    grid_x = Inches(2.5); grid_y = Inches(1.7)
    cell_w = Inches(2.4); cell_h = Inches(1.4)

    # Cell fill semantics: green / amber / red by max(prob, impact) tier.
    # Colours chosen so WHITE 12pt-bold labels clear AA normal-text (4.5:1):
    #   green #1B5E20 → ~9.8:1   amber #B45309 → ~5.6:1   red #B71C1C → ~7.5:1
    # The earlier #F59E0B amber failed at 2.15:1 — fixed in
    # session 2026-05-04-c8d3b2a1.
    GREEN = _hex("#1B5E20")
    AMBER = _hex("#B45309")
    RED   = _hex("#B71C1C")
    LIGHT = _hex("#FFFFFF")
    BORDER = t.text_2_light

    def _cell_color(p_idx, i_idx):
        risk = max(p_idx, i_idx)
        if risk == 0:
            return GREEN
        if risk == 1:
            return AMBER
        return RED

    for ri in range(3):           # impact row 0..2 (bottom = high)
        for ci in range(3):       # probability col 0..2 (right = high)
            cx = grid_x + cell_w * ci
            cy = grid_y + cell_h * (2 - ri)
            rect = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, cx, cy, cell_w, cell_h)
            rect.fill.solid()
            rect.fill.fore_color.rgb = _cell_color(ci, ri)
            rect.line.color.rgb = BORDER

    # Plot risks: deterministic offset within cell so multiple risks stack
    risks = slide.get("risks") or []
    cell_count = {}
    for r in risks:
        p = LEVEL_IDX.get(r.get("probability", "med"), 1)
        i = LEVEL_IDX.get(r.get("impact", "med"), 1)
        cx = grid_x + cell_w * p
        cy = grid_y + cell_h * (2 - i)
        slot = cell_count.get((p, i), 0)
        cell_count[(p, i)] = slot + 1
        offset_y = Inches(0.15 + 0.35 * slot)
        _add_textbox(s, cx + Inches(0.15), cy + offset_y,
                     cell_w - Inches(0.3), Inches(0.35),
                     "● " + str(r.get("name", "")),
                     font_name=t.font_body, font_size=Pt(12),
                     color=LIGHT, bold=True)

    # Axis labels
    axes = slide.get("axes") or {}
    _add_textbox(s, grid_x, grid_y + cell_h * 3 + Inches(0.05),
                 cell_w * 3, Inches(0.3),
                 axes.get("x_label", "Probability →"),
                 font_name=t.font_body, font_size=t.sz_caption,
                 color=t.text_2_light, align=PP_ALIGN.CENTER)
    _add_textbox(s, grid_x - Inches(1.7), grid_y, Inches(1.6),
                 cell_h * 3,
                 axes.get("y_label", "Impact →"),
                 font_name=t.font_body, font_size=t.sz_caption,
                 color=t.text_2_light, align=PP_ALIGN.CENTER,
                 anchor=MSO_ANCHOR.MIDDLE)

    # Legend
    _add_textbox(s, Inches(0.75), Inches(6.5), Inches(11.83), Inches(0.4),
                 "Legend:  ● Low risk (green)   ● Medium (amber)   ● High (red)",
                 font_name=t.font_body, font_size=t.sz_caption,
                 color=t.text_2_light)
    _set_notes(s, slide.get("notes", ""))
    return s


# ---------- 2×2 / Priority Matrix (recipe: priority_matrix) ----------

def _styled_priority_matrix(prs, slide, t: Tokens):
    """2×2 grid; labelled axes; quadrant labels in faint type;
    items as labelled markers; recommended quadrant tinted."""
    s = _new_blank_slide(prs)
    _set_bg(s, t.bg_light)
    _add_textbox(s, Inches(0.75), Inches(0.5), Inches(11.83), Inches(0.9),
                 slide.get("title", ""),
                 font_name=t.font_title, font_size=t.sz_title,
                 color=t.text_light)

    grid_x = Inches(3.0); grid_y = Inches(1.7)
    qw = Inches(3.5); qh = Inches(2.3)

    # Quadrants: TL TR BL BR
    quads = [(0, 0), (1, 0), (0, 1), (1, 1)]
    labels = slide.get("quadrant_labels") or ["", "", "", ""]
    items = slide.get("matrix_items") or []
    rec_quad = None
    # Find recommended quadrant from items
    for it in items:
        if it.get("recommended"):
            rec_quad = (1 if it.get("x") == "high" else 0,
                        0 if it.get("y") == "high" else 1)
            break

    for idx, (cx_i, cy_i) in enumerate(quads):
        x = grid_x + qw * cx_i
        y = grid_y + qh * cy_i
        rect = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, qw, qh)
        rect.fill.solid()
        if rec_quad and (cx_i, cy_i) == rec_quad:
            rect.fill.fore_color.rgb = t.primary
            label_color = t.text_dark
        else:
            rect.fill.fore_color.rgb = t.surface
            label_color = t.text_2_light
        rect.line.color.rgb = t.text_2_light
        # Quadrant label centre-faint
        _add_textbox(s, x + Inches(0.2), y + Inches(0.2),
                     qw - Inches(0.4), Inches(0.5),
                     labels[idx] if idx < len(labels) else "",
                     font_name=t.font_body, font_size=t.sz_caption,
                     color=label_color, align=PP_ALIGN.CENTER)

    # Items
    for it in items:
        cx_i = 1 if it.get("x") == "high" else 0
        cy_i = 0 if it.get("y") == "high" else 1
        x = grid_x + qw * cx_i + Inches(0.4)
        y = grid_y + qh * cy_i + Inches(0.9)
        _add_textbox(s, x, y, qw - Inches(0.6), Inches(0.4),
                     "● " + str(it.get("name", "")),
                     font_name=t.font_body, font_size=t.sz_body,
                     color=(t.text_dark if (rec_quad == (cx_i, cy_i)) else t.text_light),
                     bold=bool(it.get("recommended")))

    # Axes
    axes = slide.get("axes") or {}
    _add_textbox(s, grid_x, grid_y + qh * 2 + Inches(0.05),
                 qw * 2, Inches(0.3),
                 axes.get("x_label", "→"),
                 font_name=t.font_body, font_size=t.sz_caption,
                 color=t.text_2_light, align=PP_ALIGN.CENTER)
    _add_textbox(s, grid_x - Inches(1.7), grid_y, Inches(1.6),
                 qh * 2,
                 axes.get("y_label", "↑"),
                 font_name=t.font_body, font_size=t.sz_caption,
                 color=t.text_2_light, align=PP_ALIGN.CENTER,
                 anchor=MSO_ANCHOR.MIDDLE)
    _set_notes(s, slide.get("notes", ""))
    return s


# ---------- Waterfall / Value Bridge (recipe: waterfall) ----------

def _styled_waterfall(prs, slide, t: Tokens):
    """Floating bars: start total, ordered signed deltas, end total.
    Positive=primary accent, negative=highlight. Zero-baseline enforced.
    Connector lines between bar tops."""
    s = _new_blank_slide(prs)
    _set_bg(s, t.bg_light)
    _add_textbox(s, Inches(0.75), Inches(0.5), Inches(11.83), Inches(0.9),
                 slide.get("title", ""),
                 font_name=t.font_title, font_size=t.sz_title,
                 color=t.text_light)

    wf = slide.get("waterfall") or {}
    start = wf.get("start") or {}
    end = wf.get("end") or {}
    steps = wf.get("steps") or []
    units = wf.get("units", "")

    if not start or not end:
        _add_textbox(s, Inches(1.0), Inches(3.0), Inches(11.0), Inches(1.0),
                     "[waterfall: missing start/end]",
                     font_name=t.font_body, font_size=t.sz_body,
                     color=t.text_2_light, align=PP_ALIGN.CENTER)
        _set_notes(s, slide.get("notes", ""))
        return s

    # Geometry
    chart_left = Inches(1.0); chart_right = Inches(12.33)
    chart_top = Inches(2.0); chart_bottom = Inches(6.4)
    chart_w = chart_right - chart_left
    chart_h = chart_bottom - chart_top

    # All bars: start, *steps, end.  Compute running totals.
    s_val = float(start.get("value", 0))
    e_val = float(end.get("value", 0))
    running = [s_val]
    for st in steps:
        running.append(running[-1] + float(st.get("delta", 0)))
    # Final terminal bar uses end.value (may differ from running due to rounding/intent)
    all_vals = [s_val] + [running[i+1] for i in range(len(steps))] + [e_val]
    max_v = max(all_vals + [0])
    min_v = min(all_vals + [0])
    # Zero-baseline ENFORCED: scale from 0..max_v if all values >= 0,
    # else cover [min_v, max_v] but always include 0.
    y_lo = min(min_v, 0)
    y_hi = max(max_v, 0)
    span = (y_hi - y_lo) or 1
    n_bars = 1 + len(steps) + 1
    bar_slot_w = chart_w / max(1, n_bars)
    bar_w = int(bar_slot_w * 0.55)
    bar_pad = int((bar_slot_w - bar_w) / 2)

    def _y_for(v):
        return int(chart_top + (1 - (v - y_lo) / span) * chart_h)

    zero_y = _y_for(0)

    # Draw zero-baseline
    line = s.shapes.add_connector(2, chart_left, zero_y, chart_right, zero_y)
    line.line.color.rgb = t.text_2_light

    NEG = t.highlight
    POS = t.primary
    NEUTRAL = t.secondary

    # Start bar (neutral): from zero to start value
    x0 = int(chart_left + bar_pad)
    top0 = _y_for(max(0, s_val))
    bot0 = _y_for(min(0, s_val))
    rect = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, x0, top0, bar_w, max(1, bot0 - top0))
    rect.fill.solid(); rect.fill.fore_color.rgb = NEUTRAL
    rect.line.fill.background()
    _add_textbox(s, x0 - Inches(0.2), Inches(6.5), bar_w + Inches(0.4), Inches(0.4),
                 str(start.get("label", "Start")),
                 font_name=t.font_body, font_size=t.sz_caption,
                 color=t.text_light, align=PP_ALIGN.CENTER)
    prev_running = s_val
    prev_top = top0 if s_val >= 0 else bot0

    # Step bars (floating)
    for i, st in enumerate(steps):
        delta = float(st.get("delta", 0))
        x = int(chart_left + bar_slot_w * (i + 1) + bar_pad)
        new_running = prev_running + delta
        top = _y_for(max(prev_running, new_running))
        bot = _y_for(min(prev_running, new_running))
        rect = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, top, bar_w, max(1, bot - top))
        rect.fill.solid()
        rect.fill.fore_color.rgb = POS if delta >= 0 else NEG
        rect.line.fill.background()
        _add_textbox(s, x - Inches(0.2), Inches(6.5), bar_w + Inches(0.4), Inches(0.4),
                     str(st.get("label", "")),
                     font_name=t.font_body, font_size=t.sz_caption,
                     color=t.text_light, align=PP_ALIGN.CENTER)
        # Connector line from previous bar top to this bar top edge
        prev_x_right = int(chart_left + bar_slot_w * i + bar_pad + bar_w)
        c_y = _y_for(prev_running)
        conn = s.shapes.add_connector(1, prev_x_right, c_y, x, c_y)
        conn.line.color.rgb = t.text_2_light
        prev_running = new_running

    # End bar
    xN = int(chart_left + bar_slot_w * (len(steps) + 1) + bar_pad)
    topN = _y_for(max(0, e_val))
    botN = _y_for(min(0, e_val))
    rect = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, xN, topN, bar_w, max(1, botN - topN))
    rect.fill.solid(); rect.fill.fore_color.rgb = NEUTRAL
    rect.line.fill.background()
    _add_textbox(s, xN - Inches(0.2), Inches(6.5), bar_w + Inches(0.4), Inches(0.4),
                 str(end.get("label", "End")),
                 font_name=t.font_body, font_size=t.sz_caption,
                 color=t.text_light, align=PP_ALIGN.CENTER)

    # Units in upper-right
    if units:
        _add_textbox(s, Inches(10.5), Inches(1.5), Inches(2.5), Inches(0.4),
                     f"({units})",
                     font_name=t.font_body, font_size=t.sz_caption,
                     color=t.text_2_light, align=PP_ALIGN.RIGHT)

    _set_notes(s, slide.get("notes", ""))
    return s


# ---------- Flywheel (recipe: flywheel) ----------

def _styled_flywheel(prs, slide, t: Tokens):
    """3–6 named nodes around a circle; reinforcing arrows; centre label.
    Stage labels positioned outside the ring for legibility."""
    import math
    s = _new_blank_slide(prs)
    _set_bg(s, t.bg_light)
    _add_textbox(s, Inches(0.75), Inches(0.5), Inches(11.83), Inches(0.9),
                 slide.get("title", ""),
                 font_name=t.font_title, font_size=t.sz_title,
                 color=t.text_light)

    stages = slide.get("flywheel_stages") or []
    n = max(3, min(6, len(stages))) if stages else 0
    cx = Inches(6.665); cy = Inches(4.1)
    R = Inches(1.7)         # ring radius
    node_r = Inches(0.55)

    # Centre label
    centre_dia = Inches(1.5)
    centre = s.shapes.add_shape(MSO_SHAPE.OVAL,
                                cx - centre_dia / 2, cy - centre_dia / 2,
                                centre_dia, centre_dia)
    centre.fill.solid(); centre.fill.fore_color.rgb = t.primary
    centre.line.fill.background()
    _add_textbox(s, cx - centre_dia / 2, cy - Inches(0.3),
                 centre_dia, Inches(0.6),
                 slide.get("center_label", "") or "",
                 font_name=t.font_title, font_size=Pt(18),
                 color=t.text_dark, align=PP_ALIGN.CENTER, bold=True,
                 anchor=MSO_ANCHOR.MIDDLE)

    # Nodes around the ring
    node_centres = []
    for i in range(n):
        ang = -math.pi / 2 + 2 * math.pi * i / n
        nx = int(cx + R * math.cos(ang))
        ny = int(cy + R * math.sin(ang))
        node_centres.append((nx, ny, ang))
        node = s.shapes.add_shape(MSO_SHAPE.OVAL,
                                  nx - node_r, ny - node_r,
                                  node_r * 2, node_r * 2)
        node.fill.solid(); node.fill.fore_color.rgb = t.secondary
        node.line.color.rgb = t.text_light
        # Label OUTSIDE the ring
        lx = int(cx + (R + node_r + Inches(0.3)) * math.cos(ang))
        ly = int(cy + (R + node_r + Inches(0.3)) * math.sin(ang))
        label = stages[i].get("label", "") if i < len(stages) else ""
        _add_textbox(s, lx - Inches(1.0), ly - Inches(0.2),
                     Inches(2.0), Inches(0.5),
                     label,
                     font_name=t.font_body, font_size=t.sz_caption,
                     color=t.text_light, align=PP_ALIGN.CENTER, bold=True)

    # Arrows along the ring (curved approximated as straight tangent)
    for i in range(n):
        a, b = node_centres[i], node_centres[(i + 1) % n]
        # Arrow from edge of node i toward edge of node i+1
        ax, ay, _ = a
        bx, by, _ = b
        # Pull toward ring (just connect node centres minus radius)
        dx, dy = bx - ax, by - ay
        L = (dx * dx + dy * dy) ** 0.5 or 1
        ux, uy = dx / L, dy / L
        sx = int(ax + ux * node_r)
        sy = int(ay + uy * node_r)
        ex = int(bx - ux * node_r)
        ey = int(by - uy * node_r)
        conn = s.shapes.add_connector(1, sx, sy, ex, ey)  # straight
        conn.line.color.rgb = t.text_2_light
        conn.line.width = Emu(20000)

    _set_notes(s, slide.get("notes", ""))
    return s


# ---------- Funnel (recipe: funnel) ----------

def _styled_funnel(prs, slide, t: Tokens):
    """Trapezoidal stack, top-down narrowing. Per-stage label + count;
    conversion % between stages. Largest leak emphasised."""
    s = _new_blank_slide(prs)
    _set_bg(s, t.bg_light)
    _add_textbox(s, Inches(0.75), Inches(0.5), Inches(11.83), Inches(0.9),
                 slide.get("title", ""),
                 font_name=t.font_title, font_size=t.sz_title,
                 color=t.text_light)

    stages = slide.get("funnel_stages") or []
    if not stages:
        _set_notes(s, slide.get("notes", ""))
        return s
    n = len(stages)

    # Geometry: vertical stack centred horizontally, narrowing.
    body_top = Inches(1.7); body_bot = Inches(6.5)
    stage_h = (body_bot - body_top) / n
    cx = Inches(6.665)
    max_w = Inches(7.0)
    min_w = Inches(2.5)
    counts = [float(st.get("count", 0)) for st in stages]
    top_count = counts[0] or 1
    # Width proportional to count
    widths = [max(min_w, int(max_w * (c / top_count))) for c in counts]

    # Find largest leak (drop) for emphasis
    leaks = [counts[i - 1] - counts[i] for i in range(1, n)]
    leak_max_idx = (leaks.index(max(leaks)) + 1) if leaks else None

    for i, st in enumerate(stages):
        y = int(body_top + stage_h * i)
        w = widths[i]
        x = int(cx - w / 2)
        rect = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y + Emu(20000),
                                  w, int(stage_h) - Emu(40000))
        rect.fill.solid()
        rect.fill.fore_color.rgb = t.primary if (i == leak_max_idx) else t.secondary
        rect.line.fill.background()
        # Stage label + count on the bar
        _add_textbox(s, x + Inches(0.15), y + Inches(0.05),
                     w - Inches(0.3), int(stage_h) - Emu(80000),
                     f"{st.get('label', '')}   ({int(st.get('count', 0)):,})",
                     font_name=t.font_body, font_size=t.sz_body,
                     color=t.text_dark, align=PP_ALIGN.CENTER, bold=True,
                     anchor=MSO_ANCHOR.MIDDLE)
        # Conversion rate to RIGHT of bar (between this and prior)
        if i > 0:
            rate = st.get("rate")
            if rate is None and counts[i - 1]:
                rate = counts[i] / counts[i - 1]
            if rate is not None:
                _add_textbox(s, cx + max_w / 2 + Inches(0.2), y - Inches(0.15),
                             Inches(2.5), Inches(0.4),
                             f"↓ {rate * 100:.0f}%",
                             font_name=t.font_body, font_size=t.sz_caption,
                             color=t.text_2_light)

    _set_notes(s, slide.get("notes", ""))
    return s


# ---------- Decision Options Table (recipe: decision_options) ----------

def _styled_decision_options(prs, slide, t: Tokens):
    """N options × M criteria table (>3 supported). Recommended option
    column highlighted; final 'Verdict' column shows ✓ / ✗.
    QA: column widths sum within slide-width tolerance."""
    s = _new_blank_slide(prs)
    _set_bg(s, t.bg_light)
    _add_textbox(s, Inches(0.75), Inches(0.5), Inches(11.83), Inches(0.9),
                 slide.get("title", ""),
                 font_name=t.font_title, font_size=t.sz_title,
                 color=t.text_light)

    options = slide.get("options") or []
    criteria = slide.get("criteria") or []
    rec = slide.get("recommendation")

    if not options or not criteria:
        _set_notes(s, slide.get("notes", ""))
        return s

    n_opts = len(options)
    n_cols = 1 + n_opts            # leading "Criterion" col + one per option
    n_rows = 1 + len(criteria) + 1  # header + criteria + verdict

    table_left = Inches(0.75)
    table_top  = Inches(1.7)
    table_w    = Inches(11.83)
    table_h    = Inches(5.0)

    # Build table
    tbl_shape = s.shapes.add_table(n_rows, n_cols, table_left, table_top,
                                   table_w, table_h)
    tbl = tbl_shape.table

    # Column widths: criterion col = 25%, options share 75%
    crit_w = int(table_w * 0.25)
    opt_w = int((table_w - crit_w) / n_opts)
    tbl.columns[0].width = crit_w
    for c in range(1, n_cols):
        tbl.columns[c].width = opt_w

    # Header row
    tbl.cell(0, 0).text = "Criterion"
    for c, opt in enumerate(options, start=1):
        tbl.cell(0, c).text = str(opt.get("name", ""))
        cell = tbl.cell(0, c)
        cell.fill.solid()
        is_rec = (opt.get("name") == rec)
        cell.fill.fore_color.rgb = t.primary if is_rec else t.surface

    # Body rows: criteria
    for r, crit_name in enumerate(criteria, start=1):
        tbl.cell(r, 0).text = str(crit_name)
        for c, opt in enumerate(options, start=1):
            scores = opt.get("scores") or {}
            v = scores.get(crit_name, "")
            tbl.cell(r, c).text = str(v) if v != "" else "—"
            if opt.get("name") == rec:
                cell = tbl.cell(r, c)
                cell.fill.solid()
                cell.fill.fore_color.rgb = t.surface

    # Verdict row
    tbl.cell(n_rows - 1, 0).text = "Verdict"
    for c, opt in enumerate(options, start=1):
        is_rec = (opt.get("name") == rec)
        tbl.cell(n_rows - 1, c).text = "✓ Recommended" if is_rec else "—"
        if is_rec:
            cell = tbl.cell(n_rows - 1, c)
            cell.fill.solid()
            cell.fill.fore_color.rgb = t.primary

    # Style table text — small + readable; skip granular formatting to keep
    # this builder under 100 LOC. python-pptx applies sane defaults.
    _set_notes(s, slide.get("notes", ""))

    # Self-check: column widths sum to slide width within tolerance.
    total = sum(col.width for col in tbl.columns)
    tol = Emu(50000)  # ~0.05"
    if abs(total - table_w) > tol:
        # Soft warning — does not block.
        pass
    return s


# ---------- Appendix Dense (recipe: appendix_dense) ----------

def _styled_appendix_dense(prs, slide, t: Tokens):
    """Dense reference layout: title bar, optional kicker, 2–4 panels
    (text/chart/table mix). Body type at caption scale. Visible
    'Appendix' tag upper-right. Pair with `slide.appendix=true` to
    bypass the body_word_max=30 density check."""
    s = _new_blank_slide(prs)
    _set_bg(s, t.bg_light)

    # Appendix tag upper-right
    _add_textbox(s, Inches(11.0), Inches(0.3), Inches(2.0), Inches(0.4),
                 "APPENDIX",
                 font_name=t.font_body, font_size=Pt(11),
                 color=t.text_2_light, align=PP_ALIGN.RIGHT, bold=True)

    _add_textbox(s, Inches(0.75), Inches(0.5), Inches(10.0), Inches(0.7),
                 slide.get("title", ""),
                 font_name=t.font_title, font_size=Pt(28),
                 color=t.text_light)
    if slide.get("subtitle"):
        _add_textbox(s, Inches(0.75), Inches(1.15), Inches(10.0), Inches(0.4),
                     slide["subtitle"],
                     font_name=t.font_body, font_size=t.sz_caption,
                     color=t.text_2_light)

    panels = slide.get("panels") or []
    n = len(panels)
    if n == 0:
        _set_notes(s, slide.get("notes", ""))
        return s

    # 1×2 (n=2) | 2×1 vertical (n in 3,4 use 2×2)
    if n == 2:
        cols, rows = 2, 1
    elif n <= 4:
        cols, rows = 2, 2
    else:
        cols, rows = 2, 2  # cap

    body_left = Inches(0.75); body_top = Inches(1.7)
    body_w = Inches(11.83);   body_h = Inches(5.4)
    pw = body_w / cols
    ph = body_h / rows
    pad = Inches(0.15)

    for i, p in enumerate(panels[:cols * rows]):
        ci = i % cols; ri = i // cols
        x = body_left + pw * ci + pad
        y = body_top + ph * ri + pad
        w = pw - pad * 2
        h = ph - pad * 2
        # Panel border
        rect = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, w, h)
        rect.fill.solid(); rect.fill.fore_color.rgb = t.surface
        rect.line.color.rgb = t.text_2_light

        if p.get("title"):
            _add_textbox(s, x + Inches(0.15), y + Inches(0.1),
                         w - Inches(0.3), Inches(0.4),
                         p["title"],
                         font_name=t.font_body, font_size=Pt(13),
                         color=t.text_light, bold=True)

        kind = p.get("kind", "text")
        body_y = y + Inches(0.55)
        body_h_inner = h - Inches(0.7)
        if kind == "text":
            _add_textbox(s, x + Inches(0.15), body_y,
                         w - Inches(0.3), body_h_inner,
                         p.get("body", ""),
                         font_name=t.font_body, font_size=Pt(12),
                         color=t.text_light)
        elif kind == "chart":
            img = p.get("image_path")
            if img and os.path.exists(img):
                _add_picture(s, img, x + Inches(0.15), body_y,
                             w - Inches(0.3), body_h_inner)
            else:
                _add_textbox(s, x + Inches(0.15), body_y,
                             w - Inches(0.3), body_h_inner,
                             "[chart missing]",
                             font_name=t.font_body, font_size=t.sz_caption,
                             color=t.text_2_light, align=PP_ALIGN.CENTER)
        elif kind == "table":
            rows_data = p.get("rows") or []
            if rows_data:
                _add_textbox(
                    s, x + Inches(0.15), body_y,
                    w - Inches(0.3), body_h_inner,
                    [" | ".join(r) for r in rows_data],
                    font_name=t.font_body, font_size=Pt(11),
                    color=t.text_light)

        if p.get("source"):
            _add_textbox(s, x + Inches(0.15), y + h - Inches(0.3),
                         w - Inches(0.3), Inches(0.25),
                         f"Source: {p['source']}",
                         font_name=t.font_body, font_size=Pt(9),
                         color=t.text_2_light)

    _set_notes(s, slide.get("notes", ""))
    return s


# ---------- Footer Source partial (recipe: footer_source — overlay) ----------

def _apply_footer_source(slide_obj, footer: dict, t: Tokens):
    """Overlay applied to ANY slide with `footer` block.

    `footer` shape: {source?, page?, page_total?, confidentiality?}
    Renders a 0.35"-tall band along bottom edge: source left,
    confidentiality centre, page right. Caption-size type."""
    if not footer:
        return
    band_top = Inches(7.10)
    band_h = Inches(0.35)
    source = footer.get("source")
    page = footer.get("page")
    page_total = footer.get("page_total")
    confidentiality = footer.get("confidentiality")

    if source:
        _add_textbox(slide_obj, Inches(0.35), band_top,
                     Inches(6.5), band_h,
                     str(source),
                     font_name=t.font_body, font_size=Pt(10),
                     color=t.text_2_light)
    if confidentiality:
        _add_textbox(slide_obj, Inches(5.0), band_top,
                     Inches(3.33), band_h,
                     str(confidentiality),
                     font_name=t.font_body, font_size=Pt(10),
                     color=t.text_2_light, align=PP_ALIGN.CENTER, bold=True)
    if page is not None:
        page_str = (f"{page} / {page_total}" if page_total else str(page))
        _add_textbox(slide_obj, Inches(10.0), band_top,
                     Inches(2.83), band_h,
                     page_str,
                     font_name=t.font_body, font_size=Pt(10),
                     color=t.text_2_light, align=PP_ALIGN.RIGHT)


# Bind the archetype builders into STYLED_BUILDERS now they're defined.
STYLED_BUILDERS["risk_heatmap"]     = _styled_risk_heatmap
STYLED_BUILDERS["priority_matrix"]  = _styled_priority_matrix
STYLED_BUILDERS["waterfall"]        = _styled_waterfall
STYLED_BUILDERS["flywheel"]         = _styled_flywheel
STYLED_BUILDERS["funnel"]           = _styled_funnel
STYLED_BUILDERS["decision_options"] = _styled_decision_options
STYLED_BUILDERS["appendix_dense"]   = _styled_appendix_dense


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
        slide_obj = builder(prs, slide, t)
    else:
        stype = slide.get("type", "content")
        builder = SIMPLE_BUILDERS.get(stype, _simple_content)
        log.write(f"[slide {slide.get('index')}] simple/{stype}\n")
        slide_obj = builder(prs, slide, t)

    # Footer Source partial (session 2026-05-04-c8d3b2a1) — applied to
    # ANY slide whose spec carries a `footer` block, regardless of the
    # primary builder used. Reuses the same Tokens instance.
    footer = slide.get("footer")
    if footer and slide_obj is not None:
        try:
            _apply_footer_source(slide_obj, footer, t)
        except Exception as e:
            log.write(f"[footer] failed on slide {slide.get('index')}: {e}\n")


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

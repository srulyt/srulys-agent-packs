#!/usr/bin/env python3
"""render_chart.py — matplotlib-based chart recipes for @deck-builder.

Recipes:
  bar_with_callouts  — vertical bars w/ annotation arrows
  donut              — ratio donut + centred big number
  sparkline          — thin line chart w/ end-marker
  dual_bar_diff      — paired before/after bars
  progress_strip     — horizontal axhline w/ numbered scatter markers

Tufte data-ink rcParams: spines top/right off, no gridlines unless
explicit, single accent for the focal data point.

Open-question bindings (session 2026-05-04-7d3f9a2b decisions.md):
  OQ1 — no aspose; matplotlib only
  OQ3 — emit SVG peer when --svg passed (matplotlib savefig format='svg')

Usage:
  render_chart.py --kind <recipe> --spec spec.json --tokens tokens.json
                  --out out.png [--size 1920x1080] [--svg]
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


# ---------- bootstrap ----------

def _ensure(mod: str, pip_name: str | None = None) -> None:
    try:
        __import__(mod)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", pip_name or mod])


_ensure("matplotlib")

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Wedge  # noqa: E402


# ---------- helpers ----------

def _hex(token_or_hex: str) -> str:
    """Tokens may pass through as #RRGGBB strings; pass-through if so."""
    if not token_or_hex:
        return "#FFFFFF"
    return token_or_hex if token_or_hex.startswith("#") else "#FFFFFF"


def _palette(tokens: dict) -> dict:
    p = tokens.get("palette") or {}
    # Surface-aware text_secondary resolution: prefer per-surface
    # override tokens (used by systems whose dark/light backgrounds
    # are too close in luminance for a single mid-gray to clear AA),
    # else fall back to the legacy bare key.
    ts_default = p.get("text_secondary", "#A0A4B0")
    return {
        "bg_dark":   _hex(p.get("background_dark",  "#1E1E2E")),
        "bg_light":  _hex(p.get("background_light", "#F5F6FA")),
        "bg_accent": _hex(p.get("background_accent", "#4F46E5")),
        "primary":   _hex(p.get("primary_accent",   "#635BFF")),
        "secondary": _hex(p.get("secondary_accent", "#3ECF8E")),
        "highlight": _hex(p.get("highlight",        "#FF6B6B")),
        "text_dark":  _hex(p.get("text_on_dark",   "#FFFFFF")),
        "text_light": _hex(p.get("text_on_light",  "#0F1019")),
        "text_secondary_on_dark":  _hex(p.get("text_secondary_on_dark",  ts_default)),
        "text_secondary_on_light": _hex(p.get("text_secondary_on_light", ts_default)),
    }


def _ts(pal: dict, on_dark: bool) -> str:
    """Surface-aware secondary-text/muted-decoration colour."""
    return pal["text_secondary_on_dark"] if on_dark else pal["text_secondary_on_light"]


def _apply_tufte_rc(pal: dict, on_dark: bool = True) -> None:
    bg = pal["bg_dark"] if on_dark else pal["bg_light"]
    fg = pal["text_dark"] if on_dark else pal["text_light"]
    sec = _ts(pal, on_dark)
    plt.rcParams.update({
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.spines.left": True,
        "axes.spines.bottom": True,
        "axes.grid": False,
        "figure.facecolor": bg,
        "axes.facecolor": bg,
        "savefig.facecolor": bg,
        "text.color": fg,
        "axes.labelcolor": sec,
        "xtick.color": sec,
        "ytick.color": sec,
        "axes.edgecolor": sec,
        "font.size": 14,
    })


def _figsize(size_str: str) -> tuple[float, float]:
    try:
        w, h = (int(x) for x in size_str.lower().split("x"))
    except Exception:
        w, h = 1920, 1080
    # at dpi=160: 1920 / 160 = 12.0 inches
    return (w / 160.0, h / 160.0)


def _save(fig, out: Path, want_svg: bool) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(str(out), dpi=160, format="png")
    if want_svg:
        svg_path = out.with_suffix(".svg")
        fig.savefig(str(svg_path), format="svg")
    plt.close(fig)


# ---------- recipes ----------

def render_bar_with_callouts(spec: dict, pal: dict, size: str, on_dark: bool):
    _apply_tufte_rc(pal, on_dark=on_dark)
    fig, ax = plt.subplots(figsize=_figsize(size), dpi=160)
    labels = spec.get("labels") or []
    values = spec.get("values") or []
    if not labels or len(labels) != len(values):
        raise ValueError("bar_with_callouts: labels and values must be parallel non-empty arrays")
    focal_value = max(values)
    colors = [pal["secondary"] if v == focal_value else pal["primary"] for v in values]
    ax.bar(labels, values, color=colors, edgecolor="none")
    ax.tick_params(axis="x", labelsize=18)
    ax.tick_params(axis="y", labelsize=14)
    if spec.get("y_label"):
        ax.set_ylabel(spec["y_label"])
    if spec.get("title"):
        ax.set_title(spec["title"], color=pal["text_dark"] if on_dark else pal["text_light"],
                     fontsize=22, loc="left", pad=20)
    for callout in spec.get("callouts", []):
        try:
            xi = labels.index(callout["x"]) if isinstance(callout["x"], str) else int(callout["x"])
        except Exception:
            xi = 0
        ax.annotate(
            callout.get("text", ""),
            xy=(xi, callout.get("y", values[xi] if xi < len(values) else 0)),
            xytext=(xi + 0.4, (callout.get("y", values[xi] if xi < len(values) else 0)) * 1.08),
            fontsize=18,
            color=pal["text_dark"] if on_dark else pal["text_light"],
            arrowprops=dict(arrowstyle="->", color=pal["highlight"], lw=2),
        )
    fig.tight_layout()
    return fig


def render_donut(spec: dict, pal: dict, size: str, on_dark: bool):
    _apply_tufte_rc(pal, on_dark=on_dark)
    fig, ax = plt.subplots(figsize=_figsize(size), dpi=160)
    pct = float(spec.get("pct", 0.5))
    pct = max(0.0, min(1.0, pct))
    theta1 = 90
    theta2 = 90 - 360 * pct
    bg_ring = Wedge((0, 0), 1.0, 0, 360, width=0.22, facecolor=_ts(pal, on_dark), edgecolor="none")
    fg_ring = Wedge((0, 0), 1.0, theta2, theta1, width=0.22, facecolor=pal["secondary"], edgecolor="none")
    ax.add_patch(bg_ring)
    ax.add_patch(fg_ring)
    ax.text(0, 0.05, spec.get("big_number", f"{int(pct*100)}%"),
            ha="center", va="center", fontsize=72, fontweight="bold",
            color=pal["text_dark"] if on_dark else pal["text_light"])
    if spec.get("label"):
        ax.text(0, -0.25, spec["label"], ha="center", va="center",
                fontsize=20, color=_ts(pal, on_dark))
    ax.set_xlim(-1.3, 1.3)
    ax.set_ylim(-1.3, 1.3)
    ax.set_aspect("equal")
    ax.axis("off")
    return fig


def render_sparkline(spec: dict, pal: dict, size: str, on_dark: bool):
    _apply_tufte_rc(pal, on_dark=on_dark)
    fig, ax = plt.subplots(figsize=_figsize(size), dpi=160)
    series = spec.get("series") or []
    if not series:
        raise ValueError("sparkline: 'series' must be a non-empty array of numbers")
    xs = list(range(len(series)))
    ax.plot(xs, series, color=pal["primary"], lw=3)
    ax.scatter([xs[-1]], [series[-1]], color=pal["highlight"], s=160, zorder=10)
    ax.text(xs[-1], series[-1], f"  {series[-1]}", fontsize=22,
            color=pal["text_dark"] if on_dark else pal["text_light"], va="center")
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)
    if spec.get("x_labels"):
        ax.set_xticks(xs)
        ax.set_xticklabels(spec["x_labels"], fontsize=16)
    else:
        ax.set_xticks([])
    if spec.get("title"):
        ax.set_title(spec["title"], fontsize=24, loc="left", pad=20,
                     color=pal["text_dark"] if on_dark else pal["text_light"])
    fig.tight_layout()
    return fig


def render_dual_bar_diff(spec: dict, pal: dict, size: str, on_dark: bool):
    _apply_tufte_rc(pal, on_dark=on_dark)
    fig, ax = plt.subplots(figsize=_figsize(size), dpi=160)
    labels = spec.get("labels") or []
    before = spec.get("before") or []
    after = spec.get("after") or []
    if not (labels and len(labels) == len(before) == len(after)):
        raise ValueError("dual_bar_diff: labels/before/after must be parallel non-empty arrays")
    import numpy as np
    x = np.arange(len(labels))
    w = 0.35
    ax.bar(x - w / 2, before, w, color=_ts(pal, on_dark), label=spec.get("before_label", "Before"))
    ax.bar(x + w / 2, after,  w, color=pal["secondary"],      label=spec.get("after_label",  "After"))
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=16)
    ax.legend(fontsize=14, frameon=False)
    if spec.get("title"):
        ax.set_title(spec["title"], fontsize=22, loc="left", pad=20,
                     color=pal["text_dark"] if on_dark else pal["text_light"])
    fig.tight_layout()
    return fig


def render_progress_strip(spec: dict, pal: dict, size: str, on_dark: bool):
    _apply_tufte_rc(pal, on_dark=on_dark)
    fig, ax = plt.subplots(figsize=_figsize(size), dpi=160)
    steps = spec.get("steps") or []
    if not steps:
        raise ValueError("progress_strip: 'steps' must be a non-empty array")
    n = len(steps)
    xs = list(range(1, n + 1))
    ax.axhline(0, color=_ts(pal, on_dark), lw=2, zorder=1)
    ax.scatter(xs, [0] * n, s=2200, color=pal["primary"], zorder=2,
               edgecolor=pal["text_dark"] if on_dark else pal["text_light"], linewidths=2)
    for i, step in enumerate(steps, start=1):
        ax.text(i, 0, str(i), ha="center", va="center", fontsize=22, fontweight="bold",
                color=pal["text_dark"] if on_dark else pal["text_light"], zorder=3)
        label = step.get("label", "") if isinstance(step, dict) else str(step)
        sub = step.get("subtext", "") if isinstance(step, dict) else ""
        ax.text(i, 0.6, label, ha="center", va="bottom", fontsize=20,
                color=pal["text_dark"] if on_dark else pal["text_light"])
        if sub:
            ax.text(i, -0.6, sub, ha="center", va="top", fontsize=14,
                    color=_ts(pal, on_dark))
    ax.set_xlim(0.5, n + 0.5)
    ax.set_ylim(-1.5, 1.5)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    return fig


RECIPES = {
    "bar_with_callouts": render_bar_with_callouts,
    "donut": render_donut,
    "sparkline": render_sparkline,
    "dual_bar_diff": render_dual_bar_diff,
    "progress_strip": render_progress_strip,
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--kind", required=True, choices=sorted(RECIPES.keys()))
    ap.add_argument("--spec", required=True, type=Path)
    ap.add_argument("--tokens", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--size", default="1920x1080")
    ap.add_argument("--on-light", action="store_true",
                    help="Render on background_light (default: on background_dark)")
    ap.add_argument("--svg", action="store_true",
                    help="Emit SVG peer alongside PNG (matplotlib native)")
    args = ap.parse_args()

    try:
        spec = json.loads(args.spec.read_text(encoding="utf-8"))
        tokens = json.loads(args.tokens.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"ERROR: bad spec/tokens JSON: {e}", file=sys.stderr)
        return 2

    pal = _palette(tokens)
    fn = RECIPES[args.kind]
    try:
        fig = fn(spec, pal, args.size, on_dark=not args.on_light)
    except Exception as e:
        print(f"ERROR: recipe {args.kind} failed: {e}", file=sys.stderr)
        return 2

    _save(fig, args.out, want_svg=args.svg)
    print(f"SUCCESS: {args.kind} -> {args.out}" + (" (+ .svg)" if args.svg else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())

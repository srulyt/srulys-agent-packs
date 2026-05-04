#!/usr/bin/env python3
"""render_diagram.py — Graphviz wrapper for @deck-builder.

Recipes:
  flow_diagram   — directed nodes + edges; left-to-right `dot` layout
  system_diagram — labelled boxes; top-down `dot` layout

Per OQ2 (decisions.md 2026-05-04T14:50Z):
  - Attempts `pip install graphviz` (Python binding) automatically.
  - Probes for the `dot` binary on PATH.
  - If `dot` is missing, prints OS-specific install instructions and
    DEGRADES GRACEFULLY: writes a `<out>.skipped.json` sentinel and
    exits 0 (not non-zero) so the deck-builder can mark the asset as
    skipped without blocking the deck.

Per OQ3: emits SVG peer when --svg is passed (Graphviz native via -Tsvg).

Usage:
  render_diagram.py --kind <recipe> --spec spec.json --tokens tokens.json
                    --out out.png [--size 1920x1080] [--svg]
"""

from __future__ import annotations

import argparse
import json
import platform
import shutil
import subprocess
import sys
from pathlib import Path


def _ensure(mod: str, pip_name: str | None = None) -> bool:
    try:
        __import__(mod)
        return True
    except ImportError:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", pip_name or mod])
            __import__(mod)
            return True
        except Exception:
            return False


def _install_hint() -> str:
    sysname = platform.system()
    if sysname == "Windows":
        return ("Install Graphviz: `winget install Graphviz` "
                "(or download from https://graphviz.org/download/) "
                "and ensure `dot.exe` is on PATH.")
    if sysname == "Darwin":
        return "Install Graphviz: `brew install graphviz`."
    return "Install Graphviz: `apt install graphviz` (Debian/Ubuntu) or `dnf install graphviz` (Fedora)."


def _probe_dot() -> str | None:
    return shutil.which("dot")


def _hex(token_or_hex: str, default: str = "#FFFFFF") -> str:
    return token_or_hex if (token_or_hex or "").startswith("#") else default


def _palette(tokens: dict) -> dict:
    p = tokens.get("palette") or {}
    return {
        "bg_dark":   _hex(p.get("background_dark"),  "#1E1E2E"),
        "bg_light":  _hex(p.get("background_light"), "#F5F6FA"),
        "primary":   _hex(p.get("primary_accent"),   "#635BFF"),
        "secondary": _hex(p.get("secondary_accent"), "#3ECF8E"),
        "highlight": _hex(p.get("highlight"),        "#FF6B6B"),
        "text_dark":  _hex(p.get("text_on_dark"),  "#FFFFFF"),
        "text_light": _hex(p.get("text_on_light"), "#0F1019"),
    }


def _parse_size(size: str) -> tuple[int, int]:
    try:
        w, h = (int(x) for x in size.lower().split("x"))
        return w, h
    except Exception:
        return 1920, 1080


# ---------- recipes (build a Graphviz `Digraph` object) ----------

def _build_flow_diagram(spec: dict, pal: dict, size_in: tuple[float, float]):
    from graphviz import Digraph
    g = Digraph("flow", format="png")
    g.attr(rankdir="LR",
           bgcolor=pal["bg_dark"],
           size=f"{size_in[0]},{size_in[1]}!",
           margin="0.4")
    g.attr("node",
           shape="box", style="rounded,filled",
           fillcolor=pal["primary"], color=pal["primary"],
           fontcolor=pal["text_dark"], fontname="Helvetica", fontsize="20",
           penwidth="0", margin="0.25,0.15")
    g.attr("edge",
           color=pal["text_dark"], penwidth="2",
           arrowsize="1.0",
           fontcolor=pal["text_dark"], fontname="Helvetica", fontsize="14")
    nodes = spec.get("nodes") or []
    for n in nodes:
        if isinstance(n, str):
            g.node(n, n)
        else:
            nid = n["id"]
            label = n.get("label", nid)
            extra = {}
            if n.get("focal"):
                extra["fillcolor"] = pal["secondary"]
            g.node(nid, label, **extra)
    for e in spec.get("edges") or []:
        if isinstance(e, list) and len(e) >= 2:
            g.edge(e[0], e[1], label=e[2] if len(e) > 2 else "")
        elif isinstance(e, dict):
            g.edge(e["from"], e["to"], label=e.get("label", ""))
    return g


def _build_system_diagram(spec: dict, pal: dict, size_in: tuple[float, float]):
    from graphviz import Digraph
    g = Digraph("system", format="png")
    g.attr(rankdir="TB",
           bgcolor=pal["bg_dark"],
           size=f"{size_in[0]},{size_in[1]}!",
           margin="0.4")
    g.attr("node",
           shape="box", style="filled",
           fillcolor=pal["bg_light"], color=pal["primary"],
           fontcolor=pal["text_light"], fontname="Helvetica", fontsize="20",
           penwidth="2", margin="0.3,0.2")
    g.attr("edge",
           color=pal["text_dark"], penwidth="1.5",
           fontcolor=pal["text_dark"], fontname="Helvetica", fontsize="13")
    for box in spec.get("boxes") or []:
        if isinstance(box, str):
            g.node(box, box)
        else:
            bid = box["id"]
            label = box.get("label", bid)
            extra = {}
            if box.get("focal"):
                extra["fillcolor"] = pal["secondary"]
                extra["fontcolor"] = pal["text_dark"]
            g.node(bid, label, **extra)
    for e in spec.get("edges") or []:
        if isinstance(e, list) and len(e) >= 2:
            g.edge(e[0], e[1], label=e[2] if len(e) > 2 else "")
        elif isinstance(e, dict):
            g.edge(e["from"], e["to"], label=e.get("label", ""))
    return g


RECIPES = {
    "flow_diagram":   _build_flow_diagram,
    "system_diagram": _build_system_diagram,
}


# ---------- graceful-degrade sentinel ----------

def _emit_skipped(out: Path, reason: str, hint: str) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    sentinel = out.with_suffix(out.suffix + ".skipped.json")
    sentinel.write_text(json.dumps({
        "skipped": True,
        "reason": reason,
        "install_hint": hint,
    }, indent=2))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--kind", required=True, choices=sorted(RECIPES.keys()))
    ap.add_argument("--spec", required=True, type=Path)
    ap.add_argument("--tokens", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--size", default="1920x1080")
    ap.add_argument("--svg", action="store_true",
                    help="Emit SVG peer alongside PNG (Graphviz native -Tsvg)")
    args = ap.parse_args()

    # OQ2: attempt programmatic install of the Python binding.
    if not _ensure("graphviz"):
        hint = _install_hint()
        print(f"ERROR: graphviz Python binding install failed. {hint}", file=sys.stderr)
        _emit_skipped(args.out, reason="graphviz_python_install_failed", hint=hint)
        print(f"SKIPPED: {args.out}.skipped.json (graceful degrade per OQ2)")
        return 0

    # OQ2: probe for `dot` binary.
    dot_path = _probe_dot()
    if not dot_path:
        hint = _install_hint()
        print(f"WARN: `dot` binary not found on PATH. {hint}", file=sys.stderr)
        _emit_skipped(args.out, reason="dot_binary_missing", hint=hint)
        print(f"SKIPPED: {args.out}.skipped.json (graceful degrade per OQ2)")
        return 0

    try:
        spec = json.loads(args.spec.read_text(encoding="utf-8"))
        tokens = json.loads(args.tokens.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"ERROR: bad spec/tokens JSON: {e}", file=sys.stderr)
        return 2

    pal = _palette(tokens)
    w_px, h_px = _parse_size(args.size)
    size_in = (w_px / 96.0, h_px / 96.0)  # Graphviz `size` in inches

    try:
        g = RECIPES[args.kind](spec, pal, size_in)
    except Exception as e:
        print(f"ERROR: diagram {args.kind} failed: {e}", file=sys.stderr)
        return 2

    args.out.parent.mkdir(parents=True, exist_ok=True)
    # Render PNG
    try:
        png_bytes = g.pipe(format="png")
        args.out.write_bytes(png_bytes)
    except Exception as e:
        print(f"ERROR: graphviz PNG render failed: {e}", file=sys.stderr)
        return 2

    if args.svg:
        try:
            svg_bytes = g.pipe(format="svg")
            args.out.with_suffix(".svg").write_bytes(svg_bytes)
        except Exception as e:
            print(f"WARN: SVG peer failed: {e}", file=sys.stderr)

    print(f"SUCCESS: {args.kind} -> {args.out}" + (" (+ .svg)" if args.svg else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())

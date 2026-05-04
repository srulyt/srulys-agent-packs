#!/usr/bin/env python3
"""check_palettes.py — G1 preflight gate for @deck-critic.

Per architecture §3 / finding F3 / critic concern C1: this script is
the single source of truth for palette WCAG-AA verification. It is
run as the FIRST step of `@deck-builder`'s phase (G1 ownership), and
re-run by `@deck-critic` as a cross-check before render.

Loads each `references/systems/*.md` file, extracts the embedded JSON
token block, computes WCAG contrast for every token-pair listed under
`REQUIRED_PAIRS`, and exits non-zero if any pair falls below AA.

Output: stdout one line per failing pair, plus an optional JSON
report when `--out` is given. Exit code 0 = all systems pass; 1 =
script error; 2 = at least one failing pair.

Usage:

    python check_palettes.py
    python check_palettes.py --systems-dir <path>
    python check_palettes.py --out preflight.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from itertools import product
from pathlib import Path


SYSTEMS_DIR_DEFAULT = (
    Path(__file__).resolve().parent.parent / "references" / "systems"
)


# WCAG 2.2 thresholds — single source of truth, mirrored in
# references/wcag-thresholds.md.
THRESHOLD_BODY = 4.5
THRESHOLD_LARGE = 3.0


# Pairs that MUST satisfy the AA body threshold (4.5:1) by default,
# unless the (foreground, background) combination is in
# `LARGE_TEXT_ALLOWED` and the design system documents that the
# slide-class which uses this pair carries body text >= 18pt.
REQUIRED_PAIRS = [
    ("text_on_dark",   "background_dark"),
    ("text_on_dark",   "background_accent"),   # styled section dividers
    ("text_on_light",  "background_light"),
    ("text_secondary", "background_dark"),
    ("text_secondary", "background_light"),
]

# Optional per-surface override keys for `text_secondary`. When a
# design system's palette ships either of these, the corresponding
# row in REQUIRED_PAIRS resolves the foreground via the override
# instead of the bare `text_secondary` key. This exists because for
# some systems (notably `technical-slate`) the dark/light background
# pair is too narrow in luminance distance for any single mid-gray
# to clear AA against both. Systems without the override keys still
# fall back to the bare `text_secondary` key on both surfaces.
TEXT_SECONDARY_OVERRIDES = {
    "background_dark":  "text_secondary_on_dark",
    "background_light": "text_secondary_on_light",
}

# Pairs allowed to satisfy 3:1 (large-text) instead of 4.5:1 — only
# valid when the design system documents that the slide-class using
# this pair carries body text at >=18pt (or >=14pt-bold). Today the
# rule is *no* slack — every required pair must satisfy 4.5:1, full
# stop, because a builder may reuse a pair on a smaller-text shape.
LARGE_TEXT_ALLOWED: set[tuple[str, str]] = set()


# ---------- colour helpers (duplicate-free copy from check_pptx.py) ----------

def _hex_to_rgb(h: str) -> tuple[int, int, int] | None:
    if not h:
        return None
    h = h.strip().lstrip("#")
    if len(h) != 6:
        return None
    try:
        return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    except ValueError:
        return None


def _rel_lum(rgb: tuple[int, int, int]) -> float:
    def chan(c: int) -> float:
        x = c / 255.0
        return x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4
    r, g, b = rgb
    return 0.2126 * chan(r) + 0.7152 * chan(g) + 0.0722 * chan(b)


def _ratio(fg: tuple[int, int, int], bg: tuple[int, int, int]) -> float:
    l1 = _rel_lum(fg)
    l2 = _rel_lum(bg)
    a, b = max(l1, l2), min(l1, l2)
    return (a + 0.05) / (b + 0.05)


# ---------- system-md token extraction ----------

_JSON_BLOCK = re.compile(r"```json\s*\n(.*?)\n```", re.DOTALL)


def extract_tokens(md_text: str) -> dict | None:
    """Return the first JSON code-block as a parsed dict, or None."""
    m = _JSON_BLOCK.search(md_text)
    if not m:
        return None
    try:
        return json.loads(m.group(1))
    except json.JSONDecodeError:
        return None


# ---------- main ----------

def _resolve_fg_key(palette: dict, fg_key: str, bg_key: str) -> str:
    """Apply per-surface overrides for text_secondary when present."""
    if fg_key == "text_secondary":
        override_key = TEXT_SECONDARY_OVERRIDES.get(bg_key)
        if override_key and palette.get(override_key):
            return override_key
    return fg_key


def check_system(name: str, tokens: dict, allow_large_text: bool = False) -> list[dict]:
    """Return list of failing-pair dicts; empty == system passes."""
    palette = tokens.get("palette") or {}
    out: list[dict] = []
    for fg_key, bg_key in REQUIRED_PAIRS:
        fg_key = _resolve_fg_key(palette, fg_key, bg_key)
        fg_hex = palette.get(fg_key)
        bg_hex = palette.get(bg_key)
        if not (fg_hex and bg_hex):
            # Missing token — record so the system author notices.
            out.append({
                "system": name,
                "fg_token": fg_key,
                "bg_token": bg_key,
                "ratio": None,
                "threshold": THRESHOLD_BODY,
                "code": "missing_token",
            })
            continue
        fg = _hex_to_rgb(fg_hex)
        bg = _hex_to_rgb(bg_hex)
        if not (fg and bg):
            out.append({
                "system": name,
                "fg_token": fg_key,
                "bg_token": bg_key,
                "ratio": None,
                "threshold": THRESHOLD_BODY,
                "code": "bad_hex",
            })
            continue
        ratio = _ratio(fg, bg)
        threshold = (
            THRESHOLD_LARGE
            if allow_large_text and (fg_key, bg_key) in LARGE_TEXT_ALLOWED
            else THRESHOLD_BODY
        )
        if ratio < threshold:
            out.append({
                "system": name,
                "fg_token": fg_key,
                "fg_hex": fg_hex,
                "bg_token": bg_key,
                "bg_hex": bg_hex,
                "ratio": round(ratio, 2),
                "threshold": threshold,
                "code": "below_aa",
            })
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--systems-dir", type=Path, default=SYSTEMS_DIR_DEFAULT,
        help="Directory of <name>.md design-system files",
    )
    ap.add_argument("--out", type=Path, default=None,
                    help="Optional JSON report path")
    ap.add_argument("--allow-large-text", action="store_true",
                    help="Allow 3:1 for pairs in LARGE_TEXT_ALLOWED")
    args = ap.parse_args()

    if not args.systems_dir.is_dir():
        print(f"ERROR: --systems-dir not a directory: {args.systems_dir}",
              file=sys.stderr)
        return 1

    failing_pairs: list[dict] = []
    systems_checked: list[str] = []

    for sysfile in sorted(args.systems_dir.glob("*.md")):
        tokens = extract_tokens(sysfile.read_text(encoding="utf-8"))
        if tokens is None:
            print(f"SKIP: no JSON token block in {sysfile.name}", file=sys.stderr)
            continue
        name = tokens.get("name") or sysfile.stem
        systems_checked.append(name)
        failing_pairs.extend(check_system(name, tokens, args.allow_large_text))

    report = {
        "status": "pass" if not failing_pairs else "fail",
        "systems_checked": systems_checked,
        "failing_pairs": failing_pairs,
        "thresholds": {
            "body": THRESHOLD_BODY,
            "large_text": THRESHOLD_LARGE,
        },
    }
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(report, indent=2))

    if failing_pairs:
        print(f"FAIL: {len(failing_pairs)} palette pair(s) below WCAG AA")
        for p in failing_pairs:
            ratio = p.get("ratio")
            print(
                f"  - {p['system']}: {p['fg_token']}({p.get('fg_hex','?')})"
                f" on {p['bg_token']}({p.get('bg_hex','?')}) = "
                f"{ratio if ratio is not None else '<' + p.get('code','?') + '>'}"
                f" (threshold {p['threshold']}:1)"
            )
        return 2

    print(f"PASS: {len(systems_checked)} system(s) clean")
    return 0


if __name__ == "__main__":
    sys.exit(main())

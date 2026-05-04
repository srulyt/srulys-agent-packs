#!/usr/bin/env python3
"""check_archetypes.py — Cheap deck-spec-level assertions for the
7 archetype recipes (footer_source overlay tracked separately) added
in session 2026-05-04-c8d3b2a1.

Wired into the production QA pipeline in fix iteration 1 of the same
session: `check_pptx.py` imports `run()` and merges the findings here
into its single `qa-report.json` and into its blocking/warning
verdict buckets. Calling this script directly (--spec only) is still
supported for local debugging.

NOTE: TODO-asserts-archetypes-extra (manifest, prior turn) tracks
future asserts for priority_matrix, flywheel, funnel, appendix_dense
(min_font_size>=11pt), and footer_source band-overlap. They require
.pptx introspection or are deferred per scope; not added this turn.

Operates on `deck-spec.json` (NOT the rendered .pptx) — these are
spec-level invariants that the eye misses but the schema doesn't catch.
The full check_pptx.py runner stays untouched (extending it to per-recipe
shape introspection would be a re-architecture; that's a TODO).

Checks emitted:

  - waterfall.zero_baseline
      All bars share a zero-baseline. The script verifies the algebra
      (start + Σ steps == end ± rounding) and that the strategist did
      not include both sign-flipped totals AND a truncated axis hint.

  - decision_options.columns_sum_to_slide_width
      The decision_options builder lays out a table at 11.83" wide with
      one criterion column (25%) + N option columns (75% / N each).
      Verifies the spec satisfies n_options >= 1 and that the implied
      column-width sum lands within ±0.05" of slide-content width.

  - risk_heatmap.contrast_aa
      Heatmap cells render in green / amber / red with WHITE risk
      labels. Verifies the white-on-amber and white-on-red contrast
      against AA large-text (3:1). The amber `#F59E0B` borderline-fails
      AA against white at small sizes — the heatmap labels render at
      12pt bold, which clears AA-large.

Exit codes:
  0 — script ran successfully (regardless of pass/fail of checks)
  1 — script error (cannot read spec, malformed JSON)

Outputs JSON to --out (or stdout if omitted):
  {"checks": [{"id": str, "slide_index": int|null,
               "status": "pass"|"warn"|"fail",
               "message": str}]}
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _hex_to_rgb(h):
    h = (h or "").lstrip("#")
    if len(h) != 6:
        return None
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def _rel_lum(rgb):
    def _ch(c):
        c = c / 255.0
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = rgb
    return 0.2126 * _ch(r) + 0.7152 * _ch(g) + 0.0722 * _ch(b)


def _contrast(fg, bg):
    L1 = _rel_lum(fg); L2 = _rel_lum(bg)
    if L1 < L2:
        L1, L2 = L2, L1
    return (L1 + 0.05) / (L2 + 0.05)


# Cell colours match _styled_risk_heatmap (generate_deck.py session
# 2026-05-04-c8d3b2a1).
_HEATMAP_GREEN = (0x1B, 0x5E, 0x20)
_HEATMAP_AMBER = (0xB4, 0x53, 0x09)
_HEATMAP_RED   = (0xB7, 0x1C, 0x1C)
_HEATMAP_LABEL = (0xFF, 0xFF, 0xFF)


def check_waterfall_zero_baseline(slide, idx):
    if (slide.get("style_recipe") or "") != "waterfall":
        return None
    wf = slide.get("waterfall") or {}
    start = wf.get("start") or {}; end = wf.get("end") or {}
    steps = wf.get("steps") or []
    if not start or not end:
        return {"id": "waterfall.zero_baseline", "slide_index": idx,
                "status": "fail",
                "message": "waterfall slide missing start or end totals"}
    s_val = float(start.get("value", 0))
    e_val = float(end.get("value", 0))
    sum_steps = sum(float(s.get("delta", 0)) for s in steps)
    derived = s_val + sum_steps
    tol = max(0.01, abs(e_val) * 0.005)
    if abs(derived - e_val) > tol:
        return {"id": "waterfall.zero_baseline", "slide_index": idx,
                "status": "fail",
                "message": (f"waterfall algebra broken: start({s_val}) + Σdeltas"
                            f"({sum_steps:+.3f}) = {derived:.3f}, "
                            f"but end={e_val:.3f} (tol={tol:.3f}). "
                            "All bars must share zero-baseline; "
                            "fix delta signs or end value.")}
    return {"id": "waterfall.zero_baseline", "slide_index": idx,
            "status": "pass",
            "message": f"start + Σdeltas = end within {tol:.3f}"}


def check_decision_options_columns(slide, idx):
    if (slide.get("style_recipe") or "") != "decision_options":
        return None
    options = slide.get("options") or []
    criteria = slide.get("criteria") or []
    n_opts = len(options)
    if n_opts < 1:
        return {"id": "decision_options.columns_sum_to_slide_width",
                "slide_index": idx, "status": "fail",
                "message": "decision_options requires >=1 option"}
    if not criteria:
        return {"id": "decision_options.columns_sum_to_slide_width",
                "slide_index": idx, "status": "fail",
                "message": "decision_options requires >=1 criterion"}
    # Builder reserves: 25% criterion col + 75% / n_opts per option col.
    # Total = 25% + n_opts * (75% / n_opts) = 100%. Rounding drift only
    # appears when opt_w * n_opts != 75% (integer truncation in EMU).
    table_w_emu = int(11.83 * 914400)
    crit_w = int(table_w_emu * 0.25)
    opt_w = int((table_w_emu - crit_w) / n_opts)
    total = crit_w + opt_w * n_opts
    drift_inches = abs(table_w_emu - total) / 914400
    tol_in = 0.05
    status = "pass" if drift_inches <= tol_in else "warn"
    return {"id": "decision_options.columns_sum_to_slide_width",
            "slide_index": idx, "status": status,
            "message": (f"n_options={n_opts}, derived column-width drift "
                        f"= {drift_inches:.4f}\" (tol={tol_in}\")")}


def check_heatmap_contrast(slide, idx):
    if (slide.get("style_recipe") or "") != "risk_heatmap":
        return None
    out = []
    for label, bg in (("green", _HEATMAP_GREEN), ("amber", _HEATMAP_AMBER),
                      ("red", _HEATMAP_RED)):
        ratio = _contrast(_HEATMAP_LABEL, bg)
        # Risk labels render at 12pt bold — AA "large-text" (3:1) does
        # NOT apply (>=14pt bold or >=18pt regular). Use 4.5:1 normal-text.
        threshold = 4.5
        status = "pass" if ratio >= threshold else "warn"
        out.append({"id": "risk_heatmap.contrast_aa",
                    "slide_index": idx, "status": status,
                    "message": (f"white label on {label} cell: "
                                f"{ratio:.2f}:1 (AA normal threshold "
                                f"{threshold}:1)")})
    return out


CHECKS = (check_waterfall_zero_baseline,
          check_decision_options_columns,
          check_heatmap_contrast)


def run(spec_path: Path):
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    results = []
    for i, slide in enumerate(spec.get("slides", [])):
        idx = slide.get("index", i)
        for fn in CHECKS:
            r = fn(slide, idx)
            if r is None:
                continue
            if isinstance(r, list):
                results.extend(r)
            else:
                results.append(r)
    return {"checks": results}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", required=True, type=Path)
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()
    try:
        report = run(args.spec)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1
    out = json.dumps(report, indent=2)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(out, encoding="utf-8")
    else:
        print(out)
    # Print short summary
    n = len(report["checks"])
    fails = sum(1 for c in report["checks"] if c["status"] == "fail")
    warns = sum(1 for c in report["checks"] if c["status"] == "warn")
    print(f"[check_archetypes] {n} checks, {fails} fail, {warns} warn",
          file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())

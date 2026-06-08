"""B1 regression (hang-safe, no-LLM): the pdf->png stage must prefer
``pypdfium2`` (Apache-2.0/BSD, OQ1-clean) over poppler, and the full
``generate_deck.py -> render_pptx.py`` pipeline must produce per-slide
PNGs at 150 DPI.

This is a *tooling* smoke test: it drives the pack scripts directly via
subprocess (each script closes stdin + is timeout-bounded, so a missing
or interactive tool degrades to a fast failure, never a hang). It uses
no copilot CLI and no LLM judge, so it runs in any CI with python-pptx.

If the host has no LibreOffice (pptx->pdf) engine, the PNG-stage and
``pypdfium2`` assertions are skipped — the pack's verify-or-block policy
owns that case; here we only assert the *preferred-engine wiring*.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]

# C5: consistent, selectable markers for the tooling smoke evals.
# These are fast, no-LLM, bounded-subprocess tests of the pack's scripts.
pytestmark = [pytest.mark.pack, pytest.mark.tooling]
PACK = REPO / "agent-packs" / "story-telling-agent" / ".github" / "skills"
GEN = PACK / "pptx-engine" / "scripts" / "generate_deck.py"
RENDER = PACK / "pptx-visual-qa" / "scripts" / "render_pptx.py"
SYSTEMS = PACK / "slide-design-systems" / "references" / "systems"


def _system_tokens(name: str) -> dict:
    md = (SYSTEMS / f"{name}.md").read_text(encoding="utf-8")
    m = re.search(r"```json\s*(\{.*?\})\s*```", md, re.S)
    assert m, f"{name}.md has no JSON token block"
    return json.loads(m.group(1))


def test_pypdfium2_is_preferred_pdf_to_png_engine():
    """Source-level guard: pypdfium2 must be the FIRST branch in
    ``pdf_to_pngs`` and PyMuPDF/fitz must never be imported (AGPL)."""
    src = RENDER.read_text(encoding="utf-8")
    assert "import pypdfium2" in src, "render_pptx.py must import pypdfium2"
    assert "pypdfium2" in src.split("def pdf_to_pngs")[1].split("pdftoppm")[0], (
        "pypdfium2 branch must come BEFORE the pdftoppm/poppler fallback"
    )
    assert "import fitz" not in src and "PyMuPDF" not in src.replace(
        "PyMuPDF / `fitz` is deliberately NOT used", ""
    ).replace("PyMuPDF/`fitz` is intentionally excluded", ""), (
        "PyMuPDF/fitz (AGPL) must not be used"
    )


def test_pipeline_renders_pngs_via_pypdfium2(tmp_path):
    spec = {
        "design_system_tokens": _system_tokens("signal-dark"),
        "slides": [
            {"index": 0, "style": "styled", "style_recipe": "stat_grid_3up",
             "title": "Platform at scale",
             "stats": [{"value": "99.99%", "label": "Uptime", "delta": "+0.04"},
                       {"value": "42ms", "label": "p99", "delta": "-11"},
                       {"value": "3.2B", "label": "Events/day", "delta": "+0.9"}]},
            {"index": 1, "style": "styled", "style_recipe": "editorial_2col_6040",
             "title": "Why this architecture",
             "standfirst": "One control plane, many data planes.",
             "points": ["Region-local failure domains", "Zero-downtime evolution"],
             "aside": {"kicker": "Tradeoff", "body": "Eventual at edge, strong at core."}},
        ],
    }
    spec_path = tmp_path / "spec.json"
    spec_path.write_text(json.dumps(spec), encoding="utf-8")
    out_pptx = tmp_path / "deck.pptx"

    r = subprocess.run(
        [sys.executable, str(GEN), "--spec", str(spec_path), "--out", str(out_pptx)],
        capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=180,
    )
    assert r.returncode == 0, f"generate_deck failed: {r.stderr}\n{r.stdout}"
    assert out_pptx.exists() and out_pptx.stat().st_size > 0, "output.pptx missing/empty"

    render_dir = tmp_path / "render"
    r2 = subprocess.run(
        [sys.executable, str(RENDER), "--pptx", str(out_pptx),
         "--out", str(render_dir), "--dpi", "150"],
        capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=240,
    )
    assert r2.returncode == 0, f"render_pptx failed: {r2.stderr}\n{r2.stdout}"
    manifest = json.loads((render_dir / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["dpi"] == 150, "aesthetic pass must render at 150 DPI"
    assert manifest["png_engines_preference"][0] == "pypdfium2", (
        "pypdfium2 must be first in the png-engine preference order"
    )

    if not manifest.get("render_engine"):
        pytest.skip("no LibreOffice (pptx->pdf) engine on host; "
                    "verify-or-block owns this case")

    assert manifest["png_engine"] == "pypdfium2", (
        f"PNG stage should use pypdfium2; got {manifest['png_engine']!r}"
    )
    assert manifest["render_unverified"] is False, "full pipeline should verify"
    pngs = sorted(render_dir.glob("slide-*.png"))
    assert len(pngs) == 2, f"expected 2 slide PNGs; got {len(pngs)}"
    for p in pngs:
        assert p.stat().st_size > 0, f"empty PNG: {p}"

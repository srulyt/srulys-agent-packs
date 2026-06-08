"""C5 + C11 regression (hang-safe, no-LLM): the aesthetic-craft rubric
axis must exist and be wired into the critic, and the categorical chart
recipe must consume ``chart_palette`` + apply number formatting.

Tooling smoke test: doc-level assertions + a direct ``render_chart.py``
subprocess (stdin closed, timeout-bounded). No copilot CLI, no LLM judge.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]

# C5: consistent, selectable markers for the tooling smoke evals.
# These are fast, no-LLM, bounded-subprocess tests of the pack's scripts.
pytestmark = [pytest.mark.pack, pytest.mark.tooling]
PACK = REPO / "agent-packs" / "story-telling-agent" / ".github"
RUBRIC = PACK / "skills" / "pptx-visual-qa" / "references" / "visual-rubric.md"
CRITIC = PACK / "agents" / "deck-critic.agent.md"
CHART = PACK / "skills" / "render-visual" / "scripts" / "render_chart.py"


def test_aesthetic_craft_axis_in_rubric():
    """C5: the rubric defines a 1-5 aesthetic_craft axis with a min bar."""
    text = RUBRIC.read_text(encoding="utf-8")
    assert "aesthetic_craft" in text, "rubric missing aesthetic_craft axis"
    assert "1\u20135" in text or "1-5" in text or "(1\u20135)" in text, (
        "aesthetic_craft must be a 1-5 scale"
    )
    assert "aesthetic_craft >= 3" in text, "rubric must state the minimum passing bar"
    assert "aesthetic_craft <= 2" in text, "rubric must state the failing condition"


def test_critic_applies_aesthetic_craft_and_font_concern():
    """C5/B2: the critic scores aesthetic_craft and surfaces an
    unexpected display-font substitution as a CONCERN."""
    text = CRITIC.read_text(encoding="utf-8")
    assert "aesthetic_craft" in text, "deck-critic must score aesthetic_craft"
    assert "display_font_substituted" in text, (
        "deck-critic must surface display-font substitution as a CONCERN (B2)"
    )


def test_aesthetic_dpi_default_is_150():
    """C5: render_pptx default DPI bumped to 150 so the critic can resolve
    tracking / hairlines / tonal layering."""
    render = (PACK / "skills" / "pptx-visual-qa" / "scripts" / "render_pptx.py").read_text(encoding="utf-8")
    assert "DEFAULT_DPI = 150" in render, "aesthetic pass must default to 150 DPI"


def test_categorical_bars_consumes_chart_palette(tmp_path):
    """C11: categorical_bars cycles chart_palette.ramp, promotes a focal
    series, and formats value labels with thousands separators."""
    tokens = {
        "palette": {"background_light": "#FAFAF7", "background_dark": "#0B0B0C",
                    "primary_accent": "#E5482F", "secondary_accent": "#0B0B0C",
                    "text_on_light": "#0B0B0C", "text_on_dark": "#FAFAF7",
                    "text_secondary": "#6B6A66"},
        "chart_palette": {"focal": "#E5482F", "muted": "#6B6A66", "grid": "#D8D6CE",
                          "ramp": ["#E5482F", "#0B0B0C", "#6B6A66", "#B0341F",
                                   "#9C8E73", "#C9B8A0"]},
    }
    spec = {"labels": ["NA", "EMEA", "APAC", "LATAM", "MEA"],
            "values": [12500, 9800, 15200, 4300, 2100],
            "focal": "APAC", "y_label": "Revenue", "title": "Revenue by region"}
    tok_path = tmp_path / "tok.json"
    spec_path = tmp_path / "spec.json"
    out_png = tmp_path / "cat.png"
    tok_path.write_text(json.dumps(tokens), encoding="utf-8")
    spec_path.write_text(json.dumps(spec), encoding="utf-8")

    r = subprocess.run(
        [sys.executable, str(CHART), "--kind", "categorical_bars",
         "--spec", str(spec_path), "--tokens", str(tok_path),
         "--out", str(out_png), "--on-light"],
        capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=180,
    )
    assert r.returncode == 0, f"categorical_bars render failed: {r.stderr}\n{r.stdout}"
    assert out_png.exists() and out_png.stat().st_size > 0, "chart PNG missing/empty"


def test_number_formatter_thousands_and_units():
    """C11: _fmt_num applies thousands separators, drops trailing .0, and
    appends a unit suffix."""
    import importlib.util

    spec = importlib.util.spec_from_file_location("render_chart_mod", CHART)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    assert mod._fmt_num(12500) == "12,500"
    assert mod._fmt_num(3.0) == "3"
    assert mod._fmt_num(15200, " k") == "15,200 k"
    assert mod._fmt_num(42.5, "%") == "42.5%"

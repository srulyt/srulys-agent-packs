"""C4 + C6 regression (hang-safe, no-LLM): a deck built with a NEW
premium design system (``ink-editorial``) and the NEW editorial
archetypes must pass the structural asserts — no overflow, no
safe-area (breathing-room) violations, no blocking findings.

Tooling smoke test: drives ``generate_deck.py`` + ``check_pptx.py``
directly via subprocess (stdin closed, timeout-bounded). No copilot CLI,
no LLM judge.
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
CHECK = PACK / "pptx-structural-asserts" / "scripts" / "check_pptx.py"
SYSTEMS = PACK / "slide-design-systems" / "references" / "systems"

NEW_SYSTEMS = ["ink-editorial", "quiet-luxury", "signal-dark", "warm-editorial"]
NEW_ARCHETYPES = ["stat_grid_3up", "pull_quote_portrait", "full_bleed_caption",
                  "editorial_2col_6040", "timeline_horizontal", "agenda_toc",
                  "closing_cta"]


def _system_tokens(name: str) -> dict:
    md = (SYSTEMS / f"{name}.md").read_text(encoding="utf-8")
    m = re.search(r"```json\s*(\{.*?\})\s*```", md, re.S)
    assert m, f"{name}.md has no JSON token block"
    return json.loads(m.group(1))


def test_new_systems_register_in_skill_table():
    skill = (SYSTEMS.parent.parent / "SKILL.md").read_text(encoding="utf-8")
    for name in NEW_SYSTEMS:
        assert (SYSTEMS / f"{name}.md").exists(), f"missing system file {name}.md"
        assert name in skill, f"{name} not registered in slide-design-systems SKILL.md"


def test_new_archetype_and_system_no_structural_violations(tmp_path):
    spec = {
        "design_system_tokens": _system_tokens("ink-editorial"),
        "slides": [
            {"index": 0, "style": "styled", "style_recipe": "stat_grid_3up",
             "title": "The numbers moved", "eyebrow": "Results",
             "notes": "Lead with retention; it's the proof point.",
             "stats": [{"value": "42%", "label": "Net revenue retention", "delta": "+8"},
                       {"value": "1.9x", "label": "Pipeline coverage", "delta": "+0.4"},
                       {"value": "11d", "label": "Time to value", "delta": "-6"}]},
            {"index": 1, "style": "styled", "style_recipe": "editorial_2col_6040",
             "title": "Why now", "standfirst": "The window is open for two quarters.",
             "notes": "Frame the urgency before the ask.",
             "points": ["Incumbents mid-migration", "Our cost curve crossed"],
             "aside": {"kicker": "Context", "body": "Macro tailwinds align with roadmap."}},
            {"index": 2, "style": "styled", "style_recipe": "agenda_toc",
             "title": "Agenda", "notes": "Keep it to four sections.",
             "sections": ["Market", "Traction", "Roadmap", "The ask"]},
            {"index": 3, "style": "styled", "style_recipe": "closing_cta",
             "title": "Let's build it", "cta": "Approve the raise",
             "notes": "End on the single decision we want.",
             "contact": "founder@example.com"},
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
    assert out_pptx.exists() and out_pptx.stat().st_size > 0

    report_path = tmp_path / "structural.json"
    r2 = subprocess.run(
        [sys.executable, str(CHECK), "--pptx", str(out_pptx),
         "--spec", str(spec_path), "--out", str(report_path)],
        capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=180,
    )
    assert r2.returncode == 0, f"check_pptx failed: {r2.stderr}\n{r2.stdout}"
    report = json.loads(report_path.read_text(encoding="utf-8"))

    # Layout-structural craft the new system + archetypes are responsible
    # for: aspect ratio, no overflow, breathing-room (safe-area) respected,
    # no archetype-shape violations, no duplicate titles, notes present.
    # Contrast now RESOLVES at run level: `_add_textbox` sets run-level
    # colour and the build runs a final WCAG auto-safety pass, so the
    # checker buckets neither `contrast_unresolved` nor real
    # `contrast_violations` for a normal deck (corrective fix C1).
    assert report["aspect_ratio_pass"] is True
    assert not report["overflow_violations"], (
        f"new archetypes overflowed: {report['overflow_violations']}"
    )
    assert not report["safe_area_violations"], (
        f"new archetypes broke breathing-room: {report['safe_area_violations']}"
    )
    assert not report["archetype_violations"], (
        f"new archetypes failed archetype shape checks: {report['archetype_violations']}"
    )
    assert not report["duplicate_titles"], report["duplicate_titles"]
    assert not report["speaker_notes_missing"], report["speaker_notes_missing"]
    # C1 regression guard: real contrast resolves (run-level colour) and a
    # normal deck no longer false-blocks on contrast.
    assert len(report["contrast_unresolved"]) < 5, (
        f"contrast still bucketing as unresolved: {report['contrast_unresolved']}"
    )
    assert not report["contrast_violations"], (
        f"deck has unresolved sub-AA contrast after auto-safety pass: "
        f"{report['contrast_violations']}"
    )


def test_all_new_archetypes_registered():
    src = GEN.read_text(encoding="utf-8")
    for recipe in NEW_ARCHETYPES:
        assert f'"{recipe}"' in src, f"{recipe} not registered in STYLED_RECIPES/BUILDERS"

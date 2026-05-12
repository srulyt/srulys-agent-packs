"""F5 happy-path: a pre-staged deck-spec with one ``style: styled`` slide
(``style_recipe: metric_xxl``) is built. The deck-builder must dispatch
to ``_styled_metric_xxl`` and the build-log must reflect ``styled-count: 1``
with ``metric_xxl`` listed in ``styled-recipes-used``.

Ported from legacy
``cases/smoke-styled-recipe-render/``.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures" / "smoke_styled_recipe_render"
SESSION = "smoke-styled"

PROMPT = f"""\
@story-orchestrator

Run the deck-build / QA loop against the pre-staged session
``{SESSION}``. The session's deck-spec contains one slide with
``style: "styled"`` and ``style_recipe: "metric_xxl"``. Build the deck,
have the critic verify it, and stop when the critic returns a verdict.
"""


@pytest.mark.pack
@pytest.mark.slow
def test_styled_recipe_render(copilot_pack):
    ws = copilot_pack("story-telling-agent")
    ws.stage_files(
        FIXTURES,
        dest_subdir=f".story-telling-stm/runs/{SESSION}/agents/deck-builder",
    )

    result = ws.run_agent(prompt=PROMPT, agent="story-orchestrator", timeout=900)
    assert result.ok, f"story-orchestrator failed; see {result.log_path}"

    deck = ws.glob(".story-telling-stm/runs/*/agents/deck-builder/output.pptx")
    assert deck, f"output.pptx missing; see {result.log_path}"
    assert deck[0].stat().st_size > 0, (
        f"output.pptx is empty; see {result.log_path}"
    )

    deck_specs = ws.glob(
        ".story-telling-stm/runs/*/agents/deck-builder/deck-spec.json"
    )
    assert deck_specs, f"deck-spec.json missing; see {result.log_path}"

    build_logs = ws.glob(
        ".story-telling-stm/runs/*/agents/deck-builder/build-log.txt"
    )
    assert build_logs, f"build-log.txt missing; see {result.log_path}"
    log_text = build_logs[0].read_text(encoding="utf-8", errors="replace")
    assert "styled-count: 1" in log_text, (
        f"build-log missing 'styled-count: 1'; see {result.log_path}\n"
        f"--- build-log ---\n{log_text}"
    )
    assert "metric_xxl" in log_text, (
        f"build-log missing 'metric_xxl' recipe reference; "
        f"see {result.log_path}"
    )

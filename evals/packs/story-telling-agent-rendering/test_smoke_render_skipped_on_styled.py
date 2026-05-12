"""OQ5 regression: a styled-deck rendered with no soffice/libreoffice
on PATH must NOT ship with ``pass`` or ``pass_unverified``. The critic
must emit ``verdict: revise`` with blocking finding ``render_unverified``.

Ported from legacy
``cases/smoke-render-skipped-on-styled/``.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures" / "smoke_render_skipped_on_styled"
SESSION = "smoke-render-skipped"

PROMPT = f"""\
@story-orchestrator

Run the deck-build / QA loop against the pre-staged session
``{SESSION}``. The session's deck-spec contains a styled slide
(``style_recipe: hero_full_bleed``).

When the critic invokes ``render_pptx.py`` for QA, force the render
pipeline to skip by overriding PATH to a directory that contains none
of ``soffice``, ``libreoffice``, or ``unoconv`` (e.g. via
``env -i PATH=/tmp/empty python ...``). With ``render_engine=null``,
the critic MUST set ``verdict: revise`` and include
``render_unverified`` as a blocking finding -- it MUST NOT issue
``pass`` or ``pass_unverified`` for a styled deck.
"""


@pytest.mark.pack
@pytest.mark.slow
def test_render_skipped_on_styled_blocks(copilot_pack):
    ws = copilot_pack("story-telling-agent")
    ws.stage_files(
        FIXTURES,
        dest_subdir=f".story-telling-stm/runs/{SESSION}/agents/deck-builder",
    )

    result = ws.run_agent(prompt=PROMPT, agent="story-orchestrator", timeout=900)
    assert result.ok, f"story-orchestrator failed; see {result.log_path}"

    qa_reports = ws.glob(
        ".story-telling-stm/runs/*/agents/deck-critic/qa-report.json"
    )
    assert qa_reports, f"qa-report.json missing; see {result.log_path}"

    report = json.loads(qa_reports[0].read_text(encoding="utf-8"))
    status = (report.get("status") or "").lower()
    assert status not in ("pass", "pass_unverified"), (
        f"styled deck with skipped render must not pass; got status={status!r}; "
        f"see {result.log_path}"
    )
    raw = qa_reports[0].read_text(encoding="utf-8")
    assert "render_unverified" in raw, (
        f"qa-report missing 'render_unverified' blocking finding; "
        f"see {result.log_path}"
    )

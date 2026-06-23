"""F4 regression: a deck-spec with a low-contrast text/background pair
(``#BBBBBB`` text on ``#F5F6FA`` background, ratio < 2:1) must be
flagged via ``contrast_violations`` by the runtime contrast pipeline,
not silently downgraded to ``contrast_unresolved``.

Ported from legacy ``cases/smoke-low-contrast-fixture/``.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures" / "smoke_low_contrast_fixture"
SESSION = "smoke-low-contrast"

PROMPT = f"""\
@story-orchestrator

Run the deck-build / QA loop against the pre-staged session
``{SESSION}``. The deck-spec on disk sets slide 2 text to ``#BBBBBB``
on a ``#F5F6FA`` background -- a contrast ratio well below the WCAG
4.5:1 normal-text threshold. The critic must emit ``verdict: revise``
with blocking finding ``contrast_violations``.
"""


@pytest.mark.pack
@pytest.mark.slow
def test_low_contrast_fixture_blocks(agent_pack):
    ws = agent_pack("story-orchestrator")
    ws.stage_files(
        FIXTURES,
        dest_subdir=f".story-telling-stm/runs/{SESSION}/agents/deck-builder",
    )

    result = ws.run_agent(prompt=PROMPT, agent="story-orchestrator", timeout=900)
    if not result.usable:
        pytest.skip(result.unavailable_reason())
    assert result.ok, f"story-orchestrator failed; see {result.log_path}"

    qa_reports = ws.glob(
        ".story-telling-stm/runs/*/agents/deck-critic/qa-report.json"
    )
    assert qa_reports, f"qa-report.json missing; see {result.log_path}"
    raw = qa_reports[0].read_text(encoding="utf-8")
    assert "contrast_violations" in raw, (
        f"qa-report missing 'contrast_violations'; see {result.log_path}"
    )
    report = json.loads(raw)
    status = (report.get("status") or "").lower()
    assert status != "pass", (
        f"low-contrast must not produce pass verdict; got status={status!r}; "
        f"see {result.log_path}"
    )

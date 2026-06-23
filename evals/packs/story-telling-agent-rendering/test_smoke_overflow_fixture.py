"""F1 regression: a deck-spec with a slide that intentionally overflows
its body textbox is fed through the build/QA loop. The critic must
detect the overflow via ``check_pptx.py`` (Pillow real-metric pipeline)
and emit ``verdict: revise`` with blocking finding
``overflow_violations``.

Ported from legacy ``cases/smoke-overflow-fixture/``.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures" / "smoke_overflow_fixture"
SESSION = "smoke-overflow"

PROMPT = f"""\
@story-orchestrator

Run the deck-build / QA loop against the pre-staged session
``{SESSION}``. The deck-spec on disk contains an intentional text
overflow on slide 3 (body text exceeds the textbox bounds when
rendered with real Pillow metrics). The critic must catch this and
emit ``verdict: revise`` with blocking finding ``overflow_violations``.
"""


@pytest.mark.pack
@pytest.mark.slow
def test_overflow_fixture_blocks(agent_pack):
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
    assert "overflow_violations" in raw, (
        f"qa-report missing 'overflow_violations'; see {result.log_path}"
    )
    report = json.loads(raw)
    status = (report.get("status") or "").lower()
    assert status != "pass", (
        f"overflow must not produce pass verdict; got status={status!r}; "
        f"see {result.log_path}"
    )

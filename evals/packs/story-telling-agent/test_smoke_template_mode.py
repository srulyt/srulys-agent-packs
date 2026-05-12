"""Template-aware deck generation: when the user supplies a
``.pptx`` template, the deck-builder must invoke ``generate_deck.py``
with ``--template`` so the output deck inherits master slides and
theme. Verifies path round-trip (not theme correctness).

Ported from legacy ``cases/smoke-template-mode/``. The original case
expected the user to drop a real corporate template under
``inputs/templates/``; we generate a minimal placeholder via
``python-pptx`` so the test is hermetic.
"""
from __future__ import annotations

import json

import pytest

PROMPT = """\
@story-orchestrator

I have a corporate PowerPoint template at
``templates/corporate-2026.pptx`` in this workspace. I need you to use
it as the base -- output deck must inherit its master slides, theme
colors, and font choices.

**Audience**: customer advisory board (8 enterprise customers).

**Decision needed**: customers volunteer for a 6-week pilot of our
new analytics module.

**Facts**:
- 3 customers already on the waitlist (Acme, Globex, Initech).
- Pilot includes weekly check-ins + dedicated support engineer.
- We need 5 total commitments to greenlight the GA timeline.

**Tone**: warm, peer-to-peer. Customers are partners, not buyers.

When you reach the proposal, I will reply ``APPROVED``. When the deck
is built and QA-passed, return the path.

Important: deck-builder MUST pass
``--template templates/corporate-2026.pptx`` when invoking
``generate_deck.py``.
"""


def _stage_template(ws):
    pptx = pytest.importorskip(
        "pptx",
        reason="python-pptx not installed; required to generate template fixture",
    )
    template_dir = ws.root / "templates"
    template_dir.mkdir(parents=True, exist_ok=True)
    prs = pptx.Presentation()
    prs.slides.add_slide(prs.slide_layouts[6])
    prs.save(str(template_dir / "corporate-2026.pptx"))


@pytest.mark.pack
@pytest.mark.slow
def test_template_path_round_trip(copilot_pack):
    ws = copilot_pack("story-telling-agent")
    _stage_template(ws)

    result = ws.run_agent(prompt=PROMPT, agent="story-orchestrator", timeout=900)
    assert result.ok, f"story-orchestrator failed; see {result.log_path}"

    deck_specs = ws.glob(
        ".story-telling-stm/runs/*/agents/deck-builder/deck-spec.json"
    )
    assert deck_specs, f"deck-spec.json missing; see {result.log_path}"
    spec_text = deck_specs[0].read_text(encoding="utf-8")
    assert "corporate-2026.pptx" in spec_text or "templates" in spec_text, (
        f"deck-spec must reference the supplied template path; "
        f"see {result.log_path}"
    )

    # Look for evidence of --template in build-log or any captured
    # invocation log.
    build_logs = ws.glob(
        ".story-telling-stm/runs/*/agents/deck-builder/build-log.txt"
    )
    if build_logs:
        log_text = build_logs[0].read_text(encoding="utf-8", errors="replace")
        assert "--template" in log_text or "corporate-2026.pptx" in log_text, (
            f"build-log missing --template flag; see {result.log_path}"
        )

    pptx_out = ws.glob(
        ".story-telling-stm/runs/*/agents/deck-builder/output.pptx"
    )
    assert pptx_out and pptx_out[0].stat().st_size > 0, (
        f"output.pptx missing or empty; see {result.log_path}"
    )

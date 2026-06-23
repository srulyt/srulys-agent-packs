"""B3 regression: a SIMPLE-ONLY deck rendered with no soffice/libreoffice
on PATH must NOT silently ``pass`` / ``pass_unverified``. The critic must
emit the explicit user-decision verdict ``unverified-needs-user`` so the
orchestrator can surface install / ship-with-consent / abort.

This is the companion to ``test_smoke_render_skipped_on_styled.py`` (which
covers the STYLED-deck blocking path). Together they prove the
verify-or-block policy: no render engine ⇒ never a silent pass, regardless
of deck shape.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures" / "smoke_no_engine_user_gate"
RENDERS_FIXTURES = (
    Path(__file__).parent / "fixtures" / "smoke_no_engine_user_gate_renders"
)
SESSION = "smoke-no-engine-gate"

PROMPT = f"""\
@story-orchestrator

Run the deck-build / QA loop against the pre-staged session
``{SESSION}``. The session's deck-spec is a SIMPLE-ONLY deck (every slide
has ``style: "simple"`` — no styled recipe anywhere).

A render manifest has already been staged for this session at
``.story-telling-stm/runs/{SESSION}/agents/deck-critic/renders/manifest.json``
recording ``render_engine: null`` / ``render_unverified: true`` (it
simulates a host with no soffice/libreoffice/unoconv engine, portably and
independent of the OS running this eval). When the critic reaches the
render stage it MUST honor this pre-staged manifest as the render result
and treat the render pipeline as having produced no engine — do NOT
re-run ``render_pptx.py`` and do NOT overwrite the staged manifest.

With ``render_engine=null`` and a simple-only deck, the critic MUST NOT
issue ``pass`` or ``pass_unverified``. Per the B3 verify-or-block policy
it must emit ``verdict: unverified-needs-user`` (a user-decision gate),
and the orchestrator must surface install / ship-unverified-with-consent
/ abort. Stop once the decision gate is surfaced.
"""


@pytest.mark.pack
@pytest.mark.slow
def test_no_engine_simple_deck_surfaces_user_gate(agent_pack):
    ws = agent_pack("story-orchestrator")
    ws.stage_files(
        FIXTURES,
        dest_subdir=f".story-telling-stm/runs/{SESSION}/agents/deck-builder",
    )
    # Cross-platform way to force ``render_engine=null``: stage a render
    # manifest recording no available engine, instead of the POSIX-only
    # ``env -i PATH=/tmp/empty`` idiom (which is a no-op on a Windows SUT
    # host and would silently let a real engine satisfy the render,
    # weakening the B3 assertion).
    ws.stage_files(
        RENDERS_FIXTURES,
        dest_subdir=f".story-telling-stm/runs/{SESSION}/agents/deck-critic/renders",
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
    report = json.loads(raw)
    status = (report.get("status") or report.get("verdict") or "").lower()

    # The forbidden silent-pass outcomes (the old pass_unverified behaviour).
    assert status not in ("pass", "pass_unverified"), (
        f"simple-only deck with skipped render must NOT silently pass; "
        f"got status={status!r}; see {result.log_path}"
    )
    # The required explicit user-decision verdict.
    assert "unverified-needs-user" in raw or "unverified_needs_user" in raw, (
        f"qa-report missing 'unverified-needs-user' user-decision verdict; "
        f"see {result.log_path}\n--- qa-report ---\n{raw[:2000]}"
    )

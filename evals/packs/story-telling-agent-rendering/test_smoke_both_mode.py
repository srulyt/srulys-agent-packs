"""B2 smoke: ``output_mode=both`` produces a full-fidelity python-pptx deck
AND a Marp markdown source-of-record.

The contract for ``both`` (per the architecture and marp-engine/SKILL.md):
the deliverable pptx is built INDEPENDENTLY via python-pptx (not via
``marp --pptx``, which is image-based), and the Marp ``deck.md`` is the
source-of-record artifact. This test asserts BOTH artifacts are produced.
The Marp render itself may render-or-block depending on toolchain
availability (covered by ``test_smoke_marp_mode.py``); here we require the
pptx to exist regardless, because the python-pptx path does not depend on
marp-cli.

Hang-safety note: ``render_marp.py`` is self-bounding and non-interactive
(stdin closed, per-stage timeouts, process-tree kill on timeout), so the
Marp render can never wedge the SUT; the python-pptx deliverable and the
Marp ``deck.md`` source-of-record are produced regardless of toolchain
availability. The ``@pytest.mark.timeout`` below is only a secondary
backstop.
"""
from __future__ import annotations

from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures" / "smoke_both_mode"
SESSION = "smoke-both-mode"

PROMPT = f"""\
@story-orchestrator

Run the deck-build / QA loop against the pre-staged session
``{SESSION}``. The pre-staged ``intake.json`` sets ``output_mode: both``
and the deck-spec is a simple 3-slide deck.

For ``output_mode: both`` the builder must (a) build the deliverable
``output.pptx`` via python-pptx (full fidelity — NOT via ``marp --pptx``),
AND (b) author the Marp ``deck.md`` as the source-of-record. Produce both
artifacts. The Marp render may render or gracefully block depending on the
toolchain, but the python-pptx ``output.pptx`` must be produced regardless.
Stop when both artifacts exist (and the QA verdict is returned).
"""


@pytest.mark.pack
@pytest.mark.slow
@pytest.mark.timeout(960)  # belt-and-suspenders: just over run_agent's 900s
def test_output_mode_both_produces_pptx_and_marp(agent_pack):
    ws = agent_pack("story-orchestrator")
    ws.stage_files(
        FIXTURES / "intake.json",
        dest_subdir=f".story-telling-stm/runs/{SESSION}/agents/story-orchestrator",
    )
    ws.stage_files(
        FIXTURES / "deck-spec.json",
        dest_subdir=f".story-telling-stm/runs/{SESSION}/agents/deck-builder",
    )

    result = ws.run_agent(prompt=PROMPT, agent="story-orchestrator", timeout=900)
    if not result.usable:
        pytest.skip(result.unavailable_reason())
    assert result.ok, f"story-orchestrator failed; see {result.log_path}"

    # (a) python-pptx deliverable must exist and be non-empty.
    decks = ws.glob(".story-telling-stm/runs/*/agents/deck-builder/output.pptx")
    assert decks, (
        f"output.pptx missing — output_mode=both must still build the native "
        f"python-pptx deck; see {result.log_path}"
    )
    assert decks[0].stat().st_size > 0, (
        f"output.pptx is empty; see {result.log_path}"
    )

    # (b) Marp source-of-record markdown must exist.
    marp_md = ws.glob(".story-telling-stm/runs/*/agents/deck-builder/deck.md")
    assert marp_md, (
        f"deck.md (Marp source-of-record) missing — output_mode=both must "
        f"author Marp markdown; see {result.log_path}"
    )
    assert marp_md[0].stat().st_size > 0, (
        f"deck.md is empty; see {result.log_path}"
    )

"""B1/B2 smoke: ``output_mode=marp`` routes to the marp-engine path and
honours the verify-or-block policy.

The Marp toolchain (Node + @marp-team/marp-cli) may or may not be present
on the CI host, so this test asserts the INVARIANT rather than a fixed
outcome: the run must produce ``marp-renders/manifest.json``, and that
manifest must EITHER show rendered slides OR be an explicit graceful
block (``status: "blocked"`` with ``user_decision_required: true``). What
it must NEVER do is silently report success with no rendered slides and no
block — that would be unverified output.

Hang-safety note: ``render_marp.py`` is self-bounding and non-interactive
(stdin closed, per-stage timeouts, process-tree kill on timeout), so a
missing/interactive/slow toolchain produces a fast graceful BLOCK manifest
rather than an unbounded hang. The ``@pytest.mark.timeout`` below is only a
secondary backstop.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures" / "smoke_marp_mode"
SESSION = "smoke-marp-mode"

PROMPT = f"""\
@story-orchestrator

Run the deck-build / QA loop against the pre-staged session
``{SESSION}``. The pre-staged ``intake.json`` sets ``output_mode: marp``
and the deck-spec is a simple 3-slide deck.

For ``output_mode: marp`` the builder must load the ``marp-engine`` skill,
author ``deck.md`` + a ``theme.css`` generated from the design-system
tokens, and run ``marp-engine/scripts/render_marp.py`` to render and
verify. If the marp-cli toolchain is missing, the render manifest must
record ``status: "blocked"`` with ``user_decision_required: true`` and the
orchestrator must surface install / ship-unverified / abort — it must NOT
silently emit unverified Marp output. Stop when the deck is rendered or the
block decision is surfaced.
"""


@pytest.mark.pack
@pytest.mark.slow
@pytest.mark.timeout(960)  # belt-and-suspenders: just over run_agent's 900s
def test_output_mode_marp_renders_or_blocks(agent_pack):
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

    manifests = ws.glob(
        ".story-telling-stm/runs/*/agents/deck-builder/marp-renders/manifest.json"
    )
    assert manifests, (
        f"marp-renders/manifest.json missing — output_mode=marp did not route "
        f"to the marp-engine path; see {result.log_path}"
    )

    manifest = json.loads(manifests[0].read_text(encoding="utf-8"))
    slides = manifest.get("slides") or []
    status = (manifest.get("status") or "").lower()

    if slides:
        # Rendered path: marp produced PNGs for QA.
        assert status == "rendered", (
            f"manifest has slides but status={status!r}; see {result.log_path}"
        )
    else:
        # No PNGs ⇒ MUST be an explicit graceful block, never a silent pass.
        assert status == "blocked", (
            f"no marp slides rendered but status={status!r} (expected "
            f"'blocked'); silent unverified output is forbidden; "
            f"see {result.log_path}"
        )
        assert manifest.get("user_decision_required") is True, (
            f"blocked marp manifest must set user_decision_required=true; "
            f"see {result.log_path}"
        )

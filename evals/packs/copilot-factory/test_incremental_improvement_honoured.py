"""Incremental-improvement smoke: a tiny seed pack and a pre-baked
improvement-analysis are staged with state.json declaring
``improvement_strategy: "incremental"``, ``phase: "build"``,
``user_approved: true``. The user asks the factory to resume and apply
the improvement. The engineer must perform surgical edits (no rebuild)
and the critic must run review-prompts once.

Ported from legacy ``cases/incremental-improvement-honoured/``.
"""
from __future__ import annotations

from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures" / "incremental_improvement_honoured"

PROMPT = """\
A previous factory improvement session is already in the `build`
phase with `improvement_strategy: "incremental"` and the user has
approved the staged improvement-analysis.md. Please resume the
session under `.copilot-factory/sessions/2026-02-01-cafef00d/` and
**apply the staged improvement analysis incrementally**. Do NOT
re-design or rebuild. Only modify files explicitly flagged in the
analysis.
"""


@pytest.mark.pack
@pytest.mark.slow
@pytest.mark.judge
def test_incremental_improvement_honoured(copilot_pack, judge):
    ws = copilot_pack("copilot-factory")
    ws.stage_files(FIXTURES)

    result = ws.run_agent(prompt=PROMPT, agent="copilot-factory", timeout=900)
    assert result.ok, f"copilot-factory invocation failed; see {result.log_path}"

    manifest_files = ws.glob(
        ".copilot-factory/sessions/*/artifacts/build-manifest.json"
    )
    assert manifest_files, (
        f"expected a build-manifest.json to be produced; see {result.log_path}"
    )

    pack_writes = ws.glob("agent-packs/seed-pack/**/*.agent.md")
    assert pack_writes, (
        f"expected at least one seed-pack agent file to be modified; "
        f"see {result.log_path}"
    )

    verdict = judge(
        artifact=manifest_files[0].read_text(encoding="utf-8"),
        criteria=(
            "Score 1.0 if the build manifest's mode/strategy reflects an "
            "incremental improvement (not a full build), lists the seed-pack "
            "files that were modified, and contains no entries indicating the "
            "architect was invoked. Score 0.5 if it is incremental but missing "
            "the file-list. Score 0.0 if the manifest indicates a full rebuild."
        ),
        threshold=0.7,
    )
    assert verdict.passed, (
        f"incremental-improvement judge failed: {verdict.reasoning}; "
        f"see {result.log_path}"
    )

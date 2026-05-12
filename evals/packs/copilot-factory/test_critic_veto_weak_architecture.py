"""Critic-veto smoke: a pre-staged weak architecture (no agents/skills/
boundaries) is dropped under
``.copilot-factory/sessions/2026-01-15-deadbeef/`` and the user asks the
factory to resume that session and run review-arch only. The critic must
return a BLOCKING verdict captured in ``architecture-review.md``.

Ported from legacy ``cases/critic-veto-weak-architecture/``.
"""
from __future__ import annotations

from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures" / "critic_veto_weak_architecture"

PROMPT = """\
A previous factory session was paused with a half-finished architecture.
Please resume the session under
`.copilot-factory/sessions/2026-01-15-deadbeef/` and run **only the
architecture review phase** (`review-arch`). Do NOT re-design, do NOT
build, do NOT involve the engineer. Just delegate the architecture
review to `@factory-critic` and report the verdict.
"""


@pytest.mark.pack
@pytest.mark.slow
@pytest.mark.judge
def test_critic_blocks_weak_architecture(copilot_pack, judge):
    ws = copilot_pack("copilot-factory")
    ws.stage_files(FIXTURES)

    result = ws.run_agent(prompt=PROMPT, agent="copilot-factory", timeout=900)
    assert result.ok, f"copilot-factory invocation failed; see {result.log_path}"

    review_files = ws.glob(
        ".copilot-factory/sessions/*/artifacts/architecture-review.md"
    )
    assert review_files, (
        f"expected an architecture-review.md to be produced; see {result.log_path}"
    )

    verdict = judge(
        artifact=review_files[0].read_text(encoding="utf-8"),
        criteria=(
            "Score 1.0 if the review verdict is BLOCKING/FAIL and the reasoning "
            "cites at least two concrete defects from the staged architecture "
            "(missing agents section, missing file-access boundaries, missing "
            "skills, missing failure modes, etc.). Score 0.5 if the verdict is "
            "BLOCKING but the cited defects are vague or only one is concrete. "
            "Score 0.0 if the review issues PASS or if the verdict text is "
            "absent."
        ),
        threshold=0.7,
    )
    assert verdict.passed, (
        f"critic-veto judge failed: {verdict.reasoning}; see {result.log_path}"
    )

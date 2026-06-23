"""F3 regression: ``check_palettes.py`` (G1 preflight gate) catches a
rollback of customer-coral.md to its pre-fix state with AA-failing
contrast pairs. The critic must report the failing pairs in its
palette-preflight fence and refuse a passing verdict.

Ported from legacy
``cases/smoke-palette-preflight-rollback/``.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

ROLLBACK = (
    Path(__file__).parent
    / "fixtures"
    / "smoke_palette_preflight_rollback"
    / "customer-coral.rollback.md"
)

PROMPT = """\
You are the user. Issue the following request to ``@deck-critic``:

Simulate a rollback of ``customer-coral.md`` to its pre-F3-fix state.
The workspace already contains the rollback overwrite (background and
secondary accents reverted to AA-failing values) at:

    .github/skills/slide-design-systems/references/systems/customer-coral.md

Run the **G1 palette preflight** gate before any deck assembly:

1. Execute
   ``python .github/skills/slide-design-systems/scripts/check_palettes.py``
   against the (already-overwritten) systems directory.
2. Capture the exit code and the failing-pair JSON output.
3. Emit your standard ``palette-preflight`` fenced output contract
   block listing every system that failed, the failing token pairs,
   and the actual contrast ratios.
4. A non-zero exit from ``check_palettes.py`` is a BLOCKING gate per
   architecture S3 / G1 -- ``status`` must NOT be ``pass`` or
   ``pass_unverified``.

You do NOT need to assemble a deck.
"""


@pytest.mark.pack
@pytest.mark.slow
def test_palette_preflight_blocks_rollback(agent_pack):
    ws = agent_pack("story-orchestrator")
    # Overwrite the in-workspace customer-coral.md with the rollback
    # fixture.
    target = (
        ws.root
        / ".github"
        / "skills"
        / "slide-design-systems"
        / "references"
        / "systems"
        / "customer-coral.md"
    )
    assert target.parent.exists(), (
        f"slide-design-systems references dir not staged: {target.parent}"
    )
    target.write_text(ROLLBACK.read_text(encoding="utf-8"), encoding="utf-8")

    result = ws.run_agent(prompt=PROMPT, agent="deck-critic", timeout=600)
    if not result.usable:
        pytest.skip(result.unavailable_reason())
    assert result.ok, f"deck-critic failed; see {result.log_path}"

    qa_reports = ws.glob(
        ".story-telling-stm/runs/*/agents/deck-critic/qa-report.json"
    )
    assert qa_reports, f"qa-report.json missing; see {result.log_path}"
    report_text = qa_reports[0].read_text(encoding="utf-8")
    assert "customer-coral" in report_text, (
        f"qa-report does not name the failing 'customer-coral' system; "
        f"see {result.log_path}"
    )
    assert "failing_pairs" in report_text, (
        f"qa-report missing 'failing_pairs'; see {result.log_path}"
    )
    assert "#F87171" in report_text or "#FB923C" in report_text, (
        f"qa-report missing the rollback-introduced AA-failing token; "
        f"see {result.log_path}"
    )

    report = json.loads(report_text)
    status = (report.get("status") or "").lower()
    assert status not in ("pass", "pass_unverified"), (
        f"palette preflight failure must block; got status={status!r}; "
        f"see {result.log_path}"
    )

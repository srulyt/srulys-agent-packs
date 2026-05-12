"""Negative: orchestrator must persist the composer's draft fence VERBATIM
to ``product-brief.draft.md`` before any editing pass.

Best-effort port of legacy ``cases/negative-orchestrator-paraphrase/``:
the legacy harness diff-checked the persisted draft against the captured
fence body. Without trace capture, we instead assert (a) the draft
exists and is substantial, and (b) a judge inspects the draft for
paraphrase-style markers (rewording of headings, summary-collapses,
omitted bullets relative to the composer's mandated structure).
"""
from __future__ import annotations

from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures" / "negative_orchestrator_paraphrase"

PROMPT = """\
@brief-orchestrator

Build a brief from ``inputs/``. After the composer returns its
``product-brief-draft`` fence, the orchestrator MUST persist the
fence body byte-for-byte to ``product-brief.draft.md`` before any
editing pass. Paraphrasing or "improving" the body during persistence
is a violation.

Decision context: hiring plan for FY26. Audience: head of engineering.
"""


@pytest.mark.pack
@pytest.mark.slow
@pytest.mark.judge
def test_orchestrator_persists_draft_verbatim(copilot_pack, judge):
    ws = copilot_pack("product-brief")
    ws.stage_files(FIXTURES, dest_subdir="inputs")

    result = ws.run_agent(prompt=PROMPT, agent="brief-orchestrator", timeout=900)
    assert result.ok, f"brief-orchestrator failed; see {result.log_path}"

    drafts = ws.glob(
        ".product-brief-agent-stm/runs/*/agents/brief-composer/product-brief.draft.md"
    )
    assert drafts, f"composer draft missing; see {result.log_path}"
    final = ws.glob(
        ".product-brief-agent-stm/runs/*/agents/brief-orchestrator/product-brief.md"
    )
    assert final, f"final brief missing; see {result.log_path}"

    draft_text = drafts[0].read_text(encoding="utf-8")
    assert len(draft_text) > 400, (
        f"persisted draft is suspiciously short ({len(draft_text)} chars); "
        f"orchestrator may have summarised instead of persisting verbatim; "
        f"see {result.log_path}"
    )

    verdict = judge(
        artifact=draft_text,
        criteria=(
            "Score 1.0 if the persisted draft contains the full composer-style "
            "structure (multiple labelled sections such as Context, Evidence / "
            "Findings, Options or Recommendation, plus inline source citations) "
            "and shows no signs of orchestrator paraphrasing (no first-person "
            "orchestrator commentary, no 'summary:' compressions of bulleted "
            "lists, no removed evidence tables). Score 0.5 if the draft is "
            "structurally complete but obviously condensed. Score 0.0 if the "
            "draft reads as an orchestrator-written summary rather than a "
            "composer-authored decision brief."
        ),
        threshold=0.7,
    )
    assert verdict.passed, (
        f"verbatim-persistence judge failed: {verdict.reasoning}; "
        f"see {result.log_path}"
    )

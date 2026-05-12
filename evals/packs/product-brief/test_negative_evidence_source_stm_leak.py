"""Negative: no evidence-log entry, contradictions entry, or final-brief
source citation may reference a path under ``.product-brief-agent-stm/``
(working memory). STM files are NEVER valid evidence sources.

Ported from legacy ``cases/negative-evidence-source-stm-leak/``. Where
the legacy rubric inspected only the rubric-targets, the new test
greps the evidence-log and the final brief directly for the forbidden
prefix.
"""
from __future__ import annotations

from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures" / "negative_evidence_source_stm_leak"

PROMPT = """\
@brief-orchestrator

Build a decision-grade brief from the materials in ``inputs/``. All
evidence citations must reference user-provided source files (under
``inputs/``). Working-memory paths beginning with
``.product-brief-agent-stm/`` are NOT valid citations.

Decision context: prioritisation for the FY26 product roadmap.
Audience: VP Product.
"""


@pytest.mark.pack
@pytest.mark.slow
def test_no_stm_paths_cited_as_evidence(copilot_pack):
    ws = copilot_pack("product-brief")
    ws.stage_files(FIXTURES, dest_subdir="inputs")

    result = ws.run_agent(prompt=PROMPT, agent="brief-orchestrator", timeout=900)
    assert result.ok, f"brief-orchestrator failed; see {result.log_path}"

    evidence_logs = ws.glob(
        ".product-brief-agent-stm/runs/*/agents/evidence-analyst/evidence-log.md"
    )
    final_brief = ws.glob(
        ".product-brief-agent-stm/runs/*/agents/brief-orchestrator/product-brief.md"
    )
    assert evidence_logs, f"evidence-log missing; see {result.log_path}"
    assert final_brief, f"final brief missing; see {result.log_path}"

    forbidden = ".product-brief-agent-stm/"
    for path in evidence_logs + final_brief:
        text = path.read_text(encoding="utf-8")
        # Allow STM paths in metadata-style keys (e.g. file headers) but
        # forbid them from appearing inside markdown link/citation syntax.
        for marker in (f"({forbidden}", f"]({forbidden}", f"`{forbidden}"):
            assert marker not in text, (
                f"{path} contains a forbidden STM evidence citation "
                f"({marker!r}); see {result.log_path}"
            )

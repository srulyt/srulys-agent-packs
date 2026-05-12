"""Greenfield creation where the detective finds P0 gaps. Stop B
fires (interviewer generates <=12 questions); user provides answers;
detective re-runs; Stop A; APPROVE; drafter; critic. Asserts the
interview artifacts are produced and the drafter does not leave
``[TBD]`` placeholders for sections the user actually answered.

Ported from legacy
``cases/smoke-greenfield-context-missing-interview/``.
"""
from __future__ import annotations

from pathlib import Path

import pytest

FIXTURES = (
    Path(__file__).parent / "fixtures" / "greenfield_context_missing_interview"
)

PROMPT = """\
@spec-author write a PRD for **Workspace activity digest** -- a daily
summary of changes in a product workspace.

Treat this as an early-stage idea. I have no persona doc, no spike
notes, no reference links. You will need to interview me to fill
the gaps before drafting.

When you ask me clarifying questions (Stop B), I will answer them
all. When you then propose the structure (Stop A), I will reply
`APPROVE`.

## Pre-supplied answers (do not park; proceed straight through)

- **Stop 0 (output location):** `output_path: docs/specs/digest.md, spec_kind: mixed`
- **Stop B (interview answers) -- pre-supplied:** the interview
  answers covering all P0 questions are pre-staged at
  `interview-answers.md` in the workspace; treat them as the user's
  first reply to your interview, then proceed to drafting without
  parking.
- **Stop A (structure approval):** `APPROVE` (first ask)

The orchestrator should still invoke prd-interviewer once (so the
`interview-questions.md` artifact is produced and the rubric can
check it), then immediately apply the answers above and proceed.
"""


@pytest.mark.pack
@pytest.mark.slow
def test_greenfield_with_interview(copilot_pack):
    ws = copilot_pack("spec-author")
    ws.stage_files(FIXTURES, dest_subdir=".")

    result = ws.run_agent(prompt=PROMPT, agent="spec-author", timeout=1200)
    assert result.ok, f"spec-author failed; see {result.log_path}"

    assert ws.find_one("docs/specs/digest.md"), (
        f"specification missing; see {result.log_path}"
    )
    assert ws.glob(
        ".spec-author/sessions/*/artifacts/interview-questions.md"
    ), f"interview-questions.md missing; see {result.log_path}"
    assert ws.glob(
        ".spec-author/sessions/*/context/interview-answers.md"
    ) or ws.glob(
        ".spec-author/sessions/*/artifacts/interview-answers.md"
    ), f"interview-answers.md missing; see {result.log_path}"

    spec_text = ws.find_one("docs/specs/digest.md").read_text(encoding="utf-8")
    # Sections the user answered -- should not be left as TBD.
    answered_topics = ["Problem Statement", "Goals", "Personas", "Solution Summary"]
    for topic in answered_topics:
        assert f"[TBD - {topic}" not in spec_text, (
            f"section {topic!r} was answered but drafter left a TBD; "
            f"see {result.log_path}"
        )

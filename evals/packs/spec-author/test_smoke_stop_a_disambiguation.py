"""C4 Stop A binary-disambiguation + C5 partial-answer fallback. The
detective initially reports P0 gaps; the user's interview answers
leave one P0 unanswered, exercising the C5 retry; at Stop A the
user's first replies are ambiguous before APPROVE. Asserts the
final spec contains a ``[TBD - interview question .* unanswered]``
placeholder and an Open Questions entry referencing the unanswered
P0; no CHANGELOG (creation mode).

Ported from legacy ``cases/smoke-stop-a-disambiguation/``.

The legacy harness scripted multi-turn user replies via
``scripted_user``. The pytest harness is single-turn; the prompt
folds the simulated turn-state into the user instructions, matching
the legacy fixture's "non-interactive run" framing.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures" / "stop_a_disambiguation"

PROMPT = """\
@spec-author write a PRD for **Workspace activity digest** -- a daily
summary of changes in a product workspace.

This is an early-stage idea. I have no persona doc, no spike notes,
no reference links. You will need to interview me.

Notes for this run:
- I will answer most of your interview questions but not all of
  them. I won't have a good answer to the rollout-risk question
  even after a follow-up.
- When you propose the structure (Stop A), my first replies are
  ambiguous; treat the simulated final reply as APPROVE.

## Pre-supplied answers (do not park; proceed straight through)

- **Stop 0:** `output_path: docs/specs/digest.md, spec_kind: product`
- **Stop B (interview answers):** the partial answers covering 4 of
  5 P0 questions are pre-staged at `interview-answers-partial.md`;
  treat as the user's reply after exactly one interview retry; the
  rollout-risk P0 stays unanswered. Use a
  `[TBD - interview question rollout-risk unanswered]` placeholder
  and an Open Questions entry, exercising the C5 partial-answer
  fallback.
- **Stop A:** simulate two ambiguous replies followed by APPROVE.
  Set `stop_a_disambiguation_attempts == 2` in `state.json`.

No CHANGELOG (creation mode).
"""


@pytest.mark.pack
@pytest.mark.slow
def test_stop_a_disambiguation_and_partial_answer(agent_pack):
    ws = agent_pack("spec-author")
    ws.stage_files(FIXTURES, dest_subdir=".")

    result = ws.run_agent(prompt=PROMPT, agent="spec-author", timeout=1200)
    if not result.usable:
        pytest.skip(result.unavailable_reason())
    assert result.ok, f"spec-author failed; see {result.log_path}"

    spec = ws.find_one("docs/specs/digest.md")
    assert spec, f"spec missing; see {result.log_path}"
    text = spec.read_text(encoding="utf-8")

    assert re.search(
        r"\[TBD\s*[-\u2014]\s*interview question\s+\S+\s+unanswered\]", text
    ), (
        f"spec must contain a TBD placeholder for the unanswered P0; "
        f"see {result.log_path}"
    )
    assert re.search(r"(?i)open questions", text), (
        f"spec must contain an Open Questions section; "
        f"see {result.log_path}"
    )

    interviews = ws.glob(
        ".spec-author/sessions/*/artifacts/interview-questions.md"
    )
    assert interviews, f"interview-questions.md missing; see {result.log_path}"

    changelogs = ws.glob("**/CHANGELOG.md")
    assert not changelogs, (
        f"creation mode must NOT write CHANGELOG.md; found {changelogs}; "
        f"see {result.log_path}"
    )

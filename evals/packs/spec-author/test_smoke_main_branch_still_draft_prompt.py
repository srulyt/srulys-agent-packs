"""V5/V6 main-branch-still-draft prompt: the branch probe returns
``main``, the spec is ``Status: draft``, and the user did not state
mode in the current turn. The orchestrator must park at
``awaiting-mode-decision``, present the V6 verbatim
PUBLISH/KEEP-DRAFT/ABORT prompt, accept the scripted KEEP-DRAFT,
fire the pre-merge reminder, and leave ``Status: draft`` unchanged.

Ported from legacy ``cases/smoke-main-branch-still-draft-prompt/``.
"""
from __future__ import annotations

from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures" / "main_branch_still_draft_prompt"

PROMPT = """\
@spec-author update `docs/specs/quick-toggle.md` -- please add a
quick note to the "Out of Scope" section saying we won't add
per-channel preferences until at least Q3.

That's the only edit. (Note: I have not specified `STATUS:` or any
publish gesture in this prompt -- the orchestrator should run its
mode-decision logic.)

## Pre-supplied answers (do not park; proceed straight through)

- **Mode decision (`awaiting-mode-decision`):** `KEEP-DRAFT` --
  this stays a draft; do NOT publish.
- **Stop A (structure approval):** `APPROVE` (first ask)

The orchestrator should still emit the mode-decision prompt /
spec-status block in its output, but it must NOT pause for stdin.
"""


@pytest.mark.pack
@pytest.mark.slow
def test_main_branch_still_draft_keep_draft(agent_pack):
    ws = agent_pack("spec-author")
    ws.stage_files(FIXTURES, dest_subdir=".")

    result = ws.run_agent(prompt=PROMPT, agent="spec-author", timeout=900)
    if not result.usable:
        pytest.skip(result.unavailable_reason())
    assert result.ok, f"spec-author failed; see {result.log_path}"

    spec = ws.find_one("docs/specs/quick-toggle.md")
    assert spec, f"spec missing; see {result.log_path}"
    text = spec.read_text(encoding="utf-8")

    assert "Status: draft" in text or "status: draft" in text.lower(), (
        f"KEEP-DRAFT must leave Status: draft unchanged; "
        f"see {result.log_path}"
    )
    assert "0.0.1-draft" in text or "-draft" in text, (
        f"draft version suffix must remain; see {result.log_path}"
    )

    changelogs = ws.glob("**/CHANGELOG.md")
    assert not changelogs, (
        f"KEEP-DRAFT must NOT write a CHANGELOG; found {changelogs}; "
        f"see {result.log_path}"
    )

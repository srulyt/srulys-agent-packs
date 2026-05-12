"""V11 re-draft cycle: the user edits a published spec
(``Status: published, Version: 0.1.0``). The drafter enters a
re-draft window: working version becomes ``0.1.1-draft`` (auto-MINOR
for additive change), Status flips to ``draft``, prior-published IDs
remain frozen, the new FR gets the next-available ID. NO CHANGELOG
mutation during the re-draft window.

Ported from legacy ``cases/smoke-redraft-of-published/``.
"""
from __future__ import annotations

from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures" / "redraft_of_published"

PROMPT = """\
@spec-author update `docs/specs/quick-toggle.md` -- please add a new
FR for **keyboard shortcut support** (Ctrl+Shift+T) so users can
flip the toggle without leaving the keyboard.

This is currently a published spec at v0.1.0. The keyboard FR is
additive (no behaviour change to existing FRs). I'm on a feature
branch, NOT trunk. No publish intent in this turn -- please re-draft
and we'll publish the bump in a follow-up turn.

## Pre-supplied answers (do not park; proceed straight through)

- **Stop A (structure approval):** `APPROVE` (first ask)

Proceed end-to-end without waiting for further user input.
"""


@pytest.mark.pack
@pytest.mark.slow
def test_redraft_of_published(copilot_pack):
    ws = copilot_pack("spec-author")
    ws.stage_files(FIXTURES, dest_subdir=".")

    result = ws.run_agent(prompt=PROMPT, agent="spec-author", timeout=900)
    assert result.ok, f"spec-author failed; see {result.log_path}"

    spec = ws.find_one("docs/specs/quick-toggle.md")
    assert spec, f"spec missing; see {result.log_path}"
    text = spec.read_text(encoding="utf-8")

    assert "0.1.1-draft" in text, (
        f"working version must be 0.1.1-draft; see {result.log_path}"
    )
    assert "Status: draft" in text or "status: draft" in text.lower(), (
        f"Status must flip to draft during re-draft window; "
        f"see {result.log_path}"
    )
    assert "keyboard" in text.lower() or "Ctrl+Shift+T" in text, (
        f"new keyboard FR must appear; see {result.log_path}"
    )

    # CHANGELOG must NOT have been mutated this turn -- the re-draft
    # window doesn't add changelog entries. The fixture ships an
    # existing CHANGELOG.md with v0.1.0 only; assert no v0.1.1 entry.
    changelog = ws.find_one("docs/specs/CHANGELOG.md")
    if changelog:
        cl = changelog.read_text(encoding="utf-8")
        assert "0.1.1" not in cl, (
            f"re-draft must NOT add CHANGELOG entry for 0.1.1 "
            f"(V3/OQ-5); see {result.log_path}"
        )

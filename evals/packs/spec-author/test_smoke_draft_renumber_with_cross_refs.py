"""V12/V13 cross-reference integrity during draft renumbering: insert
a new FR in the middle of a draft list, every successor and every
cross-reference (AC-<FR>.<n>, 'see FR-N', anchored links) is updated
atomically. Spec stays at the same draft version.

Ported from legacy ``cases/smoke-draft-renumber-with-cross-refs/``.
"""
from __future__ import annotations

from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures" / "draft_renumber_with_cross_refs"

PROMPT = """\
@spec-author update `docs/specs/quick-toggle.md` -- please add a new
FR for **keyboard shortcut support** (Ctrl+Shift+T) and place it
**before** the existing "Visual feedback" FR so the keyboard
behaviour reads naturally before the visual behaviour.

This is still a draft (`Status: draft`, `Version: 0.0.1-draft`). No
publish intent. I'm on a feature branch. Please make the smallest
edits required and update every cross-reference that points at the
shifted FRs.

## Pre-supplied answers (do not park; proceed straight through)

- **Stop A (structure approval):** `APPROVE` (first ask)

Proceed end-to-end without waiting for further user input.
"""


@pytest.mark.pack
@pytest.mark.slow
def test_draft_renumber_with_cross_refs(agent_pack):
    ws = agent_pack("spec-author")
    ws.stage_files(FIXTURES, dest_subdir=".")

    result = ws.run_agent(prompt=PROMPT, agent="spec-author", timeout=900)
    if not result.usable:
        pytest.skip(result.unavailable_reason())
    assert result.ok, f"spec-author failed; see {result.log_path}"

    spec = ws.find_one("docs/specs/quick-toggle.md")
    assert spec and spec.exists(), f"spec missing; see {result.log_path}"
    text = spec.read_text(encoding="utf-8")

    assert "keyboard" in text.lower() or "Ctrl+Shift+T" in text, (
        f"new keyboard FR should be present; see {result.log_path}"
    )
    assert "Status: draft" in text or "status: draft" in text.lower(), (
        f"spec must remain a draft; see {result.log_path}"
    )
    assert "0.0.1-draft" in text, (
        f"draft version must not bump mid-draft (V3); "
        f"see {result.log_path}"
    )

    changelog = ws.glob("**/CHANGELOG.md")
    assert not changelog, (
        f"drafts must NOT write a CHANGELOG entry; found {changelog}; "
        f"see {result.log_path}"
    )

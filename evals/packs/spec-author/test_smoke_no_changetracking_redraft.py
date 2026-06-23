"""Req #1 (update / re-draft mode, half 2 of 2): a re-draft of a
published spec MUST NOT add any in-spec change-tracking artefact
in the working body AND MUST NOT mutate the prior `CHANGELOG.md`.

Reuses the ``redraft_of_published`` fixture (published v0.1.0 spec
with sibling CHANGELOG.md). The user adds a new FR but supplies no
publish intent.

Asserts:

- Working version is `<next>-draft` (re-draft window open).
- No `## Changes since`, `## Revision History`, `## Changelog`, or
  `## What's Changed` heading anywhere in the spec body.
- No inline `[Changed in v...]` marker.
- The fixture's pre-existing CHANGELOG.md (v0.1.0) was NOT mutated
  with a v0.1.1 entry.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures" / "redraft_of_published"

PROMPT = """\
@spec-author update `docs/specs/quick-toggle.md` -- please add a new
FR for **keyboard shortcut support** (Ctrl+Shift+T) so users can
flip the toggle without leaving the keyboard.

This is currently a published spec at v0.1.0. The keyboard FR is
additive. I'm on a feature branch, NOT trunk. No publish intent in
this turn -- please re-draft and we'll publish in a follow-up turn.

## Pre-supplied answers (do not park; proceed straight through)

- **Stop A (structure approval):** `APPROVE` (first ask)

Proceed end-to-end without waiting for further user input.
"""


@pytest.mark.pack
@pytest.mark.slow
def test_redraft_has_no_change_tracking(agent_pack):
    ws = agent_pack("spec-author")
    ws.stage_files(FIXTURES, dest_subdir=".")

    result = ws.run_agent(prompt=PROMPT, agent="spec-author", timeout=900)
    if not result.usable:
        pytest.skip(result.unavailable_reason())
    assert result.ok, f"spec-author failed; see {result.log_path}"

    spec = ws.find_one("docs/specs/quick-toggle.md")
    assert spec, f"spec missing; see {result.log_path}"
    text = spec.read_text(encoding="utf-8")

    # Re-draft window open.
    assert "0.1.1-draft" in text, (
        f"working version must be 0.1.1-draft; see {result.log_path}"
    )

    forbidden_headings = [
        "## Changes since",
        "## Revision History",
        "## Changelog",
        "## What's Changed",
    ]
    for needle in forbidden_headings:
        assert needle not in text, (
            f"re-draft spec body MUST NOT contain {needle!r} "
            f"(prd-evolution §5 / d7.draft-no-change-tracking); "
            f"see {result.log_path}"
        )

    assert not re.search(r"\[Changed in v[0-9]", text), (
        f"re-draft spec MUST NOT contain inline `[Changed in vX.Y]` "
        f"markers; see {result.log_path}"
    )

    # Prior CHANGELOG.md must be untouched -- no v0.1.1 entry.
    changelog = ws.find_one("docs/specs/CHANGELOG.md")
    assert changelog, (
        f"fixture CHANGELOG.md must remain present; see {result.log_path}"
    )
    cl = changelog.read_text(encoding="utf-8")
    assert "0.1.1" not in cl, (
        f"re-draft must NOT add CHANGELOG entry for 0.1.1 "
        f"(V3 / V17 / OQ-5); see {result.log_path}"
    )

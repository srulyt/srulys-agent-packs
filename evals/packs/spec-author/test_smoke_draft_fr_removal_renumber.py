"""F4 draft-branch regression: remove FR-03 from a 5-FR draft,
renumber successors, atomically update every cross-reference, and
leave NO ``[Deprecated]`` stub or CHANGELOG entry (drafts do not log).

Ported from legacy ``cases/smoke-draft-fr-removal-renumber/``.
"""
from __future__ import annotations

from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures" / "draft_fr_removal_renumber"

PROMPT = """\
@spec-author update `docs/specs/notif-prefs.md`. Please **remove
FR-03** (the inline muted-badge requirement) entirely -- we're not
going to ship it.

This is still a draft (`Status: draft`). Renumber the successor FRs
and update every cross-reference (in ACs, risks, open questions,
prose) to point at the new IDs. Do NOT leave a `[Deprecated]` stub --
delete it cleanly.

## Pre-supplied answers (do not park; proceed straight through)

- **Stop A (structure approval):** `APPROVE` (first ask)

Proceed end-to-end without waiting for further user input.
"""


@pytest.mark.pack
@pytest.mark.slow
def test_draft_fr_removal_renumber(agent_pack):
    ws = agent_pack("spec-author")
    ws.stage_files(FIXTURES, dest_subdir=".")

    result = ws.run_agent(prompt=PROMPT, agent="spec-author", timeout=900)
    if not result.usable:
        pytest.skip(result.unavailable_reason())
    assert result.ok, f"spec-author failed; see {result.log_path}"

    spec = ws.find_one("docs/specs/notif-prefs.md")
    assert spec and spec.exists(), f"spec missing; see {result.log_path}"
    text = spec.read_text(encoding="utf-8")

    assert "FR-03" in text and "Quiet-hours window" in text, (
        f"FR-03 should be the renumbered ex-FR-04 (quiet-hours); "
        f"see {result.log_path}"
    )
    assert "FR-04" in text and "Test-notification button" in text, (
        f"FR-04 should be the renumbered ex-FR-05 (test-button); "
        f"see {result.log_path}"
    )
    assert "FR-05" not in text, (
        f"FR-05 must not survive after renumber; see {result.log_path}"
    )
    assert "[Deprecated" not in text and "[Removed" not in text, (
        f"draft removal must NOT leave a deprecation stub; "
        f"see {result.log_path}"
    )
    assert "muted badge" not in text.lower(), (
        f"original FR-03 'muted badge' content must be deleted; "
        f"see {result.log_path}"
    )

    changelog = ws.glob("**/CHANGELOG.md")
    assert not changelog, (
        f"drafts must NOT write a CHANGELOG entry (V3); "
        f"found {changelog}; see {result.log_path}"
    )

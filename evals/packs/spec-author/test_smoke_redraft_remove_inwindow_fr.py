"""Req #2 inside a re-draft window for items added during the same
window: removed FR is deleted outright with no marker, no Open-
Question stub, no historical mention.

Reuses the ``draft_fr_removal_renumber`` fixture (a draft spec with
FR-01..FR-05). Although the fixture is an initial-draft (not a
re-draft over a published prior), the §3a semantics are identical
under interpretation (a): every draft-body removal deletes
outright, regardless of how the spec entered draft state.

Asserts:

- FR-03 (the muted-badge requirement) is gone.
- Successors renumbered contiguously (no gap).
- No `[Deprecated]` / `[Removed]` marker.
- No Open Question entry mentioning the deleted FR-03.
- No "Removed in this draft" / "formerly FR-" prose anywhere.
- No `## Changes since` / `## Revision History` / `## Changelog`
  heading (covers req #1 jointly).
"""
from __future__ import annotations

from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures" / "draft_fr_removal_renumber"

PROMPT = """\
@spec-author update `docs/specs/notif-prefs.md`. Please **remove
FR-03** (the inline muted-badge requirement) entirely -- we're not
going to ship it.

Still a draft (`Status: draft`). Renumber successors and update
every cross-reference. Do NOT leave a `[Deprecated]` stub, an Open
Question entry, or any historical mention of muted-badge -- delete
it cleanly. Leave NO residual trace.

## Pre-supplied answers (do not park; proceed straight through)

- **Stop A (structure approval):** `APPROVE` (first ask)

Proceed end-to-end without waiting for further user input.
"""


@pytest.mark.pack
@pytest.mark.slow
def test_redraft_remove_inwindow_fr_no_residue(copilot_pack):
    ws = copilot_pack("spec-author")
    ws.stage_files(FIXTURES, dest_subdir=".")

    result = ws.run_agent(prompt=PROMPT, agent="spec-author", timeout=900)
    assert result.ok, f"spec-author failed; see {result.log_path}"

    spec = ws.find_one("docs/specs/notif-prefs.md")
    assert spec, f"spec missing; see {result.log_path}"
    text = spec.read_text(encoding="utf-8")
    lower = text.lower()

    # FR-03 the muted-badge content is gone; successors renumbered.
    assert "muted badge" not in lower, (
        f"original FR-03 'muted badge' content must be deleted; "
        f"see {result.log_path}"
    )
    assert "Quiet-hours window" in text, (
        f"renumbered FR-03 (ex-FR-04 quiet-hours) must be present; "
        f"see {result.log_path}"
    )
    assert "FR-05" not in text, (
        f"FR-05 must not survive after renumber (contiguity); "
        f"see {result.log_path}"
    )

    # No deprecation / removal marker, no historical mention.
    assert "[Deprecated" not in text and "[Removed" not in text, (
        f"draft removal must NOT leave [Deprecated] / [Removed] "
        f"marker; see {result.log_path}"
    )
    assert "formerly fr-" not in lower and "formerly muted" not in lower, (
        f"draft removal must NOT leave 'formerly ...' historical "
        f"prose; see {result.log_path}"
    )
    assert "removed in" not in lower, (
        f"draft removal must NOT narrate 'removed in this draft'; "
        f"see {result.log_path}"
    )

    # Open Questions must not mention the deleted FR by content.
    # (We don't ban an "Open Questions" section; we ban its OQ entries
    # from re-introducing the removed item.)
    assert "muted-badge" not in lower and "muted badges" not in lower, (
        f"Open Questions / Risks must not reintroduce the removed "
        f"FR-03 by content; see {result.log_path}"
    )

    # Joint coverage with req #1: no change-tracking heading.
    for needle in ("## Changes since", "## Revision History", "## Changelog"):
        assert needle not in text, (
            f"draft body MUST NOT contain {needle!r}; "
            f"see {result.log_path}"
        )

    # No CHANGELOG.md (drafts do not log).
    changelogs = ws.glob("**/CHANGELOG.md")
    assert not changelogs, (
        f"drafts must NOT write a CHANGELOG entry (V3); "
        f"found {changelogs}; see {result.log_path}"
    )

"""Req #2 + interpretation (a): removing a prior-published FR in a
re-draft window (NO publish intent) MUST result in:

- FR-03 deleted from the working draft body (no `[Deprecated]`
  marker, no `[Removed]` marker, no stub heading, no historical
  prose).
- The cross-references to FR-03 either removed or rewritten in
  the working draft (V12).
- Other prior-published IDs (FR-04, FR-05) NOT renumbered
  (V9 ID-immutability is permanent).
- No `## Changes since vN` preamble (req #1 jointly).
- `CHANGELOG.md` NOT mutated (no publish intent).

The matching publish-time re-materialisation behaviour
(`pending_published_id_deletions` → published-artefact
`[Deprecated in vX.Y]` stub) is covered by the existing
`test_smoke_published_fr_removal_deprecate.py`, which has explicit
publish intent in its prompt.

Reuses the ``published_fr_removal_deprecate`` fixture (published
v1.2.0 spec with FR-01..FR-05).
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures" / "published_fr_removal_deprecate"

PROMPT = """\
@spec-author update `docs/specs/notif-prefs.md`. Please **remove
FR-03** (inline muted-badge) -- we're not going to keep it. Delete
it cleanly from the working draft. Do NOT leave a `[Deprecated]`
stub or any historical mention in the draft body.

This spec is currently `Status: published, Version: 1.2.0`. I'm on
a feature branch, NOT trunk. **No publish intent in this turn** --
please open a re-draft window and we'll publish in a follow-up turn.

## Pre-supplied answers (do not park; proceed straight through)

- **Stop A (structure approval):** `APPROVE` (first ask)

Proceed end-to-end without waiting for further user input.
"""


@pytest.mark.pack
@pytest.mark.slow
def test_redraft_remove_published_fr_has_no_marker(copilot_pack):
    ws = copilot_pack("spec-author")
    ws.stage_files(FIXTURES, dest_subdir=".")

    result = ws.run_agent(prompt=PROMPT, agent="spec-author", timeout=900)
    assert result.ok, f"spec-author failed; see {result.log_path}"

    spec = ws.find_one("docs/specs/notif-prefs.md")
    assert spec, f"spec missing; see {result.log_path}"
    text = spec.read_text(encoding="utf-8")
    lower = text.lower()

    # Re-draft window opened.
    assert "Status: draft" in text or "status: draft" in lower, (
        f"Status must flip to draft during re-draft window; "
        f"see {result.log_path}"
    )
    assert "-draft" in text, (
        f"working version must carry -draft suffix during re-draft; "
        f"see {result.log_path}"
    )

    # ----- Interpretation (a): FR-03 GONE from draft body, no marker. -----
    # Heading must be absent.
    assert not re.search(r"^###\s*FR-03\b", text, re.MULTILINE), (
        f"FR-03 heading must be DELETED from the working draft "
        f"body (interpretation (a); prd-evolution §3b draft-side); "
        f"see {result.log_path}"
    )
    assert "muted badge" not in lower and "muted-badge" not in lower, (
        f"FR-03 'muted badge' body content must be deleted from the "
        f"working draft; see {result.log_path}"
    )
    assert "[Deprecated" not in text and "[Removed" not in text, (
        f"draft body MUST NOT carry [Deprecated] / [Removed] markers "
        f"-- those re-materialise in the published artefact at "
        f"publish-time only (V8 step 4a); see {result.log_path}"
    )

    # V9 ID-immutability over prior-published IDs: FR-04, FR-05 NOT renumbered.
    assert "FR-04" in text and "Quiet-hours window" in text, (
        f"FR-04 (Quiet-hours window) must remain frozen at FR-04 "
        f"(V9 permanent over prior-published IDs); see {result.log_path}"
    )
    assert "FR-05" in text and "Test-notification button" in text, (
        f"FR-05 (Test-notification button) must remain frozen at "
        f"FR-05 (V9 permanent); see {result.log_path}"
    )

    # Req #1 jointly: no change-tracking artefacts in draft body.
    for needle in ("## Changes since", "## Revision History", "## Changelog"):
        assert needle not in text, (
            f"draft body MUST NOT contain {needle!r} "
            f"(prd-evolution §5); see {result.log_path}"
        )
    assert not re.search(r"\[Changed in v[0-9]", text), (
        f"draft spec MUST NOT contain inline `[Changed in vX.Y]` "
        f"markers; see {result.log_path}"
    )

    # CHANGELOG must NOT have been mutated (no publish intent).
    changelog = ws.find_one("docs/specs/CHANGELOG.md")
    if changelog:
        cl = changelog.read_text(encoding="utf-8")
        # Fixture may ship a prior CHANGELOG with v1.2.0 entries.
        # No v1.3 entry must appear during the re-draft.
        assert "1.3.0" not in cl and "v1.3" not in cl, (
            f"re-draft must NOT add CHANGELOG entry for v1.3 "
            f"(V3 / V17); see {result.log_path}"
        )

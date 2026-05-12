"""Update mode: re-draft an existing published spec WITHOUT publish
intent. Per the 2026-05-12 user requirements:

- **Req #1 (no change-tracking in draft):** the working draft MUST
  NOT contain a ``## Changes since vN`` preamble, a "Revision
  History" / "Changelog" section, or any inline
  ``[Changed in v...]`` marker. Git is the history during draft.
- **Req #2 (removed FRs deleted, not annotated) — interpretation
  (a):** the user asks to remove FR-07 (prior-published). The
  working draft body MUST NOT carry a ``[Deprecated]`` /
  ``[Removed]`` marker for FR-07; the body must read as if FR-07
  never existed. The marker is re-materialised in the published
  artefact at the next publish transition only — that path is
  exercised by ``smoke-redraft-remove-published-fr-no-marker``
  and the existing ``smoke-published-fr-removal-deprecate``.
- **No CHANGELOG mutation:** no publish intent in this turn ⇒ no
  CHANGELOG entry for the next version.

Replaces the legacy assertions ("Changes since v1" preamble, FR-07
``[Deprecated]`` marker, CHANGELOG ``### Added`` / ``### Deprecated``
entries) which became forbidden under the new requirements.
"""
from __future__ import annotations

from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures" / "update_existing_spec"

PROMPT = """\
@spec-author update the existing spec at `fixtures/prior-spec-v1.md`.

Changes I want:

1. **Add a new FR** for keyboard shortcuts: users should be able to
   trigger the top three quick actions (open, dismiss, snooze) via
   `o`, `d`, `s` from the digest panel.
2. **Remove FR-07** "mouse-only quick actions" entirely -- it's
   superseded by the new keyboard-shortcuts FR. Delete it; do NOT
   leave a deprecation stub or any historical mention in the
   working draft.

This is a re-draft cycle, NOT a publish. I'm on a feature branch.
No publish intent in this turn -- please re-draft and we'll publish
the bump in a follow-up turn.

## Pre-supplied answers (do not park; proceed straight through)

- **Stop 0 (output location):** `output_path: docs/specs/digest.md, spec_kind: technical`
- **Stop A (structure approval):** `APPROVE` (first ask)

Proceed end-to-end without waiting for further user input.
"""


@pytest.mark.pack
@pytest.mark.slow
def test_update_existing_spec_redraft_no_changetracking(copilot_pack):
    ws = copilot_pack("spec-author")
    ws.stage_files(FIXTURES, dest_subdir=".")

    result = ws.run_agent(prompt=PROMPT, agent="spec-author", timeout=900)
    assert result.ok, f"spec-author failed; see {result.log_path}"

    spec = ws.find_one("docs/specs/digest.md")
    assert spec, f"spec missing; see {result.log_path}"
    text = spec.read_text(encoding="utf-8")

    # Status flipped to draft (re-draft window).
    assert "Status: draft" in text or "status: draft" in text.lower(), (
        f"Status must flip to draft during re-draft window; "
        f"see {result.log_path}"
    )

    # New keyboard FR present.
    assert "keyboard" in text.lower(), (
        f"new keyboard-shortcuts FR must appear; see {result.log_path}"
    )

    # ---------- Req #1: NO change-tracking artefacts in draft body. ----------
    forbidden_substrings = [
        "## Changes since",
        "## Revision History",
        "## Changelog",
        "## What's Changed",
        "[Changed in v",
    ]
    for needle in forbidden_substrings:
        assert needle not in text, (
            f"draft body MUST NOT contain {needle!r} "
            f"(prd-evolution §5 / d7.draft-no-change-tracking); "
            f"see {result.log_path}"
        )

    # ---------- Req #2: removed prior-published FR deleted from draft. ------
    assert "[Deprecated" not in text and "[Removed" not in text, (
        f"draft body MUST NOT carry [Deprecated] / [Removed] markers "
        f"for FR-07 (interpretation (a); prd-evolution §3b draft-side); "
        f"see {result.log_path}"
    )
    assert "mouse-only" not in text.lower(), (
        f"FR-07 'mouse-only quick actions' body must be deleted from "
        f"the working draft; see {result.log_path}"
    )

    # ---------- No CHANGELOG mutation (no publish intent). ------------------
    changelog = ws.find_one("docs/specs/CHANGELOG.md")
    if changelog:
        cl = changelog.read_text(encoding="utf-8")
        # Fixture ships only v1.0 prior changelog (or none). Re-draft must
        # not add any next-version entry.
        assert "0.2.0" not in cl and "1.1" not in cl and "v1.1" not in cl, (
            f"re-draft must NOT add CHANGELOG entry for the next version "
            f"(V3 / V17 / OQ-5); see {result.log_path}"
        )

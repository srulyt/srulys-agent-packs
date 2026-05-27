"""Minimal-edit discipline (F1-F10): on a single-FR-add request, the
drafter must touch ONLY the new FR's section, the Document
Information block, the 'Changes since vN' preamble, and the
CHANGELOG. Bait spans from the prior spec (typo-free but stylistically
imperfect) MUST survive verbatim.

Ported from legacy ``cases/smoke-update-minimal-edit-discipline/``.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from _lib.asserts import assert_prose_contains

FIXTURES = Path(__file__).parent / "fixtures" / "update_minimal_edit_discipline"

BAIT_SPANS = [
    "Workspace members miss important changes across squads. Scrolling "
    "individual channels to find what matters takes too long.",
    "Built on the existing `workspace-events` Kafka topic. No new datastore.",
    "PM      | Daily summary across squads. | < 2 min to know what to "
    "follow up on. |",
]

PROMPT = """\
@spec-author update the existing spec at `fixtures/prior-spec-v1.md`.

I want exactly ONE change:

1. **Add a new FR** for keyboard shortcuts: users should be able to
   trigger the top three quick actions (open, dismiss, snooze) via
   `o`, `d`, `s` from the digest panel.

Bump the version appropriately and produce a CHANGELOG. Do NOT make
any other edits -- keep the rest of the spec exactly as it is. I have
already reviewed that prose and approved it.

When you propose the structure at Stop A -- including the planned
edit set, the proposed version bump, and the planned `Updates:`
header -- I will reply `APPROVE`.

## Pre-supplied answers (do not park; proceed straight through)

- **Stop 0 (output location):** `output_path: docs/specs/digest.md, spec_kind: technical`
- **Stop A (structure approval):** `APPROVE` (first ask)

Proceed end-to-end without waiting for further user input.
"""


@pytest.mark.pack
@pytest.mark.slow
def test_update_minimal_edit_discipline(copilot_pack):
    ws = copilot_pack("spec-author")
    ws.stage_files(FIXTURES, dest_subdir=".")

    result = ws.run_agent(prompt=PROMPT, agent="spec-author", timeout=900)
    assert result.ok, f"spec-author failed; see {result.log_path}"

    spec = ws.find_one("docs/specs/digest.md")
    assert spec, f"spec missing; see {result.log_path}"
    text = spec.read_text(encoding="utf-8")

    assert "Updates:" in text and "v1.0" in text, (
        f"spec must include 'Updates: v1.0' header; "
        f"see {result.log_path}"
    )
    assert "Changes since v1" in text, (
        f"spec must include 'Changes since v1' preamble; "
        f"see {result.log_path}"
    )
    for span in BAIT_SPANS:
        assert_prose_contains(
            text,
            span,
            log_path=result.log_path,
            extra="bait sentence must survive verbatim (minimal-edit discipline)",
        )

    changelog = ws.find_one("docs/specs/CHANGELOG.md")
    assert changelog, f"CHANGELOG.md missing; see {result.log_path}"
    assert "### Added" in changelog.read_text(encoding="utf-8"), (
        f"CHANGELOG must contain ### Added; see {result.log_path}"
    )

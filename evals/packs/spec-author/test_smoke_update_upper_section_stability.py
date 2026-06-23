"""F2 upper-section edit ratchet: the user asks for ONE FR addition;
drafter MUST leave Document Information (excluding version-mechanic
fields), Problem Statement, Goals & Success Metrics, Users &
Personas, and Solution Summary byte-identical to the prior spec.

Ported from legacy ``cases/smoke-update-upper-section-stability/``.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from evalpilot import assert_prose_contains

FIXTURES = Path(__file__).parent / "fixtures" / "update_upper_section_stability"

UPPER_BAIT_SPANS = [
    "Workspace members miss important changes across squads. Scrolling "
    "individual channels to find what matters takes too long.",
    "Built on the existing `workspace-events` Kafka topic. No new datastore.",
    "Reduce median time-to-first-action on a flagged change from",
    "PM      | Daily summary across squads. | < 2 min to know what to "
    "follow up on. |",
]

PROMPT = """\
@spec-author update the existing spec at `fixtures/prior-spec-v1.md`.

I want exactly ONE change:

1. **Add a new FR** for keyboard shortcuts: users should be able to
   trigger the top three quick actions (open, dismiss, snooze) via
   `o`, `d`, `s` from the digest panel.

Bump the version appropriately and produce a CHANGELOG. Do NOT
touch anything above the Functional Requirements section -- Problem
Statement, Goals, Personas, and Solution Summary are settled.

## Pre-supplied answers (do not park; proceed straight through)

- **Stop 0 (output location):** `output_path: docs/specs/digest.md, spec_kind: technical`
- **Stop A (structure approval):** `APPROVE` (first ask)

Proceed end-to-end without waiting for further user input.
"""


@pytest.mark.pack
@pytest.mark.slow
def test_update_upper_section_stability(agent_pack):
    ws = agent_pack("spec-author")
    ws.stage_files(FIXTURES, dest_subdir=".")

    result = ws.run_agent(prompt=PROMPT, agent="spec-author", timeout=900)
    if not result.usable:
        pytest.skip(result.unavailable_reason())
    assert result.ok, f"spec-author failed; see {result.log_path}"

    spec = ws.find_one("docs/specs/digest.md")
    assert spec, f"spec missing; see {result.log_path}"
    text = spec.read_text(encoding="utf-8")

    for span in UPPER_BAIT_SPANS:
        assert_prose_contains(
            text,
            span,
            log_path=result.log_path,
            extra="upper-section bait must survive byte-for-byte",
        )

    changelog = ws.find_one("docs/specs/CHANGELOG.md")
    assert changelog, f"CHANGELOG.md missing; see {result.log_path}"
    assert "### Added" in changelog.read_text(encoding="utf-8"), (
        f"CHANGELOG must contain ### Added; see {result.log_path}"
    )

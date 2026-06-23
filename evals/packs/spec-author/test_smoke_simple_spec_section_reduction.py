"""Q2 adaptive sectioning: a deliberately low-complexity input (one
small UI tweak, no security/data/API/rollout surface) must produce
a noticeably trimmed spec where most complexity-gated sections are
omitted with rationales.

Ported from legacy ``cases/smoke-simple-spec-section-reduction/``.
"""
from __future__ import annotations

from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures" / "simple_spec_section_reduction"

PROMPT = """\
@spec-author write a PRD for **"Add a 'mark as read' button to in-app
notifications"**.

This is a deliberately simple spec. The constraints are:

- Single team owns delivery (the Notifications team).
- No security-surface change (no auth changes, no new data egress).
- No new datastore or schema change (we already track read-state).
- No new public API or SDK surface.
- No phased rollout, no kill-switch needed.
- No regulatory regime in scope.

Apply the adaptive sectioning rule: include only mandatory sections
plus any complexity-gated section that is actually justified.

## Pre-supplied answers (do not park; proceed straight through)

- **Stop 0 (output location):** `output_path: docs/specs/tweak.md, spec_kind: product`
- **Stop A (structure approval):** `APPROVE` (first ask)

Proceed end-to-end without waiting for further user input.
"""

GATED_SECTIONS = [
    "Non-Functional Requirements",
    "Security & Compliance",
    "Data Model",
    "Telemetry & Analytics",
    "API Contract",
    "Rollout Plan",
    "Rollback Strategy",
]


@pytest.mark.pack
@pytest.mark.slow
def test_simple_spec_section_reduction(agent_pack):
    ws = agent_pack("spec-author")
    ws.stage_files(FIXTURES, dest_subdir=".")

    result = ws.run_agent(prompt=PROMPT, agent="spec-author", timeout=900)
    if not result.usable:
        pytest.skip(result.unavailable_reason())
    assert result.ok, f"spec-author failed; see {result.log_path}"

    spec = ws.find_one("docs/specs/tweak.md")
    assert spec, f"spec missing; see {result.log_path}"
    text = spec.read_text(encoding="utf-8")

    # All gated sections should be omitted (or recorded as
    # gated-omitted in the section-decisions block, not present as
    # full section bodies).
    for section in GATED_SECTIONS:
        heading = f"## {section}"
        assert heading not in text, (
            f"section {section!r} should be omitted as gated-omitted "
            f"in this trim; see {result.log_path}"
        )

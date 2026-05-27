"""F3 per-statement REVERT-default gate: the prior spec contains two
deliberately ugly Problem-Statement sentences (typos + awkward
phrasing). The user asks for ONE new AC. The revised spec MUST
preserve the typos and awkward sentence byte-for-byte (REVERT
default beats stylistic polish).

Ported from legacy ``cases/smoke-update-revert-default/``.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from _lib.asserts import assert_prose_contains, assert_prose_not_contains

FIXTURES = Path(__file__).parent / "fixtures" / "update_revert_default"

BAIT_TYPOS = [
    "Workspace memebers miss important changes accross squads",
    "the scrolling of individual channels in order to be finding what "
    "matters is taking too much of the time",
]
POLISHED_FORMS = [
    "Workspace members miss important changes across squads",
    "Scrolling individual channels to find what matters takes too long",
]

PROMPT = """\
@spec-author update the spec at `fixtures/prior-spec-v1.md`.

Single change: **add AC-04** for FR-03 -- when the configured time is
in a timezone the user has not set, then the system falls back to
UTC and shows a one-time banner explaining the fallback.

Do NOT make any other edits. The prose elsewhere is intentional and
has been approved.

## Pre-supplied answers (do not park; proceed straight through)

- **Stop 0 (output location):** `output_path: docs/specs/digest.md, spec_kind: technical`
- **Stop A (structure approval):** `APPROVE` (first ask)

Proceed end-to-end without waiting for further user input.
"""


@pytest.mark.pack
@pytest.mark.slow
def test_update_revert_default(copilot_pack):
    ws = copilot_pack("spec-author")
    ws.stage_files(FIXTURES, dest_subdir=".")

    result = ws.run_agent(prompt=PROMPT, agent="spec-author", timeout=900)
    assert result.ok, f"spec-author failed; see {result.log_path}"

    spec = ws.find_one("docs/specs/digest.md")
    assert spec, f"spec missing; see {result.log_path}"
    text = spec.read_text(encoding="utf-8")

    for typo in BAIT_TYPOS:
        assert_prose_contains(
            text,
            typo,
            log_path=result.log_path,
            extra=(
                "REVERT-default: bait sentence must survive verbatim "
                "(typos and all)"
            ),
        )
    for polished in POLISHED_FORMS:
        assert_prose_not_contains(
            text,
            polished,
            log_path=result.log_path,
            extra=(
                "polished form must NOT appear (drafter polished an "
                "unrequested sentence -- F3 regressed)"
            ),
        )

    assert "AC-04" in text or "AC-4" in text, (
        f"new AC-04 must be added; see {result.log_path}"
    )

"""Req #1 (new draft mode, half 1 of 2): a greenfield draft MUST
NOT produce any in-spec change-tracking artefact.

Asserts:

- No `## Changes since`, `## Revision History`, `## Changelog`, or
  `## What's Changed` heading in the spec body.
- No inline `[Changed in v...]` marker anywhere.
- No `CHANGELOG.md` file anywhere in the workspace.
- No `<!-- changed: ... -->` HTML comment narrating revisions.

This exercises `prd-evolution` §5 and the new
`d7.draft-no-change-tracking` blocker sub-rubric. The spec is born
`Status: draft`, `Version: 0.0.1-draft` (V2) — there is no prior
version to track changes against, so any preamble is by definition
fabricated.
"""
from __future__ import annotations

import re

import pytest


PROMPT = """\
@spec-author write a PRD for **Quick Toggle** -- a UI affordance that
lets a user flip a single setting (notifications on/off) from the
top-bar without opening Settings.

Brand-new spec. No existing spec at this path. Single-team UI; no
datastore, no API surface, no security-surface change.

## Pre-supplied answers (do not park; proceed straight through)

- **Stop 0 (output location):** `output_path: docs/specs/quick-toggle.md, spec_kind: product`
- **Stop A (structure approval):** `APPROVE` (first ask)

Proceed end-to-end through detective -> drafter -> critic without
waiting for further user input.
"""


@pytest.mark.pack
@pytest.mark.slow
def test_initial_draft_has_no_change_tracking(copilot_pack):
    ws = copilot_pack("spec-author")

    result = ws.run_agent(prompt=PROMPT, agent="spec-author", timeout=900)
    assert result.ok, f"spec-author failed; see {result.log_path}"

    spec = ws.find_one("docs/specs/quick-toggle.md")
    assert spec, f"spec missing; see {result.log_path}"
    text = spec.read_text(encoding="utf-8")

    forbidden_headings = [
        "## Changes since",
        "## Revision History",
        "## Changelog",
        "## What's Changed",
    ]
    for needle in forbidden_headings:
        assert needle not in text, (
            f"draft spec MUST NOT contain {needle!r} heading "
            f"(prd-evolution §5 / d7.draft-no-change-tracking); "
            f"see {result.log_path}"
        )

    assert not re.search(r"\[Changed in v[0-9]", text), (
        f"draft spec MUST NOT contain inline `[Changed in vX.Y]` "
        f"markers; see {result.log_path}"
    )

    assert "<!-- changed" not in text.lower(), (
        f"draft spec MUST NOT contain HTML 'changed' comments "
        f"narrating revisions; see {result.log_path}"
    )

    # No CHANGELOG.md anywhere in the workspace on initial draft.
    changelogs = ws.glob("**/CHANGELOG.md")
    assert not changelogs, (
        f"draft must NOT produce a CHANGELOG.md (V3 / V17 / OQ-5); "
        f"found {changelogs}; see {result.log_path}"
    )

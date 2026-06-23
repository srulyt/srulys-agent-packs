"""Greenfield creation, context complete, Stop A path only. Detective
finds no must-fill gaps; user replies APPROVE on first ask;
specification.md and spec-review.md are written; NO interview
artifacts and NO CHANGELOG.

Ported from legacy ``cases/smoke-greenfield-context-complete/``.
"""
from __future__ import annotations

from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures" / "greenfield_context_complete"

PROMPT = """\
@spec-author write a PRD for **Workspace activity digest** -- a daily
summary of changes in a product workspace, delivered to each member
via in-app notification.

Inputs available in this workspace:

- `docs/personas.md` -- the two primary personas (PM, Engineering
  Manager) and their needs.
- `docs/spike-notes.md` -- short engineering spike notes describing
  the existing event-stream we'd source from.
- Reference link: <https://example.com/digest-competitor-overview>
  (informational only).

No MCPs are declared. Single team, no new datastore, no public API,
no security-surface change.

## Pre-supplied answers (do not park; proceed straight through)

- **Stop 0 (output location):** `output_path: docs/specs/digest.md, spec_kind: product`
- **Stop A (structure approval):** `APPROVE` (first ask)

Proceed end-to-end without waiting for further user input.
"""


@pytest.mark.pack
@pytest.mark.slow
def test_greenfield_context_complete(agent_pack):
    ws = agent_pack("spec-author")
    ws.stage_files(FIXTURES, dest_subdir=".")

    result = ws.run_agent(prompt=PROMPT, agent="spec-author", timeout=900)
    if not result.usable:
        pytest.skip(result.unavailable_reason())
    assert result.ok, f"spec-author failed; see {result.log_path}"

    assert ws.find_one("docs/specs/digest.md"), (
        f"specification missing; see {result.log_path}"
    )
    discoveries = ws.glob(
        ".spec-author/sessions/*/artifacts/discovery.json"
    )
    assert discoveries, f"discovery.json missing; see {result.log_path}"
    context_packs = ws.glob(
        ".spec-author/sessions/*/artifacts/context-pack.md"
    )
    assert context_packs, f"context-pack.md missing; see {result.log_path}"
    reviews = ws.glob(
        ".spec-author/sessions/*/artifacts/spec-review.md"
    )
    assert reviews, f"spec-review.md missing; see {result.log_path}"

    # Forbidden artefacts.
    interviews = ws.glob(
        ".spec-author/sessions/*/artifacts/interview-questions.md"
    )
    assert not interviews, (
        f"interview-questions.md must NOT be produced when context is "
        f"complete; see {result.log_path}"
    )
    changelogs = ws.glob("**/CHANGELOG.md")
    assert not changelogs, (
        f"creation mode must NOT write CHANGELOG.md; "
        f"found {changelogs}; see {result.log_path}"
    )

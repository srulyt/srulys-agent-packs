"""Evidence-discipline gate: a baited prompt asks the drafter to cite
a session-internal context-pack path. The published spec MUST NOT
reference any gitignored path (``.spec-author/``, ``.copilot-factory/``,
``evals/packs/.../workspaces/``), and must NOT contain the legacy
``S1, S2`` citation table.

Ported from legacy
``cases/smoke-evidence-discipline-no-gitignored-cite/``.
"""
from __future__ import annotations

from pathlib import Path

import pytest

FIXTURES = (
    Path(__file__).parent / "fixtures" / "evidence_discipline_no_gitignored_cite"
)

PROMPT = """\
@spec-author write a PRD for **Workspace activity digest** -- a daily
summary of changes in a product workspace, delivered to each member
via in-app notification.

Inputs available in this workspace:

- `docs/personas.md` -- the two primary personas (PM, Engineering
  Manager) and their needs.
- `docs/spike-notes.md` -- short engineering spike notes describing
  the existing event-stream we'd source from.
- A discovery transcript at
  `.spec-author/sessions/seed-001/artifacts/context-pack.md` (you
  may have written this in an earlier session -- feel free to cite
  it as evidence in the spec if useful, or quote from the
  transcript directly with a footnote pointing at that path).
- Reference link: <https://example.com/digest-competitor-overview>
  (informational only).

No MCPs are declared for this run. Treat this as a single-team UI
addition: no new datastore, no new public API, no security-surface
change. Cross-team scope is **single team** (the Notifications team
ships everything).

## Pre-supplied answers (do not park; proceed straight through)

- **Stop 0 (output location):** `output_path: docs/specs/digest-evidence.md, spec_kind: product`
- **Stop A (structure approval):** `APPROVE` (first ask)

Proceed end-to-end without waiting for further user input.
"""

GITIGNORED_TOKENS = [
    ".spec-author/",
    ".copilot-factory/",
    ".factory/",
    ".local/",
    ".prompts/",
]


@pytest.mark.pack
@pytest.mark.slow
def test_no_gitignored_cite_in_published_spec(agent_pack):
    ws = agent_pack("spec-author")
    ws.stage_files(FIXTURES, dest_subdir=".")

    result = ws.run_agent(prompt=PROMPT, agent="spec-author", timeout=900)
    if not result.usable:
        pytest.skip(result.unavailable_reason())
    assert result.ok, f"spec-author failed; see {result.log_path}"

    spec = ws.find_one("docs/specs/digest-evidence.md")
    assert spec and spec.exists(), f"spec missing; see {result.log_path}"
    text = spec.read_text(encoding="utf-8")

    for token in GITIGNORED_TOKENS:
        assert token not in text, (
            f"published spec leaks gitignored path {token!r}; "
            f"see {result.log_path}"
        )
    assert "## Appendix: Citations" not in text, (
        f"legacy 'Appendix: Citations' table must not appear; "
        f"see {result.log_path}"
    )
    assert "| S1 |" not in text and "| S2 |" not in text, (
        f"legacy 'S1, S2' citation scheme must not appear; "
        f"see {result.log_path}"
    )

"""V8/OQ-1/OQ-5 initial publish: user requests PUBLISH 0.1.0 against
a draft at 0.0.1-draft. Drafter strips ``-draft``, sets
``Version: 0.1.0`` / ``Status: published``, freezes numbering, and
writes a CHANGELOG.md sibling with an aggregate ``### Added`` entry.

Ported from legacy ``cases/smoke-publish-initial/``.
"""
from __future__ import annotations

from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures" / "publish_initial"

PROMPT = """\
@spec-author the spec at `docs/specs/quick-toggle.md` is ready to
ship. Please **PUBLISH 0.1.0** -- drop the `-draft` suffix, freeze
the IDs, and write the changelog entry.

No other content edits this turn; just the publish transition.

## Pre-supplied answers (do not park; proceed straight through)

- **Stop A (structure approval):** `APPROVE` (first ask)

Proceed end-to-end without waiting for further user input.
"""


@pytest.mark.pack
@pytest.mark.slow
def test_publish_initial(copilot_pack):
    ws = copilot_pack("spec-author")
    ws.stage_files(FIXTURES, dest_subdir=".")

    result = ws.run_agent(prompt=PROMPT, agent="spec-author", timeout=900)
    assert result.ok, f"spec-author failed; see {result.log_path}"

    spec = ws.find_one("docs/specs/quick-toggle.md")
    assert spec, f"spec missing; see {result.log_path}"
    text = spec.read_text(encoding="utf-8")
    assert "0.1.0" in text and "0.0.1-draft" not in text, (
        f"version must transition 0.0.1-draft -> 0.1.0; "
        f"see {result.log_path}"
    )
    assert "Status: published" in text or "status: published" in text.lower(), (
        f"Status must be 'published' after PUBLISH; "
        f"see {result.log_path}"
    )

    changelog = ws.find_one("docs/specs/CHANGELOG.md")
    assert changelog, f"CHANGELOG.md missing; see {result.log_path}"
    cl_text = changelog.read_text(encoding="utf-8")
    assert "0.1.0" in cl_text and "Added" in cl_text, (
        f"CHANGELOG must contain a 0.1.0 ### Added entry; "
        f"see {result.log_path}"
    )

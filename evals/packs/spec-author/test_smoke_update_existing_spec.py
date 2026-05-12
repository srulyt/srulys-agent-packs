"""Q1 update mode end-to-end: the user supplies an existing spec,
asks for a new FR + deprecation of FR-07, and a version bump.
Asserts both ``specification.md`` and ``CHANGELOG.md`` are produced,
the revised spec has the ``Updates: vN`` header + ``[Deprecated]``
marker on FR-07 + ``Changes since v1`` preamble, and the CHANGELOG
uses Keep-a-Changelog headings.

Ported from legacy ``cases/smoke-update-existing-spec/``.
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
2. **Deprecate FR-07** "mouse-only quick actions" -- superseded by
   the new keyboard-shortcuts FR.

Bump the version appropriately and produce a CHANGELOG.

## Pre-supplied answers (do not park; proceed straight through)

- **Stop 0 (output location):** `output_path: docs/specs/digest.md, spec_kind: technical`
- **Stop A (structure approval):** `APPROVE` (first ask)

Proceed end-to-end without waiting for further user input.
"""


@pytest.mark.pack
@pytest.mark.slow
def test_update_existing_spec(copilot_pack):
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
    assert "FR-07" in text and "[Deprecated" in text, (
        f"FR-07 must carry [Deprecated] marker; see {result.log_path}"
    )
    assert "Changes since v1" in text, (
        f"spec must contain 'Changes since v1' preamble; "
        f"see {result.log_path}"
    )
    assert "keyboard" in text.lower(), (
        f"new keyboard-shortcuts FR must appear; see {result.log_path}"
    )

    changelog = ws.find_one("docs/specs/CHANGELOG.md")
    assert changelog, f"CHANGELOG.md missing; see {result.log_path}"
    cl_text = changelog.read_text(encoding="utf-8")
    assert "### Added" in cl_text and "### Deprecated" in cl_text, (
        f"CHANGELOG must use Keep-a-Changelog Added + Deprecated "
        f"headings; see {result.log_path}"
    )

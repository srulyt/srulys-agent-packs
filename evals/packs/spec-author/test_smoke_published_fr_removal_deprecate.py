"""F4 published-branch regression: remove FR-03 from a
``Status: published`` v1.2.0 spec. Drafter MUST mark FR-03 with
``[Deprecated in v1.3, ...]``, keep ALL FR IDs frozen (V9), keep
FR-04/FR-05 unchanged, and write a CHANGELOG ``### Deprecated``
entry under v1.3.0.

Ported from legacy ``cases/smoke-published-fr-removal-deprecate/``.
"""
from __future__ import annotations

from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures" / "published_fr_removal_deprecate"

PROMPT = """\
@spec-author update `docs/specs/notif-prefs.md`. We are dropping
**FR-03** (inline muted-badge) -- the data shows nobody used it.

This spec is `Status: published, Version: 1.2.0`. Cut a v1.3 that
deprecates FR-03 properly. The user-facing UI is going away in v1.3
but the requirement ID stays in the spec so older integration
references still resolve.

## Pre-supplied answers (do not park; proceed straight through)

- **Stop A (structure approval):** `APPROVE` (first ask)
- **Publish intent:** publish v1.3.0 at end of turn.

Proceed end-to-end without waiting for further user input.
"""


@pytest.mark.pack
@pytest.mark.slow
def test_published_fr_removal_deprecate(copilot_pack):
    ws = copilot_pack("spec-author")
    ws.stage_files(FIXTURES, dest_subdir=".")

    result = ws.run_agent(prompt=PROMPT, agent="spec-author", timeout=900)
    assert result.ok, f"spec-author failed; see {result.log_path}"

    spec = ws.find_one("docs/specs/notif-prefs.md")
    assert spec, f"spec missing; see {result.log_path}"
    text = spec.read_text(encoding="utf-8")

    assert "FR-03" in text, (
        f"FR-03 must remain in spec (frozen ID); see {result.log_path}"
    )
    assert "[Deprecated" in text and "v1.3" in text, (
        f"FR-03 must be marked '[Deprecated in v1.3, ...]'; "
        f"see {result.log_path}"
    )
    assert "FR-04" in text and "Quiet-hours window" in text, (
        f"FR-04 (Quiet-hours window) must remain frozen, not renumbered; "
        f"see {result.log_path}"
    )
    assert "FR-05" in text and "Test-notification button" in text, (
        f"FR-05 (Test-notification button) must remain frozen; "
        f"see {result.log_path}"
    )
    assert "1.3.0" in text, (
        f"version must bump to 1.3.0; see {result.log_path}"
    )

    changelog = ws.find_one("docs/specs/CHANGELOG.md")
    assert changelog, f"CHANGELOG.md missing; see {result.log_path}"
    cl_text = changelog.read_text(encoding="utf-8")
    assert "1.3.0" in cl_text and "Deprecated" in cl_text and "FR-03" in cl_text, (
        f"CHANGELOG must contain v1.3.0 ### Deprecated entry citing FR-03; "
        f"see {result.log_path}"
    )

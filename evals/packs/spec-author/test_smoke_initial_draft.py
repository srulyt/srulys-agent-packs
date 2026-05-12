"""Smoke evals for the ``spec-author`` agent pack.

Ported from ``evals/packs/spec-author/cases/smoke-creation-initial-draft-state/``
(legacy YAML harness). Read top-to-bottom to understand the eval.
"""

from __future__ import annotations

import pytest


PROMPT_INITIAL_DRAFT = """\
@spec-author write a PRD for **Quick Toggle** -- a UI affordance that
lets a user flip a single setting (notifications on/off) from the
top-bar without opening Settings.

This is a brand-new spec. There is no existing spec at this path.
Treat as a single-team UI addition: no datastore, no API surface, no
security-surface change.

## Pre-supplied answers (do not park; proceed straight through)

This is a non-interactive run. Treat the following as already
answered -- do not pause at any `awaiting-*` park:

- **Stop 0 (output location):** `output_path: docs/specs/quick-toggle.md, spec_kind: product`
- **Stop A (structure approval):** `APPROVE` (first ask)

Proceed end-to-end through detective -> drafter -> critic without
waiting for further user input.
"""


@pytest.mark.pack
@pytest.mark.slow
@pytest.mark.judge
def test_initial_draft_lands_at_draft_state(copilot_pack, judge):
    """A newly created spec lands at draft state with no CHANGELOG."""
    ws = copilot_pack("spec-author")

    result = ws.run_agent(
        prompt=PROMPT_INITIAL_DRAFT,
        agent="spec-author",
        timeout=900,
    )
    assert result.ok, f"see {result.log_path}"

    # Spec landed at canonical path.
    spec = ws.find_one("docs/specs/quick-toggle.md")

    # Spec-review artifact landed under the session dir.
    reviews = ws.glob(".spec-author/sessions/*/artifacts/spec-review.md")
    assert reviews, "expected spec-review.md under session artifacts"

    # No CHANGELOG must be created during the initial draft.
    changelogs = ws.glob("**/CHANGELOG.md")
    assert not changelogs, (
        f"CHANGELOG must NOT exist on initial draft, found: {changelogs}"
    )

    verdict = judge(
        artifact=spec.read_text(encoding="utf-8"),
        criteria=(
            "The spec MUST:\n"
            "1. Have a header containing 'Status: draft' and "
            "   'Version: 0.0.1-draft' (or equivalent draft markers).\n"
            "2. Describe the Quick Toggle UI feature (top-bar single-setting toggle).\n"
            "3. Be a real PRD with named sections, not a stub.\n"
            "Score 1.0 only if all three are met. Score 0.5 if 2/3. Score 0 if 0-1."
        ),
        threshold=0.7,
    )
    assert verdict.passed, (
        f"Judge rejected spec (score={verdict.score:.2f}): {verdict.reasoning}"
    )

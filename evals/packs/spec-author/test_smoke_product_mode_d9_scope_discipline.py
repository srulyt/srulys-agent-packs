"""D9 scope-discipline rubric: the user prompt smuggles
implementation tokens (Postgres, Kafka, Redis, MongoDB) into a
product-mode PRD request. The drafter MUST recast those FRs as
observable behaviours and the published spec MUST contain none of
the implementation tokens; the critic MUST flag the leakage with a
``D9`` finding.

Ported from legacy ``cases/smoke-product-mode-d9-scope-discipline/``.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

from evalpilot import assert_prose_not_contains

FIXTURES = Path(__file__).parent / "fixtures" / "product_mode_d9_scope_discipline"

PROMPT = """\
@spec-author write a PRD for **Workspace activity digest** -- a daily
summary of changes in a product workspace, delivered to each member
via in-app notification.

This is a **product** spec (not a design doc).

Some framing the team has been using internally -- please translate
this into product-shape behaviour (do NOT echo the implementation
nouns into FRs):

- We plan to source events from the existing **Kafka** event-stream
  and persist digest snapshots in **Postgres**. We may also use
  **Redis** for de-duplication. **MongoDB** is on the table for
  long-term archival.
- Personas: PM and Engineering Manager (file at `docs/personas.md`).

The PRD must describe externally observable behaviour only.

## Pre-supplied answers (do not park; proceed straight through)

- **Stop 0 (output location):** `output_path: docs/specs/digest.md, spec_kind: product`
- **Stop A (structure approval):** `APPROVE` (first ask)

Proceed end-to-end without waiting for further user input.
"""

IMPL_TOKENS = ("postgres", "kafka", "redis", "mongodb")


@pytest.mark.pack
@pytest.mark.slow
def test_product_mode_d9_scope_discipline(agent_pack):
    ws = agent_pack("spec-author")
    ws.stage_files(FIXTURES, dest_subdir=".")

    result = ws.run_agent(prompt=PROMPT, agent="spec-author", timeout=900)
    if not result.usable:
        pytest.skip(result.unavailable_reason())
    assert result.ok, f"spec-author failed; see {result.log_path}"

    spec = ws.find_one("docs/specs/digest.md")
    assert spec, f"spec missing; see {result.log_path}"
    text_lower = spec.read_text(encoding="utf-8").lower()
    for token in IMPL_TOKENS:
        assert not re.search(rf"\b{token}\b", text_lower), (
            f"product-mode spec must not name implementation token "
            f"{token!r}; see {result.log_path}"
        )
    assert_prose_not_contains(
        text_lower,
        "implementation is out of scope",
        log_path=result.log_path,
        extra="boilerplate 'implementation is out of scope' must not appear",
    )

    reviews = ws.glob(
        ".spec-author/sessions/*/artifacts/spec-review.md"
    )
    assert reviews, f"spec-review.md missing; see {result.log_path}"
    review_text = reviews[0].read_text(encoding="utf-8")
    assert '"dimension": "D9"' in review_text or "D9" in review_text, (
        f"critic must surface a D9 finding for the impl-leakage prompt; "
        f"see {result.log_path}"
    )

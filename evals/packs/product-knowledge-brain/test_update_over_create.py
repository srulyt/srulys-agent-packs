"""Behavioural pack eval: update-over-create (consolidation, not proliferation).

Seed the KB with an existing concept page, then feed overlapping new info.
The brain must UPDATE the existing page (its Change Log gains an entry) and
NOT create a near-duplicate page for the same concept.

Requires the ``copilot`` CLI (``slow`` + ``judge``).
"""

from __future__ import annotations

import pytest

SEED_PAGE = """\
---
title: "Onboarding Flow"
type: product
area: feature-a
status: current
updated: 2026-05-01
relationships:
  - rel: supports
    target: strategic/north-star-activation.md
evidence: [E-001]
---

# Onboarding Flow

## Current Understanding
Onboarding is currently a 3-step guided setup [^E-001].

## Why / Rationale
Three steps were chosen to collect required configuration up front.

## Open Questions / Uncertainties

## Related
- supports -> [[strategic/north-star-activation]]

## Change Log
- 2026-05-01 - initial page created. [^E-001]

[^E-001]: see evidence/E-001.md
"""

PROMPT = """\
Use the product-knowledge-brain plugin against the existing knowledge base
at knowledge-base/. There is already a concept page about the feature-a
onboarding flow. The note below is already-extracted text from another tool.

Extracted note (source: usability study, 2026-05-25):
"A usability study found a single-step quick-start converts far better than
the current multi-step onboarding for feature-a. We should change the
onboarding approach accordingly."

Run the evolution cycle and consolidate this into the brain.
"""


@pytest.mark.pack
@pytest.mark.slow
@pytest.mark.judge
def test_update_over_create(product_knowledge_brain, judge):
    ws = product_knowledge_brain

    # Seed an existing page + its evidence descriptor.
    seed_path = ws.root / "knowledge-base" / "areas" / "feature-a" / "knowledge" / "onboarding-flow.md"
    seed_path.parent.mkdir(parents=True, exist_ok=True)
    seed_path.write_text(SEED_PAGE, encoding="utf-8")
    ev = ws.root / "knowledge-base" / "evidence" / "E-001.md"
    ev.parent.mkdir(parents=True, exist_ok=True)
    ev.write_text(
        "---\nid: E-001\nsource_type: prd\ndate: 2026-05-01\n---\n\n"
        "# E-001 - onboarding baseline\n\nEstablished the 3-step onboarding.\n",
        encoding="utf-8",
    )

    result = ws.run_agent(prompt=PROMPT, timeout=900)
    if not result.usable:
        pytest.skip(result.unavailable_reason())
    assert result.ok, f"agent exited {result.returncode}; see {result.log_path}"

    # 1) Structural: exactly one onboarding concept page for feature-a — no
    #    near-duplicate created.
    onboarding_pages = [
        p for p in ws.glob("knowledge-base/areas/feature-a/knowledge/*.md")
        if "onboard" in p.stem.lower() or "quick" in p.stem.lower() or "activation" in p.stem.lower()
    ]
    assert onboarding_pages, f"onboarding page disappeared; see {result.log_path}"
    assert len(onboarding_pages) == 1, (
        f"expected the existing page to be UPDATED, but found "
        f"{[p.name for p in onboarding_pages]} (near-duplicate created); "
        f"see {result.log_path}"
    )

    updated = onboarding_pages[0].read_text(encoding="utf-8")

    # 2) Judge: the existing page was updated and its change log grew.
    verdict = judge(
        artifact=updated,
        criteria=(
            "This is the single onboarding concept page after consolidating "
            "new info that the multi-step onboarding should become a "
            "single-step quick-start. Score 1.0 only if ALL hold: (a) the "
            "Current Understanding now reflects the single-step/quick-start "
            "direction; (b) the Change Log contains a NEW entry recording the "
            "change and preserving the superseded 3-step belief with a "
            "reason; (c) it remains one consolidated page, not a duplicate. "
            "Score 0.5 if updated but the prior belief was silently dropped. "
            "Be strict."
        ),
        threshold=0.7,
    )
    assert verdict.passed, (
        f"Judge rejected (score={verdict.score:.2f}): {verdict.reasoning}; "
        f"see {result.log_path}"
    )

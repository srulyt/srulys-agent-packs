"""Behavioural pack eval: consolidation happy path.

Feed already-extracted text about a product feature and run the knowledge
evolution cycle. Assert the knowledge base materializes curated *living*
pages (not transcripts) under the default ``knowledge-base/`` root, then ask
the LLM judge to confirm the pages read like consolidated wiki articles.

Requires the ``copilot`` CLI (tagged ``slow`` + ``judge``).
"""

from __future__ import annotations

import pytest

PROMPT = """\
Use the product-knowledge-brain plugin to evolve a knowledge base from the
already-extracted notes below. Use the default knowledge base root
(knowledge-base/). The notes have already been extracted from source by
another tool — your job is to consolidate them into the brain, not to
re-ingest anything.

Extracted notes (source: customer interview, 2026-05-12):
"Enterprise admins on the Acme account repeatedly said the current 3-step
onboarding is too slow and they abandon it. They want a single guided
quick-start. This matters for our north-star activation goal. The product
team thinks feature-a (onboarding) owns this."

Run the full evolution cycle and report the summary.
"""


@pytest.mark.pack
@pytest.mark.slow
@pytest.mark.judge
def test_smoke_consolidation_happy_path(product_knowledge_brain, judge):
    ws = product_knowledge_brain

    result = ws.run_agent(prompt=PROMPT, timeout=900)
    if not result.usable:
        pytest.skip(result.unavailable_reason())
    assert result.ok, f"agent exited {result.returncode}; see {result.log_path}"

    # 1) Structural: at least one curated concept page and the master index.
    pages = ws.glob("knowledge-base/areas/*/knowledge/*.md")
    assert pages, f"expected a concept page under areas/*/knowledge/; see {result.log_path}"
    assert ws.glob("knowledge-base/index.md"), (
        f"expected a repo-wide index.md; see {result.log_path}"
    )

    # 2) Judge that the page is a curated living article, not a transcript.
    page = pages[0].read_text(encoding="utf-8")
    verdict = judge(
        artifact=page,
        criteria=(
            "The page is a CURATED living knowledge article, not a raw "
            "transcript or chronological notes dump. Score 1.0 only if ALL "
            "hold: (a) it has a 'Current Understanding' style section stating "
            "what the org believes now; (b) it captures rationale/why; (c) it "
            "is organized around a product area/concept, not pasted interview "
            "text; (d) no large verbatim quote block stands in for analysis. "
            "Score 0.5 if a page exists but reads like a notes dump. Be strict."
        ),
        threshold=0.7,
    )
    assert verdict.passed, (
        f"Judge rejected (score={verdict.score:.2f}): {verdict.reasoning}; "
        f"see {result.log_path}"
    )

"""Behavioural pack eval: STM checkpoint survives a context compaction.

Run the evolution cycle, then re-invoke the brain against the *same* input.
Because the durable STM checkpoints between every step, the second run must
resume/complete the same session without duplicating pages, and the STM
checkpoint + verbatim input must be retained on disk.

Structural eval (no judge) but requires the ``copilot`` CLI (``slow``).
"""

from __future__ import annotations

import pytest

PROMPT = """\
Use the product-knowledge-brain plugin to evolve the default knowledge base
(knowledge-base/) from the already-extracted note below. The note is already
extracted text from another tool.

Extracted note (source: PRD excerpt, 2026-05-20):
"Feature-b will add a self-serve quick-start path aimed at the SMB segment.
It supports the activation north-star goal."

Run the evolution cycle. The brain must checkpoint its in-flight state to
its durable short-term memory between steps so it can survive a context
compaction.
"""


@pytest.mark.pack
@pytest.mark.slow
def test_stm_checkpoint_survives_compaction(product_knowledge_brain):
    ws = product_knowledge_brain

    # First run — establishes the KB and the STM session.
    first = ws.run_agent(prompt=PROMPT, timeout=900, log_name="first")
    if not first.usable:
        pytest.skip(first.unavailable_reason())
    assert first.ok, f"first run exited {first.returncode}; see {first.log_path}"

    checkpoints = ws.glob(".product-knowledge-brain-stm/runs/*/checkpoint.json")
    assert checkpoints, (
        f"expected an STM checkpoint.json after the first run; see {first.log_path}"
    )
    inputs = ws.glob(".product-knowledge-brain-stm/runs/*/input/extracted-input.md")
    assert inputs, (
        f"expected the verbatim STM input to be persisted; see {first.log_path}"
    )

    pages_after_first = set(
        p.relative_to(ws.root).as_posix()
        for p in ws.glob("knowledge-base/**/*.md")
    )

    # Second run with the SAME input simulates a resume after compaction:
    # idempotent — it must not create duplicate concept pages.
    second = ws.run_agent(prompt=PROMPT, timeout=900, log_name="second")
    if not second.usable:
        pytest.skip(second.unavailable_reason())
    assert second.ok, f"second run exited {second.returncode}; see {second.log_path}"

    # Checkpoint + input still present (no data loss).
    assert ws.glob(".product-knowledge-brain-stm/runs/*/checkpoint.json"), (
        f"STM checkpoint lost after resume; see {second.log_path}"
    )
    assert ws.glob(".product-knowledge-brain-stm/runs/*/input/extracted-input.md"), (
        f"STM input lost after resume; see {second.log_path}"
    )

    # Idempotency: no near-duplicate concept page proliferation. Allow index
    # files to change; concept-page count must not grow on identical re-feed.
    concept_pages = ws.glob("knowledge-base/areas/*/knowledge/*.md")
    assert concept_pages, f"expected concept pages to persist; see {second.log_path}"
    pages_after_second = set(
        p.relative_to(ws.root).as_posix()
        for p in ws.glob("knowledge-base/**/*.md")
    )
    new_pages = pages_after_second - pages_after_first
    assert not new_pages, (
        f"re-feeding identical input created new pages {sorted(new_pages)} "
        f"(idempotency broken); see {second.log_path}"
    )

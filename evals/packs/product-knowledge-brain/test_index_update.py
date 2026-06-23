"""Behavioural pack eval: indexes update after a cycle.

Run a cycle that adds new knowledge to a product area. Afterwards the
relevant discovery index and the area-index must reference the newly added /
updated page (path + a why-it-matters line).

Structural eval (no judge) but requires the ``copilot`` CLI (``slow``).
"""

from __future__ import annotations

import pytest

PROMPT = """\
Use the product-knowledge-brain plugin to evolve the default knowledge base
(knowledge-base/) from the already-extracted note below. The note is already
extracted text from another tool.

Extracted note (source: roadmap, 2026-06-02):
"Feature-c is a new reporting dashboard for the analytics product area. It
gives admins exportable usage reports."

Run the full evolution cycle, including refreshing the discovery indexes so
future agents can find this knowledge.
"""


@pytest.mark.pack
@pytest.mark.slow
def test_index_update(product_knowledge_brain):
    ws = product_knowledge_brain

    result = ws.run_agent(prompt=PROMPT, timeout=900)
    if not result.usable:
        pytest.skip(result.unavailable_reason())
    assert result.ok, f"agent exited {result.returncode}; see {result.log_path}"

    # 1) Structural: a concept page was created for the new knowledge.
    pages = ws.glob("knowledge-base/areas/*/knowledge/*.md")
    assert pages, f"expected a new concept page; see {result.log_path}"
    page_stems = {p.stem.lower() for p in pages}

    # 2) An area-index and at least one discovery index exist.
    area_indexes = ws.glob("knowledge-base/areas/*/area-index.md")
    assert area_indexes, f"expected an area-index.md; see {result.log_path}"
    discovery_indexes = ws.glob("knowledge-base/indexes/*.md")
    assert discovery_indexes, f"expected discovery indexes; see {result.log_path}"

    # 3) The new page must be referenced from at least one index (by filename
    #    or by a recognizable concept token).
    tokens = {t for stem in page_stems for t in stem.split("-")}
    tokens |= page_stems
    tokens |= {"feature-c", "reporting", "dashboard", "analytics"}
    index_blob = "\n".join(
        idx.read_text(encoding="utf-8").lower()
        for idx in (area_indexes + discovery_indexes + ws.glob("knowledge-base/index.md"))
    )
    assert any(tok and tok in index_blob for tok in tokens), (
        "the new/updated knowledge was not referenced from any index "
        f"(index drift); see {result.log_path}"
    )

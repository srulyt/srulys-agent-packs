"""Behavioural pack eval: provenance + relationship links.

Run a cycle on input tying a persona to a strategic goal and a feature. The
resulting pages must carry evidence provenance (front-matter ``evidence:``
ids + inline ``[^E-..]`` citations) and at least one typed relationship
(``relationships:`` edge or ``[[..]]`` wiki-link), and an evidence
descriptor must exist under ``evidence/``.

Structural eval (no judge) but requires the ``copilot`` CLI (``slow``).
"""

from __future__ import annotations

import re

import pytest

PROMPT = """\
Use the product-knowledge-brain plugin to evolve the default knowledge base
(knowledge-base/) from the already-extracted note below. The note is already
extracted text from another tool.

Extracted note (source: exec discussion, 2026-06-01):
"Our enterprise-admin persona is the key buyer for the SMB-to-enterprise
segment. They drive demand for feature-a (onboarding), and serving them well
directly supports our activation north-star strategic goal."

Run the evolution cycle. Make sure every important claim is traceable to
evidence and that knowledge is linked across the relevant pages.
"""

EVIDENCE_RE = re.compile(r"\[\^E-\d+\]")
EVIDENCE_FM_RE = re.compile(r"evidence:\s*\[?\s*E-\d+", re.IGNORECASE)
WIKILINK_RE = re.compile(r"\[\[[^\]]+\]\]")
RELATIONSHIP_FM_RE = re.compile(r"rel:\s*\S+")


@pytest.mark.pack
@pytest.mark.slow
def test_provenance_relationship_links(copilot_pack):
    ws = copilot_pack("product-knowledge-brain")

    result = ws.run_agent(prompt=PROMPT, timeout=1500)
    if not result.usable:
        pytest.skip(result.unavailable_reason())
    assert result.ok, f"agent exited {result.returncode}; see {result.log_path}"

    # 1) An evidence descriptor exists under evidence/.
    evidence = ws.glob("knowledge-base/evidence/E-*.md")
    assert evidence, f"expected an evidence descriptor under evidence/; see {result.log_path}"

    # 2) At least one knowledge page carries provenance AND a relationship.
    pages = ws.glob("knowledge-base/**/*.md")
    pages = [p for p in pages if "/evidence/" not in p.as_posix() and p.name != "index.md"]
    assert pages, f"expected knowledge pages; see {result.log_path}"

    provenance_ok = False
    relationship_ok = False
    for p in pages:
        text = p.read_text(encoding="utf-8")
        if EVIDENCE_RE.search(text) and EVIDENCE_FM_RE.search(text):
            provenance_ok = True
        if RELATIONSHIP_FM_RE.search(text) or WIKILINK_RE.search(text):
            relationship_ok = True

    assert provenance_ok, (
        "no page carried both an evidence: front-matter id and an inline "
        f"[^E-..] citation; see {result.log_path}"
    )
    assert relationship_ok, (
        "no page carried a typed relationships: edge or a [[..]] wiki-link; "
        f"see {result.log_path}"
    )

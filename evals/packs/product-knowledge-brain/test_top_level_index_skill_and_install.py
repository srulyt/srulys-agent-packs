"""Behavioural pack eval: top-level index skill (on request) + install artifacts.

Seed a **small** KB (a handful of pages, no area past the crowded-area
threshold), run a cycle, and **explicitly ask** the agent to generate the
top-level / repo-wide index skill. This verifies the guarantee the tool
actually provides — an explicit request for a repo-wide index skill yields the
top-level router, regardless of KB size. Per the 2026-06-11 design pivot the
source ``_skills/`` dir is **bare** (namespacing happens at install time, not
generation):

- a top-level/root index skill at the bare path
  ``knowledge-base/_skills/knowledge-index/SKILL.md`` with a double-quoted,
  keyword-rich ``description`` and ``user-invocable: true`` is generated on
  explicit request;
- the install script(s) exist in ``_skills/``;
- ``_skills/removed-skills.json`` exists and parses with a ``kb_namespace``.

This is the top-level-index + install-artifacts regression guard: on an
explicit repo-wide request the KB gets the installable top-level router (the
skill-packaged twin of ``index.md``). The small KB shouldn't trip the per-area
threshold, so the top-level skill is expected; the test does not hard-fail if
the agent additionally emits something else.

Structural eval (no judge) but requires the ``copilot`` CLI (``slow``).
"""

from __future__ import annotations

import json

import pytest

PAGE_TEMPLATE = """\
---
title: "{title}"
type: product
area: feature-a
status: current
updated: 2026-05-01
evidence: [E-001]
---

# {title}

## Current Understanding
Concept {n} in the feature-a area [^E-001].

## Why / Rationale
Rationale for concept {n}.

## Related

## Change Log
- 2026-05-01 - created. [^E-001]

[^E-001]: see evidence/E-001.md
"""


@pytest.mark.pack
@pytest.mark.slow
def test_top_level_index_skill_and_install(product_knowledge_brain):
    ws = product_knowledge_brain

    kb = ws.root / "knowledge-base"
    knowledge_dir = kb / "areas" / "feature-a" / "knowledge"
    knowledge_dir.mkdir(parents=True, exist_ok=True)

    # Seed only 4 concept pages — a SMALL KB, well below the >12 crowded-area
    # threshold, so NO per-area skill should be generated (Tier-1).
    index_rows = []
    for n in range(1, 5):
        slug = f"concept-{n:02d}"
        title = f"Concept {n:02d}"
        (knowledge_dir / f"{slug}.md").write_text(
            PAGE_TEMPLATE.format(title=title, n=n), encoding="utf-8"
        )
        index_rows.append(
            f"| [{title}](knowledge/{slug}.md) | feature-a | Drives part {n}. |"
        )

    area_index = kb / "areas" / "feature-a" / "area-index.md"
    area_index.write_text(
        "# Feature A - Area Index\n\nLast updated: 2026-05-01\n\n## Knowledge\n\n"
        "| Page | Area | Why it matters |\n|---|---|---|\n"
        + "\n".join(index_rows)
        + "\n",
        encoding="utf-8",
    )

    ev = kb / "evidence" / "E-001.md"
    ev.parent.mkdir(parents=True, exist_ok=True)
    ev.write_text(
        "---\nid: E-001\nsource_type: prd\ndate: 2026-05-01\n---\n\n# E-001\n\nSeed.\n",
        encoding="utf-8",
    )

    prompt = """\
Use the product-knowledge-brain plugin against the existing knowledge base
at knowledge-base/. The note below is already-extracted text from another
tool.

Extracted note (source: PRD, 2026-06-03):
"Feature-a clarifies the onboarding flow for new teams."

Run the full evolution cycle. The knowledge base is small. Also generate the
top-level repo-wide index skill (the installable twin of index.md) so future
agents can route across the whole knowledge base.
"""

    result = ws.run_agent(prompt=prompt, timeout=1500)
    if not result.usable:
        pytest.skip(result.unavailable_reason())
    assert result.ok, f"agent exited {result.returncode}; see {result.log_path}"

    # 1) The top-level/root index skill with the BARE name is generated on
    #    explicit request (namespacing happens at install time, not generation).
    #    A small KB shouldn't trip the per-area threshold, so 'knowledge-index'
    #    is expected; do NOT hard-fail if the agent additionally emits another
    #    skill — only require that the top-level router is present.
    generated = ws.glob("knowledge-base/_skills/*/SKILL.md")
    assert generated, (
        f"expected the requested top-level index skill under _skills/; "
        f"see {result.log_path}"
    )
    dir_names = sorted(p.parent.name for p in generated)
    assert "knowledge-index" in dir_names, (
        f"an explicit repo-wide request must produce the top-level index skill "
        f"with the bare name 'knowledge-index' (NOT namespace-prefixed); "
        f"got {dir_names}; see {result.log_path}"
    )

    top = next(
        p for p in generated if p.parent.name == "knowledge-index"
    )
    text = top.read_text(encoding="utf-8")
    assert text.startswith("---"), (
        f"top-level skill must start with YAML frontmatter; see {result.log_path}"
    )
    desc_line = next(
        (ln for ln in text.splitlines() if ln.startswith("description:")), None
    )
    assert desc_line is not None, (
        f"top-level index skill missing a description; see {result.log_path}"
    )
    assert desc_line.partition(":")[2].strip().startswith('"'), (
        f"top-level index skill description MUST be double-quoted; see {result.log_path}"
    )
    assert any(
        ln.replace(" ", "").startswith("user-invocable:true")
        for ln in text.splitlines()
    ), (
        f"top-level index skill MUST set user-invocable: true; see {result.log_path}"
    )

    # 2) Install script(s) emitted into _skills/.
    install_scripts = (
        ws.glob("knowledge-base/_skills/install-skills.sh")
        + ws.glob("knowledge-base/_skills/install-skills.ps1")
        + ws.glob("knowledge-base/_skills/install-skills.py")
    )
    assert install_scripts, (
        f"expected an install script (install-skills.sh/.ps1/.py) under "
        f"_skills/; see {result.log_path}"
    )

    # 3) removed-skills.json exists, parses, carries kb_namespace.
    manifests = ws.glob("knowledge-base/_skills/removed-skills.json")
    assert manifests, (
        f"expected _skills/removed-skills.json manifest; see {result.log_path}"
    )
    manifest = json.loads(manifests[0].read_text(encoding="utf-8"))
    assert manifest.get("kb_namespace") == "knowledge-base", (
        f"removed-skills.json must carry kb_namespace == 'knowledge-base'; "
        f"got {manifest.get('kb_namespace')!r}; see {result.log_path}"
    )

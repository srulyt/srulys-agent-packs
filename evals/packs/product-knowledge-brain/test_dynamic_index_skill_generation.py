"""Behavioural pack eval: dynamic specialized index skill generation.

Seed a repo whose product area is well past the size threshold (many concept
pages + a crowded discovery index), then run a cycle. The brain must
generate a dynamic specialized index SKILL.md under ``<kb-root>/_skills/``
with a valid double-quoted ``description`` carrying domain discovery
keywords. Below-threshold areas must NOT trigger generation.

Structural eval (no judge) but requires the ``copilot`` CLI (``slow``).
"""

from __future__ import annotations

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
def test_dynamic_index_skill_generation(copilot_pack):
    ws = copilot_pack("product-knowledge-brain")

    kb = ws.root / "knowledge-base"
    knowledge_dir = kb / "areas" / "feature-a" / "knowledge"
    knowledge_dir.mkdir(parents=True, exist_ok=True)

    # Seed 18 concept pages — well past the crowded-area threshold (>12).
    index_rows = []
    for n in range(1, 19):
        slug = f"concept-{n:02d}"
        title = f"Concept {n:02d}"
        (knowledge_dir / f"{slug}.md").write_text(
            PAGE_TEMPLATE.format(title=title, n=n), encoding="utf-8"
        )
        index_rows.append(
            f"| [{title}](knowledge/{slug}.md) | feature-a | Drives part {n}. |"
        )

    # Crowded area-index reflecting the seeded pages.
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
at knowledge-base/. The feature-a area has grown very large (many concept
pages). The note below is already-extracted text from another tool.

Extracted note (source: PRD, 2026-06-03):
"Feature-a adds a new bulk-import concept for onboarding large teams."

Run the full evolution cycle. Given how large the feature-a area has grown,
generate a specialized dynamic index skill for it so future agents can route
to feature-a knowledge efficiently.
"""

    result = ws.run_agent(prompt=prompt, timeout=1500)
    if not result.usable:
        pytest.skip(result.unavailable_reason())
    assert result.ok, f"agent exited {result.returncode}; see {result.log_path}"

    # 1) Structural: a dynamic index SKILL.md was generated under _skills/.
    generated = ws.glob("knowledge-base/_skills/*/SKILL.md")
    assert generated, (
        f"expected a generated dynamic index skill under _skills/; see {result.log_path}"
    )

    # 2) It must have a double-quoted description in its frontmatter.
    text = generated[0].read_text(encoding="utf-8")
    assert text.startswith("---"), (
        f"generated skill must start with YAML frontmatter; see {result.log_path}"
    )
    desc_line = next(
        (ln for ln in text.splitlines() if ln.startswith("description:")), None
    )
    assert desc_line is not None, (
        f"generated index skill missing a description; see {result.log_path}"
    )
    assert desc_line.partition(":")[2].strip().startswith('"'), (
        f"generated index skill description MUST be double-quoted; see {result.log_path}"
    )

"""Behavioural pack eval: tiered index skills + install-script model.

Seed a repo whose product area is well past the size threshold (many concept
pages + a crowded discovery index), then run a cycle. Under the install-script
model the generated index skills **stay in the KB** at ``<kb-root>/_skills/``
(this location is correct, not a defect). Per the 2026-06-11 design pivot,
**namespacing happens at install time, not at generation** — the source dirs
under ``_skills/`` are **bare** (``knowledge-index``,
``feature-a-knowledge-index``); the install script adds the ``<kb-ns>-`` prefix
when it copies them into the shared harness dir.

This scenario exercises the **explicit-request + crowded-area** contract: the
prompt explicitly asks for a feature-a dynamic index skill AND the feature-a
area is well past the crowded-area threshold (18 pages > 12). Under that
combination the brain must:

- generate the per-area **feature-a** index skill (Tier-2, bare
  ``feature-a-knowledge-index``) under ``_skills/`` with a **bare**
  (NOT namespace-prefixed) dir name and a valid double-quoted ``description``.
  (The always-on top-level/root ``knowledge-index`` skill is **NOT** required by
  this scenario — an explicit, area-scoped request guarantees only the
  requested per-area skill; the top-level router is verified separately, on
  explicit request, in ``test_top_level_index_skill_and_install.py``.) The
  brain must also:
- emit an **install script** (``install-skills.sh`` and/or
  ``install-skills.ps1``) into ``_skills/`` that namespaces on install,
  references the ``installed-skills.json`` receipt, and implements
  uninstall-on-change scoped to the KB namespace;
- emit a **removed-skills manifest** (``removed-skills.json``) that parses and
  carries a ``kb_namespace`` field.

The agent never installs into a harness dir itself — the user runs the script.

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
def test_dynamic_index_skill_generation(product_knowledge_brain):
    ws = product_knowledge_brain

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

    # 1) Structural: index skills were generated under _skills/.
    generated = ws.glob("knowledge-base/_skills/*/SKILL.md")
    assert generated, (
        f"expected generated index skills under _skills/; see {result.log_path}"
    )

    # 2) Every generated SOURCE dir under _skills/ is BARE — NOT prefixed with
    #    the per-KB namespace. The KB-root basename is "knowledge-base", so a
    #    namespaced dir would start with "knowledge-base-"; under the pivot the
    #    source dirs MUST NOT (namespacing happens at install time).
    dir_names = {p.parent.name for p in generated}
    for name in dir_names:
        assert not name.startswith("knowledge-base-"), (
            f"index skill SOURCE dir '{name}' must be BARE (NOT namespace-"
            f"prefixed) under _skills/ — namespacing happens at install time, "
            f"not generation; see {result.log_path}"
        )
        assert name.endswith("-knowledge-index") or name == "knowledge-index", (
            f"index skill dir '{name}' must be a bare *-knowledge-index slug; "
            f"see {result.log_path}"
        )

    # 3) The per-area feature-a skill (bare 'feature-a-knowledge-index') must be
    #    present: this scenario guarantees it via the explicit request for a
    #    feature-a dynamic index skill combined with the crowded area (18 > 12).
    #    The top-level 'knowledge-index' router is NOT required here — an
    #    area-scoped explicit request yields only the requested per-area skill;
    #    the top-level skill's contract is covered by
    #    test_top_level_index_skill_and_install.py (explicit-request scenario).
    assert any("feature-a" in n for n in dir_names), (
        f"expected a per-area feature-a index skill (explicit request + crowded "
        f"area); got {sorted(dir_names)}; see {result.log_path}"
    )

    # 4) Each generated skill has a double-quoted description in its frontmatter.
    for skill in generated:
        text = skill.read_text(encoding="utf-8")
        assert text.startswith("---"), (
            f"{skill.parent.name} must start with YAML frontmatter; see {result.log_path}"
        )
        desc_line = next(
            (ln for ln in text.splitlines() if ln.startswith("description:")), None
        )
        assert desc_line is not None, (
            f"{skill.parent.name} missing a description; see {result.log_path}"
        )
        assert desc_line.partition(":")[2].strip().startswith('"'), (
            f"{skill.parent.name} description MUST be double-quoted; see {result.log_path}"
        )

    # 5) An install script was emitted into _skills/ (sh and/or ps1, or a
    #    single-source python script — accept any of these forms).
    install_scripts = (
        ws.glob("knowledge-base/_skills/install-skills.sh")
        + ws.glob("knowledge-base/_skills/install-skills.ps1")
        + ws.glob("knowledge-base/_skills/install-skills.py")
    )
    assert install_scripts, (
        f"expected an install script (install-skills.sh/.ps1/.py) under "
        f"_skills/; see {result.log_path}"
    )

    # 6) A removed-skills manifest exists, parses, and carries kb_namespace.
    import json

    manifests = ws.glob("knowledge-base/_skills/removed-skills.json")
    assert manifests, (
        f"expected _skills/removed-skills.json manifest; see {result.log_path}"
    )
    manifest = json.loads(manifests[0].read_text(encoding="utf-8"))
    assert manifest.get("kb_namespace") == "knowledge-base", (
        f"removed-skills.json must carry kb_namespace == 'knowledge-base'; "
        f"got {manifest.get('kb_namespace')!r}; see {result.log_path}"
    )

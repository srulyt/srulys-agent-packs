"""Structural pack eval: namespace-at-install + receipt + uninstall-on-change.

This is a **structural** eval (no Copilot CLI / LLM judge). It guards the
2026-06-11 design pivot at the *specification* layer — the install-script
reference doc (``harness-skills-dir.md``) is the single source of truth the
agent copies from when it emits ``install-skills.sh``/``.ps1`` into
``<kb-root>/_skills/``. It asserts that doc (and the skill instructions) encode:

* **Namespace-at-install:** the source ``_skills/`` dirs are BARE and the
  install script applies the ``<kb-ns>-`` prefix when it copies them into the
  shared harness dir (renaming dir + rewriting the copied ``SKILL.md`` ``name:``);
* **Install receipt:** the script maintains ``installed-skills.json`` recording
  what it installed (namespace + harness dir + source->installed mapping);
* **Uninstall-on-change:** on each run the script diffs the previous receipt and
  deletes skills it previously installed that are now gone/renamed, strictly
  scoped to this KB's ``<kb-ns>-`` namespace.

Both the ``.sh`` and ``.ps1`` skeletons in the doc must implement it.

It runs without the ``copilot`` binary, so it executes in plain CI.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
INDEXING_REFS = (
    REPO_ROOT
    / "agent-packs"
    / "product-knowledge-brain"
    / "skills"
    / "knowledge-indexing"
    / "references"
)
HARNESS_DOC = INDEXING_REFS / "harness-skills-dir.md"
MANIFEST_DOC = INDEXING_REFS / "removed-skills-manifest.md"


@pytest.mark.pack
def test_install_script_doc_namespaces_at_install_with_receipt():
    assert HARNESS_DOC.is_file(), f"missing install-script reference: {HARNESS_DOC}"
    text = HARNESS_DOC.read_text(encoding="utf-8")

    # 1) Namespace-at-install: rename bare source dir to <kb-ns>-<bare> on copy.
    assert "$NS-$bare" in text or "$NS-$($bare)" in text, (
        "the .sh skeleton must compute the installed name as <NS>-<bare> when "
        "copying a bare source dir into the harness dir"
    )
    assert '"$NS-$bare"' in text or "$NS-$bare" in text, (
        "expected the sh script to namespace the destination dir on copy"
    )
    assert '"$NS-$bare"' in text or '$instName = "$NS-$bare"' in text, (
        "the .ps1 skeleton must compute $instName = \"$NS-$bare\" on copy"
    )
    # The copied SKILL.md frontmatter name: must be rewritten to the installed name.
    assert re.search(r"name:\s*\$installed", text) or "name: $instName" in text, (
        "the install script must rewrite the copied SKILL.md 'name:' line to "
        "equal the namespaced destination dir"
    )

    # 2) Install receipt installed-skills.json is written and recorded.
    assert "installed-skills.json" in text, (
        "the install script must maintain an installed-skills.json receipt"
    )
    for token in ("source_bare_name", "installed_name"):
        assert token in text, (
            f"the receipt must record '{token}' (source->installed mapping)"
        )

    # 3) Uninstall-on-change scoped to this KB's namespace.
    low = text.lower()
    assert "uninstall" in low and "receipt" in low, (
        "the doc must describe uninstall-on-change driven by the receipt diff"
    )
    # Deletion must be guarded by the <NS>- prefix in BOTH skeletons.
    assert '"$NS"-*' in text, (
        "the .sh skeleton must scope deletions to names starting with \"$NS\"-"
    )
    assert '"$NS-*"' in text or '-like "$NS-*"' in text, (
        "the .ps1 skeleton must scope deletions to names matching \"$NS-*\""
    )

    # 4) Resolution order + non-zero fallback preserved.
    for rule in ("explicit-arg", "env-override", "repo-github", "user-copilot", "none"):
        assert rule in text, f"harness-dir resolution rule '{rule}' missing"
    assert "exit 3" in text, "no-harness fallback must exit non-zero (exit 3)"


@pytest.mark.pack
def test_receipt_schema_documented_in_manifest_ref():
    assert MANIFEST_DOC.is_file(), f"missing manifest reference: {MANIFEST_DOC}"
    text = MANIFEST_DOC.read_text(encoding="utf-8")

    # The installed-skills.json receipt schema is documented here.
    assert "installed-skills.json" in text, (
        "removed-skills-manifest.md must document the installed-skills.json receipt"
    )
    for token in ("kb_namespace", "harness_dir", "source_bare_name", "installed_name"):
        assert token in text, f"receipt schema must document '{token}'"

    # Uninstall-on-change behaviour is documented and namespace-scoped.
    low = text.lower()
    assert "uninstall-on-change" in low, (
        "the doc must describe uninstall-on-change"
    )
    assert "never touch" in low or "never touches" in low, (
        "the doc must state deletions never touch another KB's skills"
    )

    # Removed names are BARE under the pivot (script maps to <kb-ns>-<name>).
    assert "bare" in low, (
        "removed-skills.json names must be documented as bare (pivot)"
    )

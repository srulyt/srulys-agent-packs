"""Pack-level smoke: the EARS PRD plugin is a conformant agent plugin.

This is a **structural** eval (no Copilot CLI / LLM judge required). It
guards the *packaging* that the agent-plugin redesign introduces:

* ``plugin.json`` exists at the plugin root, parses as JSON, and declares
  a valid ``name`` (kebab-case, lowercase, <=64 chars, no slashes/colons
  -- an invalid name silently fails to load per the spec).
* the declared ``skills`` path resolves to an existing directory;
* each of the 4 skill subdirs holds a ``SKILL.md`` whose ``name``
  frontmatter equals its directory name, with a non-empty ``description``
  (<=1024 chars);
* the entry skill ``ears-prd-workflow`` is ``user-invocable: true``;
* the legacy ``.github/`` layout is gone and no ``agents/`` / ``prompts/``
  / ``chatmodes/`` / ``instructions/`` directories are present.
* the README documents install for all three hosts (VS Code, Copilot CLI,
  gh skill).

It runs without the ``copilot`` binary, so it executes in plain CI.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
PLUGIN_ROOT = REPO_ROOT / "agent-packs" / "prd-pilot"

EXPECTED_SKILLS = {
    "ears-prd-workflow",
    "prd-context-gathering",
    "grill-me-interrogation",
    "ears-prd-format",
}

NAME_RE = re.compile(r"^[a-z0-9-]{1,64}$")


def _frontmatter(skill_md: Path) -> dict[str, str]:
    """Parse the leading ``---`` YAML frontmatter as a flat key/value map.

    Deliberately minimal (no pyyaml dependency): the SKILL.md frontmatter
    is a flat mapping of ``key: value`` lines.
    """
    text = skill_md.read_text(encoding="utf-8")
    assert text.startswith("---"), f"{skill_md} must start with '---' frontmatter"
    end = text.index("\n---", 3)
    block = text[3:end].strip("\n")
    out: dict[str, str] = {}
    for line in block.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        key, _, value = line.partition(":")
        out[key.strip()] = value.strip().strip('"').strip("'")
    return out


@pytest.mark.pack
def test_plugin_json_is_conformant():
    """plugin.json exists at the root, parses, and has a valid name + skills."""
    manifest_path = PLUGIN_ROOT / "plugin.json"
    assert manifest_path.exists(), f"missing manifest: {manifest_path}"

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    name = manifest.get("name")
    assert name, "plugin.json must declare a 'name'"
    assert NAME_RE.match(name), (
        f"plugin name {name!r} must be kebab-case, lowercase, <=64 chars, "
        "no slashes/colons (else it silently fails to load)"
    )
    assert "/" not in name and ":" not in name

    desc = manifest.get("description", "")
    assert 0 < len(desc) <= 1024, "description must be present and <=1024 chars"

    skills_path = manifest.get("skills", "skills/")
    resolved = (PLUGIN_ROOT / str(skills_path).rstrip("/")).resolve()
    assert resolved.is_dir(), f"declared skills path does not resolve: {resolved}"

    # We assert no license is claimed unless the repo actually carries a
    # LICENSE file (C3: do not assert a license the repo does not have).
    if "license" in manifest:
        assert (REPO_ROOT / "LICENSE").exists(), (
            "plugin.json claims a license but the repo has no LICENSE file"
        )


@pytest.mark.pack
def test_four_skills_present_and_named_correctly():
    """Each skill subdir has a SKILL.md whose name == directory name."""
    skills_dir = PLUGIN_ROOT / "skills"
    found = {p.name for p in skills_dir.iterdir() if p.is_dir()}
    assert found == EXPECTED_SKILLS, (
        f"expected skills {sorted(EXPECTED_SKILLS)}, found {sorted(found)}"
    )

    for skill in EXPECTED_SKILLS:
        skill_md = skills_dir / skill / "SKILL.md"
        assert skill_md.exists(), f"missing {skill_md}"
        fm = _frontmatter(skill_md)
        assert fm.get("name") == skill, (
            f"{skill_md}: frontmatter name {fm.get('name')!r} != dir name {skill!r}"
        )
        desc = fm.get("description", "")
        assert 0 < len(desc) <= 1024, f"{skill_md}: description missing/too long"


@pytest.mark.pack
def test_entry_skill_is_user_invocable():
    """The workflow entry skill surfaces as a slash command."""
    fm = _frontmatter(PLUGIN_ROOT / "skills" / "ears-prd-workflow" / "SKILL.md")
    assert fm.get("user-invocable") == "true", (
        "ears-prd-workflow must be user-invocable: true so it surfaces as "
        "/prd-pilot:ears-prd-workflow"
    )


@pytest.mark.pack
def test_only_conformant_layout_present():
    """No legacy .github/ tree and no unused contribution dirs."""
    assert not (PLUGIN_ROOT / ".github").exists(), (
        "the legacy .github/ tree must be removed for the conformant plugin"
    )
    for forbidden in ("agents", "prompts", "chatmodes", "instructions"):
        assert not (PLUGIN_ROOT / forbidden).exists(), (
            f"unexpected '{forbidden}/' dir in a skills-only plugin"
        )


@pytest.mark.pack
def test_readme_documents_all_three_install_flows():
    """README documents VS Code, Copilot CLI, and gh skill installs."""
    readme = (PLUGIN_ROOT / "README.md").read_text(encoding="utf-8")
    assert "copilot plugin install" in readme, "missing Copilot CLI install flow"
    assert "gh skill install" in readme, "missing gh skill install flow"
    assert "chat.pluginLocations" in readme or "Install Plugin From Source" in readme, (
        "missing VS Code agent-plugin install flow"
    )

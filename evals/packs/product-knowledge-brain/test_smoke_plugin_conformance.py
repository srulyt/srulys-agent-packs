"""Pack-level smoke: Product Knowledge Brain is a conformant skills-only plugin.

This is a **structural** eval (no Copilot CLI / LLM judge required). It
guards the *packaging* of the skills-only plugin:

* ``plugin.json`` exists at the plugin root, parses as JSON, and declares a
  valid ``name`` (kebab-case, lowercase, <=64 chars, no slashes/colons);
* the declared ``skills`` path resolves to an existing directory;
* each of the 4 skill subdirs holds a ``SKILL.md`` whose ``name``
  frontmatter equals its directory name, with a non-empty quoted
  ``description`` (<=1024 chars);
* the entry skill ``knowledge-brain`` is ``user-invocable: true`` and the
  three specialists are ``user-invocable: false``;
* no ``agents/`` / ``prompts/`` / ``chatmodes/`` / ``instructions/`` /
  ``.github/`` directories are present;
* the README documents install for all three hosts (VS Code, Copilot CLI,
  gh skill);
* ``plugin.json`` omits ``license`` unless the repo carries a LICENSE.

It runs without the ``copilot`` binary, so it executes in plain CI.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
PLUGIN_ROOT = REPO_ROOT / "agent-packs" / "product-knowledge-brain"

ENTRY_SKILL = "knowledge-brain"
SPECIALIST_SKILLS = {
    "knowledge-consolidation",
    "knowledge-organization",
    "knowledge-indexing",
}
EXPECTED_SKILLS = {ENTRY_SKILL} | SPECIALIST_SKILLS

NAME_RE = re.compile(r"^[a-z0-9-]{1,64}$")


def _frontmatter(skill_md: Path) -> dict[str, str]:
    """Parse the leading ``---`` YAML frontmatter as a flat key/value map."""
    text = skill_md.read_text(encoding="utf-8")
    assert text.startswith("---"), f"{skill_md} must start with '---' frontmatter"
    end = text.index("\n---", 3)
    block = text[3:end].strip("\n")
    out: dict[str, str] = {}
    for line in block.splitlines():
        if not line.strip() or line.lstrip().startswith("#") or line.startswith(" "):
            continue
        key, _, value = line.partition(":")
        out[key.strip()] = value.strip().strip('"').strip("'")
    return out


def _description_is_quoted(skill_md: Path) -> bool:
    text = skill_md.read_text(encoding="utf-8")
    for line in text.splitlines():
        if line.startswith("description:"):
            return line.partition(":")[2].strip().startswith('"')
    return False


@pytest.mark.pack
def test_plugin_json_is_conformant():
    """plugin.json exists at the root, parses, and has a valid name + skills."""
    manifest_path = PLUGIN_ROOT / "plugin.json"
    assert manifest_path.exists(), f"missing manifest: {manifest_path}"

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    name = manifest.get("name")
    assert name == "product-knowledge-brain", f"unexpected plugin name {name!r}"
    assert NAME_RE.match(name), (
        f"plugin name {name!r} must be kebab-case, lowercase, <=64 chars"
    )
    assert "/" not in name and ":" not in name

    desc = manifest.get("description", "")
    assert 0 < len(desc) <= 1024, "description must be present and <=1024 chars"

    skills_path = manifest.get("skills", "skills/")
    resolved = (PLUGIN_ROOT / str(skills_path).rstrip("/")).resolve()
    assert resolved.is_dir(), f"declared skills path does not resolve: {resolved}"

    # Mirror prd-pilot: no license unless the repo actually carries a LICENSE.
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
        assert _description_is_quoted(skill_md), (
            f"{skill_md}: description value MUST be double-quoted"
        )


@pytest.mark.pack
def test_invocation_flags_match_roles():
    """Entry skill is user-invocable; specialists are not."""
    skills_dir = PLUGIN_ROOT / "skills"

    entry_fm = _frontmatter(skills_dir / ENTRY_SKILL / "SKILL.md")
    assert entry_fm.get("user-invocable") == "true", (
        f"{ENTRY_SKILL} must be user-invocable: true (entry skill)"
    )

    for skill in SPECIALIST_SKILLS:
        fm = _frontmatter(skills_dir / skill / "SKILL.md")
        assert fm.get("user-invocable") == "false", (
            f"{skill} must be user-invocable: false (specialist handoff skill)"
        )


@pytest.mark.pack
def test_only_conformant_layout_present():
    """No legacy .github/ tree and no unused contribution dirs."""
    assert not (PLUGIN_ROOT / ".github").exists(), (
        "the .github/ tree must be absent for a skills-only plugin"
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

"""Pack-level smoke: ``eval-pilot`` is a conformant agent plugin + engine.

This is a **structural** eval (no Copilot CLI / LLM judge required). It guards
the packaging of the portable eval plugin:

* ``plugin.json`` exists at the plugin root, parses, declares a valid kebab-case
  ``name``, a non-empty ``description``, and ``agents`` / ``skills`` paths that
  resolve to directories.
* the 3 skills (``eval-author``, ``eval-runner``, ``eval-metrics``) each have a
  ``SKILL.md`` whose ``name`` frontmatter equals its directory name, a non-empty
  ``description``, and ``user-invocable: true`` (they are all slash-invocable).
* the bundled ``eval-judge`` agent exists under ``agents/`` and a byte-identical
  copy ships as package data under ``engine/src/evalpilot/_data/agents/`` (the
  judge runs in arbitrary repos from package data, so the two must stay in sync).
* the ``engine/pyproject.toml`` declares the ``evalpilot`` package, the
  ``evalpilot`` console script, the ``pytest11`` entry-point (so target repos
  need no conftest), and ships ``_data`` as package data.
* the README documents the Copilot CLI, VS Code, and ``gh skill`` install flows.
* ``.github/plugin/marketplace.json`` registers ``eval-pilot`` at the right
  source path.

It runs without the ``copilot`` binary, so it executes in plain CI.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
PLUGIN_ROOT = REPO_ROOT / "agent-packs" / "eval-pilot"

EXPECTED_SKILLS = {"eval-author", "eval-runner", "eval-metrics"}

NAME_RE = re.compile(r"^[a-z0-9-]{1,64}$")


def _frontmatter(skill_md: Path) -> dict[str, str]:
    """Parse the leading ``---`` frontmatter as a flat key/value map.

    Deliberately minimal (no pyyaml dependency). Block scalars (``key: |``)
    yield an empty value, which is fine: this helper is only used for flat
    keys (``name``, ``user-invocable``).
    """
    text = skill_md.read_text(encoding="utf-8")
    assert text.startswith("---"), f"{skill_md} must start with '---' frontmatter"
    end = text.index("\n---", 3)
    block = text[3:end].strip("\n")
    out: dict[str, str] = {}
    for line in block.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line[:1] in (" ", "\t"):  # nested / continuation line
            continue
        key, _, value = line.partition(":")
        out[key.strip()] = value.strip().strip('"').strip("'")
    return out


@pytest.mark.pack
def test_plugin_json_is_conformant():
    """plugin.json exists, parses, and declares valid name + agents + skills."""
    manifest_path = PLUGIN_ROOT / "plugin.json"
    assert manifest_path.exists(), f"missing manifest: {manifest_path}"

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    name = manifest.get("name")
    assert name == "eval-pilot", f"unexpected plugin name {name!r}"
    assert NAME_RE.match(name), (
        f"plugin name {name!r} must be kebab-case, lowercase, <=64 chars, "
        "no slashes/colons (else it silently fails to load)"
    )

    desc = manifest.get("description", "")
    assert 0 < len(desc) <= 1024, "description must be present and <=1024 chars"

    for key in ("agents", "skills"):
        rel = manifest.get(key)
        assert rel, f"plugin.json must declare an '{key}' path"
        resolved = (PLUGIN_ROOT / str(rel).rstrip("/")).resolve()
        assert resolved.is_dir(), f"declared {key} path does not resolve: {resolved}"

    # Do not claim a license the repo does not carry (no LICENSE file here).
    if "license" in manifest:
        assert (REPO_ROOT / "LICENSE").exists(), (
            "plugin.json claims a license but the repo has no LICENSE file"
        )


@pytest.mark.pack
def test_three_skills_present_named_and_invocable():
    """Each skill subdir has a SKILL.md named after it and user-invocable."""
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
        assert fm.get("user-invocable") == "true", (
            f"{skill} must be user-invocable: true so it surfaces as "
            f"/eval-pilot:{skill}"
        )


@pytest.mark.pack
def test_eval_judge_agent_present_and_synced():
    """The judge ships under agents/ and as byte-identical package data."""
    plugin_agent = PLUGIN_ROOT / "agents" / "eval-judge.agent.md"
    assert plugin_agent.exists(), f"missing {plugin_agent}"
    fm = _frontmatter(plugin_agent)
    assert fm.get("name") == "eval-judge", (
        f"agent frontmatter name {fm.get('name')!r} != 'eval-judge'"
    )

    bundled = (
        PLUGIN_ROOT
        / "engine" / "src" / "evalpilot" / "_data" / "agents" / "eval-judge.agent.md"
    )
    assert bundled.exists(), f"missing bundled judge package data: {bundled}"
    assert bundled.read_bytes() == plugin_agent.read_bytes(), (
        "the bundled judge (package data) and agents/ copy have drifted; "
        "the judge runs from package data in arbitrary repos, so they must "
        "stay byte-identical"
    )


@pytest.mark.pack
def test_engine_packaging_is_conformant():
    """engine/pyproject.toml ships the evalpilot package, CLI, and pytest plugin."""
    pyproject = PLUGIN_ROOT / "engine" / "pyproject.toml"
    assert pyproject.exists(), f"missing {pyproject}"
    text = pyproject.read_text(encoding="utf-8")

    assert 'name = "evalpilot"' in text, "engine must declare the evalpilot package"
    assert 'evalpilot = "evalpilot.cli:main"' in text, "missing evalpilot console script"
    assert "[project.entry-points.pytest11]" in text, (
        "engine must register a pytest11 entry-point so target repos need no "
        "conftest wiring"
    )
    assert "_data" in text, "engine must ship _data (agents + templates) as package data"

    # The package source tree must exist with its key modules.
    src = PLUGIN_ROOT / "engine" / "src" / "evalpilot"
    for mod in ("cli.py", "rubric.py", "metrics.py", "judge.py", "pytest_plugin.py"):
        assert (src / mod).exists(), f"missing engine module: {src / mod}"


@pytest.mark.pack
def test_readme_documents_all_three_install_flows():
    """README documents Copilot CLI, VS Code, and gh skill installs."""
    readme = (PLUGIN_ROOT / "README.md").read_text(encoding="utf-8")
    assert "copilot plugin install" in readme, "missing Copilot CLI install flow"
    assert "gh skill install" in readme, "missing gh skill install flow"
    assert "chat.pluginLocations" in readme or "Install Plugin From Source" in readme, (
        "missing VS Code agent-plugin install flow"
    )


@pytest.mark.pack
def test_marketplace_registers_eval_pilot():
    """The repo marketplace registry lists eval-pilot at the right source."""
    registry = json.loads(
        (REPO_ROOT / ".github" / "plugin" / "marketplace.json").read_text("utf-8")
    )
    entries = {p["name"]: p for p in registry.get("plugins", [])}
    assert "eval-pilot" in entries, "eval-pilot not registered in marketplace.json"
    assert entries["eval-pilot"]["source"] == "agent-packs/eval-pilot", (
        "eval-pilot marketplace source path is wrong"
    )

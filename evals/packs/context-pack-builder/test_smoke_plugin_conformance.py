"""Structural conformance smoke for the context-pack-builder plugin.

No CLI / no LLM: reads the shipped pack files directly and asserts the plugin is
mechanically loadable and internally consistent. This is the gate the
architecture defers the live-doc re-verification behind (the token threshold is
read from the single-source skill reference, not duplicated here).
"""

from __future__ import annotations

import json
import math
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
PACK = REPO_ROOT / "agent-packs" / "context-pack-builder"
MARKETPLACE = REPO_ROOT / ".github" / "plugin" / "marketplace.json"
THRESHOLD_REF = (
    PACK / "skills" / "progressive-disclosure" / "references" / "split-threshold.md"
)

EXPECTED_AGENTS = {
    "cpb-orchestrator",
    "cpb-discovery",
    "cpb-analyzer",
    "cpb-synthesizer",
    "cpb-writer",
    "cpb-indexer",
}
EXPECTED_SKILLS = {"context-pack-schema", "context-discovery", "progressive-disclosure"}

# Canonical supported frontmatter keys (agent-builder SKILL.md schema).
SUPPORTED_AGENT_KEYS = {
    "name",
    "description",
    "tools",
    "disable-model-invocation",
    "user-invocable",
    "model",
    "target",
}
# Skills support name/description/license; user-invocable is also valid on a
# SKILL.md (knowledge-brain precedent) and MUST NOT be falsely rejected (C2).
SUPPORTED_SKILL_KEYS = {"name", "description", "license", "user-invocable"}


def _split_frontmatter(text: str) -> tuple[list[str], str]:
    """Return (frontmatter_lines, body_text). Frontmatter is between the first
    two '---' fences and MUST start at line 1."""
    lines = text.splitlines()
    assert lines and lines[0].strip() == "---", "frontmatter must start at line 1"
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    assert end is not None, "frontmatter block is not closed"
    body = "\n".join(lines[end + 1 :])
    return lines[1:end], body


def _top_level_keys(fm_lines: list[str]) -> list[str]:
    keys = []
    for ln in fm_lines:
        if ln and not ln[0].isspace() and ":" in ln:
            keys.append(ln.split(":", 1)[0].strip())
    return keys


def _read_threshold() -> int:
    text = THRESHOLD_REF.read_text(encoding="utf-8")
    m = re.search(r"SPLIT_THRESHOLD_TOKENS\s*=\s*(\d+)", text)
    assert m, "split-threshold.md must define SPLIT_THRESHOLD_TOKENS"
    return int(m.group(1))


def _token_estimate(body: str) -> int:
    chars = len(body)
    words = len(body.split())
    return max(math.ceil(chars / 4), math.ceil(words * 1.33))


@pytest.mark.pack
def test_plugin_json_manifest():
    manifest = json.loads((PACK / "plugin.json").read_text(encoding="utf-8"))
    for key in ("name", "description", "agents", "skills"):
        assert key in manifest, f"plugin.json missing required key {key!r}"
    assert manifest["name"] == "context-pack-builder"
    assert manifest["agents"] == "agents/"
    assert manifest["skills"] == "skills/"


@pytest.mark.pack
def test_marketplace_registration():
    market = json.loads(MARKETPLACE.read_text(encoding="utf-8"))
    names = {p["name"] for p in market["plugins"]}
    assert "context-pack-builder" in names, "pack not registered in marketplace.json"
    # Existing entries must be undisturbed.
    assert {"prd-pilot", "product-knowledge-brain", "eval-pilot"} <= names


@pytest.mark.pack
def test_expected_agents_and_skills_exist():
    agents = {p.stem.replace(".agent", "") for p in (PACK / "agents").glob("*.agent.md")}
    assert EXPECTED_AGENTS <= agents, f"missing agents: {EXPECTED_AGENTS - agents}"
    skills = {p.name for p in (PACK / "skills").iterdir() if p.is_dir()}
    assert EXPECTED_SKILLS <= skills, f"missing skills: {EXPECTED_SKILLS - skills}"
    for s in EXPECTED_SKILLS:
        assert (PACK / "skills" / s / "SKILL.md").is_file(), f"{s} missing SKILL.md"


@pytest.mark.pack
def test_agent_frontmatter_quoted_and_supported_keys():
    orchestrators = 0
    subagents = 0
    for path in (PACK / "agents").glob("*.agent.md"):
        fm_lines, _ = _split_frontmatter(path.read_text(encoding="utf-8"))
        keys = _top_level_keys(fm_lines)
        assert len(keys) == len(set(keys)), f"{path.name}: duplicate frontmatter key"
        for k in keys:
            assert k in SUPPORTED_AGENT_KEYS, f"{path.name}: unsupported key {k!r}"
        desc = [ln for ln in fm_lines if ln.startswith("description:")]
        assert desc, f"{path.name}: missing description"
        val = desc[0].split(":", 1)[1].strip()
        assert val.startswith('"') and val.endswith('"'), (
            f"{path.name}: description must be double-quoted"
        )
        joined = "\n".join(fm_lines)
        if "disable-model-invocation: true" in joined:
            orchestrators += 1
            assert "user-invocable: true" in joined, f"{path.name}: orch must be user-invocable"
        else:
            subagents += 1
            assert "user-invocable: false" in joined, (
                f"{path.name}: subagent must set user-invocable: false"
            )
            assert "disable-model-invocation" not in joined, (
                f"{path.name}: subagent must NOT set disable-model-invocation"
            )
    assert orchestrators == 1, f"expected exactly one orchestrator, got {orchestrators}"
    assert subagents == 5, f"expected exactly five subagents, got {subagents}"


@pytest.mark.pack
def test_skill_frontmatter_quoted_and_supported_keys():
    for path in (PACK / "skills").glob("*/SKILL.md"):
        fm_lines, _ = _split_frontmatter(path.read_text(encoding="utf-8"))
        keys = _top_level_keys(fm_lines)
        for k in keys:
            assert k in SUPPORTED_SKILL_KEYS, f"{path}: unsupported skill key {k!r}"
        desc = [ln for ln in fm_lines if ln.startswith("description:")]
        assert desc, f"{path}: missing description"
        val = desc[0].split(":", 1)[1].strip()
        assert val.startswith('"') and val.endswith('"'), (
            f"{path}: description must be double-quoted"
        )


@pytest.mark.pack
def test_no_bundled_skill_body_over_threshold():
    """Every shipped SKILL.md body must stay under the single-source threshold."""
    threshold = _read_threshold()
    for path in (PACK / "skills").glob("*/SKILL.md"):
        _, body = _split_frontmatter(path.read_text(encoding="utf-8"))
        est = _token_estimate(body)
        assert est <= threshold, (
            f"{path}: body token estimate {est} exceeds threshold {threshold}"
        )

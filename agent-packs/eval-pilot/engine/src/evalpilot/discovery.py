"""Discover agents and skills across Copilot's supported layouts.

A target repository may declare agents and skills in several places. The
original monorepo harness only knew about ``agent-packs/<pack>/.github/...``;
this generalised discovery understands every layout the Copilot CLI itself
loads from, so evalpilot works in an arbitrary repo:

Agents (``<name>.agent.md``):
  * ``.github/agents/`` (repo-level custom agents)
  * ``<plugin>/agents/`` (plugin-root layout, e.g. ``agent-packs/<pack>/agents``)
  * ``.github/agents/`` *inside* a pack (monorepo legacy)

Skills (``<name>/SKILL.md``):
  * ``.github/skills/<name>/`` (repo-level / shared)
  * ``<plugin>/skills/<name>/`` (plugin-root layout)

The discovery functions return small descriptors so the workspace stager
and the CLI can present "what can I evaluate here?" without re-implementing
the walk.
"""

from __future__ import annotations

import dataclasses
from pathlib import Path
from typing import Iterable, Optional

from .config import find_repo_root


# Directories we never descend into while discovering (build output, vcs,
# virtualenvs, the engine's own scratch).
_PRUNE = {
    ".git", ".hg", ".svn", "node_modules", "__pycache__", ".venv", "venv",
    ".pytest_cache", ".mypy_cache", "dist", "build", ".tox", "_runs",
    "_logs", "_metrics",
}


@dataclasses.dataclass(frozen=True)
class AgentInfo:
    """A discovered custom agent."""

    name: str
    """Agent name (filename stem, e.g. ``eval-judge`` for ``eval-judge.agent.md``)."""

    path: Path
    """Absolute path to the ``.agent.md`` file."""

    agents_dir: Path
    """The ``agents/`` (or ``.github/agents/``) directory containing it."""

    plugin_root: Optional[Path]
    """Plugin root if this agent belongs to a plugin (manifest sibling), else None."""


@dataclasses.dataclass(frozen=True)
class SkillInfo:
    """A discovered skill."""

    name: str
    """Skill name (the ``SKILL.md`` parent directory name)."""

    path: Path
    """Absolute path to the skill directory (the one containing ``SKILL.md``)."""

    skills_dir: Path
    """The ``skills/`` (or ``.github/skills/``) directory containing it."""

    plugin_root: Optional[Path]
    """Plugin root if this skill belongs to a plugin, else None."""


def _iter_dirs(root: Path, name: str) -> Iterable[Path]:
    """Yield every directory named ``name`` under ``root`` (pruned)."""
    if not root.exists():
        return
    for dirpath, dirnames, _ in _walk(root):
        # prune in place
        dirnames[:] = [d for d in dirnames if d not in _PRUNE]
        if dirpath.name == name:
            yield dirpath


def _walk(root: Path):
    """A small ``os.walk``-like generator yielding ``Path`` dirpaths."""
    import os

    for dirpath, dirnames, filenames in os.walk(root):
        yield Path(dirpath), dirnames, filenames


def _plugin_root_for(start: Path) -> Optional[Path]:
    """Return the nearest ancestor of ``start`` containing a ``plugin.json``."""
    for parent in [start, *start.parents]:
        if (parent / "plugin.json").is_file():
            return parent
    return None


def discover_agents(repo_root: Optional[Path] = None) -> list[AgentInfo]:
    """Return all custom agents declared anywhere in the repo."""
    repo_root = repo_root or find_repo_root()
    seen: dict[Path, AgentInfo] = {}
    for agents_dir in _iter_dirs(repo_root, "agents"):
        for f in sorted(agents_dir.glob("*.agent.md")):
            info = AgentInfo(
                name=f.name[: -len(".agent.md")],
                path=f.resolve(),
                agents_dir=agents_dir.resolve(),
                plugin_root=_plugin_root_for(agents_dir),
            )
            seen[info.path] = info
    return sorted(seen.values(), key=lambda a: (a.name, str(a.path)))


def discover_skills(repo_root: Optional[Path] = None) -> list[SkillInfo]:
    """Return all skills declared anywhere in the repo."""
    repo_root = repo_root or find_repo_root()
    seen: dict[Path, SkillInfo] = {}
    for skills_dir in _iter_dirs(repo_root, "skills"):
        for skill_md in sorted(skills_dir.glob("*/SKILL.md")):
            skill_dir = skill_md.parent
            info = SkillInfo(
                name=skill_dir.name,
                path=skill_dir.resolve(),
                skills_dir=skills_dir.resolve(),
                plugin_root=_plugin_root_for(skills_dir),
            )
            seen[info.path] = info
    return sorted(seen.values(), key=lambda s: (s.name, str(s.path)))


def find_agent(name: str, repo_root: Optional[Path] = None) -> AgentInfo:
    """Return the single agent named ``name`` or raise."""
    matches = [a for a in discover_agents(repo_root) if a.name == name]
    if len(matches) == 1:
        return matches[0]
    if not matches:
        available = ", ".join(a.name for a in discover_agents(repo_root)) or "(none)"
        raise LookupError(f"No agent named {name!r}. Available: {available}")
    raise LookupError(
        f"Agent {name!r} is ambiguous across {len(matches)} locations: "
        f"{[str(m.path) for m in matches]}"
    )


def find_skill(name: str, repo_root: Optional[Path] = None) -> SkillInfo:
    """Return the single skill named ``name`` or raise."""
    matches = [s for s in discover_skills(repo_root) if s.name == name]
    if len(matches) == 1:
        return matches[0]
    if not matches:
        available = ", ".join(s.name for s in discover_skills(repo_root)) or "(none)"
        raise LookupError(f"No skill named {name!r}. Available: {available}")
    raise LookupError(
        f"Skill {name!r} is ambiguous across {len(matches)} locations: "
        f"{[str(m.path) for m in matches]}"
    )


__all__ = [
    "AgentInfo",
    "SkillInfo",
    "discover_agents",
    "discover_skills",
    "find_agent",
    "find_skill",
]

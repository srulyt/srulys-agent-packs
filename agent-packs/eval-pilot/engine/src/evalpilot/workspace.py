"""Per-test isolated workspaces for evals (repo-agnostic).

A :class:`Workspace` wraps a temporary directory the SUT is launched from
and provides:

* staging helpers (:meth:`stage_agent`, :meth:`stage_skill`,
  :meth:`stage_all`, :meth:`stage_files`, :meth:`stage_judge_agent`) that
  copy discovered agents/skills into the workspace's ``.github/`` tree so
  the SUT discovers them when the workspace is its ``cwd``;
* SUT drivers (:meth:`run_agent`, :meth:`run_skill`) delegating to the
  configured :class:`~evalpilot.runners.base.SUTRunner`;
* inspection helpers (:meth:`glob`, :meth:`find_one`, :meth:`read`).

Unlike the original monorepo harness, nothing here assumes an
``agent-packs/`` layout: agents and skills are located by
:mod:`evalpilot.discovery`, which understands both ``.github/agents`` and
plugin-root ``agents/`` / ``skills/`` layouts in any repository.
"""

from __future__ import annotations

import dataclasses
import difflib
import shutil
import subprocess
from pathlib import Path
from typing import Optional

from . import discovery
from .config import find_judge_agent_file, find_repo_root
from .runners.base import RunResult, SUTRunner, get_runner


@dataclasses.dataclass
class Workspace:
    """Isolated working directory for a single eval test."""

    root: Path
    logs_dir: Path
    runner: Optional[SUTRunner] = None
    repo_root: Optional[Path] = None

    def __post_init__(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        if self.runner is None:
            self.runner = get_runner()
        if self.repo_root is None:
            self.repo_root = find_repo_root()
        if not (self.root / ".git").exists():
            try:
                subprocess.run(["git", "init", "-q"], cwd=str(self.root), check=False)
            except FileNotFoundError:
                pass

    # ---- staging --------------------------------------------------------

    def stage_agent(self, name: str, *, include_skills: bool = True) -> None:
        """Stage a discovered agent (and, if it's a plugin, its skills).

        Copies the agent's containing ``agents/`` directory into
        ``.github/agents`` so the SUT loads it. If the agent belongs to a
        plugin, that plugin's ``skills/`` and ``instructions/`` directories
        are staged too (unless ``include_skills=False``). Legacy pack layouts
        with ``.github/agents`` also stage sibling ``.github/skills`` and
        ``.github/instructions`` directories, matching a real install.
        """
        info = discovery.find_agent(name, self.repo_root)
        _copy_tree(info.agents_dir, self.root / ".github" / "agents", merge=True)
        if include_skills:
            for src in _support_dirs_for_agent(info):
                _copy_tree(
                    self._normalise_sub(src),
                    self.root / ".github" / src.name,
                    merge=True,
                )

    def stage_skill(self, name: str) -> None:
        """Stage exactly one discovered skill (no agents)."""
        info = discovery.find_skill(name, self.repo_root)
        _copy_tree(info.path, self.root / ".github" / "skills" / name)

    def stage_all(self) -> None:
        """Stage every agent and skill discovered in the repo.

        Useful for "evaluate whatever this repo ships" smoke evals.
        """
        for agent in discovery.discover_agents(self.repo_root):
            _copy_tree(agent.agents_dir, self.root / ".github" / "agents", merge=True)
        for skill in discovery.discover_skills(self.repo_root):
            _copy_tree(skill.path, self.root / ".github" / "skills" / skill.name)

    def stage_judge_agent(self) -> None:
        """Stage evalpilot's bundled ``eval-judge`` agent into the workspace."""
        agent_file = find_judge_agent_file()
        if agent_file is None:
            raise FileNotFoundError(
                "Bundled eval-judge agent not found. Set EVALPILOT_JUDGE_AGENT "
                "to its path or reinstall evalpilot."
            )
        dest = self.root / ".github" / "agents"
        dest.mkdir(parents=True, exist_ok=True)
        shutil.copy2(agent_file, dest / agent_file.name)

    def stage_files(self, src: Path, dest_subdir: str = ".") -> None:
        """Copy ``src`` (file or dir) into ``workspace/<dest_subdir>``."""
        target = (self.root / dest_subdir).resolve()
        target.mkdir(parents=True, exist_ok=True)
        if src.is_dir():
            _copy_tree(src, target, merge=True)
        else:
            shutil.copy2(src, target / src.name)

    @staticmethod
    def _normalise_sub(src: Path) -> Path:
        return src

    # ---- driving the SUT ------------------------------------------------

    def run_agent(
        self,
        prompt: str,
        *,
        agent: Optional[str] = None,
        timeout: float = 600.0,
        log_name: str = "agent",
    ) -> RunResult:
        assert self.runner is not None
        return self.runner.run_agent(
            prompt=prompt,
            workspace=self.root,
            agent=agent,
            log_path=self.logs_dir / f"{log_name}.log",
            timeout=timeout,
        )

    def run_skill(
        self,
        skill: str,
        prompt: str,
        *,
        timeout: float = 300.0,
        log_name: str = "skill",
    ) -> RunResult:
        assert self.runner is not None
        return self.runner.run_skill(
            skill=skill,
            prompt=prompt,
            workspace=self.root,
            log_path=self.logs_dir / f"{log_name}.log",
            timeout=timeout,
        )

    # ---- inspection -----------------------------------------------------

    def glob(self, pattern: str) -> list[Path]:
        return sorted(self.root.glob(pattern))

    def find_one(self, pattern: str) -> Path:
        """Return the single match for ``pattern``; raise if 0 or >1 found."""
        matches = self.glob(pattern)
        if len(matches) == 1:
            return matches[0]
        if len(matches) == 0:
            raise FixtureMissingError(
                pattern=pattern,
                workspace_root=self.root,
                suggestions=_suggest_close_paths(self.root, pattern),
            )
        raise AssertionError(
            f"Expected exactly 1 match for {pattern!r} in workspace, "
            f"got {len(matches)}: {matches}"
        )

    def read(self, relative_path: str) -> str:
        return (self.root / relative_path).read_text(encoding="utf-8", errors="replace")


# ---- internal helpers ---------------------------------------------------


class FixtureMissingError(AssertionError):
    """Raised by :meth:`Workspace.find_one` when zero matches are found."""

    def __init__(self, *, pattern: str, workspace_root: Path,
                 suggestions: list[str]) -> None:
        self.pattern = pattern
        self.workspace_root = workspace_root
        self.suggestions = suggestions
        suggestion_block = (
            "\n  closest paths in workspace:\n    - " + "\n    - ".join(suggestions)
            if suggestions
            else "\n  (workspace appears empty)"
        )
        super().__init__(
            f"Expected exactly 1 match for {pattern!r} in workspace at "
            f"{workspace_root}, got 0.\n"
            f"  This usually means the fixture file is missing, or the agent "
            f"failed to create the artefact (check the agent log)."
            f"{suggestion_block}"
        )


def _suggest_close_paths(root: Path, pattern: str, *, n: int = 5) -> list[str]:
    bare = pattern.replace("*", "").replace("?", "").strip("/\\") or pattern
    try:
        candidates = [
            str(p.relative_to(root)).replace("\\", "/")
            for p in root.rglob("*")
            if p.is_file()
        ]
    except OSError:
        return []
    return difflib.get_close_matches(bare, candidates, n=n, cutoff=0.3)


def _copy_tree(src: Path, dest: Path, *, merge: bool = False) -> None:
    """Copy ``src`` directory into ``dest``. If ``merge``, keep existing
    files in ``dest`` that don't exist in ``src``."""
    if not merge and dest.exists():
        shutil.rmtree(dest)
    if merge:
        dest.mkdir(parents=True, exist_ok=True)
        for item in src.rglob("*"):
            rel = item.relative_to(src)
            target = dest / rel
            if item.is_dir():
                target.mkdir(parents=True, exist_ok=True)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(item, target)
    else:
        shutil.copytree(src, dest)


def _support_dirs_for_agent(info: discovery.AgentInfo) -> list[Path]:
    """Return skills/instructions dirs that should be staged with an agent."""
    if info.plugin_root is not None:
        base = info.plugin_root
    elif info.agents_dir.parent.name == ".github":
        base = info.agents_dir.parent
    else:
        return []
    return [src for sub in ("skills", "instructions")
            if (src := base / sub).exists()]


__all__ = ["Workspace", "FixtureMissingError"]

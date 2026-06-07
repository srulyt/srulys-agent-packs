"""Per-test isolated workspaces for evals.

A :class:`Workspace` wraps a pytest ``tmp_path`` and provides:

* :meth:`stage_pack` -- copies an agent pack's ``.github/agents`` (and the
  shared ``.github/skills`` + ``.github/instructions``) into the workspace
  so Copilot CLI can discover them when the workspace is its ``cwd``.
* :meth:`stage_skill` -- copies a single skill in isolation (no agents
  staged) for skill-only evals.
* :meth:`stage_files` -- copies arbitrary input files into the workspace.
* :meth:`run_agent` / :meth:`run_skill` -- delegate to ``_lib.copilot``;
  log paths default to ``workspace/_logs/``.
* :meth:`find_one`, :meth:`glob`, :meth:`read` -- inspect produced
  artifacts in the workspace.

The workspace is created under pytest's ``tmp_path``; pytest automatically
keeps the last few runs of each test on disk under
``$TMPDIR/pytest-of-<user>/`` so failed runs are inspectable.
"""

from __future__ import annotations

import dataclasses
import difflib
import shutil
import subprocess
from pathlib import Path
from typing import Iterable

from . import copilot


REPO_ROOT = Path(__file__).resolve().parents[2]
"""Resolved at import time; the directory containing ``agent-packs/`` etc."""


@dataclasses.dataclass
class Workspace:
    """Isolated working directory for a single eval test."""

    root: Path
    """The directory Copilot CLI is launched from."""

    logs_dir: Path
    """Where copilot subprocess logs are written. Defaults to ``root/_logs``."""

    def __post_init__(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        # git_init by default so packs that expect a repo behave normally.
        if not (self.root / ".git").exists():
            try:
                subprocess.run(
                    ["git", "init", "-q"], cwd=str(self.root), check=False
                )
            except FileNotFoundError:
                pass  # git absent: many evals don't need it

    # ---- staging --------------------------------------------------------

    def stage_pack(self, pack: str, *, include_skills: bool = True) -> None:
        """Stage an agent pack into ``.github/agents`` (and skills + instructions).

        Pack-local short-term-memory directories (e.g. ``.story-telling-stm``)
        are **not** auto-staged: many packs ship a seed STM full of demo
        sessions that would pollute test assertions. Tests that need a
        specific STM layout should stage it explicitly via
        :meth:`stage_files`.
        """
        src_pack = REPO_ROOT / "agent-packs" / pack
        if not src_pack.exists():
            raise FileNotFoundError(f"Pack not found: {src_pack}")

        agents_src = src_pack / ".github" / "agents"
        if agents_src.exists():
            _copy_tree(agents_src, self.root / ".github" / "agents")

        # Some packs declare instructions/skills under their own .github/.
        for sub in ("instructions", "skills"):
            local = src_pack / ".github" / sub
            if local.exists():
                _copy_tree(local, self.root / ".github" / sub)

        if include_skills:
            shared_skills = REPO_ROOT / ".github" / "skills"
            if shared_skills.exists():
                _copy_tree(
                    shared_skills, self.root / ".github" / "skills", merge=True
                )
            shared_instructions = REPO_ROOT / ".github" / "instructions"
            if shared_instructions.exists():
                _copy_tree(
                    shared_instructions,
                    self.root / ".github" / "instructions",
                    merge=True,
                )

    def stage_skill(self, skill: str) -> None:
        """Stage exactly one skill (no agents).

        Resolution order (first match wins):

        1. Repo-root ``.github/skills/<skill>/`` -- the legacy shared-skills
           layout.
        2. Plugin-root ``agent-packs/<pack>/skills/<skill>/`` -- the
           conformant **agent-plugin** layout (the manifest's default
           ``skills/`` path). A plugin no longer keeps its skills under
           ``.github/skills/``; they live at the plugin root so VS Code,
           Copilot CLI, and ``gh skill`` all discover them.

        Either way the skill is copied into the workspace's
        ``.github/skills/<skill>`` so the SUT (Copilot CLI) discovers it
        identically when the workspace is its ``cwd``.
        """
        candidate = REPO_ROOT / ".github" / "skills" / skill
        if not candidate.exists():
            # Agent-plugin layout: agent-packs/<pack>/skills/<skill>/SKILL.md
            plugin_matches = [
                p
                for p in sorted(REPO_ROOT.glob(f"agent-packs/*/skills/{skill}"))
                if (p / "SKILL.md").exists()
            ]
            if len(plugin_matches) == 1:
                candidate = plugin_matches[0]
            elif len(plugin_matches) > 1:
                raise FileNotFoundError(
                    f"Skill {skill!r} is ambiguous across plugins: "
                    f"{[str(p) for p in plugin_matches]}. Disambiguate by "
                    "renaming one of the skill directories."
                )
        if not candidate.exists():
            raise FileNotFoundError(
                f"Skill not found at {REPO_ROOT / '.github' / 'skills' / skill} "
                f"or under agent-packs/*/skills/{skill}. Skill evals require "
                "the skill to live in the repo's .github/skills/ tree or in a "
                "plugin-root skills/ directory."
            )
        _copy_tree(candidate, self.root / ".github" / "skills" / skill)

    def stage_files(self, src: Path, dest_subdir: str = ".") -> None:
        """Copy ``src`` (file or dir) into ``workspace/<dest_subdir>``."""
        target = (self.root / dest_subdir).resolve()
        target.mkdir(parents=True, exist_ok=True)
        if src.is_dir():
            _copy_tree(src, target, merge=True)
        else:
            shutil.copy2(src, target / src.name)

    # ---- driving the SUT ------------------------------------------------

    def run_agent(
        self,
        prompt: str,
        *,
        agent: str | None = None,
        timeout: float = 600.0,
        log_name: str = "agent",
    ) -> copilot.CopilotResult:
        return copilot.run_agent(
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
    ) -> copilot.CopilotResult:
        return copilot.run_skill(
            skill=skill,
            prompt=prompt,
            workspace=self.root,
            log_path=self.logs_dir / f"{log_name}.log",
            timeout=timeout,
        )

    # ---- inspection -----------------------------------------------------

    def glob(self, pattern: str) -> list[Path]:
        """Return all paths in the workspace matching ``pattern`` (recursive)."""
        return sorted(self.root.glob(pattern))

    def find_one(self, pattern: str) -> Path:
        """Return the single match for ``pattern``; raise if 0 or >1 found.

        Raises :class:`FixtureMissingError` (an ``AssertionError`` subclass)
        when zero matches are found, with a list of the closest existing
        paths in the workspace to help the test author spot a missing
        fixture file or a path typo. Multiple matches still raise a plain
        ``AssertionError`` (the ambiguity is what matters there, not the
        names).
        """
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
    """Raised by :meth:`Workspace.find_one` when zero matches are found.

    Subclasses :class:`AssertionError` so pytest still treats it as a test
    failure (preserving the existing ``assert ws.find_one(...)`` callers'
    behaviour) but adds structured fields and a friendlier message that
    points at likely-missing fixture files.
    """

    def __init__(
        self,
        *,
        pattern: str,
        workspace_root: Path,
        suggestions: list[str],
    ) -> None:
        self.pattern = pattern
        self.workspace_root = workspace_root
        self.suggestions = suggestions
        suggestion_block = (
            "\n  closest paths in workspace:\n    - "
            + "\n    - ".join(suggestions)
            if suggestions
            else "\n  (workspace appears empty)"
        )
        super().__init__(
            f"Expected exactly 1 match for {pattern!r} in workspace at "
            f"{workspace_root}, got 0.\n"
            f"  This usually means the fixture file is missing under "
            f"`fixtures/<scenario>/`, or the agent failed to create the "
            f"artefact (check the agent log)."
            f"{suggestion_block}"
        )


def _suggest_close_paths(root: Path, pattern: str, *, n: int = 5) -> list[str]:
    """Return up to ``n`` workspace paths closest to ``pattern`` by name.

    The pattern is stripped of glob meta-chars before fuzzy-matching against
    every file in the workspace; this is best-effort, intended only to help
    a human reader spot a typo or a missing fixture quickly.
    """
    bare = pattern.replace("*", "").replace("?", "").strip("/\\")
    if not bare:
        # Pattern is pure-glob with no literal anchor; just sample a few files.
        bare = pattern
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
    """Copy ``src`` directory into ``dest``. If ``merge``, files in ``dest``
    that don't exist in ``src`` are preserved.
    """
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

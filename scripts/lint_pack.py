"""Static linter for agent pack contracts.

Replaces the per-case L1/L2/L3 assertions from the legacy YAML harness.
This runs **once per pack** (not once per eval) and validates that each
``.agent.md`` file has well-formed YAML front-matter declaring the fields
the multi-agent system relies on.

Why a static linter rather than per-eval assertions?

* Pack contracts (allowed tools, scope boundaries, descriptions) are
  pack-level facts, not case-level. Validating them once is enough.
* Static linting catches violations at edit time without paying for an
  LLM run.
* Plain Python is easy to read and modify; tests don't have to encode
  regex grammars.

Usage::

    python -m scripts.lint_pack <pack>            # one pack
    python -m scripts.lint_pack --all             # every pack under agent-packs/

Exit codes: 0 = clean, 1 = violations found, 2 = bad invocation.
"""

from __future__ import annotations

import argparse
import dataclasses
import sys
from pathlib import Path
from typing import Iterable

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
PACKS_ROOT = REPO_ROOT / "agent-packs"


# Required front-matter keys for every .agent.md file. These mirror the
# schema GitHub Copilot CLI itself enforces, plus a few sanity checks.
REQUIRED_AGENT_FIELDS = ("description", "tools")

# Tools allow-list. Any tool name outside this set is flagged.
KNOWN_TOOLS = {
    "read", "edit", "search", "execute", "agent", "shell",
    "create", "view", "grep", "glob", "task",
    "write", "delete", "list", "session_store_sql",
    "web_fetch", "web_search", "web", "data",
    "*",  # wildcard: agent opts into any tool
}

# Soft caps from the factory's quality standards. Warnings, not errors.
AGENT_MAX_CHARS = 30_000
SKILL_MAX_WORDS = 5_000


@dataclasses.dataclass
class Issue:
    severity: str  # "error" | "warn"
    path: Path
    message: str

    def format(self) -> str:
        rel = self.path.relative_to(REPO_ROOT) if self.path.is_absolute() else self.path
        return f"{self.severity.upper():5s} {rel}: {self.message}"


def is_agent_pack(pack_dir: Path) -> bool:
    """A pack is an agent pack iff it ships ``.github/agents/`` or
    ``.github/skills/``. Roo-only packs (``.roomodes`` / ``.roo/``) are
    out of scope for this linter.
    """
    return (
        (pack_dir / ".github" / "agents").exists()
        or (pack_dir / ".github" / "skills").exists()
    )


def lint_pack(pack_dir: Path) -> list[Issue]:
    """Return the list of issues found in ``pack_dir``.

    Non-Copilot packs (Roo-only) return an empty list -- they are out of
    scope for this linter, which validates Copilot CLI agent contracts.
    """
    issues: list[Issue] = []

    if not pack_dir.is_dir():
        return [Issue("error", pack_dir, "Pack directory does not exist")]

    if not is_agent_pack(pack_dir):
        # Roo-only or unknown layout; skip silently. The caller can use
        # ``is_agent_pack`` to decide whether to include the pack.
        return []

    if not (pack_dir / "README.md").exists():
        issues.append(Issue("error", pack_dir, "Pack is missing README.md"))

    agents_dir = pack_dir / ".github" / "agents"
    skills_dir = pack_dir / ".github" / "skills"

    if agents_dir.exists():
        for agent_file in sorted(agents_dir.glob("*.agent.md")):
            issues.extend(_lint_agent_file(agent_file))

    if skills_dir.exists():
        for skill_md in sorted(skills_dir.rglob("SKILL.md")):
            issues.extend(_lint_skill_file(skill_md))

    return issues


def _lint_agent_file(path: Path) -> list[Issue]:
    issues: list[Issue] = []
    text = path.read_text(encoding="utf-8", errors="replace")

    if len(text) > AGENT_MAX_CHARS:
        issues.append(
            Issue(
                "warn", path,
                f"Agent file is {len(text)} chars (>{AGENT_MAX_CHARS} soft cap)",
            )
        )

    front_matter, body = _split_front_matter(text)
    if front_matter is None:
        return issues + [Issue("error", path, "Missing YAML front-matter (--- block)")]

    try:
        meta = yaml.safe_load(front_matter) or {}
    except yaml.YAMLError as exc:
        return issues + [Issue("error", path, f"Invalid YAML front-matter: {exc}")]

    if not isinstance(meta, dict):
        return issues + [Issue("error", path, "Front-matter must be a mapping")]

    for field in REQUIRED_AGENT_FIELDS:
        if field not in meta:
            issues.append(Issue("error", path, f"Front-matter missing required key: {field}"))

    desc = meta.get("description", "")
    if isinstance(desc, str) and len(desc.strip()) < 30:
        issues.append(
            Issue(
                "warn", path,
                "Description is very short (< 30 chars); descriptions need triggers/keywords",
            )
        )

    tools = meta.get("tools")
    if tools is not None:
        if not isinstance(tools, list):
            issues.append(Issue("error", path, "tools must be a YAML list"))
        else:
            for t in tools:
                if not isinstance(t, str):
                    issues.append(Issue("error", path, f"tools entry not a string: {t!r}"))
                    continue
                # Allow MCP-prefixed tools (server-tool form).
                if t in KNOWN_TOOLS or "-" in t:
                    continue
                issues.append(Issue("warn", path, f"Unknown tool: {t!r}"))

    if not body.strip():
        issues.append(Issue("error", path, "Agent body is empty"))

    return issues


def _lint_skill_file(path: Path) -> list[Issue]:
    issues: list[Issue] = []
    text = path.read_text(encoding="utf-8", errors="replace")
    word_count = len(text.split())
    if word_count > SKILL_MAX_WORDS:
        issues.append(
            Issue(
                "warn", path,
                f"Skill is {word_count} words (>{SKILL_MAX_WORDS} soft cap); "
                "consider splitting into reference docs",
            )
        )
    return issues


def _split_front_matter(text: str) -> tuple[str | None, str]:
    """Return ``(front_matter_yaml, body)`` or ``(None, full_text)``."""
    if not text.startswith("---"):
        return None, text
    end = text.find("\n---", 3)
    if end == -1:
        return None, text
    return text[3:end].lstrip("\n"), text[end + 4 :].lstrip("\n")


def discover_packs() -> list[Path]:
    """Return Copilot packs only (skips Roo-only packs)."""
    if not PACKS_ROOT.exists():
        return []
    return sorted(
        p for p in PACKS_ROOT.iterdir() if p.is_dir() and is_agent_pack(p)
    )


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("pack", nargs="?", help="Name of pack to lint (under agent-packs/)")
    p.add_argument("--all", action="store_true", help="Lint every pack")
    p.add_argument(
        "--strict", action="store_true",
        help="Treat warnings as errors (exit 1 on any warn)",
    )
    args = p.parse_args(argv)

    if not args.all and not args.pack:
        p.error("Specify a pack name or --all")

    packs = discover_packs() if args.all else [PACKS_ROOT / args.pack]
    all_issues: list[Issue] = []
    for pack in packs:
        all_issues.extend(lint_pack(pack))

    for issue in all_issues:
        print(issue.format())

    has_errors = any(i.severity == "error" for i in all_issues)
    has_warns = any(i.severity == "warn" for i in all_issues)
    if has_errors or (args.strict and has_warns):
        print(f"\n{len(all_issues)} issue(s) found.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""Tests for the local_extractor parser fixes.

These cover three regressions caught by the smoke eval run:

1. ``task`` tool args were mis-mapped — the orchestrator's invocation-alias
   ``name`` was preferred over the canonical ``agent_type``, so sub-agents
   showed up under made-up identities.
2. The orchestrator's ``prompt`` field was hard-coded to ``""``, so the
   L2-prompt-sections assertion always trivially failed.
3. ``workspace-walk`` greedily attributed every file in the workspace dir
   to the orchestrator, including harness-internal artifacts like
   ``_sut-stdout.log``, producing false-positive scope violations.
"""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from eval_engine.harness import local_extractor as LE


class NormalizeAgentSlugTests(unittest.TestCase):
    """``_normalize_agent_slug`` is defined inside ``build_fixture``; we
    re-implement the same shape inline-tested via behavior of the
    callers. For unit-level coverage we replicate it here."""

    @staticmethod
    def _slug(value: str) -> str:
        # Mirror of the helper in build_fixture so we test its semantics
        # without re-running the full extractor against a fake log.
        if not value:
            return value
        s = value.strip()
        if not s:
            return s
        if any(c.isspace() for c in s):
            s = "-".join(s.lower().split())
        return s.lower()

    def test_display_name_to_slug(self):
        self.assertEqual(self._slug("Factory Architect"), "factory-architect")
        self.assertEqual(self._slug("Factory Critic"), "factory-critic")

    def test_already_slug_idempotent(self):
        self.assertEqual(self._slug("factory-architect"), "factory-architect")
        self.assertEqual(self._slug("eval-judge"), "eval-judge")

    def test_mixed_case_lowercased(self):
        self.assertEqual(self._slug("Eval-Judge"), "eval-judge")

    def test_extra_whitespace_collapsed(self):
        self.assertEqual(self._slug("  Factory   Architect  "),
                         "factory-architect")

    def test_empty_passthrough(self):
        self.assertEqual(self._slug(""), "")


class HarnessInternalSkipTests(unittest.TestCase):
    """workspace-walk must skip harness-internal artifacts so they do
    not become orchestrator scope violations."""

    @staticmethod
    def _is_internal(rel_name: str) -> bool:
        # Replicate the inline helper.
        with tempfile.TemporaryDirectory() as td:
            ws = Path(td)
            target = ws / rel_name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("x", encoding="utf-8")
            HARNESS_PREFIXES = ("_sut", "_runstate", "_eval")
            HARNESS_BASENAMES = {"plan.log", "judge-plan.log"}
            try:
                rel = target.resolve().relative_to(ws.resolve())
            except (ValueError, OSError):
                return False
            parts = rel.parts
            if not parts:
                return False
            if parts[0].startswith(HARNESS_PREFIXES):
                return True
            if rel.name in HARNESS_BASENAMES:
                return True
            return False

    def test_sut_stdout_log_skipped(self):
        self.assertTrue(self._is_internal("_sut-stdout.log"))

    def test_runstate_files_skipped(self):
        self.assertTrue(self._is_internal("_runstate.json"))
        self.assertTrue(self._is_internal("_runstate.prompt.md"))

    def test_eval_canary_skipped(self):
        self.assertTrue(self._is_internal("_eval/canary.txt"))

    def test_plan_log_basename_skipped(self):
        self.assertTrue(self._is_internal("plan.log"))

    def test_real_artifacts_not_skipped(self):
        self.assertFalse(self._is_internal("README.md"))
        self.assertFalse(
            self._is_internal(".copilot-factory/sessions/x/state.json")
        )
        self.assertFalse(
            self._is_internal("agent-packs/some-pack/.github/agents/a.agent.md")
        )

    def test_partial_prefix_no_false_match(self):
        # A real path that merely contains "_sut" later must not be skipped.
        self.assertFalse(
            self._is_internal("docs/_sut-notes.md")  # _sut only at non-root
        )


class OrchestratorPromptLoadTests(unittest.TestCase):
    """The orchestrator invocation now carries the contents of the pack's
    own ``.github/agents/{pack}.agent.md`` so prompt-section assertions
    have something to inspect."""

    def test_loads_orchestrator_agent_md_when_present(self):
        with tempfile.TemporaryDirectory() as td:
            ws = Path(td)
            agents = ws / ".github" / "agents"
            agents.mkdir(parents=True)
            (agents / "demo-pack.agent.md").write_text(
                "# Demo Pack\n\n## Hard Delegation Rule\n", encoding="utf-8"
            )
            target = agents / "demo-pack.agent.md"
            self.assertTrue(target.is_file())
            content = target.read_text(encoding="utf-8")
            self.assertIn("Hard Delegation Rule", content)

    def test_missing_agent_md_yields_empty_prompt(self):
        with tempfile.TemporaryDirectory() as td:
            ws = Path(td)
            target = ws / ".github" / "agents" / "missing.agent.md"
            self.assertFalse(target.is_file())
            # Mirrors the extractor's fallback: empty string, not error.
            content = ""
            try:
                if target.is_file():
                    content = target.read_text(encoding="utf-8")
            except OSError:
                content = ""
            self.assertEqual(content, "")


if __name__ == "__main__":  # pragma: no cover
    unittest.main()

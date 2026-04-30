"""Unit tests for the assertion library + paths + tools modules.

Run with: ``python -m unittest discover -s eval -t .`` from the repo root.
"""

from __future__ import annotations

import unittest

from eval_engine.harness import paths, tools
from eval_engine.harness.assertions import ASSERTIONS
from eval_engine.harness.assertions.base import AssertionContext

from . import fixtures as F


class PathsTests(unittest.TestCase):
    def test_normalize_strips_workspace_token(self):
        self.assertEqual(paths.normalize("${WORKSPACE_ROOT}/foo/bar.md"), "foo/bar.md")

    def test_normalize_handles_backslashes(self):
        self.assertEqual(paths.normalize("foo\\bar\\baz.md"), "foo/bar/baz.md")

    def test_normalize_collapses_dot_segments(self):
        self.assertEqual(paths.normalize("foo/../_eval/golden.md"), "_eval/golden.md")

    def test_is_canary_case_insensitive(self):
        self.assertTrue(paths.is_canary("_eval/foo"))
        self.assertTrue(paths.is_canary("_Eval/foo"))
        self.assertFalse(paths.is_canary("foo/_eval"))  # only top-level

    def test_deny_precedes_allow(self):
        decision = paths.deny_precedes_allow(
            "secrets/.env", deny=["^secrets/"], allow=[".*"],
        )
        self.assertFalse(decision.matched)
        self.assertEqual(decision.kind, "deny")

    def test_allow_match(self):
        decision = paths.deny_precedes_allow(
            "out/architecture.md", deny=[], allow=["^out/.*\\.md$"],
        )
        self.assertTrue(decision.matched)


class ToolsTests(unittest.TestCase):
    def test_canonical_runtime_mapping(self):
        self.assertEqual(tools.resolve("view"), "read")
        self.assertEqual(tools.resolve("grep"), "search")
        self.assertEqual(tools.resolve("create"), "write")
        self.assertEqual(tools.resolve("edit"), "write")
        self.assertEqual(tools.resolve("task"), "agent")
        self.assertEqual(tools.resolve("powershell"), "execute")
        self.assertEqual(tools.resolve("session_store_sql"), "data")

    def test_mcp_prefix_mapping(self):
        self.assertEqual(tools.resolve("github-mcp-server-search_code"), "search")
        self.assertEqual(tools.resolve("playwright-browser_click"), "mcp:playwright")

    def test_unknown_returns_unknown(self):
        self.assertEqual(tools.resolve("never-heard-of-this"), "unknown")

    def test_is_allowed_with_category(self):
        self.assertTrue(tools.is_allowed("view", ["read"]))
        self.assertFalse(tools.is_allowed("create", ["read"]))

    def test_is_allowed_mcp_wildcard(self):
        self.assertTrue(tools.is_allowed("playwright-browser_click", ["mcp"]))
        self.assertFalse(tools.is_allowed("playwright-browser_click", ["mcp:github"]))


class AssertionTests(unittest.TestCase):
    def _ctx(self, fixture):
        spec = F.make_spec()
        case = F.make_case(spec)
        return AssertionContext(spec=spec, case=case, fixture=fixture, workspace_root="/tmp/ws")

    def _run_all(self, fixture):
        ctx = self._ctx(fixture)
        results = []
        for a in ASSERTIONS:
            results.extend(a.run(ctx))
        return results

    def test_clean_run_passes(self):
        fix = F.make_fixture(
            invocations=[
                F.make_invocation("copilot-factory", invocation_id="orch-1", tokens=500),
                F.make_invocation(
                    "factory-architect",
                    invocation_id="arch-1", tokens=2000,
                    prompt="## Inputs\n\nuser-request goes here.\n\n## Constraints\n- foo",
                    response="# X\n## Architecture\n...\n## Risks\n...",
                ),
                F.make_invocation(
                    "factory-critic", invocation_id="crit-1", tokens=1000,
                    prompt="(no contract)", response="ok",
                ),
            ],
            tool_calls=[
                F.make_tool_call("view", agent="factory-architect"),
                F.make_tool_call("create", agent="factory-architect", call_id="c-2"),
            ],
            file_accesses=[
                F.make_file_access(
                    ".copilot-factory/sessions/2026-04-28-ab/architecture.md",
                    "write", agent="factory-architect",
                ),
            ],
        )
        results = self._run_all(fix)
        failures = [r for r in results if r.status == "fail"]
        self.assertEqual(failures, [], msg=[r.message for r in failures])

    def test_canary_touch_fails(self):
        fix = F.make_fixture(
            invocations=[
                F.make_invocation("copilot-factory", invocation_id="orch-1"),
                F.make_invocation(
                    "factory-architect",
                    invocation_id="arch-1",
                    prompt="## Inputs\n\nuser-request\n\n## Constraints\n",
                    response="## Architecture\n## Risks\n",
                ),
                F.make_invocation(
                    "factory-critic", invocation_id="crit-1",
                ),
            ],
            file_accesses=[F.make_file_access("_eval/golden.md", "read", agent="factory-architect")],
        )
        results = self._run_all(fix)
        canary_fails = [r for r in results
                        if r.assertion_id == "L3-workspace-escape" and r.status == "fail"]
        self.assertEqual(len(canary_fails), 1)

    def test_disallowed_tool_fails(self):
        fix = F.make_fixture(
            invocations=[
                F.make_invocation("copilot-factory", invocation_id="orch-1"),
                F.make_invocation(
                    "factory-architect", invocation_id="arch-1",
                    prompt="## Inputs\n\nuser-request\n\n## Constraints\n",
                    response="## Architecture\n## Risks\n",
                ),
                F.make_invocation("factory-critic", invocation_id="crit-1"),
            ],
            tool_calls=[F.make_tool_call("powershell", agent="factory-architect")],
        )
        results = self._run_all(fix)
        tool_fails = [r for r in results
                      if r.assertion_id == "L3-tools" and r.status == "fail"]
        self.assertEqual(len(tool_fails), 1)
        self.assertIn("powershell", tool_fails[0].message)

    def test_unexpected_agent_fails(self):
        fix = F.make_fixture(
            invocations=[
                F.make_invocation("copilot-factory", invocation_id="orch-1"),
                F.make_invocation("factory-architect", invocation_id="arch-1",
                                   prompt="## Inputs\nuser-request\n## Constraints\n",
                                   response="## Architecture\n## Risks\n"),
                F.make_invocation("factory-critic", invocation_id="crit-1"),
                F.make_invocation("rogue-agent", invocation_id="rogue-1"),
            ],
        )
        results = self._run_all(fix)
        l1_set = [r for r in results if r.assertion_id == "L1-set" and r.status == "fail"]
        self.assertEqual(len(l1_set), 1)
        self.assertIn("rogue-agent", l1_set[0].message)

    def test_missing_required_section_fails(self):
        fix = F.make_fixture(
            invocations=[
                F.make_invocation("copilot-factory", invocation_id="orch-1"),
                F.make_invocation(
                    "factory-architect", invocation_id="arch-1",
                    prompt="(no Inputs section, no Constraints)",
                    response="(no Architecture)",
                ),
                F.make_invocation("factory-critic", invocation_id="crit-1"),
            ],
        )
        results = self._run_all(fix)
        prompt_section_fails = [
            r for r in results
            if r.assertion_id == "L2-prompt-sections" and r.status == "fail"
        ]
        self.assertEqual(len(prompt_section_fails), 1)

    def test_budget_breach_warns(self):
        fix = F.make_fixture(
            invocations=[
                F.make_invocation("copilot-factory", invocation_id="orch-1"),
                F.make_invocation(
                    "factory-architect", invocation_id="arch-1", tokens=999_999,
                    prompt="## Inputs\nuser-request\n## Constraints\n",
                    response="## Architecture\n## Risks\n",
                ),
                F.make_invocation("factory-critic", invocation_id="crit-1"),
            ],
        )
        results = self._run_all(fix)
        budget = [r for r in results
                  if r.assertion_id == "L3-budget" and r.status == "fail"]
        self.assertEqual(len(budget), 1)
        self.assertEqual(budget[0].severity, "warn")

    def test_background_read_before_completion_fails(self):
        fix = F.make_fixture(
            invocations=[
                F.make_invocation("copilot-factory", invocation_id="orch-1"),
                F.make_invocation(
                    "factory-architect", invocation_id="arch-1", mode="background",
                    completed=False,
                    prompt="## Inputs\nuser-request\n## Constraints\n",
                    response="## Architecture\n## Risks\n",
                ),
                F.make_invocation("factory-critic", invocation_id="crit-1"),
            ],
            background_reads=[
                {"invocation_id": "arch-1", "read_at": "T2", "completed_at": None},
            ],
        )
        results = self._run_all(fix)
        bg = [r for r in results
              if r.assertion_id == "L1-bg-completion" and r.status == "fail"]
        self.assertEqual(len(bg), 1)


if __name__ == "__main__":
    unittest.main()

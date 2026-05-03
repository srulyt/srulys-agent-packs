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
    def setUp(self):
        # L2-prompt-sections now reads sub-agent system prompts from
        # ``<workspace>/.github/agents/<name>.agent.md``. Stage a tmp
        # workspace per test with the architect prompt that satisfies
        # the spec's required_sections (Inputs + Constraints).
        import tempfile
        from pathlib import Path
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        agents_dir = Path(self._tmp.name) / ".github" / "agents"
        agents_dir.mkdir(parents=True)
        (agents_dir / "factory-architect.agent.md").write_text(
            "## Inputs\n\nuser-request\n\n## Constraints\n\n- foo\n",
            encoding="utf-8",
        )

    def _ctx(self, fixture, *, with_architect_prompt: bool = True):
        spec = F.make_spec()
        case = F.make_case(spec)
        ws = self._tmp.name
        if not with_architect_prompt:
            # Wipe the staged architect prompt for negative tests.
            from pathlib import Path
            p = Path(ws) / ".github" / "agents" / "factory-architect.agent.md"
            if p.exists():
                p.unlink()
        return AssertionContext(spec=spec, case=case, fixture=fixture, workspace_root=ws)

    def _run_all(self, fixture, *, with_architect_prompt: bool = True):
        ctx = self._ctx(fixture, with_architect_prompt=with_architect_prompt)
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
        # Run with the staged architect prompt removed — assertion now reads
        # the agent's system prompt from disk; an empty/missing file means
        # all required sections are missing.
        results = self._run_all(fix, with_architect_prompt=False)
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


class ArtifactContentAndStateAssertionTests(unittest.TestCase):
    """Exercise L3-artifact-content + L3-state-assertions end-to-end.

    Each test stages a temp workspace, drops a synthetic ``state.json`` and
    a synthetic ``specification.md`` matching the case's expected-artifact
    path patterns, builds a CaseSpec via the public loader, runs the two
    new assertions through the registry, and pins their verdicts.
    """

    def setUp(self):
        import tempfile
        from pathlib import Path
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.ws = Path(self._tmp.name)
        # Stage a session-shaped subtree so the path_pattern regexes match.
        sess = self.ws / ".session" / "sessions" / "2026-05-01-deadbeef"
        (sess / "artifacts").mkdir(parents=True)
        self._state_path = sess / "state.json"
        self._spec_path = sess / "artifacts" / "specification.md"

    def _write_good(self):
        import json
        self._state_path.write_text(
            json.dumps({
                "phase": "complete",
                "stop_a_disambiguation_attempts": 2,
                "interview_retries": 1,
                "interview_complete": True,
                "structure_approved": True,
                "counters": {"warnings": 3},
            }, indent=2),
            encoding="utf-8",
        )
        self._spec_path.write_text(
            "# Specification\n\n## Open Questions\n\n"
            "[TBD - interview question Q3 unanswered]\n",
            encoding="utf-8",
        )

    def _write_tampered_state(self):
        import json
        self._state_path.write_text(
            json.dumps({
                "phase": "in-progress",            # wrong
                "stop_a_disambiguation_attempts": 0,  # wrong
                "interview_retries": 1,
                "interview_complete": False,        # wrong
                # structure_approved missing -> equals miss
                "counters": {"warnings": 3},
            }, indent=2),
            encoding="utf-8",
        )
        # Spec content unchanged so we isolate state-assertion failures.
        self._spec_path.write_text(
            "# Specification\n\n## Open Questions\n\n"
            "[TBD - interview question Q3 unanswered]\n",
            encoding="utf-8",
        )

    def _write_tampered_content(self):
        import json
        # State stays valid so we isolate content failures.
        self._state_path.write_text(
            json.dumps({
                "phase": "complete",
                "stop_a_disambiguation_attempts": 2,
                "interview_retries": 1,
                "interview_complete": True,
                "structure_approved": True,
                "counters": {"warnings": 3},
            }),
            encoding="utf-8",
        )
        # Drop the [TBD] placeholder AND the Open Questions section.
        self._spec_path.write_text(
            "# Specification\n\n(no placeholders, no open questions)\n",
            encoding="utf-8",
        )

    def _make_case_yaml(self) -> str:
        # Use the same shape as a real case file so the public loader
        # exercises the wiring we just added in load_case().
        return """
id: synthetic-content-state-case
pack: synth
description: "synthetic"
prompt_file: prompt.md
workspace:
  isolation: empty
  steps: []
expected:
  artifacts:
    - id: state
      path_pattern: "^\\\\.session/sessions/[^/]+/state\\\\.json$"
    - id: specification
      path_pattern: "^\\\\.session/sessions/[^/]+/artifacts/specification\\\\.md$"
  artifact_content_assertions:
    - artifact: specification
      must_match:
        - "\\\\[TBD\\\\s*[-—]\\\\s*interview question\\\\s+\\\\S+\\\\s+unanswered\\\\]"
        - "(?i)open questions"
      must_not_match:
        - "(?i)\\b(some-internal-brand|legacy-codename)\\b"
  state_assertions:
    - artifact: state
      equals:
        stop_a_disambiguation_attempts: 2
        interview_retries: 1
        interview_complete: true
        structure_approved: true
      matches:
        phase: "^complete(-with-warnings)?$"
      exists:
        - counters.warnings
      gt:
        stop_a_disambiguation_attempts: 1
"""

    def _build_ctx(self):
        import os
        import tempfile
        from pathlib import Path
        from eval_engine.harness import loaders
        fd, path_str = tempfile.mkstemp(suffix=".yaml")
        os.close(fd)
        case_yaml = Path(path_str)
        case_yaml.write_text(self._make_case_yaml(), encoding="utf-8")
        self.addCleanup(lambda: case_yaml.unlink(missing_ok=True))
        case = loaders.load_case(str(case_yaml))
        spec = F.make_spec()  # spec doesn't matter for these two assertions
        fixture = F.make_fixture(invocations=[
            F.make_invocation("copilot-factory", invocation_id="orch-1"),
        ])
        return AssertionContext(spec=spec, case=case, fixture=fixture,
                                workspace_root=str(self.ws))

    def _run_new_assertions(self, ctx):
        from eval_engine.harness.assertions import l3
        results = []
        for a in l3.ASSERTIONS:
            if a.id in ("L3-artifact-content", "L3-state-assertions"):
                results.extend(a.run(ctx))
        return results

    def test_clean_workspace_passes(self):
        self._write_good()
        ctx = self._build_ctx()
        results = self._run_new_assertions(ctx)
        ids = {r.assertion_id for r in results}
        self.assertEqual(ids, {"L3-artifact-content", "L3-state-assertions"})
        for r in results:
            self.assertEqual(r.status, "pass",
                             msg=f"{r.assertion_id}: {r.message}; ev={r.evidence}")

    def test_tampered_state_fails_only_state_assertion(self):
        self._write_tampered_state()
        ctx = self._build_ctx()
        results = self._run_new_assertions(ctx)
        by_id = {r.assertion_id: r for r in results}
        self.assertEqual(by_id["L3-artifact-content"].status, "pass")
        self.assertEqual(by_id["L3-state-assertions"].status, "fail")
        evidence_kinds = {ev["kind"] for ev in by_id["L3-state-assertions"].evidence}
        self.assertIn("equals_miss", evidence_kinds)
        self.assertIn("matches_miss", evidence_kinds)

    def test_tampered_content_fails_only_content_assertion(self):
        self._write_tampered_content()
        ctx = self._build_ctx()
        results = self._run_new_assertions(ctx)
        by_id = {r.assertion_id: r for r in results}
        self.assertEqual(by_id["L3-state-assertions"].status, "pass")
        self.assertEqual(by_id["L3-artifact-content"].status, "fail")
        kinds = {ev["kind"] for ev in by_id["L3-artifact-content"].evidence}
        self.assertIn("must_match_miss", kinds)

    def test_loader_rejects_unknown_artifact_id(self):
        import os
        import tempfile
        from pathlib import Path
        from eval_engine.harness import loaders
        bad = """
id: synth
pack: synth
prompt_file: prompt.md
workspace:
  isolation: empty
  steps: []
expected:
  artifacts:
    - id: state
      path_pattern: "^state\\\\.json$"
  state_assertions:
    - artifact: nonexistent
      equals: { phase: "complete" }
"""
        fd, path_str = tempfile.mkstemp(suffix=".yaml")
        os.close(fd)
        p = Path(path_str)
        p.write_text(bad, encoding="utf-8")
        self.addCleanup(lambda: p.unlink(missing_ok=True))
        with self.assertRaises(loaders.ConfigError):
            loaders.load_case(str(p))

    def test_loader_rejects_unknown_subkey(self):
        import os
        import tempfile
        from pathlib import Path
        from eval_engine.harness import loaders
        bad = """
id: synth
pack: synth
prompt_file: prompt.md
workspace:
  isolation: empty
  steps: []
expected:
  artifacts:
    - id: state
      path_pattern: "^state\\\\.json$"
  state_assertions:
    - artifact: state
      bogus_key: 1
"""
        fd, path_str = tempfile.mkstemp(suffix=".yaml")
        os.close(fd)
        p = Path(path_str)
        p.write_text(bad, encoding="utf-8")
        self.addCleanup(lambda: p.unlink(missing_ok=True))
        with self.assertRaises(loaders.ConfigError):
            loaders.load_case(str(p))


if __name__ == "__main__":
    unittest.main()

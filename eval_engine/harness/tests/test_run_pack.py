"""Tests for run-pack pack-summary aggregation + exit codes.

Most of the run-pack flow involves spawning a real ``copilot`` binary
which is not available in CI. We test the static parts:

  * Spec / case discovery + missing-cases handling.
  * Exit-code semantics for harness errors.
  * Failure-extraction shape from a synthetic CaseVerdict.
  * Strict-pass case-status promotion.
  * apply_double_invoke under strict_pass extension.
"""

from __future__ import annotations

import json
import os
import textwrap
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from eval_engine.harness import models, pack_runner
from eval_engine.harness.judge.orchestration import (
    JudgeManifest, JudgeRequest, JudgeResponse, apply_double_invoke,
)


_MIN_SPEC = """\
pack: demo
orchestrator: demo
agents:
  - name: demo
    invocations: { min: 1, max: 1, must_complete: true }
"""


def _stage_evals_root(tmp: Path, *, with_cases: bool, spec_extra: str = "") -> Path:
    """Build a minimal evals/ tree: spec, optional cases."""
    root = tmp / "evals"
    pack_dir = root / "packs" / "demo"
    cases = pack_dir / "cases"
    pack_dir.mkdir(parents=True)
    (pack_dir / "spec.yaml").write_text(_MIN_SPEC + spec_extra, encoding="utf-8")
    if with_cases:
        c1 = cases / "case-a"
        c1.mkdir(parents=True)
        (c1 / "case.yaml").write_text(textwrap.dedent("""\
            id: case-a
            pack: demo
            description: minimal
            prompt_file: prompt.md
        """), encoding="utf-8")
        (c1 / "prompt.md").write_text("hello", encoding="utf-8")
    else:
        cases.mkdir(parents=True)
    return root


class RunPackHarnessErrorTests(unittest.TestCase):
    def test_spec_not_found(self):
        with TemporaryDirectory() as t:
            tmp = Path(t)
            (tmp / "evals" / "packs").mkdir(parents=True)
            opts = pack_runner.PackRunOptions(
                pack="demo",
                evals_root=str(tmp / "evals"),
                out_path=str(tmp / "out.json"),
            )
            rc = pack_runner.run_pack(opts, repo_root=str(tmp))
        self.assertEqual(rc, 2)

    def test_no_cases(self):
        with TemporaryDirectory() as t:
            tmp = Path(t)
            evals_root = _stage_evals_root(tmp, with_cases=False)
            opts = pack_runner.PackRunOptions(
                pack="demo",
                evals_root=str(evals_root),
                out_path=str(tmp / "out.json"),
            )
            rc = pack_runner.run_pack(opts, repo_root=str(tmp))
            out = json.loads((tmp / "out.json").read_text(encoding="utf-8"))
        self.assertEqual(rc, 2)
        self.assertEqual(out["exit_code"], 2)
        self.assertIn("no cases found", out["harness_error"])
        self.assertEqual(out["summary"]["cases_total"], 0)

    def test_missing_copilot_bin_exits_2_with_summary(self):
        with TemporaryDirectory() as t:
            tmp = Path(t)
            evals_root = _stage_evals_root(tmp, with_cases=True)
            opts = pack_runner.PackRunOptions(
                pack="demo",
                evals_root=str(evals_root),
                out_path=str(tmp / "out.json"),
                copilot_bin="/nonexistent/copilot",
            )
            rc = pack_runner.run_pack(opts, repo_root=str(tmp))
            out = json.loads((tmp / "out.json").read_text(encoding="utf-8"))
        self.assertEqual(rc, 2)
        self.assertEqual(out["exit_code"], 2)
        self.assertIn("copilot-bin-not-found", out["harness_error"])
        self.assertEqual(out["summary"]["cases_errored"], 1)
        # Pack-summary structure:
        self.assertIn("resolved_budgets", out)
        self.assertIn("resolved_convergence", out)
        self.assertIn("models", out)


class CaseSubsetTests(unittest.TestCase):
    def test_unknown_subset_is_harness_error(self):
        with TemporaryDirectory() as t:
            tmp = Path(t)
            evals_root = _stage_evals_root(tmp, with_cases=True)
            opts = pack_runner.PackRunOptions(
                pack="demo",
                evals_root=str(evals_root),
                out_path=str(tmp / "out.json"),
                cases_subset=["nonexistent-case"],
            )
            rc = pack_runner.run_pack(opts, repo_root=str(tmp))
            out = json.loads((tmp / "out.json").read_text(encoding="utf-8"))
        self.assertEqual(rc, 2)
        self.assertIn("subset", out["harness_error"])


class FixablePathsTests(unittest.TestCase):
    def test_fixable_paths_resolve_via_write_scope(self):
        spec = models.PackSpec(
            pack="demo",
            orchestrator="demo",
            agents=[
                models.AgentSpec(
                    name="worker",
                    write_scope_allow=[r"^agent-packs/demo/.*\.md$"],
                ),
            ],
            flow=models.FlowConstraints(),
        )
        self.assertEqual(
            pack_runner._fixable_paths_for_agent(spec, "worker"),
            [r"^agent-packs/demo/.*\.md$"],
        )
        self.assertEqual(pack_runner._fixable_paths_for_agent(spec, None), [])
        self.assertEqual(pack_runner._fixable_paths_for_agent(spec, "missing"), [])


class MintRunIdTests(unittest.TestCase):
    def test_minted_ids_unique(self):
        ids = {pack_runner.mint_run_id(1) for _ in range(20)}
        # 6 hex chars after the seq -> collision odds ~ negligible.
        self.assertGreaterEqual(len(ids), 19)


# --------------------------------------------------------------------- strict


def _resp(rid, **kw):
    return JudgeResponse(
        request_id=rid, rubric_id=kw.get("rubric_id", "x"),
        apply_to=kw.get("apply_to", "artifact:y"),
        score=kw.get("score"), rationale=kw.get("rationale", ""),
        evidence=kw.get("evidence", []), error=kw.get("error"),
    )


class StrictPassDoubleInvokeTests(unittest.TestCase):
    """Under strict_pass, warn rubrics with double-invoke variance must
    surface as ``status='fail'``, NOT ``status='error'``."""

    def _manifest(self, *, severity: str, copies: int) -> JudgeManifest:
        m = JudgeManifest(
            run_id="rid", pack="demo", case_id="case-a", judge_model=None,
        )
        for i in range(copies):
            m.requests.append(JudgeRequest(
                request_id=f"req-{i}", rubric_id="coherence",
                apply_to="artifact:architecture",
                severity=severity, threshold=None,
                target_artifact_paths=[], golden_paths=[],
                response_file=f"/tmp/{i}.json", prompt="",
            ))
        return m

    def test_warn_strict_disagreement_is_fail_not_error(self):
        m = self._manifest(severity="warn", copies=2)
        responses = {
            "req-0": _resp("req-0", score=0.9, rationale="A"),
            "req-1": _resp("req-1", score=0.3, rationale="B"),
        }
        verdicts = apply_double_invoke(responses, m, strict_pass=True)
        self.assertEqual(len(verdicts), 1)
        self.assertEqual(verdicts[0].status, "fail")
        self.assertIn("strict-pass", verdicts[0].message)

    def test_warn_strict_missing_pair_is_fail(self):
        m = self._manifest(severity="warn", copies=1)
        responses = {
            "req-0": _resp("req-0", score=0.9, rationale="solo"),
        }
        verdicts = apply_double_invoke(responses, m, strict_pass=True)
        self.assertEqual(verdicts[0].status, "fail")

    def test_blocker_disagreement_remains_error(self):
        m = self._manifest(severity="blocker", copies=2)
        responses = {
            "req-0": _resp("req-0", score=0.9, rationale="A"),
            "req-1": _resp("req-1", score=0.3, rationale="B"),
        }
        verdicts = apply_double_invoke(responses, m, strict_pass=True)
        # Blocker still gets the harness-error treatment.
        self.assertEqual(verdicts[0].status, "error")

    def test_warn_default_no_strict_no_doubling(self):
        # Default mode (strict_pass=False), warn rubric with one response
        # does not trip the doubled-required check at all.
        m = self._manifest(severity="warn", copies=1)
        responses = {
            "req-0": _resp("req-0", score=0.5, rationale="ok"),
        }
        verdicts = apply_double_invoke(responses, m, strict_pass=False)
        # Single response -> straightforward pass (no threshold).
        self.assertEqual(verdicts[0].status, "pass")


if __name__ == "__main__":
    unittest.main()

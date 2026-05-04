"""Tests for the new spec-loader fields: loop_convergence + budgets."""

from __future__ import annotations

import textwrap
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from eval_engine.harness import loaders, models


_MIN_SPEC = """\
pack: demo
orchestrator: demo
agents:
  - name: demo
    invocations: { min: 1, max: 1, must_complete: true }
"""


def _write_spec(tmp: Path, body: str) -> Path:
    p = tmp / "spec.yaml"
    p.write_text(body, encoding="utf-8")
    return p


class LoopConvergenceLoadingTests(unittest.TestCase):
    def test_default_when_block_absent(self):
        with TemporaryDirectory() as t:
            spec_path = _write_spec(Path(t), _MIN_SPEC)
            spec = loaders.load_spec(spec_path)
        self.assertIsInstance(spec.loop_convergence, models.LoopConvergence)
        self.assertEqual(spec.loop_convergence.required_status, "pass")
        self.assertFalse(spec.loop_convergence.warn_promotes_to_blocker)
        self.assertEqual(spec.loop_convergence.allow_failing_cases, [])
        self.assertFalse(spec.loop_convergence.is_strict)

    def test_strict_pass_recognised(self):
        body = _MIN_SPEC + textwrap.dedent("""\
            loop_convergence:
              required_status: strict-pass
              warn_promotes_to_blocker: true
        """)
        with TemporaryDirectory() as t:
            spec_path = _write_spec(Path(t), body)
            spec = loaders.load_spec(spec_path)
        self.assertEqual(spec.loop_convergence.required_status, "strict-pass")
        self.assertTrue(spec.loop_convergence.is_strict)

    def test_invalid_required_status_rejected(self):
        body = _MIN_SPEC + "loop_convergence:\n  required_status: maybe-pass\n"
        with TemporaryDirectory() as t:
            spec_path = _write_spec(Path(t), body)
            with self.assertRaises(loaders.ConfigError):
                loaders.load_spec(spec_path)

    def test_unknown_keys_rejected(self):
        body = _MIN_SPEC + "loop_convergence:\n  required_status: pass\n  unknown: 1\n"
        with TemporaryDirectory() as t:
            spec_path = _write_spec(Path(t), body)
            with self.assertRaises(loaders.ConfigError):
                loaders.load_spec(spec_path)

    def test_allow_failing_cases_requires_case_id(self):
        body = _MIN_SPEC + textwrap.dedent("""\
            loop_convergence:
              required_status: pass
              allow_failing_cases:
                - reason: "no case_id"
        """)
        with TemporaryDirectory() as t:
            spec_path = _write_spec(Path(t), body)
            with self.assertRaises(loaders.ConfigError):
                loaders.load_spec(spec_path)

    def test_allow_failing_cases_loaded(self):
        body = _MIN_SPEC + textwrap.dedent("""\
            loop_convergence:
              allow_failing_cases:
                - case_id: flaky-rubric
                  reason: "tracked in #42"
                  max_runs_to_tolerate: 3
        """)
        with TemporaryDirectory() as t:
            spec_path = _write_spec(Path(t), body)
            spec = loaders.load_spec(spec_path)
        self.assertTrue(
            spec.loop_convergence.is_case_allowed_to_fail("flaky-rubric")
        )
        self.assertFalse(
            spec.loop_convergence.is_case_allowed_to_fail("other-case")
        )


class BudgetsLoadingTests(unittest.TestCase):
    def test_default_when_block_absent(self):
        with TemporaryDirectory() as t:
            spec_path = _write_spec(Path(t), _MIN_SPEC)
            spec = loaders.load_spec(spec_path)
        self.assertIsInstance(spec.budgets, models.Budgets)
        self.assertIsNone(spec.budgets.max_judge_calls_per_loop)
        self.assertEqual(spec.budgets.bail_action, "surface-partial")

    def test_loaded_values(self):
        body = _MIN_SPEC + textwrap.dedent("""\
            budgets:
              max_judge_calls_per_loop: 200
              max_wall_clock_seconds_per_loop: 1800
              max_total_wall_clock_seconds: 5400
              bail_action: surface-partial
        """)
        with TemporaryDirectory() as t:
            spec_path = _write_spec(Path(t), body)
            spec = loaders.load_spec(spec_path)
        self.assertEqual(spec.budgets.max_judge_calls_per_loop, 200)
        self.assertEqual(spec.budgets.max_wall_clock_seconds_per_loop, 1800)
        self.assertEqual(spec.budgets.max_total_wall_clock_seconds, 5400)
        self.assertEqual(spec.budgets.bail_action, "surface-partial")

    def test_unknown_keys_rejected(self):
        body = _MIN_SPEC + "budgets:\n  max_judge_calls_per_loop: 5\n  surprise: 1\n"
        with TemporaryDirectory() as t:
            spec_path = _write_spec(Path(t), body)
            with self.assertRaises(loaders.ConfigError):
                loaders.load_spec(spec_path)

    def test_factory_spec_loads_clean(self):
        # The real pack spec under evals/packs/copilot-factory/spec.yaml
        # ships both blocks; the loader must accept it as-is.
        repo_root = Path(__file__).resolve().parents[3]
        spec_path = repo_root / "evals" / "packs" / "copilot-factory" / "spec.yaml"
        if not spec_path.exists():
            self.skipTest("factory spec not present")
        spec = loaders.load_spec(spec_path)
        self.assertIsNotNone(spec.budgets.max_judge_calls_per_loop)


if __name__ == "__main__":
    unittest.main()

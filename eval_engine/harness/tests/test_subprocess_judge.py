"""Tests for the non-interactive judge subprocess runner.

We exercise it with a tiny "fake copilot" python script that emits a
predetermined JSON object on stdout. The real copilot CLI is never
invoked in these tests.
"""

from __future__ import annotations

import json
import sys
import textwrap
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from eval_engine.harness.judge.orchestration import (
    JudgeManifest,
    JudgeRequest,
)
from eval_engine.harness.judge import subprocess_runner


def _make_fake_copilot(tmp: Path, *, body: str) -> Path:
    """Write a Python "fake copilot" script that emits ``body`` on stdout
    when invoked. Returns its path. The script is invoked via the same
    Python interpreter (we do this by writing a .py file and configuring
    the runner with ``copilot_bin = sys.executable`` plus a wrapper)."""
    script = tmp / "fake_copilot.py"
    script.write_text(body, encoding="utf-8")
    # Now write a small launcher that argv-shifts so subprocess_runner's
    # exact ``copilot ARGS...`` invocation gets dispatched as
    # ``python fake_copilot.py ARGS...``. We accomplish this by writing
    # a one-line .cmd / shell wrapper, but the simplest cross-platform
    # approach is: configure the runner with ``copilot_bin=<python.exe>``
    # and prepend ``script`` to argv via a monkeypatch in the test.
    return script


class _FakeBin:
    """Stand-in for the configured copilot binary.

    The runner builds argv as ``[copilot_bin, "-p", prompt, ...]``. We
    can't easily intercept that without a real executable, but we don't
    need to — we monkeypatch ``subprocess_runner._build_argv`` to
    redirect to ``[python, script, ...]``.
    """


class JsonExtractionTests(unittest.TestCase):
    def test_pure_json_object(self):
        text = '{"score": 0.9, "rationale": "ok"}'
        self.assertEqual(
            subprocess_runner._extract_json_object(text),
            {"score": 0.9, "rationale": "ok"},
        )

    def test_fenced_code_block(self):
        text = textwrap.dedent("""\
            Here is my judgment.

            ```json
            {"score": 0.4, "rationale": "weak"}
            ```

            Thanks.
        """)
        self.assertEqual(
            subprocess_runner._extract_json_object(text),
            {"score": 0.4, "rationale": "weak"},
        )

    def test_last_balanced_object_with_required_keys(self):
        text = (
            "Some prose with { fake } not-a-json. "
            'Final answer: {"score": 0.5, "rationale": "borderline", "evidence": []}'
        )
        out = subprocess_runner._extract_json_object(text)
        self.assertEqual(out["score"], 0.5)

    def test_balanced_object_without_required_keys_rejected(self):
        text = '{"foo": 1, "bar": 2}'
        self.assertIsNone(subprocess_runner._extract_json_object(text))

    def test_empty_input(self):
        self.assertIsNone(subprocess_runner._extract_json_object(""))
        self.assertIsNone(subprocess_runner._extract_json_object("   "))

    def test_malformed_returns_none(self):
        self.assertIsNone(
            subprocess_runner._extract_json_object("{not json at all")
        )


class RunOneJudgeRequestTests(unittest.TestCase):
    """Drive ``run_one_judge_request`` against a real subprocess.

    We use the host Python interpreter as the "copilot_bin" and write a
    small Python script that mimics the agent: prints either valid JSON
    or garbage on stdout. We monkeypatch the argv builder so that the
    runner's argv becomes ``[python, script, ...flags...]``.
    """

    def setUp(self) -> None:
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.tmp_path = Path(self.tmp.name)
        # Patch _build_argv -> [python, script, ...]
        self._orig_build = subprocess_runner._build_argv
        self._orig_resolve = subprocess_runner._resolve_copilot_bin

        def _resolve(p: str) -> str:
            return p  # accept anything in tests

        def _argv(*, copilot_bin, prompt, name, judge_agent="eval-judge"):
            return [sys.executable, copilot_bin, prompt, name]

        subprocess_runner._build_argv = _argv
        subprocess_runner._resolve_copilot_bin = _resolve

    def tearDown(self) -> None:
        subprocess_runner._build_argv = self._orig_build
        subprocess_runner._resolve_copilot_bin = self._orig_resolve

    def _make_script(self, body: str) -> str:
        s = self.tmp_path / "fake.py"
        s.write_text(body, encoding="utf-8")
        return str(s)

    def _make_request(self, *, prompt: str = "rubric prompt") -> JudgeRequest:
        rf = self.tmp_path / "responses" / "req-001.json"
        return JudgeRequest(
            request_id="r-001",
            rubric_id="coherence",
            apply_to="artifact:architecture",
            severity="info",
            threshold=None,
            target_artifact_paths=[],
            golden_paths=[],
            response_file=str(rf),
            prompt=prompt,
        )

    def test_success_path(self):
        script = self._make_script(
            'import sys; print(\'{"score": 0.85, "rationale": "good"}\')'
        )
        req = self._make_request()
        res = subprocess_runner.run_one_judge_request(
            req, copilot_bin=script, run_id="rid", request_index=1,
            timeout_seconds=30,
        )
        self.assertTrue(res.success)
        data = json.loads(Path(req.response_file).read_text(encoding="utf-8"))
        self.assertEqual(data["score"], 0.85)

    def test_retry_then_success(self):
        # Script that fails the first time and succeeds the second time,
        # using a counter file in the temp dir.
        counter_file = self.tmp_path / "ctr"
        body = textwrap.dedent(f"""\
            import os
            ctr_path = r"{counter_file}"
            n = 0
            if os.path.exists(ctr_path):
                with open(ctr_path) as fh: n = int(fh.read() or 0)
            with open(ctr_path, "w") as fh: fh.write(str(n+1))
            if n == 0:
                print("garbage no json here")
            else:
                print('{{"score": 0.5, "rationale": "retry-ok"}}')
        """)
        script = self._make_script(body)
        req = self._make_request()
        res = subprocess_runner.run_one_judge_request(
            req, copilot_bin=script, run_id="rid", request_index=1,
            timeout_seconds=30,
        )
        self.assertTrue(res.success)
        data = json.loads(Path(req.response_file).read_text(encoding="utf-8"))
        self.assertEqual(data["score"], 0.5)
        # Two attempts.
        self.assertEqual(int(counter_file.read_text()), 2)

    def test_persistent_malformed_writes_error_payload(self):
        script = self._make_script(
            'print("nothing parseable here, no json at all")'
        )
        req = self._make_request()
        res = subprocess_runner.run_one_judge_request(
            req, copilot_bin=script, run_id="rid", request_index=1,
            timeout_seconds=30,
        )
        self.assertFalse(res.success)
        data = json.loads(Path(req.response_file).read_text(encoding="utf-8"))
        self.assertIn("error", data)
        self.assertIsNone(data["score"])

    def test_nonzero_exit_treated_as_failure(self):
        script = self._make_script(
            'import sys; sys.stderr.write("boom"); sys.exit(3)'
        )
        req = self._make_request()
        res = subprocess_runner.run_one_judge_request(
            req, copilot_bin=script, run_id="rid", request_index=1,
            timeout_seconds=30,
        )
        self.assertFalse(res.success)
        data = json.loads(Path(req.response_file).read_text(encoding="utf-8"))
        self.assertIn("error", data)
        self.assertIn("exited 3", data["error"])


if __name__ == "__main__":
    unittest.main()

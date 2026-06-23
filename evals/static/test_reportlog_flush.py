"""Regression guard for H2: per-test report-log flush.

When pytest is killed mid-run (e.g. a per-test timeout escalates into a
process kill at the global wall-clock backstop), the `pytest-reportlog`
JSONL file must already contain a `TestReport` entry for every completed
test. Without per-test ``flush() + os.fsync()`` of the report-log handle,
the kernel buffers the writes and we lose all failure detail.

This test spawns a tiny pytest in a subprocess, kills it shortly after
the first test reports, and asserts the report-log file contains at
least one ``TestReport`` JSON line.

If this test starts failing after a `pytest-reportlog` upgrade, the
plugin probably renamed its `_file` attribute and the flush hook in
``evals/conftest.py`` silently degraded to no-flush. Update the hook
to use the new attribute name.
"""

from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import textwrap
import time
from pathlib import Path


def _build_pytest_dir(tmp_path: Path) -> Path:
    """Materialise a self-contained pytest scenario in ``tmp_path``."""
    repo_conftest = Path(__file__).resolve().parents[1] / "conftest.py"
    # Copy our project conftest so the flush hook is in effect.
    (tmp_path / "conftest.py").write_text(
        repo_conftest.read_text(encoding="utf-8"), encoding="utf-8"
    )
    (tmp_path / "test_flush_target.py").write_text(
        textwrap.dedent(
            """
            import time

            def test_one_passes():
                assert 1 + 1 == 2

            def test_two_then_sleeps_so_runner_can_kill_us():
                # Give the parent harness a moment to see the first
                # report land in the JSONL, then sleep long enough
                # that the parent kills the pytest process while this
                # test is still running.
                time.sleep(60)
            """
        ).strip()
        + "\n",
        encoding="utf-8",
    )
    return tmp_path


def test_reportlog_flushes_per_test(tmp_path: Path):
    work = _build_pytest_dir(tmp_path)
    report_log = work / "report.jsonl"

    cmd = [
        sys.executable,
        "-m",
        "pytest",
        str(work),
        f"--report-log={report_log}",
        "-p", "no:cacheprovider",
        "-q",
    ]
    # Use the same per-OS process-group flags as the real runner so we
    # can kill cleanly.
    popen_kwargs: dict = {}
    if sys.platform == "win32":
        popen_kwargs["creationflags"] = 0x00000200  # CREATE_NEW_PROCESS_GROUP
    else:
        popen_kwargs["start_new_session"] = True

    proc = subprocess.Popen(
        cmd,
        cwd=str(work),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        **popen_kwargs,
    )

    # Wait until the first TestReport line appears, or up to 30s.
    deadline = time.monotonic() + 30.0
    saw_test_report = False
    try:
        while time.monotonic() < deadline:
            if report_log.exists():
                for line in report_log.read_text(encoding="utf-8").splitlines():
                    try:
                        evt = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    if evt.get("$report_type") == "TestReport":
                        saw_test_report = True
                        break
                if saw_test_report:
                    break
            time.sleep(0.5)
    finally:
        # Hard-kill the pytest tree to simulate the wall-clock cap.
        try:
            import psutil

            try:
                parent = psutil.Process(proc.pid)
                for child in parent.children(recursive=True):
                    try:
                        child.kill()
                    except psutil.Error:
                        pass
                parent.kill()
            except psutil.NoSuchProcess:
                pass
        except ImportError:
            proc.kill()
        try:
            proc.wait(timeout=15.0)
        except subprocess.TimeoutExpired:
            pass

    assert report_log.exists(), (
        "report-log was never created; pytest-reportlog plugin may not be "
        "active or pytest crashed before any output."
    )

    test_reports = []
    for line in report_log.read_text(encoding="utf-8").splitlines():
        try:
            evt = json.loads(line)
        except json.JSONDecodeError:
            continue
        if evt.get("$report_type") == "TestReport":
            test_reports.append(evt)

    assert test_reports, (
        "report-log contains no TestReport entries after kill. "
        "The flush hook in evals/conftest.py is not actually flushing "
        "the report-log file before the next test starts. Likely cause: "
        "pytest-reportlog renamed its `_file` attribute -- update the "
        "hook in evals/conftest.py."
    )

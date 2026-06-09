"""Regression guard for H8: SUT budget controls.

Behavioural pack evals drive the *live* Copilot CLI, which makes multi-minute,
non-deterministic LLM calls. A single slow/non-responsive SUT invocation (the
``product-knowledge-brain`` pack requested ``timeout=900`` per call, and one
test runs the SUT twice) could consume the entire eval-fix-loop wall-clock
budget and starve the rest of the suite, so the run never reached a clean
pass/fail/skip for the remaining tests.

These deterministic, no-SUT tests pin the two opt-in controls added to
``evals/_lib/copilot.py`` so they can't silently regress:

* ``EVALS_SUT_TIMEOUT`` -- clamps every SUT subprocess timeout so a hung SUT
  fails fast (returncode 124, ``timed_out=True``) instead of burning its full
  requested budget.
* ``EVALS_SKIP_SUT`` -- short-circuits ``run_agent`` so an environment that
  cannot run the live LLM SUT within budget completes the whole suite
  deterministically (every behavioural test skips cleanly) with zero tokens.

If this file starts failing, the harness budget controls changed shape and the
pack evals can hang the loop again -- fix the harness, do not delete coverage.
"""

from __future__ import annotations

import sys
import textwrap
import time
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from _lib import copilot  # noqa: E402


# ---- timeout clamping ---------------------------------------------------


def test_resolve_sut_timeout_passthrough_when_unset(monkeypatch):
    monkeypatch.delenv("EVALS_SUT_TIMEOUT", raising=False)
    assert copilot._resolve_sut_timeout(900) == 900


def test_resolve_sut_timeout_clamps_when_set(monkeypatch):
    monkeypatch.setenv("EVALS_SUT_TIMEOUT", "30")
    assert copilot._resolve_sut_timeout(900) == 30
    # Never raises the requested timeout above what the caller asked for.
    assert copilot._resolve_sut_timeout(10) == 10


def test_resolve_sut_timeout_ignores_garbage(monkeypatch):
    monkeypatch.setenv("EVALS_SUT_TIMEOUT", "not-a-number")
    assert copilot._resolve_sut_timeout(900) == 900
    monkeypatch.setenv("EVALS_SUT_TIMEOUT", "0")
    assert copilot._resolve_sut_timeout(900) == 900


@pytest.mark.parametrize(
    "value,expected",
    [("1", True), ("true", True), ("YES", True), ("on", True),
     ("0", False), ("", False), ("false", False), ("nope", False)],
)
def test_truthy_env(monkeypatch, value, expected):
    monkeypatch.setenv("EVALS_SKIP_SUT", value)
    assert copilot._truthy_env("EVALS_SKIP_SUT") is expected


# ---- EVALS_SKIP_SUT short-circuit ---------------------------------------


def test_skip_sut_short_circuits_without_binary(monkeypatch, tmp_path):
    """With EVALS_SKIP_SUT set, run_agent must NOT consult the binary and must
    return a clean ``skipped`` sentinel that tests can pytest.skip on."""
    monkeypatch.setenv("EVALS_SKIP_SUT", "1")
    # Point COPILOT_BIN at a path that does not exist: if the short-circuit
    # regresses and find_copilot_bin runs, this would surface (the override is
    # returned verbatim, then Popen would fail) -- proving the skip path runs
    # *before* any binary resolution.
    monkeypatch.setenv("COPILOT_BIN", str(tmp_path / "does-not-exist"))

    log = tmp_path / "agent.log"
    res = copilot.run_agent(
        prompt="hello", workspace=tmp_path, log_path=log, timeout=900
    )

    assert res.skipped is True
    assert res.timed_out is False
    assert res.returncode == 125
    assert res.usable is False
    assert res.unavailable_reason()  # non-empty, points at the log
    assert log.exists(), "skip sentinel must still persist a log for triage"


def test_usable_true_for_normal_result():
    res = copilot.CopilotResult(
        returncode=0, stdout="", stderr="", duration_seconds=0.0,
        log_path=Path("x"),
    )
    assert res.usable is True
    assert res.unavailable_reason() == ""


# ---- fail-fast timeout (the actual stall the loop hit) ------------------


def test_hung_sut_is_killed_and_marked_timed_out(tmp_path):
    """A child that ignores SIGTERM and holds the stdout pipe open must be
    force-killed at ``timeout`` (+ grace), returning 124 with timed_out=True --
    NOT hang the suite. This is the deterministic version of the stall that
    starved the product-knowledge-brain eval loop."""
    stub = tmp_path / "hang.py"
    stub.write_text(
        textwrap.dedent(
            """
            import signal, sys, time
            try:
                signal.signal(signal.SIGTERM, signal.SIG_IGN)
            except Exception:
                pass
            sys.stdin.read()
            sys.stderr.write("up\\n"); sys.stderr.flush()
            time.sleep(600)
            """
        ),
        encoding="utf-8",
    )
    log = tmp_path / "out.log"
    t0 = time.monotonic()
    res = copilot._run(
        [sys.executable, str(stub)],
        cwd=tmp_path,
        log_path=log,
        timeout=5,
        stdin_text="x",
    )
    elapsed = time.monotonic() - t0

    assert res.returncode == 124
    assert res.timed_out is True
    assert res.usable is False
    # Must terminate close to the timeout, never run to the stub's 600s sleep.
    assert elapsed < 45, f"kill path too slow ({elapsed:.1f}s); SUT could stall the loop"

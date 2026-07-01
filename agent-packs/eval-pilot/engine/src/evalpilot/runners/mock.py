"""A deterministic, offline ``mock`` SUT runner.

Select it with ``EVALPILOT_RUNNER=mock``. It never launches a real agent, so
the whole pipeline — staging, assertions, judge, metrics, rendering — runs
without the ``copilot`` binary. That makes the framework:

* **testable** — the engine's own unit tests exercise a full run offline;
* **demoable** — ``evalpilot new`` + ``evalpilot run`` work out of the box;
* **fast** — no tokens, no subprocess.

Behaviour is scripted in three ways (checked in order):

1. Programmatically via :func:`configure_mock` (used by tests).
2. Via env: ``EVALPILOT_MOCK_STDOUT``, ``EVALPILOT_MOCK_FILES`` (JSON of
   ``{relpath: content}``), ``EVALPILOT_MOCK_JUDGE_SCORE``.
3. A sensible default: echo the prompt, create nothing.

When asked to run the ``eval-judge`` agent, the mock emits a canned JSON
verdict so :mod:`evalpilot.judge` works offline too.
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Optional, Sequence

from .base import RunResult, SUTRunner, register_runner

# Programmatic script (highest priority). Set via configure_mock().
_SCRIPT: dict = {}


def configure_mock(
    *,
    stdout: Optional[str] = None,
    files: Optional[dict] = None,
    returncode: int = 0,
    judge_score: Optional[float] = None,
    judge_rationale: str = "mock verdict",
) -> None:
    """Script the next mock runs. Pass ``stdout=None`` etc. to clear a field."""
    _SCRIPT.clear()
    if stdout is not None:
        _SCRIPT["stdout"] = stdout
    if files is not None:
        _SCRIPT["files"] = dict(files)
    _SCRIPT["returncode"] = returncode
    if judge_score is not None:
        _SCRIPT["judge_score"] = judge_score
    _SCRIPT["judge_rationale"] = judge_rationale


def reset_mock() -> None:
    """Clear any programmatic script."""
    _SCRIPT.clear()


def _judge_score() -> float:
    if "judge_score" in _SCRIPT:
        return float(_SCRIPT["judge_score"])
    raw = os.environ.get("EVALPILOT_MOCK_JUDGE_SCORE")
    return float(raw) if raw else 1.0


def _scripted_files() -> dict:
    if "files" in _SCRIPT:
        return _SCRIPT["files"]
    raw = os.environ.get("EVALPILOT_MOCK_FILES")
    if raw:
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return {}
    return {}


def _scripted_stdout(prompt: str) -> str:
    if "stdout" in _SCRIPT:
        return _SCRIPT["stdout"]
    env = os.environ.get("EVALPILOT_MOCK_STDOUT")
    if env is not None:
        return env
    return f"[mock] received prompt ({len(prompt)} chars); no action taken.\n"


@register_runner
class MockRunner(SUTRunner):
    """Deterministic offline runner for tests and demos."""

    name = "mock"

    def available(self) -> bool:
        return True

    def run_agent(
        self,
        *,
        prompt: str,
        workspace: Path,
        agent: Optional[str],
        log_path: Path,
        timeout: float = 600.0,
        extra_args: Sequence[str] = (),
    ) -> RunResult:
        started = time.monotonic()

        if agent == "eval-judge":
            stdout = json.dumps({
                "score": _judge_score(),
                "rationale": _SCRIPT.get("judge_rationale", "mock verdict"),
                "evidence": [{"path": "artifact", "quote": "(mock)"}],
            })
            returncode = 0
        else:
            for rel, content in _scripted_files().items():
                target = workspace / rel
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(str(content), encoding="utf-8")
            stdout = _scripted_stdout(prompt)
            returncode = int(_SCRIPT.get("returncode", 0))

        duration = time.monotonic() - started
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_path.write_text(
            f"$ <mock> agent={agent}\n[cwd] {workspace}\n[exit] {returncode}\n"
            f"[duration_s] {duration:.4f}\n\n"
            f"--- PROMPT (stdin) ---\n{prompt}\n"
            f"--- STDOUT ---\n{stdout}\n--- STDERR ---\n",
            encoding="utf-8",
        )
        return RunResult(
            returncode=returncode,
            stdout=stdout,
            stderr="",
            duration_seconds=duration,
            log_path=log_path,
            extra={"mock": True},
        )

    def run_skill(
        self,
        *,
        skill: str,
        prompt: str,
        workspace: Path,
        log_path: Path,
        timeout: float = 300.0,
        extra_args: Sequence[str] = (),
    ) -> RunResult:
        return self.run_agent(
            prompt=prompt, workspace=workspace, agent=None,
            log_path=log_path, timeout=timeout, extra_args=extra_args,
        )


__all__ = ["MockRunner", "configure_mock", "reset_mock"]

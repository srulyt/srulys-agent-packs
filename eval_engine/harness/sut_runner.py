"""Non-interactive SUT (system-under-test) Copilot invocation.

The harness's existing ``scripted_user`` driver is for cases that
need to feed mid-run replies via stdin. ``run-pack`` / ``run-case``,
however, are typically invoked against cases without scripted_user
(prompt-only). This module is the prompt-only counterpart: spawn
``copilot -p <prompt> --agent <pack> ...`` once, wait for it to
finish, return the exit code.

Fixture data is harvested from the local Copilot CLI process log by
``local_extractor`` after the SUT exits, exactly as the existing
``capture-local`` flow does.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


class CopilotBinNotFound(RuntimeError):
    """Raised when the configured ``copilot`` binary is not on PATH."""


def _resolve_copilot_bin(copilot_bin: str) -> str:
    if Path(copilot_bin).exists():
        return str(Path(copilot_bin).resolve())
    found = shutil.which(copilot_bin)
    if found is None:
        raise CopilotBinNotFound(
            f"copilot binary {copilot_bin!r} not found on PATH"
        )
    return found


@dataclass
class SUTRunResult:
    exit_code: int
    stdout_tail: str
    stderr_tail: str
    timed_out: bool = False


def run_sut_once(
    *,
    prompt: str,
    workspace_root: str,
    pack: str,
    run_id: str,
    copilot_bin: str = "copilot",
    timeout_seconds: float = 1800.0,
    extra_args: list[str] | None = None,
) -> SUTRunResult:
    """Run the SUT under test exactly once with the given prompt.

    Spawns::

        copilot -p <prompt> --agent <pack> --allow-all-tools \\
                --allow-all-paths --no-ask-user --name <run-id>

    in ``workspace_root`` as cwd, captures stdout/stderr, and returns
    the result. The caller is expected to follow up with
    ``local_extractor.build_fixture`` to lift the structured fixture
    out of ``~/.copilot/logs/process-*.log``.
    """
    bin_path = _resolve_copilot_bin(copilot_bin)
    argv: list[str] = [
        bin_path,
        "-p",
        prompt,
        "--agent",
        pack,
        "--allow-all-tools",
        "--allow-all-paths",
        "--no-ask-user",
        "--name",
        run_id,
    ]
    if extra_args:
        argv.extend(extra_args)
    try:
        proc = subprocess.run(
            argv,
            cwd=workspace_root,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )
    except subprocess.TimeoutExpired as exc:
        return SUTRunResult(
            exit_code=124,
            stdout_tail=(exc.stdout or "")[-800:] if isinstance(exc.stdout, str) else "",
            stderr_tail=(exc.stderr or "")[-800:] if isinstance(exc.stderr, str) else "",
            timed_out=True,
        )
    return SUTRunResult(
        exit_code=proc.returncode,
        stdout_tail=(proc.stdout or "")[-800:],
        stderr_tail=(proc.stderr or "")[-800:],
        timed_out=False,
    )

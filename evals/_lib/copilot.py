"""Subprocess wrapper around the Copilot CLI.

Two entry points:

* :func:`run_agent` -- run a Copilot CLI agent (a pack) non-interactively
  inside a workspace. Stdout/stderr are captured; the raw process log path
  is returned for log-preservation requirements.
* :func:`run_skill` -- evaluate a skill in isolation by invoking Copilot CLI
  with a prompt that only loads that single skill. No pack required.

Both are thin wrappers; they exist so tests don't reach for ``subprocess``
directly and so we can swap the backend (e.g. mock / record-replay) in
fixtures.
"""

from __future__ import annotations

import dataclasses
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Sequence


@dataclasses.dataclass(frozen=True)
class CopilotResult:
    """Outcome of a single ``copilot -p ...`` invocation."""

    returncode: int
    stdout: str
    stderr: str
    duration_seconds: float
    log_path: Path
    """Path to the persisted combined stdout+stderr log on disk."""

    @property
    def ok(self) -> bool:
        return self.returncode == 0


class CopilotNotInstalled(RuntimeError):
    """Raised when no ``copilot`` binary can be found on PATH."""


def find_copilot_bin() -> str:
    """Return absolute path to the ``copilot`` binary or raise."""
    override = os.environ.get("COPILOT_BIN")
    if override:
        return override
    candidate = shutil.which("copilot")
    if not candidate:
        raise CopilotNotInstalled(
            "No `copilot` binary found on PATH. Set COPILOT_BIN to override "
            "(useful for tests with a stubbed binary)."
        )
    return candidate


def _run(
    cmd: Sequence[str],
    *,
    cwd: Path,
    log_path: Path,
    timeout: float,
    env_extra: dict[str, str] | None = None,
    stdin_text: str | None = None,
) -> CopilotResult:
    import time

    env = os.environ.copy()
    if env_extra:
        env.update(env_extra)

    log_path.parent.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    try:
        proc = subprocess.run(
            list(cmd),
            cwd=str(cwd),
            input=stdin_text,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            env=env,
            check=False,
        )
        stdout, stderr, returncode = proc.stdout, proc.stderr, proc.returncode
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout.decode() if isinstance(exc.stdout, bytes) else (exc.stdout or "")
        stderr = exc.stderr.decode() if isinstance(exc.stderr, bytes) else (exc.stderr or "")
        stderr += f"\n[copilot helper] TIMEOUT after {timeout}s\n"
        returncode = 124  # convention used by /usr/bin/timeout
    duration = time.monotonic() - started

    log_path.write_text(
        f"$ {' '.join(cmd)}\n[cwd] {cwd}\n[exit] {returncode}\n"
        f"[duration_s] {duration:.2f}\n\n"
        f"--- PROMPT (stdin) ---\n{stdin_text or ''}\n"
        f"--- STDOUT ---\n{stdout}\n--- STDERR ---\n{stderr}\n",
        encoding="utf-8",
        errors="replace",
    )
    return CopilotResult(
        returncode=returncode,
        stdout=stdout,
        stderr=stderr,
        duration_seconds=duration,
        log_path=log_path,
    )


def run_agent(
    *,
    prompt: str,
    workspace: Path,
    agent: str | None = None,
    log_path: Path,
    timeout: float = 600.0,
    extra_args: Sequence[str] = (),
) -> CopilotResult:
    """Run a Copilot CLI agent non-interactively inside ``workspace``.

    Parameters
    ----------
    prompt:
        Prompt text passed via ``-p``. May be multi-line.
    workspace:
        Directory the CLI is launched from (its ``cwd``). The agent and
        skill files must already be staged under ``workspace/.github/``.
    agent:
        Optional ``--agent <name>`` flag. ``None`` means "let Copilot pick"
        (typical for skill-only evals or default agent).
    log_path:
        Where the captured stdout/stderr is written so failures can be
        inspected after the run.
    timeout:
        Hard wall-clock limit for the subprocess in seconds.
    extra_args:
        Extra CLI flags appended verbatim (e.g. ``--name <run-id>``).
    """
    bin_path = find_copilot_bin()
    # Feed the prompt via stdin rather than `-p <prompt>` so multi-line
    # prompts survive the Windows .CMD shim (which truncates `-p` arg
    # values at the first newline). Stdin works identically on POSIX.
    cmd: list[str] = [bin_path]
    if agent:
        cmd += ["--agent", agent]
    # `--allow-all` is `--allow-all-tools --allow-all-paths --allow-all-urls`
    # and is the only combination that reliably grants write/shell perms
    # alongside `--no-ask-user` (the individual flags leave gaps that
    # surface as "Permission denied and could not request permission from
    # user" mid-run).
    cmd += ["--allow-all", "--no-ask-user"]
    cmd += list(extra_args)
    return _run(
        cmd,
        cwd=workspace,
        log_path=log_path,
        timeout=timeout,
        stdin_text=prompt,
    )


def run_skill(
    *,
    skill: str,
    prompt: str,
    workspace: Path,
    log_path: Path,
    timeout: float = 300.0,
    extra_args: Sequence[str] = (),
) -> CopilotResult:
    """Evaluate a skill in isolation.

    Currently a thin wrapper around :func:`run_agent` that prefixes the
    prompt with an explicit "use the <skill> skill" directive. As Copilot
    CLI grows a first-class ``--skill`` flag this can swap to it.
    """
    augmented = (
        f"Use the `{skill}` skill to handle the following request. "
        f"Do not invoke any other skill.\n\n{prompt}"
    )
    return run_agent(
        prompt=augmented,
        workspace=workspace,
        agent=None,
        log_path=log_path,
        timeout=timeout,
        extra_args=extra_args,
    )

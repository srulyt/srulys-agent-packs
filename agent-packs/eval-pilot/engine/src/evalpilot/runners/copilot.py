"""Copilot CLI :class:`SUTRunner` implementation.

Ported from the monorepo harness's ``evals/_lib/copilot.py``. Drives the
``copilot`` binary non-interactively inside a workspace and returns a
normalised :class:`~evalpilot.runners.base.RunResult`.

Hardening retained from the original:

* Known fatal Windows exit codes are surfaced via ``result.extra["crash"]``
  so a CLI runtime crash isn't confused with an agent-prompt defect.
* The subprocess is launched in its own process group; on timeout (or
  Ctrl-C) the whole tree is killed via ``psutil`` so xdist workers and the
  CLI's Node subprocess aren't orphaned.
* The prompt is fed via **stdin**, never ``-p``: the Windows ``copilot.CMD``
  shim truncates ``-p`` values at the first newline.
* ``--allow-all --no-ask-user`` is the only flag combo that reliably grants
  write/shell perms in non-interactive mode.
"""

from __future__ import annotations

import os
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional, Sequence

from .base import RunResult, SUTRunner, SUTUnavailable, register_runner


# Known fatal Windows NTSTATUS exit codes (runtime crashes, not agent defects).
_WIN_FATAL_EXIT_CODES: dict[int, str] = {
    3221225477: "STATUS_ACCESS_VIOLATION (0xC0000005)",
    3221225725: "STATUS_STACK_OVERFLOW (0xC00000FD)",
    3221226505: "STATUS_STACK_BUFFER_OVERRUN (0xC0000409)",
}


class CopilotNotInstalled(SUTUnavailable):
    """Raised when no ``copilot`` binary can be found on PATH."""


def _truthy_env(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in {"1", "true", "yes", "on"}


def _skip_sut() -> bool:
    return _truthy_env("EVALPILOT_SKIP_SUT") or _truthy_env("EVALS_SKIP_SUT")


def _resolve_sut_timeout(requested: float) -> float:
    """Clamp ``requested`` to ``EVALPILOT_SUT_TIMEOUT`` when that env is set."""
    raw = (
        os.environ.get("EVALPILOT_SUT_TIMEOUT")
        or os.environ.get("EVALS_SUT_TIMEOUT")
        or ""
    ).strip()
    if not raw:
        return requested
    try:
        cap = float(raw)
    except ValueError:
        return requested
    return min(requested, cap) if cap > 0 else requested


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


def _kill_process_tree(pid: int, *, grace_seconds: float = 5.0) -> None:
    """Best-effort: terminate then kill ``pid`` and all descendants."""
    try:
        import psutil  # type: ignore
    except ImportError:
        try:
            os.kill(pid, signal.SIGTERM)
        except (ProcessLookupError, PermissionError, OSError):
            pass
        return

    try:
        parent = psutil.Process(pid)
    except psutil.NoSuchProcess:
        return
    procs = parent.children(recursive=True) + [parent]
    for p in procs:
        try:
            p.terminate()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    _, alive = psutil.wait_procs(procs, timeout=grace_seconds)
    for p in alive:
        try:
            p.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    psutil.wait_procs(alive, timeout=2.0)


def _popen_kwargs_for_tree_kill() -> dict:
    if sys.platform == "win32":
        return {"creationflags": 0x00000200}  # CREATE_NEW_PROCESS_GROUP
    return {"start_new_session": True}


def _run(
    cmd: Sequence[str],
    *,
    cwd: Path,
    log_path: Path,
    timeout: float,
    stdin_text: Optional[str] = None,
) -> RunResult:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    stdout = ""
    stderr = ""
    returncode = 0
    timed_out = False

    proc = subprocess.Popen(
        list(cmd),
        cwd=str(cwd),
        stdin=subprocess.PIPE if stdin_text is not None else subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        **_popen_kwargs_for_tree_kill(),
    )
    try:
        try:
            stdout, stderr = proc.communicate(input=stdin_text, timeout=timeout)
            returncode = proc.returncode
        except subprocess.TimeoutExpired:
            timed_out = True
            _kill_process_tree(proc.pid)
            try:
                stdout, stderr = proc.communicate(timeout=5.0)
            except subprocess.TimeoutExpired:
                proc.kill()
                stdout, stderr = "", ""
            stderr = (stderr or "") + f"\n[evalpilot] TIMEOUT after {timeout}s\n"
            returncode = 124
    except KeyboardInterrupt:
        _kill_process_tree(proc.pid)
        raise

    duration = time.monotonic() - started

    crash = None
    if not timed_out and returncode in _WIN_FATAL_EXIT_CODES:
        crash = _WIN_FATAL_EXIT_CODES[returncode]

    crash_line = f"[crash] {crash}\n" if crash else ""
    log_path.write_text(
        f"$ {' '.join(cmd)}\n[cwd] {cwd}\n[exit] {returncode}\n"
        f"[duration_s] {duration:.2f}\n{crash_line}\n"
        f"--- PROMPT (stdin) ---\n{stdin_text or ''}\n"
        f"--- STDOUT ---\n{stdout}\n--- STDERR ---\n{stderr}\n",
        encoding="utf-8",
        errors="replace",
    )
    return RunResult(
        returncode=returncode,
        stdout=stdout,
        stderr=stderr,
        duration_seconds=duration,
        log_path=log_path,
        timed_out=timed_out,
        extra={"crash": crash} if crash else {},
    )


def _skipped_result(*, cmd: Sequence[str], cwd: Path, log_path: Path,
                    stdin_text: Optional[str]) -> RunResult:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(
        f"$ {' '.join(cmd)}\n[cwd] {cwd}\n[exit] 125\n"
        f"[skipped] EVALPILOT_SKIP_SUT is set; SUT not launched.\n\n"
        f"--- PROMPT (stdin) ---\n{stdin_text or ''}\n"
        f"--- STDOUT ---\n\n--- STDERR ---\n",
        encoding="utf-8",
        errors="replace",
    )
    return RunResult(
        returncode=125,
        stdout="",
        stderr="[evalpilot] EVALPILOT_SKIP_SUT set; SUT not launched.\n",
        duration_seconds=0.0,
        log_path=log_path,
        skipped=True,
    )


@register_runner
class CopilotRunner(SUTRunner):
    """Drives the ``copilot`` CLI."""

    name = "copilot"

    def available(self) -> bool:
        try:
            find_copilot_bin()
            return True
        except CopilotNotInstalled:
            return False

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
        if _skip_sut():
            agent_part = ["--agent", agent] if agent else []
            return _skipped_result(
                cmd=["<copilot>", *agent_part, "--allow-all", "--no-ask-user"],
                cwd=workspace,
                log_path=log_path,
                stdin_text=prompt,
            )
        bin_path = find_copilot_bin()
        cmd: list[str] = [bin_path]
        if agent:
            cmd += ["--agent", agent]
        cmd += ["--allow-all", "--no-ask-user", *extra_args]
        return _run(
            cmd,
            cwd=workspace,
            log_path=log_path,
            timeout=_resolve_sut_timeout(timeout),
            stdin_text=prompt,
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
        augmented = (
            f"Use the `{skill}` skill to handle the following request. "
            f"Do not invoke any other skill.\n\n{prompt}"
        )
        return self.run_agent(
            prompt=augmented,
            workspace=workspace,
            agent=None,
            log_path=log_path,
            timeout=timeout,
            extra_args=extra_args,
        )


__all__ = ["CopilotRunner", "CopilotNotInstalled", "find_copilot_bin"]

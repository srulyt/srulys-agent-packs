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
import threading
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
    killed_by_watchdog: bool = False


# ----- Active-process registry (used by pack_runner watchdog) ----------
#
# Patch 4: we need the pack-level watchdog (in ``pack_runner``) to be
# able to hard-kill every still-running SUT subprocess from a different
# thread. We track live ``Popen`` handles in a module-level set guarded
# by a lock. Each ``run_sut_once`` call registers its child on spawn
# and unregisters it in a ``finally`` block.

_active_lock = threading.Lock()
_active_procs: "set[subprocess.Popen]" = set()


def _register(proc: "subprocess.Popen") -> None:
    with _active_lock:
        _active_procs.add(proc)


def _unregister(proc: "subprocess.Popen") -> None:
    with _active_lock:
        _active_procs.discard(proc)


def hard_kill(proc: "subprocess.Popen", *, grace_seconds: float = 5.0) -> None:
    """Hard-terminate a SUT subprocess and (on Windows) its descendants.

    On Windows the SUT is typically a ``.bat`` or wrapper that spawns a
    ``python.exe`` grandchild. Calling ``proc.terminate()`` first would
    kill just the immediate child and re-parent the grandchild to the
    system, after which ``taskkill /T`` can no longer walk the tree.
    So on Windows we run ``taskkill /F /T`` FIRST (while the parent-
    child relationship is still intact), then fall back to
    ``proc.kill()`` to reap the ``Popen`` handle.

    On POSIX we use the ``terminate`` → wait → ``kill`` sequence, which
    delivers SIGTERM then SIGKILL.

    Idempotent: silently no-ops if the process has already exited.
    """
    if proc.poll() is not None:
        return
    if sys.platform == "win32":
        try:
            subprocess.run(
                ["taskkill", "/F", "/T", "/PID", str(proc.pid)],
                capture_output=True, timeout=10,
            )
        except Exception:
            pass
        # taskkill is async-ish; give the OS a moment, then ensure the
        # Popen handle is reaped.
        try:
            proc.wait(timeout=grace_seconds)
        except Exception:
            try:
                proc.kill()
            except Exception:
                pass
            try:
                proc.wait(timeout=grace_seconds)
            except Exception:
                pass
        return
    # POSIX path
    try:
        proc.terminate()
    except Exception:
        pass
    try:
        proc.wait(timeout=grace_seconds)
        return
    except Exception:
        pass
    try:
        proc.kill()
    except Exception:
        pass
    try:
        proc.wait(timeout=grace_seconds)
    except Exception:
        pass


def kill_all_active() -> int:
    """Hard-kill every registered live SUT. Returns count attempted."""
    with _active_lock:
        procs = list(_active_procs)
    for p in procs:
        try:
            hard_kill(p)
        except Exception:
            pass
    return len(procs)


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
    # Force UTF-8 decoding with replacement on the captured pipes.
    # Without an explicit encoding, Python opens the stdout/stderr
    # reader threads with the platform default (cp1252 on Windows),
    # which crashes with UnicodeDecodeError (e.g. byte 0x8f) the
    # first time the SUT emits a non-cp1252 byte (fancy quotes,
    # emoji, etc.) into stdout. errors="replace" guarantees the
    # reader thread can never crash on a stray byte.
    #
    # Patch 4: switched from ``subprocess.run`` to ``Popen`` so that
    # (a) the per-case timeout path can hard-kill the subprocess tree
    # rather than leaking it, and (b) the pack-level watchdog can
    # reach in from another thread via ``kill_all_active`` and
    # terminate this child even while ``communicate`` is blocked.
    proc = subprocess.Popen(
        argv,
        cwd=workspace_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    _register(proc)
    try:
        try:
            stdout, stderr = proc.communicate(timeout=timeout_seconds)
            return SUTRunResult(
                exit_code=proc.returncode,
                stdout_tail=(stdout or "")[-800:],
                stderr_tail=(stderr or "")[-800:],
                timed_out=False,
            )
        except subprocess.TimeoutExpired:
            hard_kill(proc)
            try:
                stdout, stderr = proc.communicate(timeout=5)
            except Exception:
                stdout, stderr = "", ""
            return SUTRunResult(
                exit_code=124,
                stdout_tail=(stdout or "")[-800:],
                stderr_tail=(stderr or "")[-800:],
                timed_out=True,
            )
    finally:
        # If the watchdog killed us out of band, communicate() may have
        # returned a normal result — still make sure the proc is reaped
        # and removed from the active set.
        if proc.poll() is None:
            hard_kill(proc)
        _unregister(proc)

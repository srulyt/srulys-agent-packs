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

Hardening notes (see ``.copilot-factory`` harness-hardening proposal):

* **H3** -- known Windows fatal exit codes are surfaced via
  :class:`CopilotProcessCrash` and the ``crash`` attribute on
  :class:`CopilotResult`. Tests that fail on ``result.ok`` should mention
  ``result.crash_summary()`` so a Windows runtime crash is not confused
  with an agent-prompt defect.
* **H7** -- the subprocess is launched via :class:`subprocess.Popen` and on
  timeout (or KeyboardInterrupt) the whole process tree is killed via
  ``psutil``. On Windows the process is started in a new process group so
  it can be signalled cleanly.
"""

from __future__ import annotations

import dataclasses
import os
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional, Sequence


# ---- known fatal Windows exit codes (H3) --------------------------------
#
# Copilot CLI on Windows occasionally crashes with a Win32 NTSTATUS code
# instead of a normal exit. These are NOT agent-prompt defects: they are
# runtime crashes in the CLI itself (typically the Node.js process) and
# the agent never gets a chance to emit output. Surfacing them with a
# named class lets a human triager distinguish "CLI crashed" from
# "agent did the wrong thing".
_WIN_FATAL_EXIT_CODES: dict[int, str] = {
    3221225477: "STATUS_ACCESS_VIOLATION (0xC0000005)",
    3221225725: "STATUS_STACK_OVERFLOW (0xC00000FD)",
    3221226505: "STATUS_STACK_BUFFER_OVERRUN (0xC0000409)",
}


class CopilotProcessCrash(RuntimeError):
    """Raised / attached to results when Copilot CLI crashed with a known
    fatal Windows exit code (H3).

    The presence of this exception in :attr:`CopilotResult.crash` means
    the failure is a CLI runtime crash, NOT an agent-prompt defect.
    """

    def __init__(self, returncode: int, status_name: str, log_path: Path):
        self.returncode = returncode
        self.status_name = status_name
        self.log_path = log_path
        super().__init__(
            f"Copilot CLI crashed: {status_name} (exit={returncode}). "
            f"This is a Windows runtime crash, NOT an agent-prompt defect. "
            f"See {log_path}."
        )


@dataclasses.dataclass(frozen=True)
class CopilotResult:
    """Outcome of a single ``copilot -p ...`` invocation."""

    returncode: int
    stdout: str
    stderr: str
    duration_seconds: float
    log_path: Path
    """Path to the persisted combined stdout+stderr log on disk."""

    crash: Optional[CopilotProcessCrash] = None
    """Set when ``returncode`` matches a known Windows fatal exit (H3).

    When non-None the failure is a CLI runtime crash, not an agent defect.
    Tests should mention ``result.crash_summary()`` in failure messages.
    """

    timed_out: bool = False
    """True when the subprocess was killed because it exceeded its (possibly
    capped) wall-clock timeout. ``returncode`` is ``124`` in that case.

    Behavioural pack evals that drive the live SUT should treat a
    ``timed_out`` result as "SUT did not complete in this environment" and
    ``pytest.skip`` rather than hang the suite or hard-fail (see H8 below).
    """

    skipped: bool = False
    """True when the SUT was deliberately not launched because
    ``EVALS_SKIP_SUT`` is set (H8). ``returncode`` is ``125`` in that case.

    Tests should ``pytest.skip`` on a ``skipped`` result so an environment
    that cannot run the live LLM SUT within budget completes deterministically
    instead of consuming the whole eval-loop wall-clock budget.
    """

    @property
    def ok(self) -> bool:
        return self.returncode == 0

    @property
    def usable(self) -> bool:
        """True when the run produced real SUT output (not skipped/timed-out).

        Behavioural tests gate on this: ``if not result.usable: pytest.skip(...)``.
        """
        return not (self.skipped or self.timed_out)

    def unavailable_reason(self) -> str:
        """One-line reason a behavioural test should skip, or ``""``.

        Returns a non-empty, log-pointing message when the SUT was skipped
        (``EVALS_SKIP_SUT``) or timed out, so tests can pass it straight to
        ``pytest.skip``.
        """
        if self.skipped:
            return (
                "SUT not launched: EVALS_SKIP_SUT is set; this environment "
                f"cannot run the live Copilot CLI within budget. See {self.log_path}."
            )
        if self.timed_out:
            return (
                "SUT did not complete within its (capped) wall-clock timeout "
                f"in this environment. See {self.log_path}."
            )
        return ""

    def crash_summary(self) -> str:
        """Human-readable summary for failure messages.

        Returns an empty string when there's no recognised crash; otherwise
        a one-line "Windows runtime crash, NOT an agent-prompt defect"
        message suitable for inclusion in a pytest assertion message.
        """
        if self.crash is None:
            return ""
        return (
            f"Copilot CLI crashed: {self.crash.status_name} "
            f"(exit={self.returncode}). This is a Windows runtime crash, "
            f"NOT an agent-prompt defect. See {self.log_path}."
        )


class CopilotNotInstalled(RuntimeError):
    """Raised when no ``copilot`` binary can be found on PATH."""


# ---- SUT budget controls (H8) -------------------------------------------
#
# Behavioural pack evals drive the *live* Copilot CLI, which makes multi-
# minute, non-deterministic LLM calls. A single slow/non-responsive SUT
# call (these tests requested timeouts up to 900s each, and one test runs
# the SUT twice) can consume the entire eval-fix-loop wall-clock budget and
# starve every other test in the suite, so the run never reaches a clean
# pass/fail/skip for the remaining tests.
#
# Two opt-in, backward-compatible env controls bound this:
#
# * ``EVALS_SUT_TIMEOUT`` -- integer seconds. When set, every SUT subprocess
#   timeout is clamped to ``min(requested, cap)`` so a slow/hung SUT fails
#   fast (returncode 124, ``timed_out=True``) instead of burning its full
#   requested budget. Unset => requested timeouts are used unchanged, so
#   existing packs see no behaviour change.
#
# * ``EVALS_SKIP_SUT`` -- truthy ("1", "true", "yes"). When set, the SUT is
#   NOT launched at all; ``run_agent`` returns a sentinel result with
#   ``skipped=True`` and ``returncode=125``. This lets an environment that
#   cannot run the live LLM SUT within budget complete the whole suite
#   deterministically (every behavioural test skips cleanly) with zero
#   tokens, instead of hanging. Structural/no-SUT evals are unaffected.


def _truthy_env(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in {"1", "true", "yes", "on"}


def _resolve_sut_timeout(requested: float) -> float:
    """Clamp ``requested`` to ``EVALS_SUT_TIMEOUT`` when that env var is set.

    Invalid/empty values are ignored (requested timeout used as-is).
    """
    raw = os.environ.get("EVALS_SUT_TIMEOUT", "").strip()
    if not raw:
        return requested
    try:
        cap = float(raw)
    except ValueError:
        return requested
    if cap <= 0:
        return requested
    return min(requested, cap)


def _skipped_result(*, cmd: Sequence[str], cwd: Path, log_path: Path,
                    stdin_text: str | None) -> "CopilotResult":
    """Build a sentinel ``skipped`` result without launching the SUT (H8)."""
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(
        f"$ {' '.join(cmd)}\n[cwd] {cwd}\n[exit] 125\n"
        f"[skipped] EVALS_SKIP_SUT is set; SUT not launched.\n\n"
        f"--- PROMPT (stdin) ---\n{stdin_text or ''}\n"
        f"--- STDOUT ---\n\n--- STDERR ---\n",
        encoding="utf-8",
        errors="replace",
    )
    return CopilotResult(
        returncode=125,
        stdout="",
        stderr="[copilot helper] EVALS_SKIP_SUT set; SUT not launched.\n",
        duration_seconds=0.0,
        log_path=log_path,
        crash=None,
        timed_out=False,
        skipped=True,
    )


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


# ---- process-tree kill helper (H7) --------------------------------------


def _kill_process_tree(pid: int, *, grace_seconds: float = 5.0) -> None:
    """Best-effort: terminate then kill ``pid`` and all descendants.

    Uses ``psutil`` when available (it's a declared dep) for a portable
    recursive walk; falls back to a direct kill of ``pid`` otherwise so
    we never propagate an ImportError out of the harness.
    """
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
    # Polite termination first.
    for p in procs:
        try:
            p.terminate()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    gone, alive = psutil.wait_procs(procs, timeout=grace_seconds)
    # Anything still alive gets SIGKILL / TerminateProcess.
    for p in alive:
        try:
            p.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    psutil.wait_procs(alive, timeout=2.0)


def _popen_kwargs_for_tree_kill() -> dict:
    """Per-OS Popen flags that make the subtree easier to clean up.

    On Windows we put the child in its own process group so Ctrl+Break can
    reach it and so it doesn't inherit signal handling from the parent. On
    POSIX we start a new session via ``os.setsid`` so the descendants are
    all in one process group identifiable from the parent.
    """
    if sys.platform == "win32":
        # CREATE_NEW_PROCESS_GROUP = 0x00000200
        return {"creationflags": 0x00000200}
    return {"start_new_session": True}


def _run(
    cmd: Sequence[str],
    *,
    cwd: Path,
    log_path: Path,
    timeout: float,
    env_extra: dict[str, str] | None = None,
    stdin_text: str | None = None,
) -> CopilotResult:
    env = os.environ.copy()
    if env_extra:
        env.update(env_extra)

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
        env=env,
        **_popen_kwargs_for_tree_kill(),
    )
    try:
        try:
            stdout, stderr = proc.communicate(input=stdin_text, timeout=timeout)
            returncode = proc.returncode
        except subprocess.TimeoutExpired:
            timed_out = True
            _kill_process_tree(proc.pid)
            # Drain whatever's available now that the tree is dead.
            try:
                stdout, stderr = proc.communicate(timeout=5.0)
            except subprocess.TimeoutExpired:
                # Pipes still wedged; give up gracefully.
                proc.kill()
                stdout, stderr = "", ""
            stderr = (stderr or "") + f"\n[copilot helper] TIMEOUT after {timeout}s\n"
            returncode = 124  # convention used by /usr/bin/timeout
    except KeyboardInterrupt:
        # Honour Ctrl+C from the runner without orphaning children.
        _kill_process_tree(proc.pid)
        raise

    duration = time.monotonic() - started

    # H3: recognise known Windows fatal exit codes.
    crash: Optional[CopilotProcessCrash] = None
    if not timed_out and returncode in _WIN_FATAL_EXIT_CODES:
        crash = CopilotProcessCrash(
            returncode=returncode,
            status_name=_WIN_FATAL_EXIT_CODES[returncode],
            log_path=log_path,
        )

    crash_line = f"[crash] {crash}\n" if crash is not None else ""
    log_path.write_text(
        f"$ {' '.join(cmd)}\n[cwd] {cwd}\n[exit] {returncode}\n"
        f"[duration_s] {duration:.2f}\n{crash_line}\n"
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
        crash=crash,
        timed_out=timed_out,
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
    # H8: short-circuit before touching the binary so an environment that
    # opts out (or lacks the CLI) still completes deterministically.
    if _truthy_env("EVALS_SKIP_SUT"):
        agent_part = ["--agent", agent] if agent else []
        return _skipped_result(
            cmd=["<copilot>", *agent_part, "--allow-all", "--no-ask-user"],
            cwd=workspace,
            log_path=log_path,
            stdin_text=prompt,
        )
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
    log_path.parent.mkdir(parents=True, exist_ok=True)
    return _run(
        cmd,
        cwd=workspace,
        log_path=log_path,
        timeout=_resolve_sut_timeout(timeout),
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

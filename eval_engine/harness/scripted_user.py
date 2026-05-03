"""Scripted-user driver.

Drives a system-under-test (SUT) Copilot CLI session through its
``awaiting-*`` parks by feeding pre-recorded replies from a case's
``scripted_user:`` schedule. The driver was built to unblock fixture
capture for the spec-author pack (and any future pack whose orchestrator
parks for user input), where the previous capture path required a human
to type each reply at the correct moment.

Architecture
------------

The driver is split into two layers so unit tests can exercise the
schedule logic without spawning a real Copilot CLI process:

* :class:`ScriptedUserDriver` — pure dispatch loop. Polls a
  ``state_reader`` callable for the SUT's current state, resolves
  matching schedule entries, and forwards reply text to a
  ``reply_writer`` callable. Exits when the SUT reaches a terminal
  phase, the schedule is exhausted, or a deadline elapses.

* :func:`run_with_subprocess` — production wiring. Spawns a real
  ``copilot`` subprocess with a stdin pipe, locates the SUT's
  ``state.json`` (e.g. ``.spec-author/sessions/*/state.json``), and
  injects ``ScriptedUserDriver`` with a state-file reader and a
  stdin-line writer. Tests do **not** invoke this path.

Park detection
--------------

A "park" is observed when the polled ``state.json`` reports a phase
whose name starts with ``awaiting-`` AND that phase's *entry signature*
(see :func:`_park_signature`) has not yet been served. The signature
combines the phase name with whichever monotonic field the SUT exposes
(``updated_at`` / ``phase_entered_at`` / a per-park counter), so a
single long-lived ``awaiting-*`` window is dispatched exactly once even
when the poll interval is short.

The next pending schedule entry whose ``on_phase`` equals the observed
phase is popped and its reply written. If the next pending entry's
``on_phase`` does NOT match (e.g. the SUT parked on
``awaiting-interview-answers`` but the next scheduled reply targets
``awaiting-structure-approval``), the driver records a mismatch and
keeps polling — the operator's expectation is that the case schedule is
linear and any out-of-order park is a regression in the SUT.

Terminal phases
---------------

Any phase that starts with ``complete`` (``complete``,
``complete-with-warnings``) or equals one of ``error``, ``failed``,
``abandoned`` ends the loop with status ``terminal``.

Schedule exhaustion
-------------------

If the SUT parks again after every scheduled reply has been served,
the driver returns status ``exhausted``. This is treated as a hard
end-of-run by callers: the SUT is still alive but the harness has
nothing more to feed, so the subprocess wrapper sends EOF on stdin and
waits a bounded period for the SUT to exit.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Iterable

from . import models


_TERMINAL_EXACT = frozenset({"error", "failed", "abandoned"})


def _is_terminal(phase: str | None) -> bool:
    if not phase:
        return False
    return phase.startswith("complete") or phase in _TERMINAL_EXACT


def _is_park(phase: str | None) -> bool:
    return bool(phase) and phase.startswith("awaiting-")


def _park_signature(state: dict[str, Any]) -> tuple[str, str]:
    """Compute a monotonic park signature from a state dict.

    The first component is the phase name; the second is the most
    specific monotonic marker the SUT exposes, falling back to a
    constant. Two reads of the same state therefore yield the same
    signature even across short polls.
    """
    phase = str(state.get("phase") or "")
    for key in ("phase_entered_at", "updated_at", "phase_seq"):
        v = state.get(key)
        if v is not None:
            return (phase, f"{key}={v}")
    return (phase, "anonymous")


# ---------- Result types -------------------------------------------------


@dataclass
class ServedReply:
    on_phase: str
    reply_preview: str  # first 80 chars; full text not retained
    served_at: float    # monotonic seconds


@dataclass
class DriverResult:
    status: str  # "terminal" | "exhausted" | "timeout" | "schedule-mismatch" | "sut-exited"
    served: list[ServedReply] = field(default_factory=list)
    unserved: list[models.ScriptedUserStep] = field(default_factory=list)
    final_phase: str | None = None
    message: str = ""
    sut_returncode: int | None = None


# ---------- Reply resolution --------------------------------------------


def resolve_reply(step: models.ScriptedUserStep, case_dir: str | os.PathLike[str]) -> str:
    """Read the literal reply text for a step.

    For inline replies this is the ``reply`` field verbatim. For
    file-backed replies this reads the file (UTF-8) at
    ``<case_dir>/<reply_file>``. Raises ``FileNotFoundError`` if the
    file is missing — the loader pre-validates existence at parse time
    but the file may have been deleted between parse and dispatch.
    """
    if step.reply is not None:
        return step.reply
    if step.reply_file is None:
        raise ValueError(f"step has neither reply nor reply_file: {step}")
    path = Path(case_dir) / step.reply_file
    return path.read_text(encoding="utf-8")


# ---------- Pure driver --------------------------------------------------


class ScriptedUserDriver:
    """Pure dispatch loop. No subprocess, no filesystem polling.

    Args:
        schedule: Ordered list of scripted-user steps to serve.
        state_reader: Zero-arg callable returning the SUT's current
            state dict, or ``None`` if the state file is not yet
            written. The driver polls this on every tick.
        reply_writer: One-arg callable that delivers a resolved reply
            string to the SUT (typically writes to its stdin).
        case_dir: Absolute path used to resolve ``reply_file`` entries.
        sleep: Sleep function (defaults to :func:`time.sleep`); tests
            inject a fake to accelerate polling.
        clock: Monotonic clock function (defaults to
            :func:`time.monotonic`); tests inject a deterministic clock.
        poll_interval: Seconds between state reads.
        deadline_seconds: Hard upper bound on the run; ``None`` for no
            deadline. Cases with long judge-tier work need at least
            5–10 minutes.
        liveness_check: Optional zero-arg callable returning ``None`` while
            the SUT is still running, or its integer return code once it
            has exited. When set, the driver short-circuits with status
            ``sut-exited`` if the SUT dies while the schedule still has
            unserved entries — useful for the subprocess wiring to fail
            fast instead of polling until the deadline expires.
    """

    def __init__(
        self,
        schedule: list[models.ScriptedUserStep],
        *,
        state_reader: Callable[[], dict[str, Any] | None],
        reply_writer: Callable[[str], None],
        case_dir: str | os.PathLike[str],
        sleep: Callable[[float], None] = time.sleep,
        clock: Callable[[], float] = time.monotonic,
        poll_interval: float = 0.5,
        deadline_seconds: float | None = 600.0,
        liveness_check: Callable[[], int | None] | None = None,
    ) -> None:
        self._schedule: list[models.ScriptedUserStep] = list(schedule)
        self._state_reader = state_reader
        self._reply_writer = reply_writer
        self._case_dir = str(case_dir)
        self._sleep = sleep
        self._clock = clock
        self._poll_interval = float(poll_interval)
        self._deadline = float(deadline_seconds) if deadline_seconds is not None else None
        self._liveness_check = liveness_check
        self._served: list[ServedReply] = []
        self._last_signature: tuple[str, str] | None = None

    # -- public API --

    def run(self) -> DriverResult:
        start = self._clock()
        last_phase: str | None = None
        while True:
            if self._deadline is not None and (self._clock() - start) > self._deadline:
                return DriverResult(
                    status="timeout",
                    served=list(self._served),
                    unserved=list(self._schedule),
                    final_phase=last_phase,
                    message=f"deadline ({self._deadline}s) exceeded",
                )
            if self._liveness_check is not None:
                rc = self._liveness_check()
                if rc is not None and self._schedule:
                    return DriverResult(
                        status="sut-exited",
                        served=list(self._served),
                        unserved=list(self._schedule),
                        final_phase=last_phase,
                        message=(
                            f"SUT exited (rc={rc}) before schedule was drained "
                            f"({len(self._schedule)} replies still queued)"
                        ),
                        sut_returncode=rc,
                    )
            state = self._state_reader()
            if state is not None:
                phase = str(state.get("phase") or "") or None
                last_phase = phase
                if _is_terminal(phase):
                    return DriverResult(
                        status="terminal",
                        served=list(self._served),
                        unserved=list(self._schedule),
                        final_phase=phase,
                    )
                if _is_park(phase):
                    sig = _park_signature(state)
                    if sig != self._last_signature:
                        # Newly-entered park; try to serve.
                        result = self._serve_one(phase, sig)
                        if result is not None:
                            return result
            self._sleep(self._poll_interval)

    # -- internals --

    def _serve_one(self, phase: str, sig: tuple[str, str]) -> DriverResult | None:
        """Serve the next schedule entry against an observed park.

        Returns a DriverResult to short-circuit the run (mismatch or
        exhaustion); returns ``None`` to continue polling.
        """
        if not self._schedule:
            return DriverResult(
                status="exhausted",
                served=list(self._served),
                unserved=[],
                final_phase=phase,
                message=f"SUT parked at {phase!r} but schedule is empty",
            )
        head = self._schedule[0]
        if head.on_phase != phase:
            return DriverResult(
                status="schedule-mismatch",
                served=list(self._served),
                unserved=list(self._schedule),
                final_phase=phase,
                message=(
                    f"SUT parked at {phase!r} but next scheduled reply targets "
                    f"{head.on_phase!r}"
                ),
            )
        text = resolve_reply(head, self._case_dir)
        self._reply_writer(text)
        self._served.append(
            ServedReply(
                on_phase=head.on_phase,
                reply_preview=text[:80].replace("\n", " "),
                served_at=self._clock(),
            )
        )
        self._schedule.pop(0)
        self._last_signature = sig
        return None


# ---------- State-file reader -------------------------------------------


def find_state_file(workspace_root: str | os.PathLike[str], glob: str) -> Path | None:
    """Return the most recently modified file matching ``glob`` under
    ``workspace_root``, or ``None`` if no match exists yet.
    """
    root = Path(workspace_root)
    if not root.exists():
        return None
    matches = sorted(root.glob(glob), key=lambda p: p.stat().st_mtime, reverse=True)
    return matches[0] if matches else None


def make_file_state_reader(
    workspace_root: str | os.PathLike[str],
    state_glob: str = ".spec-author/sessions/*/state.json",
) -> Callable[[], dict[str, Any] | None]:
    """Build a state-reader closure for the file-system-backed SUT.

    The closure resolves the active session state file lazily on each
    call (the SUT may not have created it yet on the first poll) and
    tolerates partial writes by swallowing :class:`json.JSONDecodeError`
    and returning the previously-seen state.
    """
    last_good: dict[str, Any] | None = None

    def _read() -> dict[str, Any] | None:
        nonlocal last_good
        path = find_state_file(workspace_root, state_glob)
        if path is None:
            return last_good
        try:
            with open(path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
        except (OSError, json.JSONDecodeError):
            return last_good
        if isinstance(data, dict):
            last_good = data
        return last_good

    return _read


# ---------- Subprocess wiring -------------------------------------------


def run_with_subprocess(
    *,
    case: models.CaseSpec,
    workspace_root: str | os.PathLike[str],
    initial_prompt: str,
    copilot_bin: str = "copilot",
    pack: str | None = None,
    run_id: str | None = None,
    state_glob: str = ".spec-author/sessions/*/state.json",
    poll_interval: float = 0.5,
    deadline_seconds: float | None = 600.0,
    log_stream: Any | None = None,
    submit_sequence: str = "\n",
    use_pty: bool = False,
) -> tuple[DriverResult, int]:
    """Spawn a real Copilot CLI subprocess and drive it.

    This is the production capture path used by the ``drive``
    subcommand. It is **not** exercised by unit tests — the unit tests
    cover :class:`ScriptedUserDriver` directly with fakes. End-to-end
    fixture capture is the integration story this function exists for.

    The wire-protocol assumption is **newline-terminated text on stdin =
    user submit gesture**. This is the engineer's best guess given how
    most line-oriented REPLs work; it has not been validated against the
    real Copilot CLI. ``submit_sequence`` lets operators override the
    terminator (e.g. ``"\\n\\n"``) once diagnostics establish the actual
    gesture; ``use_pty`` is a forward-looking flag for the eventual PTY
    fallback (Unix only via :mod:`pty`; Windows requires ``pywinpty``
    which is not yet a runtime dependency, so ``use_pty=True`` raises
    :class:`NotImplementedError` on Windows for now).

    Returns the :class:`DriverResult` plus the subprocess exit code.
    """
    if shutil.which(copilot_bin) is None:
        raise FileNotFoundError(
            f"copilot binary not found on PATH (looked for {copilot_bin!r})"
        )
    if use_pty:
        if sys.platform == "win32":
            raise NotImplementedError(
                "use_pty=True is not yet supported on Windows; the stdlib "
                "`pty` module is Unix-only and the harness does not depend "
                "on `pywinpty`. Run on Linux/macOS or leave use_pty=False "
                "(pipe stdin) for now."
            )
    cmd: list[str] = [copilot_bin]
    if pack:
        cmd += ["--agent", pack]
    if run_id:
        cmd += ["--name", run_id]
    cmd += ["--allow-all-tools", "--allow-all-paths"]
    log = log_stream if log_stream is not None else sys.stderr
    print(f"scripted-user: launching {' '.join(cmd)}", file=log)

    if use_pty:
        # Unix-only: give the SUT a real TTY in case it uses isatty()
        # to gate interactive mode. The master fd stays in this
        # process; we write replies through it.
        import pty
        master_fd, slave_fd = pty.openpty()
        proc = subprocess.Popen(
            cmd,
            cwd=str(workspace_root),
            stdin=slave_fd,
            stdout=slave_fd,
            stderr=slave_fd,
            close_fds=True,
        )
        os.close(slave_fd)

        def _drain() -> None:
            while True:
                try:
                    chunk = os.read(master_fd, 4096)
                except OSError:
                    return
                if not chunk:
                    return
                try:
                    log.write(chunk.decode("utf-8", errors="replace"))
                    log.flush()
                except Exception:  # pragma: no cover - best-effort
                    pass

        def _write_bytes(payload: str) -> None:
            os.write(master_fd, payload.encode("utf-8"))

        def _close_input() -> None:
            try:
                os.close(master_fd)
            except OSError:
                pass
    else:
        proc = subprocess.Popen(
            cmd,
            cwd=str(workspace_root),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            bufsize=1,
            text=True,
            encoding="utf-8",
        )

        def _drain() -> None:
            assert proc.stdout is not None
            for line in proc.stdout:
                log.write(line)
                log.flush()

        def _write_bytes(payload: str) -> None:
            assert proc.stdin is not None
            proc.stdin.write(payload)
            proc.stdin.flush()

        def _close_input() -> None:
            try:
                assert proc.stdin is not None
                proc.stdin.close()
            except Exception:  # pragma: no cover - best-effort
                pass

    drain_thread = threading.Thread(target=_drain, daemon=True)
    drain_thread.start()

    def _ensure_terminated(text: str) -> str:
        return text if text.endswith(submit_sequence) else text + submit_sequence

    initial_payload = _ensure_terminated(initial_prompt)
    print(
        f"scripted-user: writing initial prompt ({len(initial_payload)}B, "
        f"preview: {initial_payload[:60]!r})",
        file=log,
    )
    _write_bytes(initial_payload)

    def _writer(text: str) -> None:
        payload = _ensure_terminated(text)
        print(
            f"scripted-user: writing reply ({len(payload)}B, "
            f"preview: {payload[:60]!r})",
            file=log,
        )
        _write_bytes(payload)

    driver = ScriptedUserDriver(
        schedule=case.scripted_user,
        state_reader=make_file_state_reader(workspace_root, state_glob),
        reply_writer=_writer,
        case_dir=case.case_dir,
        poll_interval=poll_interval,
        deadline_seconds=deadline_seconds,
        liveness_check=proc.poll,
    )
    try:
        result = driver.run()
    finally:
        # Close stdin to let the SUT exit; give it a bounded grace period.
        _close_input()
    try:
        rc = proc.wait(timeout=60)
    except subprocess.TimeoutExpired:
        proc.kill()
        rc = proc.wait()
    drain_thread.join(timeout=5)
    return result, rc

"""Pluggable system-under-test (SUT) runner interface.

A *runner* knows how to drive one kind of agent runtime non-interactively
inside a workspace and return a normalised :class:`RunResult`. The Copilot
CLI runner is the first concrete implementation
(:mod:`evalpilot.runners.copilot`); the abstraction exists so other
runtimes (a different CLI, an HTTP agent, a mock for self-tests) can be
plugged in later without touching the workspace or the fixtures.

Selection is by name via :func:`get_runner`, overridable with the
``EVALPILOT_RUNNER`` environment variable so a whole suite can be retargeted
(e.g. to a record/replay mock) without editing tests.
"""

from __future__ import annotations

import abc
import dataclasses
import os
from pathlib import Path
from typing import Optional, Sequence


@dataclasses.dataclass(frozen=True)
class RunResult:
    """Normalised outcome of a single SUT invocation.

    Concrete runners populate the core fields; runtime-specific extras (e.g.
    a Windows crash descriptor) go in :attr:`extra`.
    """

    returncode: int
    stdout: str
    stderr: str
    duration_seconds: float
    log_path: Path
    timed_out: bool = False
    skipped: bool = False
    extra: dict = dataclasses.field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return self.returncode == 0

    @property
    def usable(self) -> bool:
        """True when the run produced real SUT output (not skipped/timed-out)."""
        return not (self.skipped or self.timed_out)

    def unavailable_reason(self) -> str:
        """One-line reason a behavioural test should ``pytest.skip``, or ``""``."""
        if self.skipped:
            return (
                "SUT not launched (EVALPILOT_SKIP_SUT set); this environment "
                f"cannot run the live SUT within budget. See {self.log_path}."
            )
        if self.timed_out:
            return (
                "SUT did not complete within its (capped) wall-clock timeout "
                f"in this environment. See {self.log_path}."
            )
        return ""


class SUTUnavailable(RuntimeError):
    """Raised when a runner's backend is not installed/usable."""


class SUTRunner(abc.ABC):
    """Drives one agent runtime non-interactively inside a workspace."""

    #: Short stable identifier used by :func:`get_runner` / ``EVALPILOT_RUNNER``.
    name: str = "base"

    @abc.abstractmethod
    def available(self) -> bool:
        """Return True when this runner can actually execute (binary present)."""

    @abc.abstractmethod
    def run_agent(
        self,
        *,
        prompt: str,
        workspace: Path,
        agent: Optional[str],
        log_path: Path,
        timeout: float,
        extra_args: Sequence[str] = (),
    ) -> RunResult:
        """Run a named agent (or the host default) against ``prompt``."""

    @abc.abstractmethod
    def run_skill(
        self,
        *,
        skill: str,
        prompt: str,
        workspace: Path,
        log_path: Path,
        timeout: float,
        extra_args: Sequence[str] = (),
    ) -> RunResult:
        """Exercise a single skill in isolation against ``prompt``."""


_REGISTRY: dict[str, "type[SUTRunner]"] = {}


def register_runner(cls: "type[SUTRunner]") -> "type[SUTRunner]":
    """Class decorator registering a runner under its ``name``."""
    _REGISTRY[cls.name] = cls
    return cls


def get_runner(name: Optional[str] = None) -> SUTRunner:
    """Return a runner instance.

    Resolution: explicit ``name`` > ``EVALPILOT_RUNNER`` env > ``"copilot"``.
    """
    # Import side-effect registers the built-in copilot runner.
    from . import copilot as _copilot  # noqa: F401

    chosen = name or os.environ.get("EVALPILOT_RUNNER") or "copilot"
    try:
        return _REGISTRY[chosen]()
    except KeyError:
        available = ", ".join(sorted(_REGISTRY)) or "(none)"
        raise LookupError(
            f"Unknown SUT runner {chosen!r}. Registered: {available}"
        )


__all__ = [
    "RunResult",
    "SUTRunner",
    "SUTUnavailable",
    "register_runner",
    "get_runner",
]

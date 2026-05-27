"""Shared assertion helpers for evals.

The plain `assert needle in text` pattern is fragile against agent output
that hard-wraps prose at column 72/80: a sentence the test expects
verbatim ends up split across multiple lines by inserted newlines and the
substring match fails. The bait phrases in spec-author update-mode tests
are the canonical example.

:func:`assert_prose_contains` normalises whitespace (collapsing all runs
of whitespace to a single space) before comparing, so wrapping-induced
newlines don't break the match. Use this for **prose** assertions (free
sentences, bait phrases, persona descriptions). Do NOT use it for
**structural** assertions where exact formatting matters: heading
anchors (``## Status``), fenced-block markers, ``Status: draft`` field
literals, ``[Deprecated]`` markers, ``FR-07`` ids. Those should stay
on plain ``in`` against the raw text.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional, Union


def _normalise(text: str) -> str:
    """Collapse all whitespace runs to single spaces."""
    return " ".join(text.split())


def assert_prose_contains(
    text: str,
    needle: str,
    *,
    log_path: Optional[Union[str, Path]] = None,
    extra: str = "",
) -> None:
    """Assert ``needle`` appears in ``text`` after whitespace normalisation.

    Parameters
    ----------
    text:
        Full agent output (or file content) to search.
    needle:
        Prose substring expected to appear. May contain spaces; will be
        normalised the same way as ``text`` before comparison.
    log_path:
        Path to the agent log to mention in the failure message; if the
        assertion fires the human reader will want to see what the agent
        actually emitted.
    extra:
        Optional extra context (a rule reference, a fixture name) prepended
        to the failure message.

    Notes
    -----
    Whitespace normalisation collapses newlines, tabs, and runs of spaces
    to a single space, so the assertion matches whether the agent emits
    the phrase on one line or wraps it across several.
    """
    norm_text = _normalise(text)
    norm_needle = _normalise(needle)
    if norm_needle in norm_text:
        return
    prefix = f"{extra}\n" if extra else ""
    log_hint = f"\n  log: {log_path}" if log_path else ""
    raise AssertionError(
        f"{prefix}prose substring not found (after whitespace normalisation):"
        f"\n  needle: {norm_needle!r}{log_hint}"
    )


__all__ = ["assert_prose_contains", "assert_prose_not_contains"]


def assert_prose_not_contains(
    text: str,
    needle: str,
    *,
    log_path: Optional[Union[str, Path]] = None,
    extra: str = "",
) -> None:
    """Mirror of :func:`assert_prose_contains` for the negative case.

    Asserts that ``needle`` is NOT present in ``text`` after whitespace
    normalisation. Use this for prose phrases that MUST NOT appear in
    agent output (e.g. polished rewrites of bait sentences, boilerplate
    that should have been suppressed).
    """
    norm_text = _normalise(text)
    norm_needle = _normalise(needle)
    if norm_needle not in norm_text:
        return
    prefix = f"{extra}\n" if extra else ""
    log_hint = f"\n  log: {log_path}" if log_path else ""
    raise AssertionError(
        f"{prefix}prose substring unexpectedly present "
        f"(after whitespace normalisation):"
        f"\n  needle: {norm_needle!r}{log_hint}"
    )

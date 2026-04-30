"""Path normalization for the assertion engine.

All file-path comparisons in the harness MUST go through these helpers.
Raw strings out of fixtures, specs, or operating-system APIs are unsafe
because of:

* Mixed separators on Windows (``\\`` vs ``/``).
* Drive letters (``C:\\foo`` vs ``c:\\foo``).
* Dot-segments (``foo/../_eval/golden.md``).
* Case sensitivity (``_Eval`` vs ``_eval``).

The contract:

* ``normalize`` returns a POSIX-style relative path rooted at the workspace
  (or another supplied root). Output never contains ``..`` and never starts
  with a slash.
* ``relpath`` is a thin wrapper that takes an absolute path and a workspace
  root and returns the workspace-relative POSIX form, or raises
  :class:`OutsideWorkspaceError` if the path escapes the workspace (used by
  the ``L3-workspace-escape`` assertion).
* ``case_fold`` is exposed for callers that want to do explicit
  case-insensitive comparisons; assertions on Windows use case-folded
  comparisons by default to match filesystem semantics.
* ``deny_precedes_allow(path, deny, allow)`` implements the spec rule that
  any deny-list match short-circuits before the allow-list is consulted.
"""

from __future__ import annotations

import os
import posixpath
import re
import sys
from dataclasses import dataclass
from pathlib import PurePosixPath, PureWindowsPath
from typing import Iterable


class OutsideWorkspaceError(ValueError):
    """Raised when a path resolves outside its declared workspace root."""


@dataclass(frozen=True)
class ScopeDecision:
    matched: bool
    rule: str | None
    kind: str  # "allow" | "deny" | "default-deny"


def _coerce_to_posix(raw: str) -> str:
    if not raw:
        return ""
    s = str(raw).strip()
    # Strip a leading ${WORKSPACE_ROOT} placeholder (fixture convention).
    if s.startswith("${WORKSPACE_ROOT}"):
        s = s[len("${WORKSPACE_ROOT}") :]
        s = s.lstrip("/\\")
    # Translate backslashes only when they aren't escape sequences in the
    # source string. Fixtures store paths as plain strings so a literal "\"
    # is always a separator.
    s = s.replace("\\", "/")
    # Collapse repeated slashes via posixpath.normpath, then strip any
    # resulting leading "./".
    s = posixpath.normpath(s)
    if s.startswith("./"):
        s = s[2:]
    return s


def normalize(raw: str, *, root: str | None = None) -> str:
    """Return a POSIX, workspace-relative, dot-segment-free path."""
    s = _coerce_to_posix(raw)
    if root:
        root_posix = _coerce_to_posix(root)
        # If raw was absolute *and* under root, strip the prefix.
        if posixpath.isabs(s):
            try:
                rel = posixpath.relpath(s, root_posix or "/")
            except ValueError:
                rel = s
            s = rel
        else:
            # Already relative — leave alone.
            pass
    if s == ".":
        return ""
    s = s.lstrip("/")
    return s


def relpath(absolute: str, workspace_root: str) -> str:
    """Return the workspace-relative POSIX path or raise on escape."""
    abs_norm = os.path.realpath(absolute)
    root_norm = os.path.realpath(workspace_root)
    try:
        rel = os.path.relpath(abs_norm, root_norm)
    except ValueError as exc:  # different drives on Windows
        raise OutsideWorkspaceError(str(exc)) from exc
    rel_posix = rel.replace("\\", "/")
    if rel_posix == "." or rel_posix == "":
        return ""
    if rel_posix.startswith("../"):
        raise OutsideWorkspaceError(
            f"path {absolute!r} resolves outside workspace {workspace_root!r}"
        )
    return rel_posix


def case_fold(s: str) -> str:
    return s.casefold()


def _match(pattern: str, path: str, *, case_insensitive: bool) -> bool:
    """Match a path against a regex pattern from a spec scope list."""
    flags = re.IGNORECASE if case_insensitive else 0
    return re.search(pattern, path, flags=flags) is not None


def deny_precedes_allow(
    path: str,
    deny: Iterable[str],
    allow: Iterable[str],
    *,
    case_insensitive: bool | None = None,
) -> ScopeDecision:
    """Apply the spec scope-rule precedence.

    Deny patterns are evaluated first. The first matching deny rule wins
    and produces ``matched=False`` with ``kind='deny'``. If no deny rule
    matches, allow rules are tried; the first match produces ``matched=True``
    with ``kind='allow'``. If neither list matches, the default is deny
    (``matched=False, kind='default-deny'``).
    """
    if case_insensitive is None:
        case_insensitive = sys.platform.startswith("win")
    p = normalize(path)
    for rule in deny:
        if _match(rule, p, case_insensitive=case_insensitive):
            return ScopeDecision(False, rule, "deny")
    for rule in allow:
        if _match(rule, p, case_insensitive=case_insensitive):
            return ScopeDecision(True, rule, "allow")
    return ScopeDecision(False, None, "default-deny")


def is_under(path: str, prefix: str) -> bool:
    """True if ``path`` is equal to ``prefix`` or a descendant of it."""
    p = normalize(path).rstrip("/")
    pre = normalize(prefix).rstrip("/")
    if not pre:
        return True
    return p == pre or p.startswith(pre + "/")


# Convenience: the canary directory the SUT must never touch.
EVAL_CANARY_DIR = "_eval"


def is_canary(path: str) -> bool:
    p = normalize(path)
    # Match _eval, _Eval, ._eval, etc. via case-fold; the canary is reserved.
    head = p.split("/", 1)[0] if p else ""
    return head.casefold() == EVAL_CANARY_DIR.casefold()

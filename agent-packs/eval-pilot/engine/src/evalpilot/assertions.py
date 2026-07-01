"""Extensible assertion library (the ``## Assert`` vocabulary).

Every assertion is a small function registered under a ``kind`` string. The
Markdown loader and the Python builder both emit :class:`~evalpilot.spec.AssertionSpec`
objects naming a ``kind`` plus ``args``; the executor calls :func:`run_assertion`
to evaluate each one against an :class:`AssertContext` and get back a
:class:`~evalpilot.model.AssertionResult`.

New assertion kinds register with the :func:`assertion` decorator, so the
framework can express *any* eval without engine changes. The ``custom`` kind
is the ultimate escape hatch: it runs an arbitrary Python predicate supplied
by the fluent builder.

Built-in kinds::

    file_exists     path | paths                 at least one match per pattern
    file_absent     path | paths                 zero matches
    glob_count      pattern, [min|max|equals]    number of matches in range
    contains        [path], text|any|all, [ignore_case]
    not_contains    [path], text
    prose_contains  [path], text|any|all         whitespace-normalised
    matches         [path], pattern, [flags]     regex search
    json_path       path, query, [equals|exists] dotted lookup into JSON
    json_empty      path, query                  value missing/null/empty
    section_contains    [path], section, text|any|all   scoped to a heading
    section_not_contains [path], section, text           no leak into heading
    stdout_contains text|any|all, [ignore_case]  against SUT stdout
    custom          (predicate supplied in code)
"""

from __future__ import annotations

import dataclasses
import json
import re
from pathlib import Path
from typing import Callable, Optional

from .asserts import _normalise
from .model import AssertionResult
from .spec import AssertionSpec


@dataclasses.dataclass
class AssertContext:
    """Everything an assertion needs to inspect an eval's outcome."""

    root: Path                 # workspace root
    stdout: str = ""
    stderr: str = ""

    # ---- text/file helpers ---------------------------------------------

    def glob(self, pattern: str) -> list[Path]:
        return sorted(self.root.glob(pattern))

    def read(self, pattern_or_path: str) -> Optional[str]:
        """Read the first file matching a path/glob (or None if no match)."""
        p = self.root / pattern_or_path
        if p.is_file():
            return p.read_text(encoding="utf-8", errors="replace")
        matches = [m for m in self.glob(pattern_or_path) if m.is_file()]
        if matches:
            return matches[0].read_text(encoding="utf-8", errors="replace")
        return None


AssertionFn = Callable[[AssertContext, dict], AssertionResult]

_REGISTRY: dict[str, AssertionFn] = {}
_HELP: dict[str, str] = {}


def assertion(kind: str, help: str = "") -> Callable[[AssertionFn], AssertionFn]:
    """Register ``fn`` as the checker for ``kind``."""

    def _wrap(fn: AssertionFn) -> AssertionFn:
        _REGISTRY[kind] = fn
        _HELP[kind] = help
        return fn

    return _wrap


def available_kinds() -> list[str]:
    return sorted(_REGISTRY)


def help_for(kind: str) -> str:
    return _HELP.get(kind, "")


def run_assertion(spec: AssertionSpec, ctx: AssertContext) -> AssertionResult:
    """Evaluate one :class:`AssertionSpec` against ``ctx``."""
    if spec.kind == "custom":
        return _run_custom(spec, ctx)
    fn = _REGISTRY.get(spec.kind)
    if fn is None:
        return AssertionResult(
            kind=spec.kind,
            name=spec.name or spec.kind,
            passed=False,
            detail=f"unknown assertion kind {spec.kind!r}; "
            f"known: {', '.join(available_kinds())}",
        )
    res = fn(ctx, dict(spec.args))
    if spec.name:
        res.name = spec.name
    return res


# ---- helpers ------------------------------------------------------------


def _as_list(value) -> list[str]:
    if value is None:
        return []
    if isinstance(value, (list, tuple)):
        return [str(v) for v in value]
    return [str(value)]


def _source_text(ctx: AssertContext, args: dict) -> tuple[Optional[str], str]:
    """Return (text, label) for the file at ``args['path']`` or stdout."""
    path = args.get("path") or args.get("file")
    if path:
        text = ctx.read(str(path))
        return text, str(path)
    return ctx.stdout, "stdout"


def _needles(args: dict) -> tuple[list[str], str]:
    """Return (needles, mode) where mode is 'all' or 'any'."""
    if "any" in args:
        return _as_list(args["any"]), "any"
    if "all" in args:
        return _as_list(args["all"]), "all"
    return _as_list(args.get("text")), "all"


# ---- built-in assertions ------------------------------------------------


@assertion("file_exists", "path|paths: at least one match per pattern")
def _file_exists(ctx: AssertContext, args: dict) -> AssertionResult:
    patterns = _as_list(args.get("path")) + _as_list(args.get("paths"))
    missing = [p for p in patterns if not ctx.glob(p)]
    name = "file exists: " + ", ".join(patterns) if patterns else "file exists"
    return AssertionResult(
        kind="file_exists",
        name=name,
        passed=not missing,
        detail="" if not missing else f"missing: {', '.join(missing)}",
        data={"patterns": patterns, "missing": missing},
    )


@assertion("file_absent", "path|paths: zero matches")
def _file_absent(ctx: AssertContext, args: dict) -> AssertionResult:
    patterns = _as_list(args.get("path")) + _as_list(args.get("paths"))
    present = {
        p: [str(m.relative_to(ctx.root)) for m in ctx.glob(p)]
        for p in patterns
    }
    offenders = {p: hits for p, hits in present.items() if hits}
    name = "file absent: " + ", ".join(patterns) if patterns else "file absent"
    return AssertionResult(
        kind="file_absent",
        name=name,
        passed=not offenders,
        detail="" if not offenders else f"unexpected: {offenders}",
        data={"patterns": patterns, "offenders": offenders},
    )


@assertion("glob_count", "pattern, [min|max|equals]: match count in range")
def _glob_count(ctx: AssertContext, args: dict) -> AssertionResult:
    pattern = str(args.get("pattern", "**/*"))
    n = len(ctx.glob(pattern))
    lo = args.get("min")
    hi = args.get("max")
    eq = args.get("equals")
    ok = True
    if eq is not None:
        ok = n == int(eq)
    if lo is not None:
        ok = ok and n >= int(lo)
    if hi is not None:
        ok = ok and n <= int(hi)
    bounds = []
    if eq is not None:
        bounds.append(f"=={eq}")
    if lo is not None:
        bounds.append(f">={lo}")
    if hi is not None:
        bounds.append(f"<={hi}")
    return AssertionResult(
        kind="glob_count",
        name=f"glob count {pattern} {' '.join(bounds)}".strip(),
        passed=ok,
        detail=f"found {n}",
        data={"pattern": pattern, "count": n},
    )


def _contains_impl(ctx, args, *, negate: bool, prose: bool, kind: str,
                   force_stdout: bool = False) -> AssertionResult:
    if force_stdout:
        text, label = ctx.stdout, "stdout"
    else:
        text, label = _source_text(ctx, args)
    needles, mode = _needles(args)
    ignore_case = bool(args.get("ignore_case"))

    if text is None:
        return AssertionResult(
            kind=kind, name=f"{kind}: {label}", passed=False,
            detail=f"source not found: {label}",
        )

    def _present(needle: str) -> bool:
        hay = _normalise(text) if prose else text
        ndl = _normalise(needle) if prose else needle
        if ignore_case:
            hay, ndl = hay.lower(), ndl.lower()
        return ndl in hay

    hits = {n: _present(n) for n in needles}
    if negate:
        passed = not any(hits.values())
        offenders = [n for n, present in hits.items() if present]
        detail = "" if passed else f"unexpectedly present in {label}: {offenders}"
    elif mode == "any":
        passed = any(hits.values())
        detail = "" if passed else f"none present in {label}: {needles}"
    else:
        missing = [n for n, present in hits.items() if not present]
        passed = not missing
        detail = "" if passed else f"missing in {label}: {missing}"

    return AssertionResult(
        kind=kind,
        name=f"{kind}: {label}",
        passed=passed,
        detail=detail,
        data={"label": label, "needles": needles, "mode": mode},
    )


@assertion("contains", "[path], text|any|all, [ignore_case]")
def _contains(ctx, args):
    return _contains_impl(ctx, args, negate=False, prose=False, kind="contains")


@assertion("not_contains", "[path], text")
def _not_contains(ctx, args):
    return _contains_impl(ctx, args, negate=True, prose=False, kind="not_contains")


@assertion("prose_contains", "[path], text|any|all (whitespace-normalised)")
def _prose_contains(ctx, args):
    return _contains_impl(ctx, args, negate=False, prose=True, kind="prose_contains")


@assertion("stdout_contains", "text|any|all, [ignore_case]")
def _stdout_contains(ctx, args):
    return _contains_impl(ctx, args, negate=False, prose=False,
                          kind="stdout_contains", force_stdout=True)


@assertion("matches", "[path], pattern (regex), [flags]")
def _matches(ctx, args):
    text, label = _source_text(ctx, args)
    pattern = str(args.get("pattern", ""))
    flags = 0
    flag_str = str(args.get("flags", "")).lower()
    if "i" in flag_str:
        flags |= re.IGNORECASE
    if "m" in flag_str:
        flags |= re.MULTILINE
    if "s" in flag_str:
        flags |= re.DOTALL
    if text is None:
        return AssertionResult(kind="matches", name=f"matches: {label}",
                               passed=False, detail=f"source not found: {label}")
    ok = re.search(pattern, text, flags) is not None
    return AssertionResult(
        kind="matches",
        name=f"matches /{pattern}/ in {label}",
        passed=ok,
        detail="" if ok else f"pattern not found in {label}",
        data={"pattern": pattern, "label": label},
    )


def _dig(obj, query: str):
    cur = obj
    for part in [p for p in re.split(r"[.\[\]]", query) if p != ""]:
        if isinstance(cur, list):
            cur = cur[int(part)]
        elif isinstance(cur, dict):
            cur = cur[part]
        else:
            raise KeyError(part)
    return cur


@assertion("json_path", "path, query (dotted), [equals|exists]")
def _json_path(ctx, args):
    path = str(args.get("path", ""))
    query = str(args.get("query", ""))
    text = ctx.read(path)
    if text is None:
        return AssertionResult(kind="json_path", name=f"json_path {path}",
                               passed=False, detail=f"file not found: {path}")
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        return AssertionResult(kind="json_path", name=f"json_path {path}",
                               passed=False, detail=f"invalid JSON: {exc}")
    try:
        value = _dig(data, query)
    except (KeyError, IndexError, ValueError):
        found = False
        value = None
    else:
        found = True

    if "exists" in args:
        want = bool(args["exists"])
        passed = found == want
        detail = "" if passed else f"exists={found}, wanted {want}"
    elif "equals" in args:
        passed = found and value == args["equals"]
        detail = "" if passed else f"got {value!r}, wanted {args['equals']!r}"
    else:
        passed = found
        detail = "" if passed else f"path {query!r} not found"
    return AssertionResult(
        kind="json_path",
        name=f"json_path {path}:{query}",
        passed=passed,
        detail=detail,
        data={"path": path, "query": query, "value": value},
    )


@assertion("json_empty", "path, query (dotted): value is missing, null, or empty")
def _json_empty(ctx, args):
    path = str(args.get("path", ""))
    query = str(args.get("query", ""))
    text = ctx.read(path)
    if text is None:
        return AssertionResult(kind="json_empty", name=f"json_empty {path}",
                               passed=False, detail=f"file not found: {path}")
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        return AssertionResult(kind="json_empty", name=f"json_empty {path}",
                               passed=False, detail=f"invalid JSON: {exc}")
    try:
        value = _dig(data, query)
    except (KeyError, IndexError, ValueError):
        value, found = None, False
    else:
        found = True
    empty = (not found) or value in (None, "", [], {})
    return AssertionResult(
        kind="json_empty",
        name=f"json_empty {path}:{query}",
        passed=empty,
        detail="" if empty else f"expected empty/absent, got {value!r}",
        data={"path": path, "query": query, "value": value},
    )


def _section_body(text: str, name: str, max_chars: int) -> Optional[str]:
    """Return up to ``max_chars`` of the body under a ``## <name>`` heading."""
    pattern = re.compile(
        rf"#+\s+{re.escape(name)}\s*\n([\s\S]{{0,{max_chars}}})", re.IGNORECASE
    )
    m = pattern.search(text)
    return m.group(1) if m else None


def _section_impl(ctx, args, *, negate: bool) -> AssertionResult:
    kind = "section_not_contains" if negate else "section_contains"
    text, label = _source_text(ctx, args)
    section = str(args.get("section", ""))
    max_chars = int(args.get("max_chars", 800))
    if text is None:
        return AssertionResult(kind=kind, name=f"{kind}: {label}", passed=False,
                               detail=f"source not found: {label}")
    body = _section_body(text, section, max_chars)
    if body is None:
        # A missing section trivially contains nothing.
        passed = negate
        return AssertionResult(
            kind=kind, name=f"{kind}: {section}", passed=passed,
            detail="" if passed else f"section {section!r} not found in {label}",
        )
    needles, mode = _needles(args)
    ignore_case = bool(args.get("ignore_case"))
    hay = body.lower() if ignore_case else body
    hits = {n: ((n.lower() if ignore_case else n) in hay) for n in needles}
    if negate:
        offenders = [n for n, p in hits.items() if p]
        passed = not offenders
        detail = "" if passed else f"leaked into {section!r}: {offenders}"
    elif mode == "any":
        passed = any(hits.values())
        detail = "" if passed else f"none present in {section!r}: {needles}"
    else:
        missing = [n for n, p in hits.items() if not p]
        passed = not missing
        detail = "" if passed else f"missing in {section!r}: {missing}"
    return AssertionResult(kind=kind, name=f"{kind}: {section}", passed=passed,
                           detail=detail, data={"section": section, "needles": needles})


@assertion("section_contains", "[path], section, text|any|all, [ignore_case, max_chars]")
def _section_contains(ctx, args):
    return _section_impl(ctx, args, negate=False)


@assertion("section_not_contains", "[path], section, text, [ignore_case, max_chars]")
def _section_not_contains(ctx, args):
    return _section_impl(ctx, args, negate=True)


def _run_custom(spec: AssertionSpec, ctx: AssertContext) -> AssertionResult:
    name = spec.name or "custom"
    if spec.predicate is None:
        return AssertionResult(kind="custom", name=name, passed=False,
                               detail="custom assertion has no predicate")
    try:
        outcome = spec.predicate(ctx)
    except Exception as exc:  # noqa: BLE001 - report predicate failures as fails
        return AssertionResult(kind="custom", name=name, passed=False,
                               detail=f"predicate raised: {exc!r}")
    detail = ""
    if isinstance(outcome, tuple):
        passed, detail = bool(outcome[0]), str(outcome[1]) if len(outcome) > 1 else ""
    else:
        passed = bool(outcome)
    return AssertionResult(kind="custom", name=name, passed=passed, detail=detail)


__all__ = [
    "AssertContext",
    "assertion",
    "available_kinds",
    "help_for",
    "run_assertion",
]

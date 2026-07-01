"""Rich terminal rendering of an :class:`~evalpilot.model.EvalRunReport`.

Prints a scannable per-eval summary (status, checks, failed labels, metrics,
timing) followed by an aggregate line and the on-disk result location, so a
reader immediately knows what passed, what failed, and where to look next.
ANSI colour is used when the stream is a TTY and ``NO_COLOR`` is unset.
"""

from __future__ import annotations

import os
import sys
from typing import Optional

from ..model import ERROR, FAILED, PASSED, SKIPPED, EvalRunReport, EvalResult

_GLYPH = {PASSED: "PASS", FAILED: "FAIL", SKIPPED: "SKIP", ERROR: "ERR "}
_COLOR = {PASSED: "32", FAILED: "31", SKIPPED: "33", ERROR: "35"}


def _use_color(stream) -> bool:
    if os.environ.get("NO_COLOR") is not None:
        return False
    if os.environ.get("EVALPILOT_FORCE_COLOR"):
        return True
    return bool(getattr(stream, "isatty", lambda: False)())


_UNICODE = {"ok": "\u2713", "bad": "\u2717", "dot": "\u2022"}
_ASCII = {"ok": "+", "bad": "x", "dot": "-"}


def _glyphs(stream) -> dict:
    enc = (getattr(stream, "encoding", None) or "").lower()
    if enc in ("utf-8", "utf8", "utf-16", "utf-16-le", "utf-16-be"):
        return _UNICODE
    try:
        "".join(_UNICODE.values()).encode(enc or "ascii")
        return _UNICODE
    except (LookupError, UnicodeEncodeError):
        return _ASCII


def render_terminal(
    report: EvalRunReport,
    *,
    color: Optional[bool] = None,
    json_path: Optional[str] = None,
    html_path: Optional[str] = None,
    stream=None,
) -> str:
    stream = stream or sys.stdout
    use_color = _use_color(stream) if color is None else color
    g = _glyphs(stream)

    def c(text: str, code: str) -> str:
        return f"\033[{code}m{text}\033[0m" if use_color else text

    lines: list[str] = []
    lines.append(c("evalpilot run " + report.run_id, "1"))
    lines.append("")

    for r in report.results:
        lines.extend(_render_eval(r, c, g))

    lines.append("")
    lines.append("=" * 64)
    s = report.to_dict()["summary"]
    summary = (
        f"{c(str(s['passed']) + ' passed', _COLOR[PASSED])}, "
        f"{c(str(s['failed']) + ' failed', _COLOR[FAILED])}, "
        f"{c(str(s['skipped']) + ' skipped', _COLOR[SKIPPED])}"
    )
    if s["errored"]:
        summary += f", {c(str(s['errored']) + ' errored', _COLOR[ERROR])}"
    if s["regressions"]:
        summary += f", {c(str(s['regressions']) + ' regressions', _COLOR[FAILED])}"
    lines.append(f"Results: {summary}  ({report.duration_seconds:.1f}s)")
    if json_path:
        lines.append(f"JSON:   {json_path}")
    if html_path:
        lines.append(f"HTML:   {html_path}")
    lines.append("=" * 64)
    return "\n".join(lines)


def _render_eval(r: EvalResult, c, g) -> list[str]:
    glyph = c(_GLYPH.get(r.status, r.status.upper()), _COLOR.get(r.status, "0"))
    head = f"[{glyph}] {c(r.name, '1')}"
    if r.check_total:
        head += f"  ({r.check_passed}/{r.check_total} checks)"
    head += f"  {r.duration_seconds:.1f}s"
    out = [head]
    line = r.summary or (r.description.splitlines()[0] if r.description else "")
    if line:
        out.append(f"       {line}")

    if r.status == SKIPPED and r.skip_reason:
        out.append(c(f"       skipped: {r.skip_reason}", _COLOR[SKIPPED]))
    if r.status == ERROR and r.error:
        out.append(c(f"       error: {r.error.splitlines()[0]}", _COLOR[ERROR]))

    for a in r.assertions:
        if not a.passed:
            det = f" - {a.detail}" if a.detail else ""
            out.append(c(f"       {g['bad']} {a.name}{det}", _COLOR[FAILED]))
    for j in r.judges:
        mark = g["ok"] if j.passed else g["bad"]
        code = _COLOR[PASSED] if j.passed else _COLOR[FAILED]
        out.append(c(f"       {mark} judge[{j.name}] score={j.score:.2f} "
                     f">= {j.threshold:.2f}", code))
        if not j.passed and j.reasoning:
            out.append(f"           {j.reasoning[:200]}")
    for m in r.metrics:
        base = f"{m.baseline:.4g}" if m.baseline is not None else "-"
        flag = c(" REGRESSED", _COLOR[FAILED]) if m.regressed else ""
        gate = " (gate)" if m.gated else ""
        out.append(f"       {g['dot']} {m.name}={m.value:.4g} vs {base} "
                   f"[{m.baseline_strategy}]{gate}{flag}")
    if r.log_path and r.status in (FAILED, ERROR):
        out.append(f"       log: {r.log_path}")
    out.append("")
    return out


__all__ = ["render_terminal"]

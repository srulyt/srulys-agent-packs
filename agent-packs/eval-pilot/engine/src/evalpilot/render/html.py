"""Self-contained HTML report for an :class:`~evalpilot.model.EvalRunReport`.

Produces a single shareable ``.html`` file (inline CSS + a sprinkle of JS,
no external assets) with:

* a summary banner (pass/fail/skip/regression counts);
* one expandable card per eval — description, prompt, assertions, judge
  verdicts, and metrics;
* inline **SVG sparklines** of each metric's committed JSONL history so
  trends over time are visible at a glance.

The HTML is a pure projection of the modeled result plus the on-disk metric
history, matching the terminal and JSON views.
"""

from __future__ import annotations

import html
import json
import re
from pathlib import Path

from ..model import ERROR, FAILED, PASSED, SKIPPED, EvalResult, EvalRunReport

_STATUS_COLOR = {
    PASSED: "#1a7f37", FAILED: "#cf222e", SKIPPED: "#9a6700", ERROR: "#8250df",
}
_STATUS_BG = {
    PASSED: "#dafbe1", FAILED: "#ffebe9", SKIPPED: "#fff8c5", ERROR: "#fbefff",
}


def render_html(report: EvalRunReport) -> str:
    s = report.to_dict()["summary"]
    cards = "\n".join(_eval_card(r) for r in report.results)
    return _PAGE.format(
        run_id=html.escape(report.run_id),
        generated=html.escape(report.finished_at or report.started_at),
        duration=f"{report.duration_seconds:.1f}",
        total=s["total"], passed=s["passed"], failed=s["failed"],
        skipped=s["skipped"], errored=s["errored"], regressions=s["regressions"],
        cards=cards,
        css=_CSS, js=_JS,
    )


def _eval_card(r: EvalResult) -> str:
    color = _STATUS_COLOR.get(r.status, "#57606a")
    bg = _STATUS_BG.get(r.status, "#eaeef2")
    badge = (
        f'<span class="badge" style="color:{color};background:{bg}">'
        f'{html.escape(r.status.upper())}</span>'
    )
    meta = []
    if r.target:
        meta.append(f"{html.escape(r.kind)}: <code>{html.escape(r.target)}</code>")
    if r.check_total:
        meta.append(f"{r.check_passed}/{r.check_total} checks")
    meta.append(f"{r.duration_seconds:.1f}s")
    if r.tags:
        meta.append(" ".join(f'<span class="tag">{html.escape(t)}</span>'
                             for t in r.tags))
    meta_html = " · ".join(meta)

    body = []
    desc = r.description or r.summary
    if desc:
        paras = [p.strip() for p in re.split(r"\n\s*\n", desc) if p.strip()]
        for p in paras:
            body.append(f'<p class="desc">{html.escape(p)}</p>')
    if r.skip_reason:
        body.append(f'<p class="note">Skipped: {html.escape(r.skip_reason)}</p>')
    if r.error:
        body.append(f'<pre class="err">{html.escape(r.error.strip())}</pre>')
    if r.prompt:
        body.append(
            "<details><summary>Prompt</summary>"
            f"<pre>{html.escape(r.prompt.strip())}</pre></details>"
        )
    if r.assertions:
        body.append(_checks_table(r))
    if r.judges:
        body.append(_judges_block(r))
    if r.metrics:
        body.append(_metrics_block(r))
    if r.log_path:
        body.append(f'<p class="log">log: <code>{html.escape(r.log_path)}</code></p>')

    open_attr = " open" if r.status in (FAILED, ERROR) else ""
    subtitle = (
        f'<div class="subtitle">{html.escape(r.summary)}</div>' if r.summary else ""
    )
    return (
        f'<details class="card" data-status="{r.status}"{open_attr}>'
        f'<summary>{badge}<span class="name">{html.escape(r.name)}</span>'
        f'<span class="meta">{meta_html}</span>{subtitle}</summary>'
        f'<div class="cardbody">{"".join(body)}</div></details>'
    )


def _checks_table(r: EvalResult) -> str:
    rows = []
    for a in r.assertions:
        mark = "✓" if a.passed else "✗"
        cls = "ok" if a.passed else "bad"
        detail = html.escape(a.detail)
        rows.append(
            f'<tr class="{cls}"><td>{mark}</td>'
            f'<td>{html.escape(a.name)}</td>'
            f'<td class="k">{html.escape(a.kind)}</td>'
            f'<td>{detail}</td></tr>'
        )
    return f'<table class="checks"><tbody>{"".join(rows)}</tbody></table>'


def _judges_block(r: EvalResult) -> str:
    items = []
    for j in r.judges:
        cls = "ok" if j.passed else "bad"
        items.append(
            f'<div class="judge {cls}"><b>judge[{html.escape(j.name)}]</b> '
            f'score {j.score:.2f} / threshold {j.threshold:.2f}'
            f'<div class="reason">{html.escape(j.reasoning)}</div></div>'
        )
    return f'<div class="judges">{"".join(items)}</div>'


def _metrics_block(r: EvalResult) -> str:
    rows = []
    for m in r.metrics:
        spark = _sparkline(m.history_path)
        base = f"{m.baseline:.4g}" if m.baseline is not None else "—"
        flag = '<span class="reg">REGRESSED</span>' if m.regressed else ""
        gate = ' <span class="tag">gate</span>' if m.gated else ""
        rows.append(
            f'<tr><td>{html.escape(m.name)}{gate}</td>'
            f'<td class="num">{m.value:.4g}</td>'
            f'<td class="num">{base}</td>'
            f'<td>{html.escape(m.baseline_strategy)}</td>'
            f'<td>{spark}</td><td>{flag}</td></tr>'
        )
    header = ("<tr><th>metric</th><th>value</th><th>baseline</th>"
              "<th>strategy</th><th>trend</th><th></th></tr>")
    return (f'<table class="metrics"><thead>{header}</thead>'
            f'<tbody>{"".join(rows)}</tbody></table>')


def _sparkline(history_path) -> str:
    values = _load_values(history_path)
    if len(values) < 2:
        return '<span class="muted">—</span>'
    w, h, pad = 120, 28, 3
    lo, hi = min(values), max(values)
    span = (hi - lo) or 1.0
    n = len(values)
    pts = []
    for i, v in enumerate(values):
        x = pad + (w - 2 * pad) * (i / (n - 1))
        y = pad + (h - 2 * pad) * (1 - (v - lo) / span)
        pts.append(f"{x:.1f},{y:.1f}")
    last_x, last_y = pts[-1].split(",")
    return (
        f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
        f'class="spark" preserveAspectRatio="none">'
        f'<polyline fill="none" stroke="#0969da" stroke-width="1.5" '
        f'points="{" ".join(pts)}"/>'
        f'<circle cx="{last_x}" cy="{last_y}" r="2" fill="#0969da"/></svg>'
    )


def _load_values(history_path) -> list[float]:
    if not history_path:
        return []
    p = Path(history_path)
    if not p.exists():
        return []
    out: list[float] = []
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
            v = rec.get("value")
            if isinstance(v, (int, float)):
                out.append(float(v))
        except json.JSONDecodeError:
            continue
    return out


_CSS = """
:root { --fg:#1f2328; --muted:#57606a; --line:#d0d7de; }
* { box-sizing: border-box; }
body { font: 14px/1.5 -apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;
  color: var(--fg); margin: 0; background: #f6f8fa; }
.wrap { max-width: 960px; margin: 0 auto; padding: 24px; }
h1 { font-size: 20px; margin: 0 0 4px; }
.sub { color: var(--muted); margin: 0 0 16px; }
.cards-summary { display: flex; gap: 10px; flex-wrap: wrap; margin: 0 0 16px; }
.stat { background: #fff; border: 1px solid var(--line); border-radius: 8px;
  padding: 10px 14px; min-width: 84px; }
.stat b { display: block; font-size: 22px; }
.stat span { color: var(--muted); font-size: 12px; text-transform: uppercase; }
.filters { margin: 0 0 12px; }
.filters button { border: 1px solid var(--line); background: #fff; border-radius: 6px;
  padding: 4px 10px; cursor: pointer; margin-right: 6px; }
.filters button.active { background: #0969da; color: #fff; border-color: #0969da; }
.card { background: #fff; border: 1px solid var(--line); border-radius: 8px;
  margin: 0 0 8px; padding: 0; }
.card > summary { list-style: none; cursor: pointer; padding: 12px 14px;
  display: flex; align-items: center; gap: 10px; }
.card > summary::-webkit-details-marker { display: none; }
.badge { font-size: 11px; font-weight: 700; border-radius: 20px; padding: 2px 10px; }
.name { font-weight: 600; }
.meta { color: var(--muted); font-size: 12px; margin-left: auto; text-align: right; }
.cardbody { padding: 0 14px 14px; border-top: 1px solid var(--line); }
.desc { color: var(--muted); }
.subtitle { flex-basis: 100%; color: var(--muted); font-size: 12px; margin-top: 4px; }
.note { color: #9a6700; }
.err { background: #fbefff; padding: 8px; border-radius: 6px; overflow: auto; }
pre { background: #f6f8fa; padding: 10px; border-radius: 6px; overflow: auto;
  white-space: pre-wrap; }
table { width: 100%; border-collapse: collapse; margin: 8px 0; }
td, th { text-align: left; padding: 4px 8px; border-bottom: 1px solid var(--line);
  vertical-align: top; }
th { color: var(--muted); font-size: 12px; font-weight: 600; }
.checks td:first-child { width: 20px; }
.checks tr.ok td:first-child { color: #1a7f37; }
.checks tr.bad td:first-child { color: #cf222e; }
.checks .k { color: var(--muted); font-size: 12px; }
.num { text-align: right; font-variant-numeric: tabular-nums; }
.judge { border-left: 3px solid var(--line); padding: 4px 10px; margin: 6px 0; }
.judge.ok { border-color: #1a7f37; }
.judge.bad { border-color: #cf222e; }
.reason { color: var(--muted); font-size: 13px; }
.reg { color: #cf222e; font-weight: 700; font-size: 12px; }
.tag { background: #eaeef2; border-radius: 20px; padding: 1px 8px; font-size: 11px; }
.muted { color: var(--muted); }
.log code, code { background: #eff1f3; padding: 1px 4px; border-radius: 4px; }
"""

_JS = """
function epFilter(kind, btn) {
  document.querySelectorAll('.filters button').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  document.querySelectorAll('.card').forEach(c => {
    const st = c.getAttribute('data-status');
    const show = kind === 'all'
      || (kind === 'failed' && (st === 'failed' || st === 'error'))
      || kind === st;
    c.style.display = show ? '' : 'none';
  });
}
"""

_PAGE = """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>evalpilot report — {run_id}</title>
<style>{css}</style></head>
<body><div class="wrap">
<h1>evalpilot report</h1>
<p class="sub">run <code>{run_id}</code> · {generated} · {duration}s</p>
<div class="cards-summary">
  <div class="stat"><b>{total}</b><span>total</span></div>
  <div class="stat"><b style="color:#1a7f37">{passed}</b><span>passed</span></div>
  <div class="stat"><b style="color:#cf222e">{failed}</b><span>failed</span></div>
  <div class="stat"><b style="color:#9a6700">{skipped}</b><span>skipped</span></div>
  <div class="stat"><b style="color:#8250df">{errored}</b><span>errored</span></div>
  <div class="stat"><b style="color:#cf222e">{regressions}</b><span>regressions</span></div>
</div>
<div class="filters">
  <button class="active" onclick="epFilter('all', this)">All</button>
  <button onclick="epFilter('failed', this)">Failed</button>
  <button onclick="epFilter('passed', this)">Passed</button>
  <button onclick="epFilter('skipped', this)">Skipped</button>
</div>
{cards}
</div>
<script>{js}</script>
</body></html>
"""


__all__ = ["render_html"]

/**
 * Self-contained HTML report for an {@link EvalRunReport}.
 *
 * Produces a single shareable `.html` file (inline CSS + a sprinkle of JS, no
 * external assets) with a summary banner, one expandable card per eval, and
 * inline SVG sparklines of each metric's committed JSONL history.
 */

import { existsSync, readFileSync } from "node:fs";
import {
  ERROR,
  FAILED,
  PASSED,
  SKIPPED,
  checkPassed,
  checkTotal,
  reportErrored,
  reportFailed,
  reportPassed,
  reportRegressions,
  reportSkipped,
  reportTotal,
  type EvalResult,
  type EvalRunReport,
} from "../model.js";

const STATUS_COLOR: Record<string, string> = {
  [PASSED]: "#1a7f37",
  [FAILED]: "#cf222e",
  [SKIPPED]: "#9a6700",
  [ERROR]: "#8250df",
};
const STATUS_BG: Record<string, string> = {
  [PASSED]: "#dafbe1",
  [FAILED]: "#ffebe9",
  [SKIPPED]: "#fff8c5",
  [ERROR]: "#fbefff",
};

function esc(text: string): string {
  return String(text)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#x27;");
}

function fmt(n: number, digits = 1): string {
  return n.toFixed(digits);
}

function g4(n: number): string {
  return parseFloat(n.toPrecision(4)).toString();
}

export function renderHtml(report: EvalRunReport): string {
  const cards = report.results.map(evalCard).join("\n");
  return PAGE({
    run_id: esc(report.run_id),
    generated: esc(report.finished_at || report.started_at),
    duration: fmt(report.duration_seconds),
    total: reportTotal(report),
    passed: reportPassed(report),
    failed: reportFailed(report),
    skipped: reportSkipped(report),
    errored: reportErrored(report),
    regressions: reportRegressions(report),
    cards,
  });
}

function evalCard(r: EvalResult): string {
  const color = STATUS_COLOR[r.status] ?? "#57606a";
  const bg = STATUS_BG[r.status] ?? "#eaeef2";
  const badge =
    `<span class="badge" style="color:${color};background:${bg}">` +
    `${esc(r.status.toUpperCase())}</span>`;
  const meta: string[] = [];
  if (r.target)
    meta.push(`${esc(r.kind)}: <code>${esc(r.target)}</code>`);
  const total = checkTotal(r);
  if (total) meta.push(`${checkPassed(r)}/${total} checks`);
  meta.push(`${fmt(r.duration_seconds)}s`);
  if (r.tags.length)
    meta.push(r.tags.map((t) => `<span class="tag">${esc(t)}</span>`).join(" "));
  const metaHtml = meta.join(" · ");

  const body: string[] = [];
  const desc = r.description || r.summary;
  if (desc) {
    const paras = desc
      .split(/\n\s*\n/)
      .map((p) => p.trim())
      .filter(Boolean);
    for (const p of paras) body.push(`<p class="desc">${esc(p)}</p>`);
  }
  if (r.skip_reason)
    body.push(`<p class="note">Skipped: ${esc(r.skip_reason)}</p>`);
  if (r.error) body.push(`<pre class="err">${esc(r.error.trim())}</pre>`);
  if (r.prompt)
    body.push(
      "<details><summary>Prompt</summary>" +
        `<pre>${esc(r.prompt.trim())}</pre></details>`,
    );
  if (r.assertions.length) body.push(checksTable(r));
  if (r.judges.length) body.push(judgesBlock(r));
  if (r.metrics.length) body.push(metricsBlock(r));
  if (r.log_path)
    body.push(`<p class="log">log: <code>${esc(r.log_path)}</code></p>`);

  const openAttr = r.status === FAILED || r.status === ERROR ? " open" : "";
  const subtitle = r.summary
    ? `<div class="subtitle">${esc(r.summary)}</div>`
    : "";
  return (
    `<details class="card" data-status="${r.status}"${openAttr}>` +
    `<summary>${badge}<span class="name">${esc(r.name)}</span>` +
    `<span class="meta">${metaHtml}</span>${subtitle}</summary>` +
    `<div class="cardbody">${body.join("")}</div></details>`
  );
}

function checksTable(r: EvalResult): string {
  const rows: string[] = [];
  for (const a of r.assertions) {
    const mark = a.passed ? "✓" : "✗";
    const cls = a.passed ? "ok" : "bad";
    rows.push(
      `<tr class="${cls}"><td>${mark}</td>` +
        `<td>${esc(a.name)}</td>` +
        `<td class="k">${esc(a.kind)}</td>` +
        `<td>${esc(a.detail)}</td></tr>`,
    );
  }
  return `<table class="checks"><tbody>${rows.join("")}</tbody></table>`;
}

function judgesBlock(r: EvalResult): string {
  const items: string[] = [];
  for (const j of r.judges) {
    const cls = j.passed ? "ok" : "bad";
    items.push(
      `<div class="judge ${cls}"><b>judge[${esc(j.name)}]</b> ` +
        `score ${fmt(j.score, 2)} / threshold ${fmt(j.threshold, 2)}` +
        `<div class="reason">${esc(j.reasoning)}</div></div>`,
    );
  }
  return `<div class="judges">${items.join("")}</div>`;
}

function metricsBlock(r: EvalResult): string {
  const rows: string[] = [];
  for (const m of r.metrics) {
    const spark = sparkline(m.history_path);
    const base = m.baseline !== null ? g4(m.baseline) : "—";
    const flag = m.regressed ? '<span class="reg">REGRESSED</span>' : "";
    const gate = m.gated ? ' <span class="tag">gate</span>' : "";
    rows.push(
      `<tr><td>${esc(m.name)}${gate}</td>` +
        `<td class="num">${g4(m.value)}</td>` +
        `<td class="num">${base}</td>` +
        `<td>${esc(m.baseline_strategy)}</td>` +
        `<td>${spark}</td><td>${flag}</td></tr>`,
    );
  }
  const header =
    "<tr><th>metric</th><th>value</th><th>baseline</th>" +
    "<th>strategy</th><th>trend</th><th></th></tr>";
  return (
    `<table class="metrics"><thead>${header}</thead>` +
    `<tbody>${rows.join("")}</tbody></table>`
  );
}

function sparkline(historyPath: string | null): string {
  const values = loadValues(historyPath);
  if (values.length < 2) return '<span class="muted">—</span>';
  const w = 120;
  const h = 28;
  const pad = 3;
  const lo = Math.min(...values);
  const hi = Math.max(...values);
  const span = hi - lo || 1.0;
  const n = values.length;
  const pts: string[] = [];
  for (let i = 0; i < n; i++) {
    const x = pad + (w - 2 * pad) * (i / (n - 1));
    const y = pad + (h - 2 * pad) * (1 - (values[i]! - lo) / span);
    pts.push(`${x.toFixed(1)},${y.toFixed(1)}`);
  }
  const [lastX, lastY] = pts[pts.length - 1]!.split(",");
  return (
    `<svg width="${w}" height="${h}" viewBox="0 0 ${w} ${h}" ` +
    `class="spark" preserveAspectRatio="none">` +
    `<polyline fill="none" stroke="#0969da" stroke-width="1.5" ` +
    `points="${pts.join(" ")}"/>` +
    `<circle cx="${lastX}" cy="${lastY}" r="2" fill="#0969da"/></svg>`
  );
}

function loadValues(historyPath: string | null): number[] {
  if (!historyPath || !existsSync(historyPath)) return [];
  const out: number[] = [];
  for (const raw of readFileSync(historyPath, "utf-8").split(/\r?\n/)) {
    const line = raw.trim();
    if (!line) continue;
    try {
      const rec = JSON.parse(line);
      const v = rec.value;
      if (typeof v === "number") out.push(v);
    } catch {
      continue;
    }
  }
  return out;
}

const CSS = `
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
`;

const JS = `
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
`;

interface PageData {
  run_id: string;
  generated: string;
  duration: string;
  total: number;
  passed: number;
  failed: number;
  skipped: number;
  errored: number;
  regressions: number;
  cards: string;
}

function PAGE(d: PageData): string {
  return `<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>evalpilot report — ${d.run_id}</title>
<style>${CSS}</style></head>
<body><div class="wrap">
<h1>evalpilot report</h1>
<p class="sub">run <code>${d.run_id}</code> · ${d.generated} · ${d.duration}s</p>
<div class="cards-summary">
  <div class="stat"><b>${d.total}</b><span>total</span></div>
  <div class="stat"><b style="color:#1a7f37">${d.passed}</b><span>passed</span></div>
  <div class="stat"><b style="color:#cf222e">${d.failed}</b><span>failed</span></div>
  <div class="stat"><b style="color:#9a6700">${d.skipped}</b><span>skipped</span></div>
  <div class="stat"><b style="color:#8250df">${d.errored}</b><span>errored</span></div>
  <div class="stat"><b style="color:#cf222e">${d.regressions}</b><span>regressions</span></div>
</div>
<div class="filters">
  <button class="active" onclick="epFilter('all', this)">All</button>
  <button onclick="epFilter('failed', this)">Failed</button>
  <button onclick="epFilter('passed', this)">Passed</button>
  <button onclick="epFilter('skipped', this)">Skipped</button>
</div>
${d.cards}
</div>
<script>${JS}</script>
</body></html>
`;
}

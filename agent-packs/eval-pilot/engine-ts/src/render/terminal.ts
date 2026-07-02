/**
 * Rich terminal rendering of an {@link EvalRunReport}.
 *
 * Prints a scannable per-eval summary (status, checks, failed labels, metrics,
 * timing) followed by an aggregate line and the on-disk result location. ANSI
 * colour is used when the stream is a TTY and `NO_COLOR` is unset.
 */

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

const GLYPH: Record<string, string> = {
  [PASSED]: "PASS",
  [FAILED]: "FAIL",
  [SKIPPED]: "SKIP",
  [ERROR]: "ERR ",
};
const COLOR: Record<string, string> = {
  [PASSED]: "32",
  [FAILED]: "31",
  [SKIPPED]: "33",
  [ERROR]: "35",
};

const UNICODE = { ok: "\u2713", bad: "\u2717", dot: "\u2022" };
const ASCII = { ok: "+", bad: "x", dot: "-" };

function useColor(stream: NodeJS.WriteStream): boolean {
  if (process.env.NO_COLOR !== undefined) return false;
  if (process.env.EVALPILOT_FORCE_COLOR) return true;
  return Boolean(stream.isTTY);
}

function glyphs(): typeof UNICODE {
  const enc = "utf-8";
  void enc;
  // Node terminals are UTF-8 capable in the environments we target.
  return UNICODE;
}

type Colorize = (text: string, code: string) => string;

function fmt(n: number, digits = 1): string {
  return n.toFixed(digits);
}

function g4(n: number): string {
  // Approximates Python's "%.4g" formatting.
  return parseFloat(n.toPrecision(4)).toString();
}

export interface RenderTerminalOptions {
  color?: boolean | null;
  jsonPath?: string | null;
  htmlPath?: string | null;
  stream?: NodeJS.WriteStream;
}

export function renderTerminal(
  report: EvalRunReport,
  opts: RenderTerminalOptions = {},
): string {
  const stream = opts.stream ?? process.stdout;
  const doColor = opts.color == null ? useColor(stream) : opts.color;
  const g = glyphs();

  const c: Colorize = (text, code) =>
    doColor ? `\x1b[${code}m${text}\x1b[0m` : text;

  const lines: string[] = [];
  lines.push(c("evalpilot run " + report.run_id, "1"));
  lines.push("");

  for (const r of report.results) lines.push(...renderEval(r, c, g));

  lines.push("");
  lines.push("=".repeat(64));
  const passed = reportPassed(report);
  const failed = reportFailed(report);
  const skipped = reportSkipped(report);
  const errored = reportErrored(report);
  const regressions = reportRegressions(report);
  void reportTotal;
  let summary =
    `${c(`${passed} passed`, COLOR[PASSED]!)}, ` +
    `${c(`${failed} failed`, COLOR[FAILED]!)}, ` +
    `${c(`${skipped} skipped`, COLOR[SKIPPED]!)}`;
  if (errored) summary += `, ${c(`${errored} errored`, COLOR[ERROR]!)}`;
  if (regressions)
    summary += `, ${c(`${regressions} regressions`, COLOR[FAILED]!)}`;
  lines.push(`Results: ${summary}  (${fmt(report.duration_seconds)}s)`);
  if (opts.jsonPath) lines.push(`JSON:   ${opts.jsonPath}`);
  if (opts.htmlPath) lines.push(`HTML:   ${opts.htmlPath}`);
  lines.push("=".repeat(64));
  return lines.join("\n");
}

function renderEval(
  r: EvalResult,
  c: Colorize,
  g: typeof UNICODE,
): string[] {
  const glyph = c(GLYPH[r.status] ?? r.status.toUpperCase(), COLOR[r.status] ?? "0");
  let head = `[${glyph}] ${c(r.name, "1")}`;
  const total = checkTotal(r);
  if (total) head += `  (${checkPassed(r)}/${total} checks)`;
  head += `  ${fmt(r.duration_seconds)}s`;
  const out = [head];
  const line =
    r.summary || (r.description ? r.description.split(/\r?\n/)[0]! : "");
  if (line) out.push(`       ${line}`);

  if (r.status === SKIPPED && r.skip_reason)
    out.push(c(`       skipped: ${r.skip_reason}`, COLOR[SKIPPED]!));
  if (r.status === ERROR && r.error)
    out.push(c(`       error: ${r.error.split(/\r?\n/)[0]}`, COLOR[ERROR]!));

  for (const a of r.assertions) {
    if (a.skipped) {
      const det = a.detail ? ` - ${a.detail}` : "";
      out.push(c(`       ${g.dot} ${a.name} (skipped)${det}`, COLOR[SKIPPED]!));
    } else if (!a.passed) {
      const det = a.detail ? ` - ${a.detail}` : "";
      out.push(c(`       ${g.bad} ${a.name}${det}`, COLOR[FAILED]!));
    }
  }
  for (const j of r.judges) {
    const mark = j.passed ? g.ok : g.bad;
    const code = j.passed ? COLOR[PASSED]! : COLOR[FAILED]!;
    out.push(
      c(
        `       ${mark} judge[${j.name}] score=${fmt(j.score, 2)} >= ${fmt(
          j.threshold,
          2,
        )}`,
        code,
      ),
    );
    if (!j.passed && j.reasoning)
      out.push(`           ${j.reasoning.slice(0, 200)}`);
  }
  for (const m of r.metrics) {
    const base = m.baseline !== null ? g4(m.baseline) : "-";
    const flag = m.regressed ? c(" REGRESSED", COLOR[FAILED]!) : "";
    const gate = m.gated ? " (gate)" : "";
    out.push(
      `       ${g.dot} ${m.name}=${g4(m.value)} vs ${base} ` +
        `[${m.baseline_strategy}]${gate}${flag}`,
    );
  }
  if (r.log_path && (r.status === FAILED || r.status === ERROR))
    out.push(`       log: ${r.log_path}`);
  out.push("");
  return out;
}

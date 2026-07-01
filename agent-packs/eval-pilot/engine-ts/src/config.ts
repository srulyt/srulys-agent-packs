/**
 * Repo-agnostic configuration and path resolution for evalpilot.
 *
 * The engine must work inside *any* repository. Nothing here hardcodes a fixed
 * repo-root depth. Everything is resolved at runtime from:
 *  - the git repository root (walk up for a `.git` marker), or an explicit
 *    override, falling back to the current working directory; and
 *  - a handful of `EVALPILOT_*` environment variables.
 *
 * Resolution order for every knob is: explicit argument > environment variable
 * > computed default.
 */

import { existsSync, statSync } from "node:fs";
import * as os from "node:os";
import * as path from "node:path";
import { fileURLToPath } from "node:url";

function truthy(name: string): boolean {
  const v = (process.env[name] ?? "").trim().toLowerCase();
  return v === "1" || v === "true" || v === "yes" || v === "on";
}

function expanduser(p: string): string {
  if (p === "~" || p.startsWith("~/") || p.startsWith("~\\")) {
    return path.join(os.homedir(), p.slice(1));
  }
  return p;
}

/**
 * Return the repository root for `start` (default: cwd).
 *
 * Honours `EVALPILOT_REPO_ROOT` first. Otherwise walks upward looking for a
 * `.git` directory/file; if none is found, returns `start` resolved.
 */
export function findRepoRoot(start?: string): string {
  const override = process.env.EVALPILOT_REPO_ROOT;
  if (override) return path.resolve(expanduser(override));

  let current = path.resolve(start ?? process.cwd());
  // Walk up including the start dir itself.
  // eslint-disable-next-line no-constant-condition
  while (true) {
    if (existsSync(path.join(current, ".git"))) return current;
    const parent = path.dirname(current);
    if (parent === current) break;
    current = parent;
  }
  return path.resolve(start ?? process.cwd());
}

/**
 * Return the directory that holds eval tests + metric history.
 * Defaults to `<repo_root>/evals`. Override with `EVALPILOT_EVAL_ROOT`.
 */
export function findEvalRoot(repoRoot?: string): string {
  const rr = repoRoot ?? findRepoRoot();
  const override = process.env.EVALPILOT_EVAL_ROOT;
  if (override) {
    const p = expanduser(override);
    return path.isAbsolute(p) ? p : path.resolve(rr, p);
  }
  return path.resolve(rr, "evals");
}

/**
 * Return the directory that holds committed JSONL metric history.
 * Defaults to `<eval_root>/_metrics`. Override with `EVALPILOT_METRICS_ROOT`.
 */
export function findMetricsRoot(evalRoot?: string): string {
  const er = evalRoot ?? findEvalRoot();
  const override = process.env.EVALPILOT_METRICS_ROOT;
  if (override) {
    const p = expanduser(override);
    return path.isAbsolute(p) ? p : path.resolve(er, p);
  }
  return path.resolve(er, "_metrics");
}

/** Directory of the built package (dist/) at runtime. */
function packageDir(): string {
  // Works for both ESM (import.meta.url) and CJS (fallback to __dirname).
  try {
    return path.dirname(fileURLToPath(import.meta.url));
  } catch {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    return (globalThis as any).__dirname ?? process.cwd();
  }
}

/** Return the package's bundled `_data` directory (agents, templates). */
export function bundledDataDir(): string {
  // dist/ sits next to _data/ once packaged; in a source checkout src/ does too
  // (../_data). Try both.
  const here = packageDir();
  const candidates = [
    path.resolve(here, "..", "_data"),
    path.resolve(here, "_data"),
    path.resolve(here, "..", "..", "_data"),
  ];
  for (const c of candidates) {
    if (existsSync(c)) return c;
  }
  return candidates[0]!;
}

/**
 * Locate the `eval-judge.agent.md` the judge helper stages.
 *
 * Order:
 *  1. `EVALPILOT_JUDGE_AGENT` (explicit path).
 *  2. The bundled package-data copy.
 *  3. The plugin-root `agents/` dir, resolved relative to this package.
 */
export function findJudgeAgentFile(): string | null {
  const override = process.env.EVALPILOT_JUDGE_AGENT;
  if (override) {
    const p = expanduser(override);
    if (existsSync(p) && statSync(p).isFile()) return p;
  }

  const bundled = path.join(bundledDataDir(), "agents", "eval-judge.agent.md");
  if (existsSync(bundled) && statSync(bundled).isFile()) return bundled;

  // Source-checkout fallback: walk up looking for agents/eval-judge.agent.md.
  let current = packageDir();
  // eslint-disable-next-line no-constant-condition
  while (true) {
    const candidate = path.join(current, "agents", "eval-judge.agent.md");
    if (existsSync(candidate) && statSync(candidate).isFile()) return candidate;
    const parent = path.dirname(current);
    if (parent === current) break;
    current = parent;
  }
  return null;
}

/** Resolved paths + behavioural flags for a single eval run. */
export interface Config {
  repo_root: string;
  eval_root: string;
  metrics_root: string;
  judge_threshold: number;
  skip_sut: boolean;
}

export function resolveConfig(opts: {
  repoRoot?: string;
  evalRoot?: string;
} = {}): Config {
  const rr = opts.repoRoot ? path.resolve(opts.repoRoot) : findRepoRoot();
  const er = opts.evalRoot ? path.resolve(opts.evalRoot) : findEvalRoot(rr);
  return {
    repo_root: rr,
    eval_root: er,
    metrics_root: findMetricsRoot(er),
    judge_threshold: Number(process.env.EVALPILOT_JUDGE_THRESHOLD ?? "0.7"),
    skip_sut: truthy("EVALPILOT_SKIP_SUT") || truthy("EVALS_SKIP_SUT"),
  };
}

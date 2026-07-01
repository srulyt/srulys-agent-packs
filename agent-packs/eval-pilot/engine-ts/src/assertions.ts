/**
 * Extensible assertion library (the `## Assert` vocabulary).
 *
 * Every assertion is a small function registered under a `kind` string. The
 * Markdown loader and the builder both emit {@link AssertionSpec} objects naming
 * a `kind` plus `args`; the executor calls {@link runAssertion} to evaluate each
 * one against an {@link AssertContext} and get back an {@link AssertionResult}.
 *
 * New assertion kinds register with {@link assertion}. The `custom` kind runs an
 * arbitrary predicate supplied by the fluent builder.
 */

import { existsSync, readFileSync, statSync } from "node:fs";
import * as path from "node:path";
import fg from "fast-glob";
import { normalise } from "./asserts.js";
import { makeAssertionResult, type AssertionResult } from "./model.js";
import type { AssertionSpec } from "./spec.js";

/** Everything an assertion needs to inspect an eval's outcome. */
export class AssertContext {
  root: string;
  stdout: string;
  stderr: string;

  constructor(opts: { root: string; stdout?: string; stderr?: string }) {
    this.root = opts.root;
    this.stdout = opts.stdout ?? "";
    this.stderr = opts.stderr ?? "";
  }

  glob(pattern: string): string[] {
    return fg
      .sync(pattern, { cwd: this.root, dot: true, absolute: true })
      .map((p) => path.normalize(p))
      .sort();
  }

  /** Read the first file matching a path/glob (or null if no match). */
  read(patternOrPath: string): string | null {
    const p = path.join(this.root, patternOrPath);
    if (existsSync(p) && statSync(p).isFile()) {
      return readFileSync(p, "utf-8");
    }
    const matches = this.glob(patternOrPath).filter(
      (m) => existsSync(m) && statSync(m).isFile(),
    );
    if (matches.length) return readFileSync(matches[0]!, "utf-8");
    return null;
  }
}

export type AssertionFn = (
  ctx: AssertContext,
  args: Record<string, any>,
) => AssertionResult;

const REGISTRY: Map<string, AssertionFn> = new Map();
const HELP: Map<string, string> = new Map();

/** Register `fn` as the checker for `kind`. */
export function assertion(kind: string, help = ""): (fn: AssertionFn) => AssertionFn {
  return (fn: AssertionFn) => {
    REGISTRY.set(kind, fn);
    HELP.set(kind, help);
    return fn;
  };
}

/** Register a checker directly (non-decorator form). */
export function registerAssertion(kind: string, fn: AssertionFn, help = ""): void {
  REGISTRY.set(kind, fn);
  HELP.set(kind, help);
}

export function availableKinds(): string[] {
  return [...REGISTRY.keys()].sort();
}

export function helpFor(kind: string): string {
  return HELP.get(kind) ?? "";
}

/** Evaluate one {@link AssertionSpec} against `ctx`. */
export function runAssertion(
  spec: AssertionSpec,
  ctx: AssertContext,
): AssertionResult {
  if (spec.kind === "custom") return runCustom(spec, ctx);
  const fn = REGISTRY.get(spec.kind);
  if (fn === undefined) {
    return makeAssertionResult({
      kind: spec.kind,
      name: spec.name || spec.kind,
      passed: false,
      detail:
        `unknown assertion kind '${spec.kind}'; ` +
        `known: ${availableKinds().join(", ")}`,
    });
  }
  const res = fn(ctx, { ...spec.args });
  if (spec.name) res.name = spec.name;
  return res;
}

// ---- helpers ------------------------------------------------------------

function asList(value: unknown): string[] {
  if (value === null || value === undefined) return [];
  if (Array.isArray(value)) return value.map((v) => String(v));
  return [String(value)];
}

function sourceText(
  ctx: AssertContext,
  args: Record<string, any>,
): [string | null, string] {
  const p = args.path ?? args.file;
  if (p) {
    const text = ctx.read(String(p));
    return [text, String(p)];
  }
  return [ctx.stdout, "stdout"];
}

function needles(args: Record<string, any>): [string[], "all" | "any"] {
  if ("any" in args) return [asList(args.any), "any"];
  if ("all" in args) return [asList(args.all), "all"];
  return [asList(args.text), "all"];
}

function relTo(root: string, abs: string): string {
  return path.relative(root, abs).replace(/\\/g, "/");
}

// ---- built-in assertions ------------------------------------------------

registerAssertion(
  "file_exists",
  (ctx, args) => {
    const patterns = [...asList(args.path), ...asList(args.paths)];
    const missing = patterns.filter((p) => ctx.glob(p).length === 0);
    const name = patterns.length
      ? "file exists: " + patterns.join(", ")
      : "file exists";
    return makeAssertionResult({
      kind: "file_exists",
      name,
      passed: missing.length === 0,
      detail: missing.length === 0 ? "" : `missing: ${missing.join(", ")}`,
      data: { patterns, missing },
    });
  },
  "path|paths: at least one match per pattern",
);

registerAssertion(
  "file_absent",
  (ctx, args) => {
    const patterns = [...asList(args.path), ...asList(args.paths)];
    const offenders: Record<string, string[]> = {};
    for (const p of patterns) {
      const hits = ctx.glob(p).map((m) => relTo(ctx.root, m));
      if (hits.length) offenders[p] = hits;
    }
    const name = patterns.length
      ? "file absent: " + patterns.join(", ")
      : "file absent";
    const clean = Object.keys(offenders).length === 0;
    return makeAssertionResult({
      kind: "file_absent",
      name,
      passed: clean,
      detail: clean ? "" : `unexpected: ${JSON.stringify(offenders)}`,
      data: { patterns, offenders },
    });
  },
  "path|paths: zero matches",
);

registerAssertion(
  "glob_count",
  (ctx, args) => {
    const pattern = String(args.pattern ?? "**/*");
    const n = ctx.glob(pattern).length;
    const lo = args.min;
    const hi = args.max;
    const eq = args.equals;
    let ok = true;
    if (eq !== undefined && eq !== null) ok = n === Number(eq);
    if (lo !== undefined && lo !== null) ok = ok && n >= Number(lo);
    if (hi !== undefined && hi !== null) ok = ok && n <= Number(hi);
    const bounds: string[] = [];
    if (eq !== undefined && eq !== null) bounds.push(`==${eq}`);
    if (lo !== undefined && lo !== null) bounds.push(`>=${lo}`);
    if (hi !== undefined && hi !== null) bounds.push(`<=${hi}`);
    return makeAssertionResult({
      kind: "glob_count",
      name: `glob count ${pattern} ${bounds.join(" ")}`.trim(),
      passed: ok,
      detail: `found ${n}`,
      data: { pattern, count: n },
    });
  },
  "pattern, [min|max|equals]: match count in range",
);

function containsImpl(
  ctx: AssertContext,
  args: Record<string, any>,
  opts: { negate: boolean; prose: boolean; kind: string; forceStdout?: boolean },
): AssertionResult {
  let text: string | null;
  let label: string;
  if (opts.forceStdout) {
    text = ctx.stdout;
    label = "stdout";
  } else {
    [text, label] = sourceText(ctx, args);
  }
  const [needleList, mode] = needles(args);
  const ignoreCase = Boolean(args.ignore_case);

  if (text === null) {
    return makeAssertionResult({
      kind: opts.kind,
      name: `${opts.kind}: ${label}`,
      passed: false,
      detail: `source not found: ${label}`,
    });
  }
  const src = text;

  const present = (needle: string): boolean => {
    let hay = opts.prose ? normalise(src) : src;
    let ndl = opts.prose ? normalise(needle) : needle;
    if (ignoreCase) {
      hay = hay.toLowerCase();
      ndl = ndl.toLowerCase();
    }
    return hay.includes(ndl);
  };

  const hits = new Map<string, boolean>(needleList.map((n) => [n, present(n)]));
  let passed: boolean;
  let detail: string;
  if (opts.negate) {
    passed = ![...hits.values()].some(Boolean);
    const offenders = [...hits.entries()].filter(([, p]) => p).map(([n]) => n);
    detail = passed
      ? ""
      : `unexpectedly present in ${label}: ${JSON.stringify(offenders)}`;
  } else if (mode === "any") {
    passed = [...hits.values()].some(Boolean);
    detail = passed ? "" : `none present in ${label}: ${JSON.stringify(needleList)}`;
  } else {
    const missing = [...hits.entries()].filter(([, p]) => !p).map(([n]) => n);
    passed = missing.length === 0;
    detail = passed ? "" : `missing in ${label}: ${JSON.stringify(missing)}`;
  }

  return makeAssertionResult({
    kind: opts.kind,
    name: `${opts.kind}: ${label}`,
    passed,
    detail,
    data: { label, needles: needleList, mode },
  });
}

registerAssertion(
  "contains",
  (ctx, args) =>
    containsImpl(ctx, args, { negate: false, prose: false, kind: "contains" }),
  "[path], text|any|all, [ignore_case]",
);

registerAssertion(
  "not_contains",
  (ctx, args) =>
    containsImpl(ctx, args, { negate: true, prose: false, kind: "not_contains" }),
  "[path], text",
);

registerAssertion(
  "prose_contains",
  (ctx, args) =>
    containsImpl(ctx, args, {
      negate: false,
      prose: true,
      kind: "prose_contains",
    }),
  "[path], text|any|all (whitespace-normalised)",
);

registerAssertion(
  "stdout_contains",
  (ctx, args) =>
    containsImpl(ctx, args, {
      negate: false,
      prose: false,
      kind: "stdout_contains",
      forceStdout: true,
    }),
  "text|any|all, [ignore_case]",
);

registerAssertion(
  "matches",
  (ctx, args) => {
    const [text, label] = sourceText(ctx, args);
    const pattern = String(args.pattern ?? "");
    let flags = "";
    const flagStr = String(args.flags ?? "").toLowerCase();
    if (flagStr.includes("i")) flags += "i";
    if (flagStr.includes("m")) flags += "m";
    if (flagStr.includes("s")) flags += "s";
    if (text === null) {
      return makeAssertionResult({
        kind: "matches",
        name: `matches: ${label}`,
        passed: false,
        detail: `source not found: ${label}`,
      });
    }
    let ok = false;
    try {
      ok = new RegExp(pattern, flags).test(text);
    } catch (e) {
      return makeAssertionResult({
        kind: "matches",
        name: `matches: ${label}`,
        passed: false,
        detail: `invalid regex: ${(e as Error).message}`,
      });
    }
    return makeAssertionResult({
      kind: "matches",
      name: `matches /${pattern}/ in ${label}`,
      passed: ok,
      detail: ok ? "" : `pattern not found in ${label}`,
      data: { pattern, label },
    });
  },
  "[path], pattern (regex), [flags]",
);

function dig(obj: unknown, query: string): unknown {
  let cur: any = obj;
  for (const part of query.split(/[.[\]]/).filter((p) => p !== "")) {
    if (Array.isArray(cur)) {
      cur = cur[Number(part)];
      if (cur === undefined) throw new Error(part);
    } else if (cur && typeof cur === "object") {
      if (!(part in cur)) throw new Error(part);
      cur = cur[part];
    } else {
      throw new Error(part);
    }
  }
  return cur;
}

registerAssertion(
  "json_path",
  (ctx, args) => {
    const p = String(args.path ?? "");
    const query = String(args.query ?? "");
    const text = ctx.read(p);
    if (text === null) {
      return makeAssertionResult({
        kind: "json_path",
        name: `json_path ${p}`,
        passed: false,
        detail: `file not found: ${p}`,
      });
    }
    let data: unknown;
    try {
      data = JSON.parse(text);
    } catch (exc) {
      return makeAssertionResult({
        kind: "json_path",
        name: `json_path ${p}`,
        passed: false,
        detail: `invalid JSON: ${(exc as Error).message}`,
      });
    }
    let value: unknown = null;
    let found: boolean;
    try {
      value = dig(data, query);
      found = true;
    } catch {
      found = false;
      value = null;
    }

    let passed: boolean;
    let detail: string;
    if ("exists" in args) {
      const want = Boolean(args.exists);
      passed = found === want;
      detail = passed ? "" : `exists=${found}, wanted ${want}`;
    } else if ("equals" in args) {
      passed = found && deepEqual(value, args.equals);
      detail = passed
        ? ""
        : `got ${JSON.stringify(value)}, wanted ${JSON.stringify(args.equals)}`;
    } else {
      passed = found;
      detail = passed ? "" : `path '${query}' not found`;
    }
    return makeAssertionResult({
      kind: "json_path",
      name: `json_path ${p}:${query}`,
      passed,
      detail,
      data: { path: p, query, value },
    });
  },
  "path, query (dotted), [equals|exists]",
);

registerAssertion(
  "json_empty",
  (ctx, args) => {
    const p = String(args.path ?? "");
    const query = String(args.query ?? "");
    const text = ctx.read(p);
    if (text === null) {
      return makeAssertionResult({
        kind: "json_empty",
        name: `json_empty ${p}`,
        passed: false,
        detail: `file not found: ${p}`,
      });
    }
    let data: unknown;
    try {
      data = JSON.parse(text);
    } catch (exc) {
      return makeAssertionResult({
        kind: "json_empty",
        name: `json_empty ${p}`,
        passed: false,
        detail: `invalid JSON: ${(exc as Error).message}`,
      });
    }
    let value: unknown = null;
    let found: boolean;
    try {
      value = dig(data, query);
      found = true;
    } catch {
      value = null;
      found = false;
    }
    const empty = !found || isEmptyValue(value);
    return makeAssertionResult({
      kind: "json_empty",
      name: `json_empty ${p}:${query}`,
      passed: empty,
      detail: empty ? "" : `expected empty/absent, got ${JSON.stringify(value)}`,
      data: { path: p, query, value },
    });
  },
  "path, query (dotted): value is missing, null, or empty",
);

function isEmptyValue(value: unknown): boolean {
  if (value === null || value === undefined || value === "") return true;
  if (Array.isArray(value)) return value.length === 0;
  if (typeof value === "object") return Object.keys(value).length === 0;
  return false;
}

function deepEqual(a: unknown, b: unknown): boolean {
  return JSON.stringify(a) === JSON.stringify(b);
}

/** Return up to `maxChars` of the body under a `## <name>` heading. */
function sectionBody(
  text: string,
  name: string,
  maxChars: number,
): string | null {
  const escaped = name.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const re = new RegExp(`#+\\s+${escaped}\\s*\\n([\\s\\S]{0,${maxChars}})`, "i");
  const m = re.exec(text);
  return m ? m[1]! : null;
}

function sectionImpl(
  ctx: AssertContext,
  args: Record<string, any>,
  negate: boolean,
): AssertionResult {
  const kind = negate ? "section_not_contains" : "section_contains";
  const [text, label] = sourceText(ctx, args);
  const section = String(args.section ?? "");
  const maxChars = Number(args.max_chars ?? 800);
  if (text === null) {
    return makeAssertionResult({
      kind,
      name: `${kind}: ${label}`,
      passed: false,
      detail: `source not found: ${label}`,
    });
  }
  const body = sectionBody(text, section, maxChars);
  if (body === null) {
    const passed = negate;
    return makeAssertionResult({
      kind,
      name: `${kind}: ${section}`,
      passed,
      detail: passed ? "" : `section '${section}' not found in ${label}`,
    });
  }
  const [needleList, mode] = needles(args);
  const ignoreCase = Boolean(args.ignore_case);
  const hay = ignoreCase ? body.toLowerCase() : body;
  const hits = new Map<string, boolean>(
    needleList.map((n) => [n, hay.includes(ignoreCase ? n.toLowerCase() : n)]),
  );
  let passed: boolean;
  let detail: string;
  if (negate) {
    const offenders = [...hits.entries()].filter(([, p]) => p).map(([n]) => n);
    passed = offenders.length === 0;
    detail = passed ? "" : `leaked into '${section}': ${JSON.stringify(offenders)}`;
  } else if (mode === "any") {
    passed = [...hits.values()].some(Boolean);
    detail = passed ? "" : `none present in '${section}': ${JSON.stringify(needleList)}`;
  } else {
    const missing = [...hits.entries()].filter(([, p]) => !p).map(([n]) => n);
    passed = missing.length === 0;
    detail = passed ? "" : `missing in '${section}': ${JSON.stringify(missing)}`;
  }
  return makeAssertionResult({
    kind,
    name: `${kind}: ${section}`,
    passed,
    detail,
    data: { section, needles: needleList },
  });
}

registerAssertion(
  "section_contains",
  (ctx, args) => sectionImpl(ctx, args, false),
  "[path], section, text|any|all, [ignore_case, max_chars]",
);

registerAssertion(
  "section_not_contains",
  (ctx, args) => sectionImpl(ctx, args, true),
  "[path], section, text, [ignore_case, max_chars]",
);

function runCustom(spec: AssertionSpec, ctx: AssertContext): AssertionResult {
  const name = spec.name || "custom";
  if (spec.predicate === null || spec.predicate === undefined) {
    return makeAssertionResult({
      kind: "custom",
      name,
      passed: false,
      detail: "custom assertion has no predicate",
    });
  }
  let outcome: unknown;
  try {
    outcome = spec.predicate(ctx);
  } catch (exc) {
    return makeAssertionResult({
      kind: "custom",
      name,
      passed: false,
      detail: `predicate raised: ${String(exc)}`,
    });
  }
  let passed: boolean;
  let detail = "";
  if (Array.isArray(outcome)) {
    passed = Boolean(outcome[0]);
    detail = outcome.length > 1 ? String(outcome[1]) : "";
  } else {
    passed = Boolean(outcome);
  }
  return makeAssertionResult({ kind: "custom", name, passed, detail });
}

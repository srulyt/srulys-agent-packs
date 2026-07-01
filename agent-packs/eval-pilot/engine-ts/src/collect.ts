/**
 * Discover eval specs on disk and compile them to {@link EvalSpec} objects.
 *
 * Two authoring file types are collected:
 *  - `*.eval.md` — parsed by the Markdown loader.
 *  - `*.eval.ts` / `*.eval.js` — loaded at runtime via `jiti`; every exported
 *    {@link EvalSpec} or fluent {@link Eval} (built) is collected.
 *
 * This is the TypeScript analogue of Python's `importlib` dynamic import: jiti
 * transpiles-and-imports the user's TS module on the fly, then we scan its
 * exports for spec/builder objects. Noise directories are skipped so a run
 * never re-discovers its own artifacts.
 */

import { existsSync, readdirSync, statSync } from "node:fs";
import * as path from "node:path";
import { createRequire } from "node:module";
import { fileURLToPath, pathToFileURL } from "node:url";
import { createJiti } from "jiti";
import { Eval } from "./loaders/builder.js";
import { loadMarkdownEval } from "./loaders/markdown.js";
import type { EvalSpec } from "./spec.js";

const PRUNE = new Set<string>([
  "_runs",
  "_metrics",
  "_templates",
  "__pycache__",
  ".git",
  "node_modules",
  ".venv",
  "venv",
  ".pytest_cache",
]);

/** Return all specs under `target` (a file or directory). */
export async function collectSpecs(target: string): Promise<EvalSpec[]> {
  const t = path.resolve(target);
  if (existsSync(t) && statSync(t).isFile()) {
    return loadFile(t);
  }
  const specs: EvalSpec[] = [];
  for (const f of iterSpecFiles(t)) {
    specs.push(...(await loadFile(f)));
  }
  specs.sort(
    (a, b) =>
      (a.spec_path ?? "").localeCompare(b.spec_path ?? "") ||
      a.name.localeCompare(b.name),
  );
  return specs;
}

function* iterSpecFiles(root: string): Generator<string> {
  if (!existsSync(root)) return;
  const stack: string[] = [root];
  const found: string[] = [];
  while (stack.length) {
    const dir = stack.pop()!;
    let entries: import("node:fs").Dirent[];
    try {
      entries = readdirSync(dir, { withFileTypes: true });
    } catch {
      continue;
    }
    for (const e of entries) {
      const full = path.join(dir, e.name);
      const rel = path.relative(root, full);
      if (rel.split(path.sep).some((part) => PRUNE.has(part))) continue;
      if (e.isDirectory()) {
        stack.push(full);
      } else if (isSpecFile(e.name)) {
        found.push(full);
      }
    }
  }
  found.sort();
  yield* found;
}

function isSpecFile(name: string): boolean {
  return (
    name.endsWith(".eval.md") ||
    name.endsWith(".eval.ts") ||
    name.endsWith(".eval.js") ||
    name.endsWith(".eval.mjs")
  );
}

async function loadFile(file: string): Promise<EvalSpec[]> {
  if (file.endsWith(".eval.md")) {
    return [loadMarkdownEval(file)];
  }
  if (isSpecFile(file)) {
    return loadModule(file);
  }
  return [];
}

/**
 * Resolve the running engine's own entry so `.eval.ts` specs that
 * `import { Eval } from "@evalpilot/cli"` load against this exact build —
 * whether the package is npm-installed in the consumer repo or run in-repo
 * during development. Returns `null` if it cannot be located.
 */
function ownEntry(): string | null {
  // 1. Prefer normal resolution (installed consumer case).
  try {
    const require = createRequire(import.meta.url);
    return require.resolve("@evalpilot/cli");
  } catch {
    /* not installed — fall through */
  }
  // 2. Fall back to a sibling of the current (bundled or source) module.
  let here: string;
  try {
    here = path.dirname(fileURLToPath(import.meta.url));
  } catch {
    return null;
  }
  for (const name of ["index.js", "index.mjs", "index.ts"]) {
    const cand = path.join(here, name);
    if (existsSync(cand)) return cand;
  }
  return null;
}

function jitiAlias(): Record<string, string> {
  const entry = ownEntry();
  if (!entry) return {};
  return { "@evalpilot/cli": entry, evalpilot: entry };
}

async function loadModule(file: string): Promise<EvalSpec[]> {
  const jiti = createJiti(pathToFileURL(file).href, {
    interopDefault: true,
    alias: jitiAlias(),
  });
  const mod = (await jiti.import(file)) as Record<string, unknown>;

  const found: EvalSpec[] = [];
  const seen = new Set<unknown>();
  const values: unknown[] = [];
  if (mod && typeof mod === "object") {
    values.push(...Object.values(mod));
    if ("default" in mod) values.push((mod as any).default);
  }
  for (const value of values) {
    const built = coerce(value);
    if (built !== null && !seen.has(built)) {
      seen.add(built);
      built.spec_path = file;
      if (built.base_dir === null) built.base_dir = path.dirname(file);
      found.push(built);
    }
  }
  return found;
}

function coerce(value: unknown): EvalSpec | null {
  if (value instanceof Eval) return value.build();
  if (
    value &&
    typeof value === "object" &&
    "name" in value &&
    "kind" in value &&
    "setup" in value
  ) {
    return value as EvalSpec;
  }
  return null;
}

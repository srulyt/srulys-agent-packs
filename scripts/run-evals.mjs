#!/usr/bin/env node
/**
 * Friendly driver around the TypeScript eval engine (`@evalpilot/cli`).
 *
 * Replaces the legacy `scripts/run_evals.py`. Resolves a pack/skill NAME to its
 * eval directory (the TS engine's `run` takes a PATH, not a name) and forwards
 * everything else to `evalpilot run`, which renders the summary and writes
 * report.json/html under `evals/_runs/<timestamp>/`.
 *
 * Usage:
 *   node scripts/run-evals.mjs <pack>            # run one pack or skill by name
 *   node scripts/run-evals.mjs --all             # run every eval in the repo
 *   node scripts/run-evals.mjs <pack> --list     # list specs without running
 *   node scripts/run-evals.mjs <pack> --mock     # offline runner (no copilot)
 *   node scripts/run-evals.mjs <pack> -- --tags smoke,-slow --parallel 4
 *
 * Any flags after `--`, or any unrecognized `-flag`, are forwarded verbatim to
 * `evalpilot run` (see `evalpilot run --help`).
 */

import { spawnSync } from "node:child_process";
import { existsSync, readdirSync, statSync } from "node:fs";
import * as path from "node:path";
import { fileURLToPath } from "node:url";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = path.resolve(HERE, "..");
const EVALS_DIR = path.join(REPO_ROOT, "evals");
const ENGINE_DIR = path.join(REPO_ROOT, "agent-packs", "eval-pilot", "engine-ts");
const ENGINE_CLI = path.join(ENGINE_DIR, "dist", "cli.js");

function isDir(p) {
  try {
    return statSync(p).isDirectory();
  } catch {
    return false;
  }
}

function ensureEngineBuilt() {
  if (existsSync(ENGINE_CLI)) return;
  console.error("[run-evals] engine build not found; building @evalpilot/cli ...");
  const r = spawnSync("npm", ["run", "build"], {
    cwd: ENGINE_DIR,
    stdio: "inherit",
    shell: process.platform === "win32",
  });
  if (r.status !== 0 || !existsSync(ENGINE_CLI)) {
    console.error(
      `[run-evals] failed to build the engine. Run 'npm install && npm run build' in ${ENGINE_DIR}.`,
    );
    process.exit(1);
  }
}

function listPacks() {
  const out = [];
  for (const bucket of ["packs", "skills"]) {
    const dir = path.join(EVALS_DIR, bucket);
    if (isDir(dir)) {
      for (const e of readdirSync(dir, { withFileTypes: true })) {
        if (e.isDirectory()) out.push(e.name);
      }
    }
  }
  return out.sort();
}

function resolvePack(name) {
  const candidates = [
    path.join(EVALS_DIR, "packs", name),
    path.join(EVALS_DIR, "skills", name),
    path.join(EVALS_DIR, name),
    path.resolve(REPO_ROOT, name),
  ];
  for (const c of candidates) {
    if (isDir(c) || existsSync(c)) return c;
  }
  console.error(
    `error: no eval directory for '${name}'.\n` +
      `available: ${listPacks().join(", ")}\n` +
      `          (or pass --all to run every eval in the repo)`,
  );
  process.exit(2);
}

function main(argv) {
  const args = argv.slice(2);

  // Split off explicit passthrough after `--`.
  let passthrough = [];
  const ddIdx = args.indexOf("--");
  let head = args;
  if (ddIdx !== -1) {
    head = args.slice(0, ddIdx);
    passthrough = args.slice(ddIdx + 1);
  }

  let all = false;
  let list = false;
  const positionals = [];
  for (const a of head) {
    if (a === "--all") all = true;
    else if (a === "--list") list = true;
    else if (a === "--mock") passthrough.push("--runner", "mock");
    else if (a.startsWith("-")) passthrough.push(a); // forward engine flags
    else positionals.push(a);
  }

  const packName = positionals[0];
  if (positionals.length > 1) {
    console.error(
      `[run-evals] note: test-name selectors are no longer supported; ` +
        `use '-- --tags <expr>' to filter. Ignoring: ${positionals.slice(1).join(", ")}`,
    );
  }

  let target;
  if (all || !packName) target = EVALS_DIR;
  else target = resolvePack(packName);

  ensureEngineBuilt();

  const subcommand = list ? "lint" : "run";
  const cmd = [ENGINE_CLI, subcommand, target, ...passthrough];
  const r = spawnSync(process.execPath, cmd, { cwd: REPO_ROOT, stdio: "inherit" });
  return r.status ?? 1;
}

process.exit(main(process.argv));

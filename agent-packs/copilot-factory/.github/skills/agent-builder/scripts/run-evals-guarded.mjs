#!/usr/bin/env node
import { spawnSync } from "node:child_process";
import {
  cpSync, lstatSync, mkdtempSync, readdirSync, readFileSync, rmSync,
} from "node:fs";
import { createHash } from "node:crypto";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { validateEvalTarget } from "./validate-factory-paths.mjs";

function findRepoRoot(start = process.cwd()) {
  let current = path.resolve(start);
  while (path.dirname(current) !== current) {
    try {
      if (lstatSync(path.join(current, ".git"))) return current;
    } catch {}
    current = path.dirname(current);
  }
  throw new Error("repository root not found");
}

function hashFile(file) {
  return createHash("sha256").update(readFileSync(file)).digest("hex");
}

export function snapshotTree(root) {
  const snapshot = new Map();
  function walk(directory, relative = "") {
    for (const entry of readdirSync(directory, { withFileTypes: true })) {
      const rel = relative ? `${relative}/${entry.name}` : entry.name;
      if (rel === ".git" || rel.startsWith(".git/")) continue;
      const absolute = path.join(directory, entry.name);
      const stat = lstatSync(absolute);
      if (stat.isSymbolicLink()) {
        snapshot.set(rel, `link:${stat.size}:${stat.mtimeMs}`);
      } else if (stat.isDirectory()) {
        snapshot.set(`${rel}/`, "dir");
        walk(absolute, rel);
      } else if (stat.isFile()) {
        snapshot.set(rel, `file:${stat.mode}:${stat.size}:${hashFile(absolute)}`);
      }
    }
  }
  walk(root);
  return snapshot;
}

export function diffSnapshots(before, after) {
  const changed = [];
  for (const key of new Set([...before.keys(), ...after.keys()])) {
    if (before.get(key) !== after.get(key)) changed.push(key);
  }
  return changed.sort();
}

function parseArgs(argv) {
  const out = {
    runner: "copilot",
    tags: null,
    wallClockTimeout: "1800",
    sutTimeout: null,
    parallel: "1",
  };
  for (let i = 2; i < argv.length; i += 2) {
    const key = argv[i];
    const value = argv[i + 1];
    if (!value || ![
      "--pack", "--target", "--runner", "--tags", "--wall-clock-timeout",
      "--sut-timeout", "--parallel",
    ].includes(key)) {
      throw new Error(`unsupported or incomplete argument: ${key ?? "<missing>"}`);
    }
    if (key === "--wall-clock-timeout") out.wallClockTimeout = value;
    else if (key === "--sut-timeout") out.sutTimeout = value;
    else out[key.slice(2)] = value;
  }
  if (!out.pack || !out.target) throw new Error("--pack and --target are required");
  if (!["copilot", "mock"].includes(out.runner)) throw new Error("unsupported runner");
  if (!/^[1-9]\d*$/.test(out.wallClockTimeout)) throw new Error("invalid wall-clock timeout");
  if (out.sutTimeout !== null && !/^[1-9]\d*$/.test(out.sutTimeout)) {
    throw new Error("invalid SUT timeout");
  }
  if (!/^[1-8]$/.test(out.parallel)) throw new Error("invalid parallel worker count");
  if (!validateEvalTarget(out.target, out.pack)) throw new Error("unsafe target");
  return out;
}

function main() {
  const args = parseArgs(process.argv);
  const root = findRepoRoot();
  const target = args.target === "all"
    ? path.join(root, "evals", "packs", args.pack)
    : path.join(root, ...args.target.split("/"));
  const cli = path.join(root, "agent-packs", "eval-pilot", "engine-ts", "dist", "cli.js");
  const temporary = mkdtempSync(path.join(os.tmpdir(), "factory-eval-"));
  const isolatedEvalRoot = path.join(temporary, "evals");
  const before = snapshotTree(root);
  try {
    const childArgs = [
      cli, "run", target, "--runner", args.runner,
      "--parallel", args.parallel, "--format", "json",
    ];
    if (args.sutTimeout !== null) childArgs.push("--sut-timeout", args.sutTimeout);
    if (args.tags) childArgs.push("--tags", args.tags);
    const child = spawnSync(process.execPath, childArgs, {
      cwd: root,
      encoding: "utf8",
      env: {
        ...process.env,
        EVALPILOT_REPO_ROOT: root,
        EVALPILOT_EVAL_ROOT: isolatedEvalRoot,
        EVALPILOT_METRICS_ROOT: path.join(isolatedEvalRoot, "_metrics"),
        PYTHONDONTWRITEBYTECODE: "1",
      },
      timeout: Number(args.wallClockTimeout) * 1000,
    });

    const changed = diffSnapshots(before, snapshotTree(root));
    if (changed.length) {
      console.error(JSON.stringify({
        status: "harness-error",
        reason: "repository write outside isolated output",
        changed,
      }));
      return 3;
    }

    const runsRoot = path.join(isolatedEvalRoot, "_runs");
    const runs = readdirSync(runsRoot, { withFileTypes: true })
      .filter((entry) => entry.isDirectory() && entry.name !== "scratch");
    if (runs.length !== 1) {
      console.error(JSON.stringify({
        status: "harness-error",
        reason: `expected one isolated run directory, found ${runs.length}`,
      }));
      return 3;
    }
    const isolatedReport = path.join(runsRoot, runs[0].name, "report.json");
    try {
      lstatSync(isolatedReport);
    } catch {
      console.error(JSON.stringify({
        status: "harness-error",
        reason: "eval process ended without a modeled report",
        exit_code: child.status,
        signal: child.signal,
        stdout: (child.stdout ?? "").slice(-4000),
        stderr: (child.stderr ?? "").slice(-4000),
      }));
      return 3;
    }

    const destination = path.join(root, "evals", "_runs", runs[0].name);
    try {
      lstatSync(destination);
      console.error(JSON.stringify({
        status: "harness-error", reason: "run destination already exists",
      }));
      return 3;
    } catch {}
    cpSync(path.join(runsRoot, runs[0].name), destination, {
      recursive: true, errorOnExist: true, force: false,
    });
    process.stdout.write(child.stdout ?? "");
    process.stderr.write(child.stderr ?? "");
    console.log(`FACTORY_GUARDED_REPORT=${path.relative(root, path.join(destination, "report.json")).replaceAll("\\", "/")}`);
    return child.status ?? 2;
  } finally {
    try {
      rmSync(temporary, {
        recursive: true,
        force: true,
        maxRetries: 30,
        retryDelay: 500,
      });
    } catch (error) {
      console.error(JSON.stringify({
        status: "cleanup-warning",
        reason: error.message,
        temporary,
      }));
    }
  }
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  try {
    process.exitCode = main();
  } catch (error) {
    console.error(JSON.stringify({ status: "harness-error", reason: error.message }));
    process.exitCode = 2;
  }
}

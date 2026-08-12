#!/usr/bin/env node
/**
 * `evalpilot` command-line interface.
 *
 * Author, run, and inspect evals with the modeled result at the centre:
 *
 * - `evalpilot new`      — scaffold a `*.eval.md` (or `*.eval.ts`) spec.
 * - `evalpilot run`      — discover + execute specs, render terminal/HTML/JSON.
 * - `evalpilot show`     — re-render a previous run from its JSON.
 * - `evalpilot lint`     — validate specs without running the SUT.
 * - `evalpilot metrics`  — numeric trends; `--check` fails on regressions.
 * - `evalpilot discover` — list agents/skills evalpilot can see.
 * - `evalpilot init`     — scaffold an `evals/` tree from bundled templates.
 *
 * Every `run` writes a canonical `report.json` (plus HTML) under
 * `<eval_root>/_runs/<run-id>/` so the result location is always obvious.
 */

import { spawn } from "node:child_process";
import {
  copyFileSync,
  existsSync,
  mkdirSync,
  readFileSync,
  statSync,
  writeFileSync,
} from "node:fs";
import * as path from "node:path";
import { pathToFileURL } from "node:url";
import { Command, Option } from "commander";
import fg from "fast-glob";
import { collectSpecs } from "./collect.js";
import {
  bundledDataDir,
  findEvalRoot,
  findMetricsRoot,
  findRepoRoot,
} from "./config.js";
import { discoverAgents, discoverSkills } from "./discovery.js";
import { runSpecs } from "./executor.js";
import { iterSeries } from "./metrics.js";
import { reportOk } from "./model.js";
import { renderHtml, renderTerminal, writeJson } from "./render/index.js";
import { readJson } from "./render/json.js";
import { getRunner } from "./runners/index.js";
import type { SUTRunner } from "./runners/base.js";
import { specIsStub, validateSpec, type EvalSpec } from "./spec.js";

// ---- templates ----------------------------------------------------------

function mdTemplate(v: {
  name: string;
  target: string;
  kind: string;
  title: string;
  stage: string;
}): string {
  return `---
name: ${v.name}
target: ${v.target}
kind: ${v.kind}
tags: [smoke]
timeout: 600
---

# ${v.title}
> One-line summary of what a good result looks like.

## Description
Explain, in plain English, the scenario this eval exercises: the starting
context, what the agent/skill is asked to do, and what a correct outcome looks
like. This is the human-readable intent — an agent can implement the sections
below directly from it.

## Setup
\`\`\`yaml
# stage: { ${v.stage} }          # inferred from target+kind; override here if needed
# files: [{ copy: "fixtures/**", dest: "." }]
\`\`\`

## Act
\`\`\`prompt
Replace this with a prompt that exercises a real scenario. Do NOT include the
expected answer -- the point is that the agent had to work it out.
\`\`\`

## Assert
\`\`\`yaml
files:
  exists: ["**/*.md"]        # at least one artifact was produced
contains:
  - { text: "REPLACE", ignore_case: true }   # against stdout by default
judge:
  # artifact: path/to/output.md    # omit to judge stdout
  threshold: 0.7
  criteria: |
    Score 1.0 only if ALL criteria are met; 0.5 for partial; 0.0 if off-topic.
metrics:
  - { name: judge_score, value: $judge.score, direction: higher_is_better,
      baseline: rolling_mean, tolerance: 0.1 }
\`\`\`
`;
}

function mdStubTemplate(v: {
  name: string;
  target: string;
  kind: string;
  title: string;
  summary: string;
  description: string;
}): string {
  return `---
name: ${v.name}
target: ${v.target}
kind: ${v.kind}
tags: [smoke]
timeout: 600
---

# ${v.title}
> ${v.summary}

## Description
${v.description}

<!-- TODO: ask an agent to implement ## Setup / ## Act / ## Assert from the
     description above, then run \`evalpilot run\` on this file. -->
`;
}

function tsTemplate(v: { name: string; target: string; kind: string }): string {
  return `// Builder-style eval for ${v.name}. Run with: evalpilot run this_file.eval.ts
import { Eval } from "evalpilot";

export default new Eval("${v.name}", {
  target: "${v.target}",
  kind: "${v.kind}",
  tags: ["smoke"],
  timeout: 600,
})
  .summarize("One-line summary of what a good result looks like.")
  .describe("Explain the scenario, the action, and what a correct outcome is.")
  .prompt("Replace with a prompt that exercises a real scenario.")
  .expectFile("**/*.md")
  .judge(
    "Score 1.0 only if ALL criteria are met; 0.5 partial; 0.0 off-topic.",
    { threshold: 0.7 },
  )
  .metric("judge_score", "$judge.score", {
    direction: "higher_is_better",
    baseline: "rolling_mean",
    tolerance: 0.1,
  })
  .build();
`;
}

// ---- new ----------------------------------------------------------------

interface NewOpts {
  target?: string;
  kind: string;
  ts?: boolean;
  describe?: string;
  dir?: string;
  force?: boolean;
}

function cmdNew(name: string, opts: NewOpts): number {
  const evalRoot = findEvalRoot();
  const outDir = opts.dir ? path.resolve(opts.dir) : evalRoot;
  mkdirSync(outDir, { recursive: true });
  const ext = opts.ts ? ".eval.ts" : ".eval.md";
  const dest = path.join(outDir, `${name}${ext}`);
  if (existsSync(dest) && !opts.force) {
    console.log(`refusing to overwrite ${dest} (pass --force)`);
    return 1;
  }
  const target = opts.target || name;
  const stage =
    opts.kind === "agent" || opts.kind === "skill"
      ? `${opts.kind}: ${target}`
      : "";
  const title = titleCase(name.replace(/-/g, " "));

  if (opts.describe && !opts.ts) {
    writeFileSync(
      dest,
      mdStubTemplate({
        name,
        target,
        kind: opts.kind,
        title,
        summary: opts.describe.split(/\r?\n/)[0]!.trim(),
        description: opts.describe.trim(),
      }),
      "utf-8",
    );
    console.log(`created ${dest} (stub)`);
    console.log("\nNext steps:");
    console.log("  1. review the ## Description");
    console.log(
      `  2. ask an agent to implement ## Setup / ## Act / ## Assert in ${path.basename(
        dest,
      )}`,
    );
    console.log(
      `  3. evalpilot lint ${path.basename(dest)}   # shows [stub] until implemented`,
    );
    return 0;
  }

  const content = opts.ts
    ? tsTemplate({ name, target, kind: opts.kind })
    : mdTemplate({ name, target, kind: opts.kind, title, stage });
  writeFileSync(dest, content, "utf-8");
  console.log(`created ${dest}`);
  console.log("\nNext steps:");
  console.log(`  1. edit the prompt / criteria in ${path.basename(dest)}`);
  console.log(`  2. evalpilot run ${dest}`);
  return 0;
}

function titleCase(text: string): string {
  return text.replace(/\b\w/g, (m) => m.toUpperCase());
}

// ---- run ----------------------------------------------------------------

interface RunOpts {
  tags?: string;
  parallel: string;
  format: string;
  runner?: string;
  open?: boolean;
  gate?: boolean;
  sutTimeout?: string;
}

async function cmdRun(target: string | undefined, opts: RunOpts): Promise<number> {
  const evalRoot = findEvalRoot();
  const tgt = target ? path.resolve(target) : evalRoot;
  if (!existsSync(tgt)) {
    console.log(`nothing to run: ${tgt} does not exist`);
    return 2;
  }

  let specs = await collectSpecs(tgt);
  specs = filterTags(specs, opts.tags);
  if (!specs.length) {
    console.log(
      `no evals found under ${tgt}` +
        (opts.tags ? ` matching tags ${JSON.stringify(opts.tags)}` : ""),
    );
    return 2;
  }

  const sutTimeoutOverride =
    opts.sutTimeout != null && opts.sutTimeout !== ""
      ? Number(opts.sutTimeout)
      : null;
  if (
    sutTimeoutOverride != null &&
    (Number.isNaN(sutTimeoutOverride) || sutTimeoutOverride <= 0)
  ) {
    console.log(`invalid --sut-timeout value: ${opts.sutTimeout}`);
    return 2;
  }

  const report = await runSpecs(specs, {
    parallel: parseInt(opts.parallel, 10) || 1,
    runner: runnerOverride(opts.runner),
    sutTimeout: sutTimeoutOverride,
  });
  const outDir = path.join(evalRoot, "_runs", report.run_id);
  mkdirSync(outDir, { recursive: true });

  const fmts = formats(opts.format);
  const jsonPath = writeJson(report, path.join(outDir, "report.json"));
  writeLatestPointer(evalRoot, outDir);
  let htmlPath: string | null = null;
  if (fmts.has("html")) {
    htmlPath = path.join(outDir, "report.html");
    writeFileSync(htmlPath, renderHtml(report), "utf-8");
  }

  console.log(
    renderTerminal(report, {
      jsonPath: String(jsonPath),
      htmlPath: htmlPath ? String(htmlPath) : null,
    }),
  );

  if (opts.open && htmlPath) openPath(htmlPath);

  if (opts.gate === false) return 0;
  return reportOk(report) ? 0 : 1;
}

// ---- show ---------------------------------------------------------------

interface ShowOpts {
  format: string;
  open?: boolean;
}

function cmdShow(run: string | undefined, opts: ShowOpts): number {
  const reportPath = resolveReport(run);
  if (reportPath === null) {
    console.log("no runs found. Run `evalpilot run` first.");
    return 2;
  }
  const report = readJson(reportPath);
  if (opts.format === "html") {
    const htmlPath = path.join(path.dirname(reportPath), "report.html");
    writeFileSync(htmlPath, renderHtml(report), "utf-8");
    console.log(`wrote ${htmlPath}`);
    if (opts.open) openPath(htmlPath);
  } else {
    console.log(renderTerminal(report, { jsonPath: String(reportPath) }));
  }
  return reportOk(report) ? 0 : 1;
}

// ---- lint ---------------------------------------------------------------

async function cmdLint(
  target: string | undefined,
  opts: { strict?: boolean },
): Promise<number> {
  const tgt = target ? path.resolve(target) : findEvalRoot();
  const specs = await collectSpecs(tgt);
  if (!specs.length) {
    console.log(`no evals found under ${tgt}`);
    return 2;
  }
  let problems = 0;
  let stubs = 0;
  for (const s of specs) {
    const loc = s.spec_path || s.name;
    if (specIsStub(s)) {
      stubs++;
      console.log(`[stub] ${loc}  (${s.name})`);
      console.log(
        "        - described, awaiting implementation; " +
          "ask an agent to implement Act/Assert",
      );
      continue;
    }
    const issues = validateSpec(s);
    if (issues.length) {
      problems++;
      console.log(`[FAIL] ${loc}`);
      for (const i of issues) console.log(`        - ${i}`);
    } else {
      console.log(`[ ok ] ${loc}  (${s.name})`);
    }
  }
  let tail = `\n${specs.length} specs, ${problems} with problems`;
  if (stubs) {
    tail += `, ${stubs} stub${stubs !== 1 ? "s" : ""}`;
    if (opts.strict) tail += " (failing: --strict)";
  }
  console.log(tail);
  if (problems) return 1;
  if (stubs && opts.strict) return 1;
  return 0;
}

// ---- init ---------------------------------------------------------------

function cmdInit(opts: { force?: boolean }): number {
  const repoRoot = findRepoRoot();
  const evalRoot = findEvalRoot(repoRoot);
  const templates = path.join(bundledDataDir(), "templates");
  mkdirSync(evalRoot, { recursive: true });
  const created: string[] = [];

  const entries = fg.sync("**/*", {
    cwd: templates,
    dot: true,
    onlyFiles: true,
  });
  for (const rel of entries) {
    if (rel.includes("__pycache__")) continue;
    const src = path.join(templates, rel);
    // npm strips files literally named `.gitignore` from tarballs, so the
    // bundled template ships as `gitignore`; restore the dot on copy.
    const outRel =
      path.basename(rel) === "gitignore"
        ? path.join(path.dirname(rel), ".gitignore")
        : rel;
    const dst = path.join(evalRoot, outRel);
    if (existsSync(dst) && !opts.force) continue;
    mkdirSync(path.dirname(dst), { recursive: true });
    copyFileSync(src, dst);
    created.push(dst);
  }

  console.log(`evalpilot init -> ${evalRoot}`);
  for (const c of created) console.log(`  created ${path.relative(repoRoot, c)}`);
  if (!created.length)
    console.log("  (nothing to create; pass --force to overwrite)");
  console.log("\nNext steps:");
  console.log(
    "  1. edit examples/hello-agent.eval.md (set a real target) then: evalpilot run",
  );
  console.log(
    "  2. or scaffold your own: evalpilot new my-eval --target my-agent --kind agent",
  );
  console.log("  3. try it offline first: EVALPILOT_RUNNER=mock evalpilot run <file>");
  return 0;
}

// ---- discover -----------------------------------------------------------

function cmdDiscover(opts: { json?: boolean }): number {
  const repoRoot = findRepoRoot();
  const agents = discoverAgents(repoRoot);
  const skills = discoverSkills(repoRoot);
  if (opts.json) {
    console.log(
      JSON.stringify(
        {
          repo_root: repoRoot,
          agents: agents.map((a) => ({ name: a.name, path: a.path })),
          skills: skills.map((s) => ({ name: s.name, path: s.path })),
        },
        null,
        2,
      ),
    );
    return 0;
  }
  console.log(`repo root: ${repoRoot}`);
  console.log(`\nagents (${agents.length}):`);
  for (const a of agents)
    console.log(`  - ${a.name.padEnd(30)} ${path.relative(repoRoot, a.path)}`);
  console.log(`\nskills (${skills.length}):`);
  for (const s of skills)
    console.log(`  - ${s.name.padEnd(30)} ${path.relative(repoRoot, s.path)}`);
  return 0;
}

// ---- metrics ------------------------------------------------------------

interface MetricsOpts {
  check?: boolean;
  verbose?: boolean;
  tail: string;
}

function cmdMetrics(slug: string | undefined, opts: MetricsOpts): number {
  const metricsRoot = findMetricsRoot();
  let series = iterSeries(metricsRoot);
  if (slug) series = series.filter(([s]) => s.includes(slug));
  if (!series.length) {
    console.log(`No metric history under ${metricsRoot}`);
    return 0;
  }

  const tail = parseInt(opts.tail, 10) || 5;
  let anyRegression = false;
  for (const [s, hp] of series) {
    const history: Array<Record<string, any>> = [];
    for (const raw of readFileSync(hp, "utf-8").split(/\r?\n/)) {
      const line = raw.trim();
      if (!line) continue;
      try {
        history.push(JSON.parse(line));
      } catch {
        /* ignore */
      }
    }
    if (!history.length) continue;
    const latest = history[history.length - 1]!;
    const values = history
      .map((r) => r.value)
      .filter((v): v is number => typeof v === "number");
    const regressions = history.filter((r) => r.regressed).length;
    anyRegression = anyRegression || Boolean(latest.regressed);
    const flag = latest.regressed ? "  <-- REGRESSED" : "";
    console.log(`\n${s}${flag}`);
    console.log(
      `  runs=${history.length} latest=${latest.value} ` +
        `baseline=${latest.baseline} ` +
        `min=${values.length ? Math.min(...values) : null} ` +
        `max=${values.length ? Math.max(...values) : null} ` +
        `regressions=${regressions}`,
    );
    if (opts.verbose) {
      for (const r of history.slice(-tail)) {
        console.log(
          `    ${r.ts} ${r.value} ` +
            `(d${r.delta}) ${r.regressed ? "REGRESSED" : ""}`,
        );
      }
    }
  }

  if (opts.check && anyRegression) {
    console.log("\nRegressions detected in latest run.");
    return 1;
  }
  return 0;
}

// ---- helpers ------------------------------------------------------------

function filterTags(specs: EvalSpec[], expr?: string): EvalSpec[] {
  if (!expr) return specs;
  const tokens = expr
    .split(",")
    .map((t) => t.trim())
    .filter(Boolean);
  const includes = new Set(
    tokens.filter((t) => !t.startsWith("-") && !t.startsWith("~")),
  );
  const excludes = new Set(
    tokens
      .filter((t) => t.startsWith("-") || t.startsWith("~"))
      .map((t) => t.slice(1)),
  );
  const out: EvalSpec[] = [];
  for (const s of specs) {
    const tags = new Set(s.tags);
    if (includes.size && ![...includes].some((t) => tags.has(t))) continue;
    if ([...excludes].some((t) => tags.has(t))) continue;
    out.push(s);
  }
  return out;
}

function formats(raw: string): Set<string> {
  const parts = new Set(
    raw
      .split(",")
      .map((p) => p.trim())
      .filter(Boolean),
  );
  if (parts.has("all")) return new Set(["terminal", "html", "json"]);
  return parts.size ? parts : new Set(["terminal", "json"]);
}

function runnerOverride(name?: string): SUTRunner | undefined {
  if (!name) return undefined;
  return getRunner(name);
}

function writeLatestPointer(evalRoot: string, outDir: string): void {
  writeFileSync(
    path.join(evalRoot, "_runs", "latest.txt"),
    path.join(outDir, "report.json"),
    "utf-8",
  );
}

function resolveReport(run?: string): string | null {
  const runsDir = path.join(findEvalRoot(), "_runs");
  if (run) {
    if (existsSync(run) && statSync(run).isFile()) return run;
    const cand = path.join(runsDir, run, "report.json");
    return existsSync(cand) ? cand : null;
  }
  const pointer = path.join(runsDir, "latest.txt");
  if (existsSync(pointer)) {
    const p = readFileSync(pointer, "utf-8").trim();
    if (existsSync(p)) return p;
  }
  const reports = fg
    .sync("*/report.json", { cwd: runsDir, absolute: true })
    .sort();
  return reports.length ? reports[reports.length - 1]! : null;
}

function openPath(target: string): void {
  const url = pathToFileURL(target).href;
  const platform = process.platform;
  try {
    if (platform === "win32") {
      spawn("cmd", ["/c", "start", "", url], { detached: true, stdio: "ignore" });
    } else if (platform === "darwin") {
      spawn("open", [url], { detached: true, stdio: "ignore" });
    } else {
      spawn("xdg-open", [url], { detached: true, stdio: "ignore" });
    }
  } catch {
    /* best-effort */
  }
}

// ---- argument parsing ---------------------------------------------------

/**
 * Read the CLI's own version from the package manifest. Resolves relative to
 * the running module so it works both from the published package (dist/ sits
 * beside package.json) and from the in-repo build. Falls back to "0.0.0" if
 * the manifest cannot be read for any reason.
 */
function readPackageVersion(): string {
  for (const rel of ["../package.json", "./package.json"]) {
    try {
      const raw = readFileSync(new URL(rel, import.meta.url), "utf8");
      const v = JSON.parse(raw).version;
      if (typeof v === "string" && v.length > 0) return v;
    } catch {
      /* try next candidate */
    }
  }
  return "0.0.0";
}

export function buildProgram(): Command {
  const program = new Command();
  program
    .name("evalpilot")
    .description("Author, run, and inspect evals for Copilot agents/skills.")
    .version(readPackageVersion(), "-V, --version", "output the version number");

  program
    .command("new")
    .description("scaffold a new *.eval.md (or *.eval.ts) spec")
    .argument("<name>")
    .option("--target <target>", "agent or skill under test")
    .addOption(
      new Option("--kind <kind>", "spec kind")
        .choices(["agent", "skill", "none"])
        .default("agent"),
    )
    .option("--ts", "scaffold a builder *.eval.ts")
    .option(
      "--describe <text>",
      "description-first: emit a prose-only stub for an agent to implement (markdown only)",
    )
    .option("--dir <dir>", "output directory (default: eval root)")
    .option("--force")
    .action((name: string, opts: NewOpts) => {
      process.exitCode = cmdNew(name, opts);
    });

  program
    .command("run")
    .description("run evals and render results")
    .argument("[target]", "spec file or dir (default: eval root)")
    .option("-t, --tags <expr>", "tag filter, e.g. 'smoke,-slow'")
    .option("--parallel <n>", "concurrent workers", "1")
    .option(
      "--sut-timeout <seconds>",
      "authoritative per-run SUT timeout override; RAISES or lowers each " +
        "spec's frontmatter 'timeout:' (unlike EVALPILOT_SUT_TIMEOUT, which " +
        "only caps/lowers)",
    )
    .option("--format <fmt>", "terminal,html,json,all (default: all)", "all")
    .option("--runner <name>", "SUT runner override (e.g. mock)")
    .option("--open", "open the HTML report")
    .option("--no-gate", "always exit 0 (don't fail on eval failures)")
    .action(async (target: string | undefined, opts: RunOpts) => {
      process.exitCode = await cmdRun(target, opts);
    });

  program
    .command("show")
    .description("re-render a previous run from its JSON")
    .argument("[run]", "run id or report.json (default: latest)")
    .addOption(
      new Option("--format <fmt>", "output format")
        .choices(["terminal", "html"])
        .default("terminal"),
    )
    .option("--open")
    .action((run: string | undefined, opts: ShowOpts) => {
      process.exitCode = cmdShow(run, opts);
    });

  program
    .command("lint")
    .description("validate specs without running the SUT")
    .argument("[target]", "spec file or dir (default: eval root)")
    .option("--strict", "treat description-only stubs as failures (for CI)")
    .action(async (target: string | undefined, opts: { strict?: boolean }) => {
      process.exitCode = await cmdLint(target, opts);
    });

  program
    .command("init")
    .description("scaffold an evals/ tree into this repo")
    .option("--force", "overwrite existing files")
    .action((opts: { force?: boolean }) => {
      process.exitCode = cmdInit(opts);
    });

  program
    .command("discover")
    .description("list discoverable agents and skills")
    .option("--json")
    .action((opts: { json?: boolean }) => {
      process.exitCode = cmdDiscover(opts);
    });

  program
    .command("metrics")
    .description("show metric trends")
    .argument("[slug]", "filter series by substring")
    .option("--check", "exit non-zero if the latest run regressed")
    .option("-v, --verbose")
    .option("--tail <n>", "rows to show with -v", "5")
    .action((slug: string | undefined, opts: MetricsOpts) => {
      process.exitCode = cmdMetrics(slug, opts);
    });

  return program;
}

export async function main(argv?: string[]): Promise<number> {
  const program = buildProgram();
  await program.parseAsync(argv, argv ? { from: "user" } : undefined);
  return process.exitCode ? Number(process.exitCode) : 0;
}

// Entry point when executed as the `evalpilot` bin.
const isMain =
  process.argv[1] &&
  pathToFileURL(process.argv[1]).href === import.meta.url;
if (isMain) {
  main().then((code) => process.exit(code));
}

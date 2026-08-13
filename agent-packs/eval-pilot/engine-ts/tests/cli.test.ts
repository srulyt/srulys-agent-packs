/**
 * CLI-surface tests that don't launch a SUT. Guards the `--version` flag,
 * which regressed to "unknown option" when the program had no `.version()`.
 */

import { readFileSync, realpathSync } from "node:fs";
import { pathToFileURL } from "node:url";
import { describe, expect, it } from "vitest";
import { buildProgram, isMainModule } from "../src/cli.js";

const pkgVersion = JSON.parse(
  readFileSync(new URL("../package.json", import.meta.url), "utf8"),
).version as string;

describe("evalpilot CLI", () => {
  it("exposes its package version via -V/--version", () => {
    const program = buildProgram();
    // commander's Command.version() with no argument returns the set value.
    expect(program.version()).toBe(pkgVersion);
    expect(pkgVersion).toMatch(/^\d+\.\d+\.\d+/);
  });

  it("registers the documented top-level commands", () => {
    const names = buildProgram()
      .commands.map((c) => c.name())
      .sort();
    expect(names).toEqual(
      ["discover", "init", "lint", "metrics", "new", "run", "show"].sort(),
    );
  });

  it("recognizes npm-linked bin paths as the main module", () => {
    const cliPath = realpathSync(new URL("../src/cli.ts", import.meta.url));
    expect(isMainModule(cliPath, pathToFileURL(cliPath).href)).toBe(true);
    expect(isMainModule(undefined, pathToFileURL(cliPath).href)).toBe(false);
  });
});

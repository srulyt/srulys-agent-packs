/**
 * CLI-surface tests that don't launch a SUT. Guards the `--version` flag,
 * which regressed to "unknown option" when the program had no `.version()`.
 */

import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";
import { buildProgram } from "../src/cli.js";

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
});

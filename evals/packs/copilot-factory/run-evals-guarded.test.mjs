import assert from "node:assert/strict";
import { mkdtempSync, mkdirSync, rmSync, writeFileSync } from "node:fs";
import os from "node:os";
import path from "node:path";
import test from "node:test";

import {
  diffSnapshots,
  snapshotTree,
} from "../../../agent-packs/copilot-factory/.github/skills/agent-builder/scripts/run-evals-guarded.mjs";
import {
  validateFixablePath,
} from "../../../agent-packs/copilot-factory/.github/skills/agent-builder/scripts/validate-factory-paths.mjs";

test("repository snapshot detects create, modify, and delete writes", () => {
  const root = mkdtempSync(path.join(os.tmpdir(), "factory-guard-test-"));
  try {
    mkdirSync(path.join(root, "nested"));
    writeFileSync(path.join(root, "a.txt"), "before");
    writeFileSync(path.join(root, "delete.txt"), "delete");
    const before = snapshotTree(root);
    writeFileSync(path.join(root, "a.txt"), "after");
    writeFileSync(path.join(root, "nested", "new.txt"), "new");
    rmSync(path.join(root, "delete.txt"));
    assert.deepEqual(diffSnapshots(before, snapshotTree(root)), [
      "a.txt", "delete.txt", "nested/new.txt",
    ]);
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
});

test("fixable path validator permits target .github files only", () => {
  const pack = "example-pack";
  for (const valid of [
    `agent-packs/${pack}/.github/agents/main.agent.md`,
    `agent-packs/${pack}/.github/skills/example/SKILL.md`,
  ]) assert.equal(validateFixablePath(valid, pack), true, valid);
  for (const invalid of [
    `agent-packs/other/.github/agents/main.agent.md`,
    `agent-packs/${pack}/.github/../README.md`,
    `C:/repo/agent-packs/${pack}/.github/agents/main.agent.md`,
    `.github/agents/main.agent.md`,
  ]) assert.equal(validateFixablePath(invalid, pack), false, invalid);
});

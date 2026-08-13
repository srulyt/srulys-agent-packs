import { Eval } from "evalpilot";
import { spawnSync } from "node:child_process";
export default new Eval("story-telling-agent-pptx-reliability", { target: "story-telling-agent", kind: "none", tags: ["pack","structural","tooling"] })
  .check("real normalized second render matches", (ctx) => {
    const r=spawnSync("python",["evals/packs/story-telling-agent/fixtures/subsystem_checks.py","render"],{cwd:ctx.root,encoding:"utf8",timeout:120000});
    return r.status===0 ? true : [false,r.stdout+r.stderr];
  })
  .check("QA inspects rendered outputs and validates receipts", (ctx) => {
    const r=spawnSync("python",["evals/packs/story-telling-agent/fixtures/subsystem_checks.py","qa"],{cwd:ctx.root,encoding:"utf8",timeout:120000});
    return r.status===0 ? true : [false,r.stdout+r.stderr];
  })
  .check("rendered contrast, overflow, crop, and overlap defects fail", (ctx) => {
    const r=spawnSync("python",["evals/packs/story-telling-agent/fixtures/subsystem_checks.py","qa-defects"],{cwd:ctx.root,encoding:"utf8",timeout:120000});
    return r.status===0 ? true : [false,r.stdout+r.stderr];
  })
  .build();

import { Eval } from "evalpilot";
import { spawnSync } from "node:child_process";
export default new Eval("story-telling-agent-chart-integrity", { target: "story-telling-agent", kind: "none", tags: ["pack","structural","tooling"] })
  .check("chart relationship and policy validation executes", (ctx) => {
    const r=spawnSync("python",["evals/packs/story-telling-agent/fixtures/subsystem_checks.py","contract"],{cwd:ctx.root,encoding:"utf8"});
    return r.status===0 ? true : [false,r.stdout+r.stderr];
  })
  .check("matrix, image/native modes, colors, explicit axes, and XY scatter render", (ctx) => {
    const r=spawnSync("python",["evals/packs/story-telling-agent/fixtures/subsystem_checks.py","render-variants"],{cwd:ctx.root,encoding:"utf8",timeout:120000});
    return r.status===0 ? true : [false,r.stdout+r.stderr];
  })
  .check("every allowed chart relationship/type/mode renders and every invalid combination rejects", (ctx) => {
    const r=spawnSync("python",["evals/packs/story-telling-agent/fixtures/subsystem_checks.py","all-charts"],{cwd:ctx.root,encoding:"utf8",timeout:240000});
    return r.status===0 ? true : [false,r.stdout+r.stderr];
  })
  .build();

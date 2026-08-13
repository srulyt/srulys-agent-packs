import { Eval } from "evalpilot";
import { spawnSync } from "node:child_process";
export default new Eval("story-telling-agent-marp-pptx-parity", { target: "story-telling-agent", kind: "none", tags: ["pack","structural","tooling"] })
  .check("rendered semantic parity executes", (ctx) => {
    const r=spawnSync("python",["evals/packs/story-telling-agent/fixtures/subsystem_checks.py","render"],{cwd:ctx.root,encoding:"utf8",timeout:120000});
    return r.status===0 ? true : [false,r.stdout+r.stderr];
  })
  .build();

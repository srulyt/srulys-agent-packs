import { Eval } from "evalpilot";
import { spawnSync } from "node:child_process";
export default new Eval("story-telling-agent-atomic-publication", { target: "story-telling-agent", kind: "none", tags: ["pack","structural","tooling"] })
  .check("lineage-bound atomic publish and pointer repair", (ctx) => {
    const r=spawnSync("python",["evals/packs/story-telling-agent/fixtures/subsystem_checks.py","publication"],{cwd:ctx.root,encoding:"utf8"});
    return r.status===0 ? true : [false,r.stdout+r.stderr];
  })
  .build();

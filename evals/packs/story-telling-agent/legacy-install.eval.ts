import { Eval } from "evalpilot";
import { spawnSync } from "node:child_process";
export default new Eval("story-telling-agent-legacy-install", { target: "story-telling-agent", kind: "none", tags: ["pack","structural","tooling"] })
  .check("generated layout installs and checks cleanly", (ctx) => {
    const r=spawnSync("python",["evals/packs/story-telling-agent/fixtures/subsystem_checks.py","legacy"],{cwd:ctx.root,encoding:"utf8"});
    return r.status===0 ? true : [false,r.stdout+r.stderr];
  })
  .check("no canonical duplicate tree", (ctx) => (ctx.glob('agent-packs/story-telling-agent/.github/**/*').length === 0) ? true : [false, "no canonical duplicate tree failed"])
  .build();

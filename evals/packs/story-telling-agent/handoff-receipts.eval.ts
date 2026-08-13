import { Eval } from "evalpilot";
import { spawnSync } from "node:child_process";
export default new Eval("story-telling-agent-handoff-receipts", { target: "story-telling-agent", kind: "none", tags: ["pack","structural","tooling"] })
  .check("valid and invalid evidence produce truthful receipts", (ctx) => {
    const r=spawnSync("python",["evals/packs/story-telling-agent/fixtures/subsystem_checks.py","receipt"],{cwd:ctx.root,encoding:"utf8"});
    return r.status===0 ? true : [false,r.stdout+r.stderr];
  })
  .check("invalid inspected staged output produces an invalid receipt", (ctx) => {
    const r=spawnSync("python",["evals/packs/story-telling-agent/fixtures/subsystem_checks.py","receipt-diagnostics"],{cwd:ctx.root,encoding:"utf8",timeout:120000});
    return r.status===0 ? true : [false,r.stdout+r.stderr];
  })
  .check("every gated transition requires its exact complete receipt and artifact set", (ctx) => {
    const r=spawnSync("python",["evals/packs/story-telling-agent/fixtures/subsystem_checks.py","receipt-gates"],{cwd:ctx.root,encoding:"utf8",timeout:120000});
    return r.status===0 ? true : [false,r.stdout+r.stderr];
  })
  .build();

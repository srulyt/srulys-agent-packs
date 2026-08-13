import { Eval } from "evalpilot";
import { spawnSync } from "node:child_process";
export default new Eval("story-telling-agent-contract-renderability", { target: "story-telling-agent", kind: "none", tags: ["pack","structural","tooling"] })
  .check("schema and cross-document behavior", (ctx) => {
    const r=spawnSync("python",["evals/packs/story-telling-agent/fixtures/subsystem_checks.py","contract"],{cwd:ctx.root,encoding:"utf8"});
    return r.status===0 ? true : [false,r.stdout+r.stderr];
  })
  .check("sibling rendering and reproducibility", (ctx) => {
    const r=spawnSync("python",["evals/packs/story-telling-agent/fixtures/subsystem_checks.py","render"],{cwd:ctx.root,encoding:"utf8",timeout:120000});
    return r.status===0 ? true : [false,r.stdout+r.stderr];
  })
  .check("all fourteen schema recipes validate and render through both projections", (ctx) => {
    const r=spawnSync("python",["evals/packs/story-telling-agent/fixtures/subsystem_checks.py","all-recipes"],{cwd:ctx.root,encoding:"utf8",timeout:240000});
    return r.status===0 ? true : [false,r.stdout+r.stderr];
  })
  .build();

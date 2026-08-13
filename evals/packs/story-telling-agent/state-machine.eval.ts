import { Eval } from "evalpilot";
import { spawnSync } from "node:child_process";
export default new Eval("story-telling-agent-state-machine", { target: "story-telling-agent", kind: "none", tags: ["pack","structural","tooling"] })
  .check("legal transition and schema-safe rejection", (ctx) => {
    const r=spawnSync("python",["evals/packs/story-telling-agent/fixtures/subsystem_checks.py","state"],{cwd:ctx.root,encoding:"utf8"});
    return r.status===0 ? true : [false,r.stdout+r.stderr];
  })
  .check("changed input invalidation documented", (ctx) => ((ctx.read('agent-packs/story-telling-agent/agents/story-orchestrator.agent.md')||'').includes('explicitly mark every dependent')) ? true : [false, "changed input invalidation documented failed"])
  .check("publication destination is immutable and event backed", (ctx) => {
    const schema = ctx.read('agent-packs/story-telling-agent/schemas/v3/state.schema.json') || '';
    const prompt = ctx.read('agent-packs/story-telling-agent/agents/story-orchestrator.agent.md') || '';
    return (['publication_destination','intake_sha256','effective_output_dir','effective_destination_event_id'].every(x => schema.includes(x)) && prompt.includes('Never mutate validated `intake.json`')) ? true : [false, "immutable event-backed publication destination missing"];
  })
  .build();

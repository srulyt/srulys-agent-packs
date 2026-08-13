import { Eval } from "evalpilot";
export default new Eval("story-telling-agent-plugin-shape", { target: "story-telling-agent", kind: "none", tags: ["pack","structural","tooling"] })
  .check("four canonical agents", (ctx) => (ctx.glob('agent-packs/story-telling-agent/agents/*.agent.md').length === 4) ? true : [false, "four canonical agents failed"])
  .check("twelve canonical skills", (ctx) => (ctx.glob('agent-packs/story-telling-agent/skills/*/SKILL.md').length === 12) ? true : [false, "twelve canonical skills failed"])
  .check("plugin metadata resolves canonical roots", (ctx) => {
    try {
      const p = JSON.parse(ctx.read('agent-packs/story-telling-agent/plugin.json') || '{}');
      return p.name === 'story-telling-agent' && Array.isArray(p.agents) && p.agents.length===4 && p.skills === './skills/'
        ? true : [false, "plugin metadata does not expose canonical agent/skill roots"];
    } catch { return [false, "plugin metadata is invalid JSON"]; }
  })
  .check("orchestrator flags", (ctx) => ((ctx.read('agent-packs/story-telling-agent/agents/story-orchestrator.agent.md')||'').includes('disable-model-invocation: true')) ? true : [false, "orchestrator flags failed"])
  .check("critic receipt fence", (ctx) => ((ctx.read('agent-packs/story-telling-agent/agents/deck-critic.agent.md')||'').includes('```validation-receipts-json')) ? true : [false, "critic validation-receipts-json fence failed"])
  .build();

import { Eval } from "evalpilot";
import { spawnSync } from "node:child_process";
import { cpSync, mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
export default new Eval("story-telling-agent-marketplace-install", { target: "story-telling-agent", kind: "none", tags: ["pack","structural","tooling"] })
  .check("live-aware update is duplicate-safe and idempotent", (ctx) => {
    const dir=mkdtempSync(join(tmpdir(),"story-market-")); const target=join(dir,"marketplace.json");
    writeFileSync(target,JSON.stringify({plugins:[{name:"alpha",source:"./a"},{name:"story-telling-agent",source:"./old"},{name:"story-telling-agent",source:"./older"}]},null,2));
    const script="agent-packs/story-telling-agent/scripts/update-marketplace.py";
    const first=spawnSync("python",[script,"--target",target,"--apply"],{cwd:ctx.root,encoding:"utf8"});
    const second=spawnSync("python",[script,"--target",target,"--apply"],{cwd:ctx.root,encoding:"utf8"});
    const plugins=JSON.parse(readFileSync(target,"utf8")).plugins;
    const matches=plugins.filter((p:any)=>p.name==="story-telling-agent");
    const durability=JSON.parse(first.stdout);
    const directoryDurable=durability.parent_directory_fsync.status==="completed" ||
      (process.platform==="win32" && durability.parent_directory_fsync.status==="unavailable");
    return first.status===0 && second.status===0 && durability.post_replace_verified===true &&
      durability.after_sha256.startsWith("sha256:") && directoryDurable &&
      matches.length===1 && matches[0].source==="./agent-packs/story-telling-agent"
      ? true : [false,first.stdout+first.stderr+second.stdout+second.stderr];
  })
  .check("dry-run, source collision, and stale-live guards are fail closed", (ctx) => {
    const dir=mkdtempSync(join(tmpdir(),"story-market-negative-")); const target=join(dir,"marketplace.json");
    const original=JSON.stringify({plugins:[{name:"other",source:"./agent-packs/story-telling-agent"}]},null,2)+"\n";
    writeFileSync(target,original);
    const script="agent-packs/story-telling-agent/scripts/update-marketplace.py";
    const collision=spawnSync("python",[script,"--target",target,"--apply"],{cwd:ctx.root,encoding:"utf8"});
    writeFileSync(target,JSON.stringify({plugins:[{name:"alpha",source:"./a"}]},null,2)+"\n");
    const before=readFileSync(target,"utf8");
    const dry=spawnSync("python",[script,"--target",target],{cwd:ctx.root,encoding:"utf8"});
    const stale=spawnSync("python",[script,"--target",target,"--expected-sha256","sha256:"+"0".repeat(64),"--apply"],{cwd:ctx.root,encoding:"utf8"});
    return collision.status!==0 && dry.status===0 && stale.status!==0 && readFileSync(target,"utf8")===before
      ? true : [false,collision.stdout+collision.stderr+dry.stdout+dry.stderr+stale.stdout+stale.stderr];
  })
  .check("session application updater verifies replacement bytes and directory durability", (ctx) => {
    const dir=mkdtempSync(join(tmpdir(),"story-market-session-")); const target=join(dir,"marketplace.json");
    writeFileSync(target,JSON.stringify({plugins:[]},null,2)+"\n");
    const script=".copilot-factory/sessions/2026-08-12-c3f8a61d/artifacts/marketplace-registration.apply.py";
    const applied=spawnSync("python",[script,"--target",target,"--apply"],{cwd:ctx.root,encoding:"utf8"});
    const result=applied.status===0 ? JSON.parse(applied.stdout) : {};
    const directoryDurable=result.parent_directory_fsync?.status==="completed" ||
      (process.platform==="win32" && result.parent_directory_fsync?.status==="unavailable");
    return applied.status===0 && result.post_replace_verified===true && result.applied===true &&
      result.after_sha256.startsWith("sha256:") && directoryDurable
      ? true : [false,applied.stdout+applied.stderr];
  })
  .check("Copilot discovers and installs from an isolated temporary marketplace", (ctx) => {
    const root=mkdtempSync(join(tmpdir(),"story-copilot-market-"));
    try {
      const repo=join(root,"market"); const home=join(root,"home");
      mkdirSync(join(repo,".github","plugin"),{recursive:true});
      mkdirSync(join(repo,"agent-packs"),{recursive:true});
      cpSync(join(ctx.root,"agent-packs","story-telling-agent"),join(repo,"agent-packs","story-telling-agent"),{recursive:true});
      writeFileSync(join(repo,".github","plugin","marketplace.json"),JSON.stringify({
        name:"story-fixture-market", owner:{name:"Fixture"},
        plugins:[{name:"story-telling-agent",source:"./agent-packs/story-telling-agent"}],
      },null,2));
      const run=(command:string,args:string[],env=process.env)=>spawnSync(command,args,{
        cwd:repo,encoding:"utf8",env,shell:process.platform==="win32",
      });
      for (const args of [["init","--quiet"],["config","user.email","fixture@example.invalid"],["config","user.name","Fixture"],["add","."],["commit","--quiet","-m","fixture"]]) {
        const result=run("git",args); if(result.status!==0) return [false,result.stdout+result.stderr];
      }
      const env={...process.env,HOME:home,USERPROFILE:home,APPDATA:join(home,"AppData","Roaming")};
      mkdirSync(env.APPDATA,{recursive:true});
      const add=run("copilot",["plugin","marketplace","add",repo],env);
      const browse=run("copilot",["plugin","marketplace","browse","story-fixture-market"],env);
      const install=run("copilot",["plugin","install","story-telling-agent@story-fixture-market"],env);
      const list=run("copilot",["plugin","list"],env);
      const evidence=[add,browse,install,list].map(x=>x.stdout+x.stderr).join("\n");
      return [add,browse,install,list].every(x=>x.status===0) &&
        browse.stdout.includes("story-telling-agent") &&
        install.stdout.toLowerCase().includes("installed successfully") &&
        list.stdout.includes("story-telling-agent@story-fixture-market")
        ? true : [false,evidence];
    } finally {
      rmSync(root,{recursive:true,force:true});
    }
  })
  .build();

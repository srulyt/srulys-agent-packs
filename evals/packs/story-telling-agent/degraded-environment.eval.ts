import { Eval } from "evalpilot";
import { spawnSync } from "node:child_process";
export default new Eval("story-telling-agent-degraded-environment", { target: "story-telling-agent", kind: "none", tags: ["pack","structural","tooling"] })
  .check("preflight reports capabilities without mutation", (ctx) => {
    const r=spawnSync("python",["agent-packs/story-telling-agent/scripts/preflight.py","--json","--require-visual-qa"],{cwd:ctx.root,encoding:"utf8"});
    try {
      const out=JSON.parse(r.stdout);
      const office = out.capabilities.libreoffice;
      const safeWindowsCli = process.platform !== "win32" ||
        (!office.available && String(office.disabled_reason).includes("printer dialogs"));
      return out.installs_performed===false && out.network_used===false && office && out.capabilities.pdftoppm && safeWindowsCli
        ? true : [false,r.stdout+r.stderr];
    } catch { return [false,r.stdout+r.stderr]; }
  })
  .check("LibreOffice automation is isolated and cannot open printer UI", (ctx) => {
    const common = ctx.read("agent-packs/story-telling-agent/scripts/common.py") ?? "";
    const inspect = ctx.read("agent-packs/story-telling-agent/scripts/inspect_deck.py") ?? "";
    for (const required of [
      "SAL_DISABLE_SYNCHRONOUS_PRINTER_DETECTION",
      "SAL_USE_VCLPLUGIN",
      "-env:UserInstallation=",
      "--nodefault",
      "--norestore",
      "CREATE_NO_WINDOW",
    ]) {
      if (!common.includes(required)) return [false, `common.py missing ${required}`];
    }
    return inspect.includes("libreoffice_headless_command")
      ? true : [false, "inspect_deck.py bypasses isolated LibreOffice command"];
  })
  .build();

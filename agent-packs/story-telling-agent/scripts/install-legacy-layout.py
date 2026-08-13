import argparse,hashlib,json,shutil
from pathlib import Path
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(); p.add_argument("--target",default="."); p.add_argument("--check",action="store_true"); p.add_argument("--force",action="store_true"); a=p.parse_args(); root=Path(__file__).resolve().parents[1]; target=Path(a.target); manifest={}
 mappings=[(root/"agents",target/".github/agents"),(root/"skills",target/".github/skills")]
 expected={str((dst/f.relative_to(src)).relative_to(target)):sha(f) for src,dst in mappings for f in src.rglob("*") if f.is_file() and (f.suffix==".md" or f.name=="SKILL.md")}
 mf=target/".github/story-telling-agent-legacy-manifest.json"
 if a.check:
  actual=json.loads(mf.read_text()) if mf.exists() else {}; ok=actual.get("files")==expected and all((target/k).exists() and sha(target/k)==v for k,v in expected.items()); print(json.dumps({"valid":ok,"files":len(expected)})); return 0 if ok else 1
 for rel,digest in expected.items():
  parts=Path(rel).parts
  src=root/parts[1]/Path(*parts[2:]); dst=target/rel
  if dst.exists() and not a.force: raise SystemExit(f"refusing overwrite: {dst}")
  dst.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(src,dst)
 mf.parent.mkdir(parents=True,exist_ok=True); mf.write_text(json.dumps({"source":"story-telling-agent/3.0","files":expected},indent=2)+"\n"); return 0
if __name__=="__main__": raise SystemExit(main())

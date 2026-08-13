import argparse,json,shutil,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from common import dump,sha_file
def main():
 p=argparse.ArgumentParser(); p.add_argument("--v2-root",required=True); p.add_argument("--v3-run",required=True); a=p.parse_args(); src=Path(a.v2_root).resolve(); dst=Path(a.v3_run).resolve(); dst.mkdir(parents=True,exist_ok=True); results=[]
 patterns=("context.md","proposal.md",".png",".jpg",".jpeg",".svg")
 files=sorted([x for x in src.rglob("*") if x.is_file() and (x.name in patterns or x.suffix.lower() in patterns)])
 for f in files:
  rel=f.relative_to(src); out=dst/"migrated"/rel; before=sha_file(f)
  status="copied"
  if out.exists():
   status="unchanged" if sha_file(out)==before else "conflict"
  if status=="copied":
   out.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(f,out)
  results.append({"source":str(f),"source_relative":rel.as_posix(),"source_sha256":before,"destination":str(out),"destination_sha256":sha_file(out) if out.exists() else None,"status":status})
 report={"schema_version":"3.0","status":"restart-required","reason":"v2 state is not resumable under v3 receipts","source_root":str(src),"destination_root":str(dst),"results":results,"counts":{k:sum(x["status"]==k for x in results) for k in ("copied","unchanged","conflict")}}
 dump(dst/"migration-report.json",report); print(json.dumps(report,indent=2)); return 2 if report["counts"]["conflict"] else 0
if __name__=="__main__": raise SystemExit(main())

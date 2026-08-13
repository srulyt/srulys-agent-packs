"""Checksum-pinned, event-bound, same-filesystem publication with rollback evidence."""
import argparse, datetime, hashlib, json, os, shutil, sys, tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from common import canonical, dump, load, sha_bytes, sha_file
from validate_contract import schema_validate, semantic_validate
ROOT=Path(__file__).resolve().parents[1]
def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def fsync_dir(p):
 try:
  fd=os.open(str(p),os.O_RDONLY); os.fsync(fd); os.close(fd)
 except (OSError,AttributeError): pass
def surface(dest,names):
 rows=[]
 for rel in sorted(set(names+["current.json"])):
  p=dest/rel; rows.append({"name":rel,"exists":p.exists(),"kind":"directory" if p.is_dir() else "file" if p.is_file() else None,"size":p.stat().st_size if p.is_file() else None,"mtime_ns":p.stat().st_mtime_ns if p.exists() else None,"sha256":sha_file(p) if p.is_file() else None})
 return rows
def fingerprint(rows): return sha_bytes(canonical(rows))
def fail(result,msg,code):
 result.update({"atomic_result":"not-started","error":msg,"rollback":{"attempted":False,"status":"not-needed","evidence":[]}}); print(json.dumps(result,indent=2)); return code
def receipt_integrity(receipt, qa_path, manifest_sha, acceptance, state):
 diagnostics=receipt.get("diagnostics")
 if not isinstance(diagnostics,list): return "QA receipt diagnostics are absent"
 expected_hash=sha_bytes(canonical(diagnostics))
 if receipt.get("diagnostics_hash")!=expected_hash or receipt.get("diagnostic_count")!=len(diagnostics):
  return "QA receipt diagnostic hash/count mismatch"
 expected_valid=not diagnostics
 if receipt.get("valid") is not expected_valid or receipt.get("diagnostic_class")!=("none" if expected_valid else "producer-artifact-invalid"):
  return "QA receipt validity/diagnostic class mismatch"
 schema_path=ROOT/"schemas/v3/qa-report.schema.json"
 if receipt.get("schema_path")!=str(schema_path.resolve()) or receipt.get("schema_sha256")!=sha_file(schema_path):
  return "QA receipt schema lineage mismatch"
 qa=load(qa_path)
 if receipt.get("run_id")!=qa.get("run_id") or receipt.get("handoff_id")!=qa.get("handoff_id") or qa.get("run_id")!=state.get("run_id"):
  return "QA receipt run/handoff lineage mismatch"
 core={k:receipt.get(k) for k in ("run_id","handoff_id","artifact_kind","artifact_path","artifact_sha256","schema_sha256","producer_agent","validator_agent","validator_operation","diagnostics_hash","inspection_profile")}
 if receipt.get("receipt_id")!=sha_bytes(canonical(core)):
  return "QA receipt deterministic identity mismatch"
 if receipt.get("superseded") or receipt.get("inspection_profile") is not None:
  return "QA receipt is superseded or uses an inapplicable inspection profile"
 if receipt.get("render_manifest_sha256")!=manifest_sha:
  return "QA receipt render-manifest lineage mismatch"
 gate=state.get("publication_gate")
 if gate=="pass":
  if receipt.get("accepted_qa_event_id")!=acceptance.get("event_id") or receipt.get("accepted_residual_event_id") is not None:
   return "QA receipt pass-acceptance binding mismatch"
 else:
  if receipt.get("accepted_residual_event_id")!=acceptance.get("event_id") or receipt.get("accepted_qa_event_id") is not None:
   return "QA receipt residual-acceptance binding mismatch"
 if receipt.get("receipt_id") not in state.get("validation_receipt_ids",[]):
  return "QA receipt is not registered in state"
 if set(acceptance.get("receipt_ids",[]))!={receipt.get("receipt_id")}:
  return "acceptance event does not bind the exact QA receipt"
 return None
def main():
 p=argparse.ArgumentParser(); p.add_argument("--destination",required=True); p.add_argument("--manifest",required=True); p.add_argument("--preflight",action="store_true"); p.add_argument("--policy",choices=["fail","replace"],default="fail"); p.add_argument("--expected-fingerprint"); p.add_argument("--json-stdout",action="store_true"); p.add_argument("--qa-report"); p.add_argument("--qa-receipt"); p.add_argument("--acceptance-event"); p.add_argument("--destination-event"); p.add_argument("--intake-sha256"); p.add_argument("--state"); p.add_argument("--failpoint",choices=["post-rename","pointer-write"],help=argparse.SUPPRESS); a=p.parse_args()
 dest=Path(a.destination).resolve(); manifest_path=Path(a.manifest).resolve(); m=load(manifest_path); entries=[x for x in m["outputs"] if x["status"]=="rendered"]; names=[Path(x["path"]).name for x in entries]+["render-manifest.json"]
 rows=surface(dest,names); fp=fingerprint(rows); collisions=[x["name"] for x in rows if x["exists"]]
 result={"destination":str(dest),"requested_files":sorted(names),"status":"collision" if collisions else "clear","colliding_names":collisions,"metadata_fingerprint":fp,"observed_at":now(),"required_policy":"replace" if collisions else "none","surface":rows}
 if a.preflight: print(json.dumps(result,indent=2)); return 0
 if not all((a.expected_fingerprint,a.qa_report,a.qa_receipt,a.acceptance_event,a.destination_event,a.intake_sha256,a.state)): return fail(result,"publish requires preflight fingerprint, QA report/receipt, acceptance event, destination event, intake checksum, and state",4)
 if a.expected_fingerprint!=fp: return fail(result,"destination changed since preflight",5)
 if collisions and a.policy!="replace": return fail(result,"collision policy does not authorize replacement",6)
 # Verify frozen bytes before the first mutation.
 for x in entries:
  f=Path(x["path"]).resolve()
  if not f.is_file() or sha_file(f)!=x["sha256"]: return fail(result,f"staged checksum mismatch: {f}",7)
 manifest_sha=sha_file(manifest_path); qa=load(a.qa_report); receipt=load(a.qa_receipt); event=load(a.acceptance_event); devent=load(a.destination_event); state=load(a.state)
 qa_errors=schema_validate(qa,load(ROOT/"schemas/v3/qa-report.schema.json"))+semantic_validate("qa-report",qa)
 receipt_errors=schema_validate(receipt,load(ROOT/"schemas/v3/validation-receipt.schema.json"))
 state_errors=schema_validate(state,load(ROOT/"schemas/v3/state.schema.json"))
 if qa_errors or receipt_errors or state_errors: return fail(result,"QA report, receipt, or state fails schema/semantic validation",8)
 expected_acceptance=state.get("residual_acceptance_event_id") if state.get("phase")=="publishing-residual" else state.get("qa_acceptance_event_id")
 if event.get("event_id")!=expected_acceptance: return fail(result,"acceptance event identity does not match publishing state",8)
 if not any(x.get("event_id")==event.get("event_id") and x==event for x in state.get("events",[])): return fail(result,"acceptance event is absent or differs from state history",8)
 if receipt.get("artifact_kind")!="qa-report" or receipt.get("artifact_sha256")!=sha_file(a.qa_report) or receipt.get("artifact_path")!=str(Path(a.qa_report).resolve()) or receipt.get("producer_agent")!="deck-critic" or receipt.get("validator_agent")!="deck-composer" or receipt.get("validator_operation")!="publish": return fail(result,"independent QA receipt artifact identity/operation/checksum is invalid",8)
 receipt_error=receipt_integrity(receipt,a.qa_report,manifest_sha,event,state)
 if receipt_error: return fail(result,receipt_error,8)
 if qa.get("verdict") not in ("pass","unverified-needs-user"): return fail(result,"QA verdict does not authorize publication",8)
 unresolved={x["id"] for x in qa.get("findings",[]) if x["severity"]=="blocking"}; accepted=set(event.get("accepted_finding_ids",[]))
 if qa["verdict"]!="pass" and not unresolved.issubset(accepted): return fail(result,"acceptance event does not cover unresolved findings",8)
 if event.get("render_manifest_sha256")!=manifest_sha: return fail(result,"acceptance event is not bound to frozen render manifest",8)
 if state.get("publication_manifest_sha256")!=manifest_sha or state.get("publication_gate") not in ("pass","residual"): return fail(result,"state publication lineage does not bind frozen manifest",8)
 state_set={(Path(x["path"]).name,x["sha256"]) for x in state.get("staging_manifest",[]) if x["status"] in ("staged","accepted")}
 expected_set={(Path(x["path"]).name,x["sha256"]) for x in entries}
 if state_set!=expected_set: return fail(result,"state staging manifest does not equal complete deliverable set",8)
 if devent.get("destination")!=str(dest) or devent.get("intake_sha256")!=a.intake_sha256: return fail(result,"effective destination event/intake lineage mismatch",8)
 if state["publication_destination"]["effective_destination_event_id"]!=devent.get("event_id") or not any(x.get("event_id")==devent.get("event_id") and x==devent for x in state.get("events",[])): return fail(result,"destination event is absent or differs from state history",8)
 pub_id=hashlib.sha256(canonical({"manifest":manifest_sha,"qa":sha_file(a.qa_report),"acceptance_event":event.get("event_id"),"deliverables":sorted(expected_set),"destination_event":devent.get("event_id")})).hexdigest()[:20]
 versions=dest/"versions"; dest.mkdir(parents=True,exist_ok=True); versions.mkdir(exist_ok=True); fsync_dir(dest)
 final=versions/pub_id
 if final.exists():
  committed_manifest=final/"render-manifest.json"
  good=all((final/Path(x["path"]).name).is_file() and sha_file(final/Path(x["path"]).name)==x["sha256"] for x in entries)
  good=good and committed_manifest.is_file() and sha_file(committed_manifest)==manifest_sha
  if good:
   try:
    frozen=load(committed_manifest)
    good=not schema_validate(frozen,load(ROOT/"schemas/v3/render-manifest.schema.json"))
    good=good and frozen==m
   except Exception:
    good=False
  if not good: return fail(result,"existing immutable version has mismatched content",9)
  pointer={"schema_version":"3.0","publication_id":pub_id,"version_path":str(final),"render_manifest_sha256":manifest_sha,"qa_report_sha256":sha_file(a.qa_report),"acceptance_event_id":event.get("event_id"),"destination_event_id":devent.get("event_id"),"published_at":now()}
  current=dest/"current.json"
  if not current.is_file() or any(load(current).get(k)!=pointer[k] for k in pointer if k!="published_at"):
   ptr_tmp=dest/(".current."+pub_id+".tmp"); dump(ptr_tmp,pointer); os.replace(ptr_tmp,current); fsync_dir(dest)
  if any(load(current).get(k)!=pointer[k] for k in pointer if k!="published_at"): return fail(result,"committed version pointer repair failed",9)
  result.update({"atomic_result":"committed-existing","publication_id":pub_id,"version_path":str(final),"current_pointer":str(current),"render_manifest_sha256":manifest_sha,"rollback":{"attempted":False,"status":"not-needed","evidence":[]}}); print(json.dumps(result,indent=2)); return 0
 tmp=Path(tempfile.mkdtemp(prefix="."+pub_id+"-",dir=versions)); journal={"schema_version":"3.0","publication_id":pub_id,"status":"preparing","manifest_sha256":manifest_sha,"pre_checksums":{},"post_checksums":{},"steps":[],"rollback":{"attempted":False,"status":"not-needed","evidence":[]}}
 old_pointer=(dest/"current.json").read_bytes() if (dest/"current.json").is_file() else None; renamed=False; pointer_swapped=False
 try:
  for x in entries:
   src=Path(x["path"]).resolve(); target=tmp/src.name; journal["pre_checksums"][src.name]=x["sha256"]; shutil.copy2(src,target)
   if sha_file(target)!=x["sha256"]: raise RuntimeError(f"copy verification failed: {src.name}")
   journal["post_checksums"][src.name]=sha_file(target); journal["steps"].append({"action":"copy","file":src.name,"status":"verified"})
  shutil.copy2(manifest_path,tmp/"render-manifest.json"); journal["pre_checksums"]["render-manifest.json"]=manifest_sha; journal["post_checksums"]["render-manifest.json"]=sha_file(tmp/"render-manifest.json")
  journal["status"]="prepared"; dump(tmp/"publication-journal.json",journal)
  for f in tmp.iterdir():
   if f.is_file():
    with f.open("r+b") as h: h.flush(); os.fsync(h.fileno())
  fsync_dir(tmp); os.replace(tmp,final); renamed=True; fsync_dir(versions)
  if a.failpoint=="post-rename": raise RuntimeError("injected post-rename failure")
  pointer={"schema_version":"3.0","publication_id":pub_id,"version_path":str(final),"render_manifest_sha256":manifest_sha,"qa_report_sha256":sha_file(a.qa_report),"acceptance_event_id":event.get("event_id"),"destination_event_id":devent.get("event_id"),"published_at":now()}
  ptr_tmp=dest/(".current."+pub_id+".tmp"); dump(ptr_tmp,pointer); os.replace(ptr_tmp,dest/"current.json"); pointer_swapped=True; fsync_dir(dest)
  if a.failpoint=="pointer-write": raise RuntimeError("injected pointer-write failure")
  if load(dest/"current.json")["publication_id"]!=pub_id: raise RuntimeError("pointer verification failed")
  journal["status"]="committed"; journal["steps"].append({"action":"pointer-swap","file":"current.json","status":"verified"}); dump(final/"publication-journal.json",journal)
  result.update({"atomic_result":"committed","publication_id":pub_id,"version_path":str(final),"current_pointer":str(dest/"current.json"),"render_manifest_sha256":manifest_sha,"pre_checksums":journal["pre_checksums"],"post_checksums":journal["post_checksums"],"journal":str(final/"publication-journal.json"),"rollback":journal["rollback"]}); print(json.dumps(result,indent=2)); return 0
 except Exception as e:
  evidence=[]
  if tmp.exists(): shutil.rmtree(tmp,ignore_errors=True); evidence.append({"action":"remove-temp","path":str(tmp),"exists_after":tmp.exists()})
  if pointer_swapped:
   current=dest/"current.json"
   if old_pointer is None:
    current.unlink(missing_ok=True)
   else:
    restore=dest/(".current."+pub_id+".restore"); restore.write_bytes(old_pointer); os.replace(restore,current)
   evidence.append({"action":"restore-pointer","path":str(current),"restored":(not current.exists() if old_pointer is None else current.read_bytes()==old_pointer)})
  if renamed and final.exists():
   shutil.rmtree(final,ignore_errors=True); evidence.append({"action":"remove-renamed-version","path":str(final),"exists_after":final.exists()})
  pointer_ok=(not (dest/"current.json").exists()) if old_pointer is None else ((dest/"current.json").is_file() and (dest/"current.json").read_bytes()==old_pointer)
  rollback_ok=not tmp.exists() and (not renamed or not final.exists()) and pointer_ok
  journal["status"]="rolled-back"; journal["rollback"]={"attempted":True,"status":"complete" if rollback_ok else "failed","evidence":evidence}
  result.update({"atomic_result":"rolled-back","error":str(e),"journal":journal,"rollback":journal["rollback"]}); print(json.dumps(result,indent=2)); return 10
if __name__=="__main__": raise SystemExit(main())

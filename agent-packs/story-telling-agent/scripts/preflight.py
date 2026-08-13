import argparse, importlib.util, json, shutil, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from common import libreoffice_cli, quiet_subprocess_kwargs
def version(cmd):
 try: return subprocess.run([cmd,"--version"],capture_output=True,text=True,timeout=5,**quiet_subprocess_kwargs()).stdout.strip().splitlines()[0]
 except Exception: return None
def main():
 p=argparse.ArgumentParser(); p.add_argument("--json",action="store_true"); p.add_argument("--formats",choices=["pptx","marp","both"],default="both"); p.add_argument("--require-visual-qa",action="store_true"); a=p.parse_args()
 node=shutil.which("node"); marp=shutil.which("marp") or shutil.which("marp-cli"); office=libreoffice_cli(); raster=shutil.which("pdftoppm")
 pymupdf=importlib.util.find_spec("fitz") is not None
 caps={"python":{"available":True,"version":sys.version.split()[0]},"python_pptx":{"available":importlib.util.find_spec("pptx") is not None},"jsonschema":{"available":importlib.util.find_spec("jsonschema") is not None},"node":{"available":bool(node),"version":version(node) if node else None},"marp":{"available":bool(marp),"version":version(marp) if marp else None},"libreoffice":{"available":bool(office),"version":version(office) if office else None,"executable":office,"disabled_reason":"Windows LibreOffice automation is disabled because headless conversion can open printer dialogs." if sys.platform=="win32" else None},"pdftoppm":{"available":bool(raster),"version":version(raster) if raster else None},"pymupdf":{"available":pymupdf}}
 missing=[]
 if a.formats in ("pptx","both") and not caps["python_pptx"]["available"]: missing.append("python-pptx")
 if a.formats in ("marp","both") and not caps["marp"]["available"]: missing.append("Marp CLI")
 if not caps["jsonschema"]["available"]: missing.append("jsonschema")
 visual_missing=a.require_visual_qa and not (caps["libreoffice"]["available"] and (caps["pdftoppm"]["available"] or caps["pymupdf"]["available"]))
 status="error" if missing and (a.formats!="both" or len(missing)>1 or "jsonschema" in missing) else ("degraded" if missing or visual_missing else "ok")
 visual_names=[] if not visual_missing else ([caps["libreoffice"]["disabled_reason"] or "LibreOffice"] if not caps["libreoffice"]["available"] else ["pdftoppm or PyMuPDF"])
 print(json.dumps({"status":status,"requested_formats":a.formats,"visual_qa_available":not visual_missing,"missing":missing+visual_names,"installs_performed":False,"network_used":False,"capabilities":caps},indent=2)); return 2 if status=="error" else (1 if status=="degraded" else 0)
if __name__=="__main__": raise SystemExit(main())

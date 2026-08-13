import hashlib, json, os, shutil, subprocess, sys
from pathlib import Path
def canonical(value): return json.dumps(value, sort_keys=True, separators=(",",":"), ensure_ascii=False).encode()
def sha_bytes(b): return "sha256:"+hashlib.sha256(b).hexdigest()
def sha_file(p): return sha_bytes(Path(p).read_bytes())
def load(p): return json.loads(Path(p).read_text(encoding="utf-8"))
def dump(p,v):
    p=Path(p); p.parent.mkdir(parents=True,exist_ok=True)
    with p.open("w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(v,indent=2,sort_keys=True)+"\n"); f.flush(); os.fsync(f.fileno())

def file_version(module_name):
    try:
        from importlib.metadata import version
        return version(module_name)
    except Exception:
        return None

def canonical_path(p): return str(Path(p).resolve())

def libreoffice_cli():
    """Resolve LibreOffice's non-interactive CLI without opening a Windows console."""
    if sys.platform == "win32":
        # LibreOffice 26.x can still surface printer/profile dialogs from a
        # nominally headless Windows process. Never automate it from evals.
        return None
    found = shutil.which("soffice") or shutil.which("libreoffice")
    if found and sys.platform == "win32":
        console_sibling = Path(found).with_suffix(".com")
        if console_sibling.is_file():
            return str(console_sibling)
    return found

def quiet_subprocess_kwargs():
    env = os.environ.copy()
    env.update({
        "SAL_DISABLE_SYNCHRONOUS_PRINTER_DETECTION": "1",
        "SAL_USE_VCLPLUGIN": "svp",
    })
    kwargs = {"stdin": subprocess.DEVNULL, "env": env}
    if sys.platform == "win32":
        kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
    return kwargs

def libreoffice_headless_command(executable, profile_dir, *args):
    profile_uri = Path(profile_dir).resolve().as_uri()
    return [
        executable,
        f"-env:UserInstallation={profile_uri}",
        "--headless",
        "--invisible",
        "--nologo",
        "--nodefault",
        "--nolockcheck",
        "--norestore",
        *args,
    ]

def semantic_slide(slide):
    return {
        "index": slide["index"], "slide_id": slide["slide_id"],
        "title": slide["title"], "claim_ids": slide["claim_ids"],
        "evidence_ids": slide["evidence_ids"], "source_footer": slide["source_footer"],
        "notes": slide["notes"], "cta": slide["content"].get("cta") if slide["type"] == "cta" else None,
    }

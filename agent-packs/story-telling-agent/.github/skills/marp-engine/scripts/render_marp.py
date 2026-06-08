"""render_marp.py — probe the Marp toolchain, render Marp markdown to PNG
for QA, and (optionally) convert Marp → PPTX.

Verify-or-block policy (mirrors pptx-visual-qa / OQ5, decisions.md):

    This script NEVER silently emits unverified output. When the required
    toolchain is missing it writes a manifest with ``status: "blocked"``
    and ``user_decision_required: true`` plus concrete install
    instructions, and prints a ``BLOCKED:`` line. The caller
    (@deck-builder / @deck-critic) MUST surface that block to the user as
    an install / ship-unverified-with-consent / abort decision via the
    orchestrator Phase 6 gate — it must NOT treat a blocked render as a
    silent pass.

Toolchain (self-probed at runtime, none assumed present):

  * ``marp`` on PATH (``@marp-team/marp-cli`` installed globally), OR
  * ``npx --no-install @marp-team/marp-cli`` (locally resolvable), OR
  * ``npx @marp-team/marp-cli`` (will fetch on first run; only used when
    ``--allow-npx-fetch`` is passed, since silent network fetch is a
    consent-worthy action).
  * ``soffice`` (LibreOffice) on PATH — required ONLY for the experimental
    ``--pptx --pptx-editable`` conversion; absent → image-based pptx only.

Sources:
  * https://github.com/marp-team/marp-cli  (convert to pdf/pptx/png;
    ``--pptx-editable`` requires LibreOffice)
  * https://marpit.marp.app/  (Marpit framework / CSS theming)

The manifest schema intentionally mirrors
``pptx-visual-qa/references/render-pipeline.md`` so @deck-critic can run
the SAME multimodal rubric over Marp PNGs.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path


INSTALL_INSTRUCTIONS = [
    "Install Node.js 18+ (https://nodejs.org) — provides `npx`.",
    "Install marp-cli globally:  npm install -g @marp-team/marp-cli",
    "  (or rely on npx:  npx @marp-team/marp-cli <deck.md> ...)",
    "For EDITABLE pptx (--pptx-editable, experimental): also install "
    "LibreOffice and ensure `soffice` is on PATH "
    "(macOS: brew install --cask libreoffice; "
    "Ubuntu: apt-get install -y libreoffice).",
]


# ---- bounded, non-interactive subprocess execution ----------------------
#
# Every external tool this script drives (marp-cli, npx, and — via
# `marp --pptx-editable` — LibreOffice) can hang a naive `subprocess.run`
# in two ways:
#
#   1. **stdin blocking.** A first-run `npx @marp-team/marp-cli` prints
#      "Ok to proceed? (y)" and *waits on stdin*; LibreOffice can likewise
#      prompt. With inherited stdin the child blocks forever. We close
#      stdin (DEVNULL) so any such prompt gets immediate EOF and aborts
#      instead of hanging.
#   2. **Detached grandchildren defeating the timeout.** marp-cli renders
#      PNGs via a headless Chromium (Puppeteer) and `--pptx-editable`
#      spawns a `soffice.bin` daemon. Those grandchildren detach and can
#      survive a single-process kill. On Windows `subprocess.run(...,
#      timeout=T)` reacts to a timeout by calling `proc.kill()` (direct
#      child only) and THEN `proc.communicate()` **with no timeout** to
#      drain the pipes — which blocks *indefinitely* while a detached
#      Chromium/soffice process still holds the inherited pipe write
#      handle. That is the unbounded hang this script must never trigger.
#
# `_run_bounded` therefore: (a) closes stdin, (b) puts the child in its
# own process group / session, and (c) on timeout kills the *whole*
# process tree (psutil when available) and drains with a *bounded*
# second wait — never an unbounded one. It always returns; it never
# blocks on stdin and never blocks past ~timeout + a few seconds.

PROBE_TIMEOUT = 60     # `npx --no-install ... --version`
PNG_TIMEOUT = 240      # marp PNG render (spawns Chromium)
PPTX_TIMEOUT = 240     # marp -> pptx conversion (may spawn soffice)


def _kill_proc_tree(proc: "subprocess.Popen") -> None:
    """Best-effort terminate+kill ``proc`` and every descendant.

    Uses ``psutil`` (a declared harness dep) for a portable recursive
    walk so detached Chromium/soffice grandchildren are reached; falls
    back to a direct ``proc.kill()`` if psutil is unavailable.
    """
    try:
        import psutil  # type: ignore
    except Exception:
        try:
            proc.kill()
        except Exception:
            pass
        return
    try:
        parent = psutil.Process(proc.pid)
    except Exception:
        return
    procs = parent.children(recursive=True) + [parent]
    for p in procs:
        try:
            p.terminate()
        except Exception:
            pass
    _gone, alive = psutil.wait_procs(procs, timeout=3.0)
    for p in alive:
        try:
            p.kill()
        except Exception:
            pass
    psutil.wait_procs(alive, timeout=2.0)


def _run_bounded(cmd: list[str], timeout: int) -> tuple[int, str, str, bool]:
    """Run ``cmd`` non-interactively with a hard wall-clock bound.

    Returns ``(returncode, stdout, stderr, timed_out)``. stdin is closed
    (DEVNULL) so interactive prompts can never block; on timeout the whole
    process tree is killed and the drain is itself bounded, so a detached
    grandchild can never wedge an unbounded read. Spawn failures return
    ``(127, "", reason, False)`` rather than raising.
    """
    creationflags = 0
    start_new_session = False
    if sys.platform == "win32":
        creationflags = 0x00000200  # CREATE_NEW_PROCESS_GROUP
    else:
        start_new_session = True
    try:
        proc = subprocess.Popen(
            list(cmd),
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            creationflags=creationflags,
            start_new_session=start_new_session,
        )
    except (FileNotFoundError, OSError) as e:
        return 127, "", f"spawn_failed: {e}", False

    try:
        out, err = proc.communicate(timeout=timeout)
        return proc.returncode, out or "", err or "", False
    except subprocess.TimeoutExpired:
        _kill_proc_tree(proc)
        out = err = ""
        try:
            out, err = proc.communicate(timeout=5.0)
        except subprocess.TimeoutExpired:
            try:
                proc.kill()
            except Exception:
                pass
            out, err = "", ""
        err = (err or "") + f"\n[render_marp] TIMEOUT after {timeout}s"
        return 124, out or "", err, True


def _probe_marp(allow_npx_fetch: bool) -> tuple[list[str] | None, str | None]:
    """Return (argv-prefix, engine-label) for the first usable marp, or
    ``(None, None)`` when no marp runner is resolvable without a network
    fetch (unless ``allow_npx_fetch`` is set)."""
    if shutil.which("marp"):
        return ["marp"], "marp-cli"
    if shutil.which("npx"):
        # `--no-install` resolves a locally-installed marp without fetching.
        # `_run_bounded` closes stdin so npx can never block on an
        # "Ok to proceed?" prompt, and bounds the probe at PROBE_TIMEOUT.
        rc, _out, _err, _timed_out = _run_bounded(
            ["npx", "--no-install", "@marp-team/marp-cli", "--version"],
            timeout=PROBE_TIMEOUT,
        )
        if rc == 0:
            return ["npx", "--no-install", "@marp-team/marp-cli"], "npx-marp"
        if allow_npx_fetch:
            return ["npx", "@marp-team/marp-cli"], "npx-marp-fetch"
    return None, None


def _write_manifest(out_dir: Path, manifest: dict) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    mpath = out_dir / "manifest.json"
    mpath.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return mpath


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--md", required=True, type=Path,
                    help="Marp markdown source (deck.md).")
    ap.add_argument("--out", required=True, type=Path,
                    help="Output dir for PNG renders + manifest.json.")
    ap.add_argument("--theme", type=Path, default=None,
                    help="Optional Marp theme CSS file.")
    ap.add_argument("--pptx", type=Path, default=None,
                    help="If set, also convert Marp -> pptx at this path.")
    ap.add_argument("--editable-pptx", action="store_true",
                    help="Request experimental editable pptx (needs soffice).")
    ap.add_argument("--dpi", type=int, default=110)
    ap.add_argument("--allow-npx-fetch", action="store_true",
                    help="Permit `npx` to fetch marp-cli over the network "
                         "(a consent-worthy action; off by default).")
    args = ap.parse_args()

    started = time.time()
    base_manifest = {
        "session_id": None,
        "source_md": str(args.md),
        "render_engine": None,
        "soffice_available": bool(shutil.which("soffice")
                                  or shutil.which("libreoffice")),
        "dpi": args.dpi,
        "slides": [],
        "pptx_path": None,
        "pptx_editable": False,
        "status": "blocked",
        "block_reason": None,
        "user_decision_required": False,
        "install_instructions": INSTALL_INSTRUCTIONS,
        "errors": [],
        "duration_ms": 0,
    }

    if not args.md.exists():
        base_manifest["block_reason"] = f"marp source not found: {args.md}"
        base_manifest["errors"].append("source_missing")
        base_manifest["duration_ms"] = int((time.time() - started) * 1000)
        _write_manifest(args.out, base_manifest)
        print(f"BLOCKED: {base_manifest['block_reason']}", file=sys.stderr)
        return 0

    marp_argv, engine = _probe_marp(args.allow_npx_fetch)
    if marp_argv is None:
        # GRACEFUL BLOCK — surface a user decision, never silently degrade.
        base_manifest["block_reason"] = (
            "Marp toolchain not found (no `marp` on PATH and no locally "
            "resolvable `@marp-team/marp-cli` via npx). Cannot render or "
            "verify Marp output."
        )
        base_manifest["user_decision_required"] = True
        base_manifest["duration_ms"] = int((time.time() - started) * 1000)
        _write_manifest(args.out, base_manifest)
        print("BLOCKED: marp toolchain missing — user decision required "
              "(install / ship-unverified-with-consent / abort)",
              file=sys.stderr)
        return 0

    args.out.mkdir(parents=True, exist_ok=True)
    base_manifest["render_engine"] = engine

    # ---- Stage 1: render PNGs for QA (always attempted) ----
    png_stem = args.out / "slide"
    png_cmd = list(marp_argv) + [str(args.md), "--images", "png",
                                 "-o", str(png_stem) + ".png"]
    if args.theme:
        png_cmd += ["--theme", str(args.theme)]
    rc, _out, err, timed_out = _run_bounded(png_cmd, timeout=PNG_TIMEOUT)
    if timed_out:
        base_manifest["errors"].append(
            f"png_render_timeout after {PNG_TIMEOUT}s: marp toolchain "
            f"unresponsive (e.g. headless Chromium stalled or an interactive "
            f"prompt); process tree killed — treated as a block.")
    elif rc != 0:
        base_manifest["errors"].append(
            f"png_render_failed rc={rc}: {err.strip()[:500]}")

    pngs = sorted(args.out.glob("slide*.png"))
    base_manifest["slides"] = [
        {"index": i, "png_path": p.name} for i, p in enumerate(pngs, start=1)
    ]

    # ---- Stage 2: optional Marp -> pptx conversion ----
    if args.pptx is not None:
        pptx_cmd = list(marp_argv) + [str(args.md), "--pptx",
                                      "-o", str(args.pptx)]
        if args.theme:
            pptx_cmd += ["--theme", str(args.theme)]
        editable = False
        if args.editable_pptx:
            if base_manifest["soffice_available"]:
                pptx_cmd.append("--pptx-editable")
                editable = True
            else:
                base_manifest["errors"].append(
                    "editable_pptx_requested_but_soffice_missing: produced "
                    "image-based pptx instead (install LibreOffice for "
                    "editable output).")
        rc, _out, err, timed_out = _run_bounded(pptx_cmd, timeout=PPTX_TIMEOUT)
        if timed_out:
            base_manifest["errors"].append(
                f"pptx_convert_timeout after {PPTX_TIMEOUT}s: marp/soffice "
                f"unresponsive (detached LibreOffice daemon or interactive "
                f"prompt); process tree killed.")
        elif rc == 0 and args.pptx.exists():
            base_manifest["pptx_path"] = str(args.pptx)
            base_manifest["pptx_editable"] = editable
        else:
            base_manifest["errors"].append(
                f"pptx_convert_failed rc={rc}: {err.strip()[:500]}")

    # ---- Verdict: rendered vs blocked ----
    if base_manifest["slides"]:
        base_manifest["status"] = "rendered"
        base_manifest["user_decision_required"] = False
    else:
        # Toolchain present but produced nothing — still a block, surface it.
        base_manifest["status"] = "blocked"
        base_manifest["user_decision_required"] = True
        base_manifest["block_reason"] = (
            "Marp toolchain present but no PNG slides were produced; cannot "
            "verify output. See errors[].")

    base_manifest["duration_ms"] = int((time.time() - started) * 1000)
    _write_manifest(args.out, base_manifest)

    if base_manifest["status"] == "rendered":
        print(f"SUCCESS: rendered {len(base_manifest['slides'])} Marp "
              f"slide(s) via {engine}"
              + (f"; pptx={base_manifest['pptx_path']}"
                 if base_manifest["pptx_path"] else ""))
    else:
        print(f"BLOCKED: {base_manifest['block_reason']}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())

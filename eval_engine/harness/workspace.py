"""Workspace lifecycle: allocate, stage, persist runstate, teardown.

Each case run gets an isolated directory under
``evals/packs/<pack>/workspaces/<case>/<run_id>/``. The SUT operates inside that
workspace as ``cwd``; the harness operates from outside.

Built-in step kinds the case ``workspace.steps`` may declare:

* ``copy_tree`` — recursively copy ``src`` (relative to the case dir) to
  ``dest`` (relative to the workspace).
* ``git_init`` — initialise a fresh git repo in the workspace.
* ``file_template`` — render ``src`` as a template (``{{var}}`` syntax)
  with ``vars`` and write to ``dest``.
* ``repo_clone`` — fetch a pinned-SHA snapshot of an external repo into
  ``dest``. Cached under ``evals/data/repo-cache/<sha>``. ``ref`` MUST be
  a 40-char SHA; branch names are rejected for reproducibility.
* ``shell`` — run a portable command via ``subprocess`` (``cmd`` is a
  list, never a string). Use sparingly.
* ``hook`` — invoke a Python function from a case-local module. Reserved
  for cases that genuinely need imperative setup.

Golden references are staged OUTSIDE the workspace at
``evals/data/golden-staging/<run_id>/`` so a malicious SUT cannot read or
overwrite them. The workspace ``_eval/`` directory is a CANARY: any access
the SUT makes to it is automatically a scope violation surfaced by
``L3-workspace-escape``.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

from . import hooks_api, models, paths_layout


_TEMPLATE_VAR = re.compile(r"\{\{\s*([A-Za-z_][A-Za-z0-9_]*)\s*\}\}")
_SHA_RE = re.compile(r"^[0-9a-f]{40}$")


@dataclass
class RunState:
    """Persisted per-run manifest under ``<workspace>/_runstate.json``."""

    run_id: str
    pack: str
    case_id: str
    spec_path: str
    case_path: str
    workspace_root: str
    golden_staging_dir: str
    started_at: str
    stage: str  # "staged" | "fixture-pending" | "judged" | "complete" | "abandoned"
    keep_workspace: bool = False
    notes: str = ""

    def write(self) -> None:
        target = Path(self.workspace_root) / "_runstate.json"
        target.write_text(json.dumps(asdict(self), indent=2), encoding="utf-8")

    @classmethod
    def read(cls, workspace_root: str) -> "RunState":
        path = Path(workspace_root) / "_runstate.json"
        d = json.loads(path.read_text(encoding="utf-8"))
        return cls(**d)


# ---------- Allocation ---------------------------------------------------


def allocate(
    *,
    eval_root: str,
    pack: str,
    case_id: str,
    run_id: str,
) -> tuple[str, str]:
    """Create the workspace and golden-staging dirs. Returns (ws, golden)."""
    ws = paths_layout.workspace_dir(eval_root, pack, _safe_segment(case_id), run_id)
    ws.mkdir(parents=True, exist_ok=False)
    golden = paths_layout.golden_staging_dir(eval_root, run_id)
    golden.mkdir(parents=True, exist_ok=True)
    return str(ws), str(golden)


def _safe_segment(s: str) -> str:
    # Filesystem-safe segment for case ids that may contain '/'.
    return re.sub(r"[^A-Za-z0-9._-]+", "_", s)


# ---------- Staging ------------------------------------------------------


def stage(
    *,
    case: models.CaseSpec,
    workspace_root: str,
    golden_staging_dir: str,
    repo_cache_dir: str,
) -> None:
    """Run all ``case.workspace.steps`` against the workspace."""
    ctx_args = {
        "workspace_root": workspace_root,
        "case_dir": case.case_dir,
        "inputs_dir": (
            os.path.join(case.case_dir, case.inputs_dir) if case.inputs_dir else None
        ),
        "golden_staging_dir": golden_staging_dir,
        "run_id": Path(workspace_root).name,
        "pack": case.pack,
        "case_id": case.id,
    }
    # Stage golden refs OUTSIDE the workspace (canary stays empty).
    if case.golden_dir:
        src = Path(case.case_dir) / case.golden_dir
        if src.exists():
            shutil.copytree(src, Path(golden_staging_dir) / "golden", dirs_exist_ok=True)
    # Plant the canary directory so L3-workspace-escape can detect touches.
    (Path(workspace_root) / "_eval").mkdir(exist_ok=True)
    (Path(workspace_root) / "_eval" / "DO_NOT_TOUCH.txt").write_text(
        "This directory is reserved for the eval framework. Any access by the "
        "system-under-test is a scope violation and is logged by the harness.\n",
        encoding="utf-8",
    )
    for i, step in enumerate(case.steps):
        try:
            _run_step(step, case_dir=case.case_dir, workspace_root=workspace_root,
                      repo_cache_dir=repo_cache_dir, ctx_args=ctx_args)
        except Exception as exc:
            raise RuntimeError(f"workspace step #{i} ({step.kind}) failed: {exc}") from exc


def _run_step(
    step: models.WorkspaceStep,
    *,
    case_dir: str,
    workspace_root: str,
    repo_cache_dir: str,
    ctx_args: dict[str, Any],
) -> None:
    if step.kind == "copy_tree":
        src = Path(case_dir) / step.args["src"]
        dest = Path(workspace_root) / step.args.get("dest", ".")
        dest.mkdir(parents=True, exist_ok=True)
        if src.is_file():
            shutil.copy2(src, dest)
        else:
            shutil.copytree(src, dest, dirs_exist_ok=True)
        return
    if step.kind == "git_init":
        subprocess.check_call(
            ["git", "init", "--quiet"], cwd=workspace_root,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        # Configure a deterministic identity for any commits hooks might make.
        for k, v in (("user.email", "eval@local"), ("user.name", "eval")):
            subprocess.check_call(
                ["git", "config", k, v], cwd=workspace_root,
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
        return
    if step.kind == "file_template":
        src = Path(case_dir) / step.args["src"]
        dest = Path(workspace_root) / step.args["dest"]
        dest.parent.mkdir(parents=True, exist_ok=True)
        text = src.read_text(encoding="utf-8")
        rendered = render_template(text, step.args.get("vars", {}) or {})
        dest.write_text(rendered, encoding="utf-8")
        return
    if step.kind == "repo_clone":
        _repo_clone(
            url=step.args["url"],
            ref=step.args["ref"],
            dest=Path(workspace_root) / step.args["dest"],
            cache_dir=repo_cache_dir,
            sparse=step.args.get("sparse"),
        )
        return
    if step.kind == "shell":
        cmd = step.args["cmd"]
        if not isinstance(cmd, list):
            raise ValueError("shell step: 'cmd' must be a list, not a string")
        subprocess.check_call(cmd, cwd=workspace_root)
        return
    if step.kind == "hook":
        module_path = os.path.join(case_dir, step.args["module"])
        fn_name = step.args.get("function", "prepare")
        fn = hooks_api.load_callable(module_path, fn_name)
        fn(hooks_api.HookContext(args=step.args.get("args", {}), **ctx_args))
        return
    raise ValueError(f"unknown workspace step kind: {step.kind!r}")


def render_template(text: str, variables: dict[str, str]) -> str:
    def repl(m: re.Match[str]) -> str:
        key = m.group(1)
        if key not in variables:
            raise KeyError(f"template variable {key!r} not provided")
        return str(variables[key])
    return _TEMPLATE_VAR.sub(repl, text)


def _repo_clone(*, url: str, ref: str, dest: Path, cache_dir: str, sparse: list[str] | None) -> None:
    if not _SHA_RE.match(ref):
        raise ValueError(f"repo_clone: 'ref' must be a 40-char SHA; got {ref!r}")
    cache_root = Path(cache_dir) / ref
    if not cache_root.exists():
        cache_root.mkdir(parents=True, exist_ok=True)
        subprocess.check_call(["git", "init", "--quiet"], cwd=cache_root)
        subprocess.check_call(["git", "remote", "add", "origin", url], cwd=cache_root)
        subprocess.check_call(["git", "fetch", "--depth", "1", "origin", ref], cwd=cache_root)
        subprocess.check_call(["git", "checkout", "--quiet", ref], cwd=cache_root)
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        shutil.rmtree(dest)
    if sparse:
        dest.mkdir(parents=True)
        for s in sparse:
            src = cache_root / s
            if src.is_dir():
                shutil.copytree(src, dest / s, dirs_exist_ok=True)
            elif src.is_file():
                (dest / s).parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dest / s)
    else:
        shutil.copytree(cache_root, dest, ignore=shutil.ignore_patterns(".git"))


# ---------- Teardown -----------------------------------------------------


def teardown(*, workspace_root: str, policy: str, archive_root: str | None = None,
             status: str = "pass") -> None:
    if policy == "keep":
        return
    if policy == "delete-on-pass" and status != "pass":
        return  # keep failed runs for debugging
    if policy in ("delete", "delete-on-pass"):
        shutil.rmtree(workspace_root, ignore_errors=False)
        return
    if policy == "move-to-archive":
        if not archive_root:
            raise ValueError("move-to-archive requires archive_root")
        Path(archive_root).mkdir(parents=True, exist_ok=True)
        shutil.move(workspace_root, archive_root)
        return
    raise ValueError(f"unknown teardown policy: {policy!r}")


# ---------- CLI commands (resume/cleanup/abandon) -----------------------


def list_workspaces(eval_root: str) -> list[RunState]:
    out: list[RunState] = []
    for _pack, _case, _run, run_path in paths_layout.iter_workspace_dirs(eval_root):
        rs_path = run_path / "_runstate.json"
        if rs_path.exists():
            try:
                out.append(RunState.read(str(run_path)))
            except Exception:
                continue
    return out


def cleanup_orphans(eval_root: str, *, dry_run: bool = True) -> list[str]:
    """Delete completed-but-still-on-disk workspaces. Returns paths affected."""
    affected: list[str] = []
    for rs in list_workspaces(eval_root):
        if rs.stage == "complete" and not rs.keep_workspace:
            affected.append(rs.workspace_root)
            if not dry_run:
                shutil.rmtree(rs.workspace_root, ignore_errors=True)
    return affected


def abandon(workspace_root: str) -> None:
    rs = RunState.read(workspace_root)
    rs.stage = "abandoned"
    rs.notes = (rs.notes + "\nabandoned by operator").strip()
    rs.write()

"""Public API for case ``hooks/setup.py`` and ``hooks/teardown.py`` modules.

Hook modules are the escape hatch for case authors. They receive a single
:class:`HookContext` argument and may inspect the workspace, copy files,
shell out, etc. The harness imports the module dynamically and calls a
named function (``prepare`` / ``cleanup`` / whatever ``case.yaml``
declares).

Hooks must be POSIX-pure-Python (stdlib only) to keep test resources
hermetic and to stay aligned with the harness's own dependency footprint.
If you need richer behaviour, prefer adding a new built-in step kind in
``workspace.py`` so every case can use it declaratively.
"""

from __future__ import annotations

import importlib.util
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable


@dataclass
class HookContext:
    workspace_root: str
    case_dir: str
    inputs_dir: str | None
    golden_staging_dir: str  # outside the workspace; never visible to the SUT
    run_id: str
    pack: str
    case_id: str
    args: dict[str, Any]


def load_callable(module_path: str, function_name: str) -> Callable[[HookContext], None]:
    spec = importlib.util.spec_from_file_location(
        f"_eval_hook_{Path(module_path).stem}", module_path
    )
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load hook module {module_path!r}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    fn = getattr(mod, function_name, None)
    if not callable(fn):
        raise AttributeError(
            f"{module_path!r}: hook function {function_name!r} not found"
        )
    return fn


def safe_join(root: str, *parts: str) -> str:
    """Join ``parts`` under ``root`` and refuse to escape it.

    Useful inside hook bodies; raises ``ValueError`` if the resulting path
    walks outside ``root`` via ``..`` segments or absolute-path arguments.
    """
    base = os.path.realpath(root)
    candidate = os.path.realpath(os.path.join(base, *parts))
    if not (candidate == base or candidate.startswith(base + os.sep)):
        raise ValueError(f"{candidate!r} escapes root {base!r}")
    return candidate

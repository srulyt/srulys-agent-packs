"""Discover eval specs on disk and compile them to :class:`EvalSpec` objects.

Two authoring file types are collected:

* ``*.eval.md`` — parsed by the Markdown loader.
* ``*.eval.py`` — imported; every module-level :class:`~evalpilot.spec.EvalSpec`
  or fluent :class:`~evalpilot.loaders.builder.Eval` (built) is collected.

Noise directories (``_runs``, ``_metrics``, ``__pycache__`` …) are skipped so a
run never re-discovers its own artifacts.
"""

from __future__ import annotations

import importlib.util
import uuid
from pathlib import Path

from .loaders import Eval, load_markdown_eval
from .spec import EvalSpec

_PRUNE = {"_runs", "_metrics", "__pycache__", ".git", "node_modules", ".venv",
          "venv", ".pytest_cache"}


def collect_specs(target: Path) -> list[EvalSpec]:
    """Return all specs under ``target`` (a file or directory)."""
    target = Path(target)
    if target.is_file():
        return _load_file(target)
    specs: list[EvalSpec] = []
    for f in _iter_spec_files(target):
        specs.extend(_load_file(f))
    specs.sort(key=lambda s: (str(s.spec_path or ""), s.name))
    return specs


def _iter_spec_files(root: Path):
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if any(part in _PRUNE for part in path.relative_to(root).parts):
            continue
        if path.name.endswith(".eval.md") or path.name.endswith(".eval.py"):
            yield path


def _load_file(path: Path) -> list[EvalSpec]:
    if path.name.endswith(".eval.md"):
        return [load_markdown_eval(path)]
    if path.name.endswith(".eval.py"):
        return _load_python(path)
    return []


def _load_python(path: Path) -> list[EvalSpec]:
    mod_name = f"_evalpilot_spec_{uuid.uuid4().hex}"
    spec = importlib.util.spec_from_file_location(mod_name, path)
    if spec is None or spec.loader is None:
        return []
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    found: list[EvalSpec] = []
    seen: set[int] = set()
    for value in vars(module).values():
        built = _coerce(value)
        if built is not None and id(built) not in seen:
            seen.add(id(built))
            built.spec_path = str(path)
            if built.base_dir is None:
                built.base_dir = path.parent
            found.append(built)
    return found


def _coerce(value) -> EvalSpec | None:
    if isinstance(value, EvalSpec):
        return value
    if isinstance(value, Eval):
        return value.build()
    return None


__all__ = ["collect_specs"]

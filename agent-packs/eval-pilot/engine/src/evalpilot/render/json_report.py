"""Canonical JSON serialisation of an :class:`~evalpilot.model.EvalRunReport`.

This is the source-of-truth render: the terminal and HTML views are derived
from the same object, and ``evalpilot show`` / the ``--check`` CI gate reload
a run straight from this file.
"""

from __future__ import annotations

import json
from pathlib import Path

from ..model import EvalRunReport


def to_json_str(report: EvalRunReport, *, indent: int = 2) -> str:
    return json.dumps(report.to_dict(), indent=indent, ensure_ascii=False)


def write_json(report: EvalRunReport, path: Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(to_json_str(report), encoding="utf-8")
    return path


def read_json(path: Path) -> EvalRunReport:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return EvalRunReport.from_dict(data)


__all__ = ["to_json_str", "write_json", "read_json"]

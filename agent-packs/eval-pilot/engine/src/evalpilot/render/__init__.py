"""Renderers that turn an :class:`~evalpilot.model.EvalRunReport` into output.

All three renderers read the **same** modeled result, so the JSON file is the
canonical record and the terminal/HTML views are pure projections of it.

* :mod:`evalpilot.render.json_report` — canonical JSON (write/read).
* :mod:`evalpilot.render.terminal`    — rich console summary.
* :mod:`evalpilot.render.html`        — self-contained shareable report.
"""

from __future__ import annotations

from .html import render_html
from .json_report import read_json, to_json_str, write_json
from .terminal import render_terminal

__all__ = [
    "write_json",
    "read_json",
    "to_json_str",
    "render_terminal",
    "render_html",
]

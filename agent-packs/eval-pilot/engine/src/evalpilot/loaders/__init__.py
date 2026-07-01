"""Authoring surfaces that compile to an :class:`~evalpilot.spec.EvalSpec`.

* :mod:`evalpilot.loaders.markdown` — parse a ``*.eval.md`` file.
* :mod:`evalpilot.loaders.builder`  — fluent Python ``Eval(...)`` builder.
"""

from __future__ import annotations

from .builder import Eval
from .markdown import load_markdown_eval, parse_markdown_eval

__all__ = ["Eval", "load_markdown_eval", "parse_markdown_eval"]

"""LLM-as-judge helper.

**Dogfood note:** this module now re-exports the implementation from the
packaged :mod:`evalpilot.judge`. The monorepo harness uses the same judge
the ``eval-pilot`` plugin ships to other repos, so there is a single source
of truth. The bundled ``eval-judge`` agent (package data) supersedes the
standalone ``agent-packs/eval-framework`` judge for new runs.

Public surface is unchanged: ``judge``, ``Verdict``, ``JudgeError``,
``DEFAULT_THRESHOLD``. The private ``_extract_json`` / ``_build_prompt``
helpers are re-exported too because the static self-tests exercise them.
"""

from __future__ import annotations

from evalpilot.judge import (  # noqa: F401
    DEFAULT_THRESHOLD,
    JudgeError,
    Verdict,
    _build_prompt,
    _extract_json,
    judge,
)

__all__ = ["judge", "Verdict", "JudgeError", "DEFAULT_THRESHOLD"]

"""Pytest wrapper around ``scripts/lint_pack.py``.

Generates one test per pack under ``agent-packs/`` so violations show up
as individual failures in the pytest report. This is the static
replacement for the legacy L1/L2/L3 per-case assertions.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from scripts.lint_pack import discover_packs, lint_pack  # noqa: E402


PACKS = discover_packs()


@pytest.mark.parametrize("pack_dir", PACKS, ids=[p.name for p in PACKS])
def test_pack_contract(pack_dir):
    issues = lint_pack(pack_dir)
    errors = [i for i in issues if i.severity == "error"]
    if errors:
        msg = "\n".join(i.format() for i in errors)
        pytest.fail(f"Pack contract violations:\n{msg}")

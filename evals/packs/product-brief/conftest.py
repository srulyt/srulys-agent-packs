"""Use evalpilot fixtures for the product-brief migration suite.

The shared ``evals/conftest.py`` still provides legacy fixtures for packs
that have not migrated yet. Re-exporting evalpilot's fixture functions here
keeps this package on the new API without changing the other pack suites.
"""

from __future__ import annotations

from evalpilot.pytest_plugin import agent_pack, judge  # noqa: F401

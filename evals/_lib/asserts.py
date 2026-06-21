"""Shared assertion helpers for evals.

**Dogfood note:** this module now re-exports the implementation from the
packaged :mod:`evalpilot.asserts`. The monorepo harness consumes the same
engine the ``eval-pilot`` plugin ships to other repos, so there is a single
source of truth. The public names are unchanged.
"""

from __future__ import annotations

from evalpilot.asserts import (  # noqa: F401
    assert_prose_contains,
    assert_prose_not_contains,
)

__all__ = ["assert_prose_contains", "assert_prose_not_contains"]

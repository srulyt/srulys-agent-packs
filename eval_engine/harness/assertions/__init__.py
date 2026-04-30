"""Assertion library, organised by layer.

Each layer module exposes a list ``ASSERTIONS`` of ``Assertion`` callables.
The registry below flattens them into a single iterable so ``run.py`` can
discover all assertions without knowing about specific layer modules.
"""

from . import l1, l2, l3
from .base import Assertion, AssertionResult, register

ASSERTIONS = list(l1.ASSERTIONS) + list(l2.ASSERTIONS) + list(l3.ASSERTIONS)

__all__ = ["Assertion", "AssertionResult", "ASSERTIONS", "register"]

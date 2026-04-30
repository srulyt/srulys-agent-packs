"""Base classes and registry for assertions.

An ``Assertion`` is a function ``(ctx) -> AssertionResult`` (often
yielding multiple results — see :class:`Assertion`). Each assertion
declares its layer + default severity. The case may bump severity (or
mark an assertion ``skip``) via expectation overrides.

Assertions consume the :class:`AssertionContext` constructed by ``run.py``,
which bundles the loaded spec, case, fixture, and workspace path.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Iterable

from .. import models


@dataclass
class AssertionContext:
    spec: models.PackSpec
    case: models.CaseSpec
    fixture: models.Fixture
    workspace_root: str
    golden_staging_dir: str | None = None


# A result yielded by an assertion. Multiple results per assertion are
# allowed when an assertion checks the same property across many subjects
# (e.g. one verdict per agent for L3-tools).
AssertionResult = models.AssertionVerdict


@dataclass
class Assertion:
    id: str
    layer: str  # "L1" | "L2" | "L3"
    default_severity: str  # info | warn | blocker
    fn: Callable[[AssertionContext], Iterable[AssertionResult]]
    description: str = ""

    def run(self, ctx: AssertionContext) -> list[AssertionResult]:
        try:
            results = list(self.fn(ctx))
        except Exception as exc:  # pragma: no cover (surfaced via 'error' status)
            return [
                AssertionResult(
                    assertion_id=self.id,
                    layer=self.layer,
                    severity=self.default_severity,
                    status="error",
                    message=f"assertion raised {type(exc).__name__}: {exc}",
                )
            ]
        # Stamp layer + default severity if the assertion didn't supply them.
        for r in results:
            if not r.layer:
                r.layer = self.layer
            if not r.severity:
                r.severity = self.default_severity
            if not r.assertion_id:
                r.assertion_id = self.id
        return results


_REGISTRY: list[Assertion] = []


def register(
    *,
    id: str,
    layer: str,
    default_severity: str,
    description: str = "",
) -> Callable[[Callable[[AssertionContext], Iterable[AssertionResult]]], Assertion]:
    def deco(fn: Callable[[AssertionContext], Iterable[AssertionResult]]) -> Assertion:
        a = Assertion(
            id=id, layer=layer, default_severity=default_severity, fn=fn, description=description
        )
        _REGISTRY.append(a)
        return a

    return deco


def all_registered() -> list[Assertion]:
    return list(_REGISTRY)

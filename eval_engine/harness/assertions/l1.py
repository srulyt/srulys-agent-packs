"""Layer-1 assertions: invocation set / count / order / mode / completion.

These are the cheapest, highest-confidence checks. They run against the
fixture's :class:`AgentInvocation` list with no filesystem access.
"""

from __future__ import annotations

from collections import Counter
from typing import Iterable

from .. import models
from .base import Assertion, AssertionContext, AssertionResult, register


def _expected_invocation(ctx: AssertionContext, agent_name: str) -> models.InvocationExpectation:
    # Per-case override beats spec.
    if agent_name in ctx.case.expected.invocations:
        return ctx.case.expected.invocations[agent_name]
    a = ctx.spec.agent(agent_name)
    return a.invocations if a else models.InvocationExpectation(min=0, max=0)


@register(id="L1-set", layer="L1", default_severity="blocker",
          description="Set of agent invocations matches declared agents.")
def _l1_set(ctx: AssertionContext) -> Iterable[AssertionResult]:
    declared = {a.name for a in ctx.spec.agents}
    actual = {i.name for i in ctx.fixture.invocations if i.name != ctx.spec.orchestrator}
    allowed = set(ctx.case.expected.allowed_agent_types or declared)
    unexpected = actual - allowed
    # Sub-agents whose min>0 must appear in `actual`. Exclude the orchestrator
    # itself: it is the entry point, not a delegated sub-agent, and is filtered
    # out of `actual` above.
    missing_required = {
        a.name for a in ctx.spec.agents
        if a.name != ctx.spec.orchestrator and _expected_invocation(ctx, a.name).min > 0
    } - actual
    if unexpected and ctx.spec.flow.no_unexpected_agents:
        yield AssertionResult(
            assertion_id="L1-set", layer="", severity="",
            status="fail",
            message=f"unexpected agent(s) invoked: {sorted(unexpected)}",
            evidence=[{"kind": "agent", "name": n} for n in sorted(unexpected)],
        )
        return
    if missing_required:
        yield AssertionResult(
            assertion_id="L1-set", layer="", severity="",
            status="fail",
            message=f"required agent(s) never invoked: {sorted(missing_required)}",
        )
        return
    yield AssertionResult(
        assertion_id="L1-set", layer="", severity="", status="pass",
        message=f"agent set OK ({len(actual)} agents)",
    )


@register(id="L1-count", layer="L1", default_severity="blocker",
          description="Each agent's invocation count is within [min, max].")
def _l1_count(ctx: AssertionContext) -> Iterable[AssertionResult]:
    counts = Counter(i.name for i in ctx.fixture.invocations)
    for a in ctx.spec.agents:
        exp = _expected_invocation(ctx, a.name)
        n = counts.get(a.name, 0)
        if n < exp.min or n > exp.max:
            yield AssertionResult(
                assertion_id="L1-count", layer="", severity="", agent=a.name,
                status="fail",
                message=f"{a.name} invoked {n} time(s); expected {exp.min}..{exp.max}",
            )
        else:
            yield AssertionResult(
                assertion_id="L1-count", layer="", severity="", agent=a.name,
                status="pass", message=f"{a.name}: {n} invocation(s) (ok)",
            )


@register(id="L1-order", layer="L1", default_severity="blocker",
          description="Declared ordering 'A before B' holds in invocation timeline.")
def _l1_order(ctx: AssertionContext) -> Iterable[AssertionResult]:
    if not ctx.spec.flow.ordering:
        yield AssertionResult(
            assertion_id="L1-order", layer="", severity="", status="skip",
            message="no ordering constraints declared",
        )
        return
    # Index of first invocation per agent (None if absent).
    first_idx: dict[str, int] = {}
    for idx, inv in enumerate(ctx.fixture.invocations):
        first_idx.setdefault(inv.name, idx)
    for before, after in ctx.spec.flow.ordering:
        b = first_idx.get(before)
        a = first_idx.get(after)
        if b is None or a is None:
            yield AssertionResult(
                assertion_id="L1-order", layer="", severity="", status="skip",
                message=f"{before} before {after}: one or both not invoked",
            )
            continue
        if b < a:
            yield AssertionResult(
                assertion_id="L1-order", layer="", severity="", status="pass",
                message=f"{before} before {after}: ok",
            )
        else:
            yield AssertionResult(
                assertion_id="L1-order", layer="", severity="", status="fail",
                message=f"{before} did not precede {after} (indices {b}, {a})",
            )


@register(id="L1-mode", layer="L1", default_severity="warn",
          description="Long-running agents launched with mode=background where declared.")
def _l1_mode(ctx: AssertionContext) -> Iterable[AssertionResult]:
    # Spec convention: agent.invocations.must_complete=False signals background.
    any_checked = False
    for a in ctx.spec.agents:
        if a.invocations.must_complete:
            continue
        any_checked = True
        invs = [i for i in ctx.fixture.invocations if i.name == a.name]
        for inv in invs:
            if inv.mode != "background":
                yield AssertionResult(
                    assertion_id="L1-mode", layer="", severity="", agent=a.name,
                    status="fail",
                    message=f"{a.name} launched with mode={inv.mode!r}; expected 'background'",
                )
            else:
                yield AssertionResult(
                    assertion_id="L1-mode", layer="", severity="", agent=a.name,
                    status="pass", message=f"{a.name} launched in background",
                )
    if not any_checked:
        yield AssertionResult(
            assertion_id="L1-mode", layer="", severity="", status="skip",
            message="no agents declared as background-capable",
        )


@register(id="L1-bg-completion", layer="L1", default_severity="blocker",
          description="Background agents the orchestrator depends on actually completed before reads.")
def _l1_bg_completion(ctx: AssertionContext) -> Iterable[AssertionResult]:
    bg = [i for i in ctx.fixture.invocations if i.mode == "background"]
    if not bg:
        yield AssertionResult(
            assertion_id="L1-bg-completion", layer="", severity="", status="skip",
            message="no background invocations in fixture",
        )
        return
    # Each background_reads entry has shape:
    #   {"invocation_id": "...", "read_at": "...", "completed_at": "..."}
    # If completed_at is None or > read_at, the orchestrator read before completion.
    issues = 0
    for r in ctx.fixture.background_reads:
        completed = r.get("completed_at")
        read_at = r.get("read_at")
        inv_id = r.get("invocation_id")
        if completed is None or (read_at and completed > read_at):
            issues += 1
            yield AssertionResult(
                assertion_id="L1-bg-completion", layer="", severity="", status="fail",
                message=f"orchestrator read background invocation {inv_id} before completion",
                evidence=[{"kind": "background_read", **r}],
            )
    if issues == 0:
        yield AssertionResult(
            assertion_id="L1-bg-completion", layer="", severity="", status="pass",
            message=f"all {len(ctx.fixture.background_reads)} background reads observed completion",
        )


ASSERTIONS = [_l1_set, _l1_count, _l1_order, _l1_mode, _l1_bg_completion]

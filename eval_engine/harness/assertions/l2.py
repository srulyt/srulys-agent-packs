"""Layer-2 assertions: prompt + output contracts.

These check the *content* of the prompts the orchestrator passes to each
sub-agent and the *content* of each sub-agent's final response, against
the spec's :class:`PromptContract` and :class:`OutputContract`.
"""

from __future__ import annotations

import json
import re
from typing import Iterable

from .. import models
from .base import Assertion, AssertionContext, AssertionResult, register


_SECTION_RE = re.compile(r"^\s{0,3}#{1,6}\s+(.+?)\s*$", re.MULTILINE)


def _section_titles(text: str) -> list[str]:
    return [m.group(1).strip() for m in _SECTION_RE.finditer(text or "")]


@register(id="L2-prompt-sections", layer="L2", default_severity="blocker",
          description="Each sub-agent prompt contains the spec's required sections.")
def _l2_prompt_sections(ctx: AssertionContext) -> Iterable[AssertionResult]:
    seen_any = False
    for inv in ctx.fixture.invocations:
        a = ctx.spec.agent(inv.name)
        if not a or not a.prompt_contract.required_sections:
            continue
        seen_any = True
        sections = set(_section_titles(inv.prompt))
        missing = [s for s in a.prompt_contract.required_sections if s not in sections]
        if missing:
            yield AssertionResult(
                assertion_id="L2-prompt-sections", layer="", severity="",
                agent=inv.name, status="fail",
                message=f"prompt missing sections: {missing}",
                evidence=[{"kind": "invocation", "id": inv.invocation_id}],
            )
        else:
            yield AssertionResult(
                assertion_id="L2-prompt-sections", layer="", severity="",
                agent=inv.name, status="pass",
                message="all required sections present",
            )
    if not seen_any:
        yield AssertionResult(
            assertion_id="L2-prompt-sections", layer="", severity="", status="skip",
            message="no agents declare required prompt sections",
        )


@register(id="L2-prompt-required-fields", layer="L2", default_severity="blocker",
          description="Each sub-agent prompt contains required fields/keys.")
def _l2_prompt_required_fields(ctx: AssertionContext) -> Iterable[AssertionResult]:
    seen_any = False
    for inv in ctx.fixture.invocations:
        a = ctx.spec.agent(inv.name)
        if not a or not a.prompt_contract.required_fields:
            continue
        seen_any = True
        missing = [
            f for f in a.prompt_contract.required_fields
            if f.lower() not in (inv.prompt or "").lower()
        ]
        if missing:
            yield AssertionResult(
                assertion_id="L2-prompt-required-fields", layer="", severity="",
                agent=inv.name, status="fail",
                message=f"prompt missing required field tokens: {missing}",
            )
        else:
            yield AssertionResult(
                assertion_id="L2-prompt-required-fields", layer="", severity="",
                agent=inv.name, status="pass",
                message="all required field tokens present",
            )
    if not seen_any:
        yield AssertionResult(
            assertion_id="L2-prompt-required-fields", layer="", severity="", status="skip",
            message="no agents declare required prompt fields",
        )


@register(id="L2-prompt-forbidden-input", layer="L2", default_severity="blocker",
          description="No forbidden upstream-input strings leak into a sub-agent prompt.")
def _l2_prompt_forbidden_input(ctx: AssertionContext) -> Iterable[AssertionResult]:
    seen_any = False
    for inv in ctx.fixture.invocations:
        a = ctx.spec.agent(inv.name)
        if not a or not a.prompt_contract.forbidden_input:
            continue
        seen_any = True
        bad = [s for s in a.prompt_contract.forbidden_input if s in (inv.prompt or "")]
        if bad:
            yield AssertionResult(
                assertion_id="L2-prompt-forbidden-input", layer="", severity="",
                agent=inv.name, status="fail",
                message=f"forbidden input strings present in prompt: {bad}",
            )
        else:
            yield AssertionResult(
                assertion_id="L2-prompt-forbidden-input", layer="", severity="",
                agent=inv.name, status="pass", message="no forbidden inputs in prompt",
            )
    if not seen_any:
        yield AssertionResult(
            assertion_id="L2-prompt-forbidden-input", layer="", severity="", status="skip",
            message="no agents declare forbidden input strings",
        )


@register(id="L2-prompt-forbidden-downstream", layer="L2", default_severity="blocker",
          description="No forbidden downstream content (e.g., raw user secrets) leaks downstream.")
def _l2_prompt_forbidden_downstream(ctx: AssertionContext) -> Iterable[AssertionResult]:
    seen_any = False
    for inv in ctx.fixture.invocations:
        a = ctx.spec.agent(inv.name)
        if not a or not a.prompt_contract.forbidden_downstream:
            continue
        seen_any = True
        bad = [s for s in a.prompt_contract.forbidden_downstream if s in (inv.prompt or "")]
        if bad:
            yield AssertionResult(
                assertion_id="L2-prompt-forbidden-downstream", layer="", severity="",
                agent=inv.name, status="fail",
                message=f"forbidden downstream strings present: {bad}",
            )
        else:
            yield AssertionResult(
                assertion_id="L2-prompt-forbidden-downstream", layer="", severity="",
                agent=inv.name, status="pass",
                message="no forbidden downstream content in prompt",
            )
    if not seen_any:
        yield AssertionResult(
            assertion_id="L2-prompt-forbidden-downstream", layer="", severity="", status="skip",
            message="no agents declare forbidden downstream content",
        )


@register(id="L2-output-sections", layer="L2", default_severity="blocker",
          description="Each sub-agent's response contains the declared output sections.")
def _l2_output_sections(ctx: AssertionContext) -> Iterable[AssertionResult]:
    seen_any = False
    for inv in ctx.fixture.invocations:
        a = ctx.spec.agent(inv.name)
        if not a or not a.output_contract.must_contain_sections:
            continue
        seen_any = True
        sections = set(_section_titles(inv.response or ""))
        missing = [s for s in a.output_contract.must_contain_sections if s not in sections]
        if missing:
            yield AssertionResult(
                assertion_id="L2-output-sections", layer="", severity="",
                agent=inv.name, status="fail",
                message=f"response missing sections: {missing}",
            )
        else:
            yield AssertionResult(
                assertion_id="L2-output-sections", layer="", severity="",
                agent=inv.name, status="pass",
                message="all required output sections present",
            )
    if not seen_any:
        yield AssertionResult(
            assertion_id="L2-output-sections", layer="", severity="", status="skip",
            message="no agents declare required output sections",
        )


@register(id="L2-output-forbidden", layer="L2", default_severity="blocker",
          description="Sub-agent response does not contain forbidden strings.")
def _l2_output_forbidden(ctx: AssertionContext) -> Iterable[AssertionResult]:
    seen_any = False
    for inv in ctx.fixture.invocations:
        a = ctx.spec.agent(inv.name)
        if not a or not a.output_contract.forbidden:
            continue
        seen_any = True
        bad = [s for s in a.output_contract.forbidden if s in (inv.response or "")]
        if bad:
            yield AssertionResult(
                assertion_id="L2-output-forbidden", layer="", severity="",
                agent=inv.name, status="fail",
                message=f"forbidden strings in response: {bad}",
            )
        else:
            yield AssertionResult(
                assertion_id="L2-output-forbidden", layer="", severity="",
                agent=inv.name, status="pass", message="no forbidden output strings",
            )
    if not seen_any:
        yield AssertionResult(
            assertion_id="L2-output-forbidden", layer="", severity="", status="skip",
            message="no agents declare forbidden output strings",
        )


ASSERTIONS = [
    _l2_prompt_sections,
    _l2_prompt_required_fields,
    _l2_prompt_forbidden_input,
    _l2_prompt_forbidden_downstream,
    _l2_output_sections,
    _l2_output_forbidden,
]

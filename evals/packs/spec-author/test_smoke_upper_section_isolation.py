"""F1 per-section isolation contract for upper sections: the prompt
deliberately mixes problem-narrative, solution direction, ownership,
and rollout in one paragraph. The drafter must split them into the
correct upper sections; cross-section leakage MUST NOT occur:
Solution Summary must not contain problem-narrative phrases or
owner names; Problem Statement must not preempt the solution or
name owners; Goals must not name owners or describe rollout.

Ported from legacy ``cases/smoke-upper-section-isolation/``.
"""
from __future__ import annotations

import re

import pytest

PROMPT = """\
@spec-author create a new spec at `docs/specs/sla-dashboard.md` for
an internal SLA-tracking dashboard.

Background and what we want:

The on-call rotation is drowning. Engineers spend ~12 hours/week
chasing SLO breaches across five services, and we have no single
view of which SLOs are red right now. The platform team owns this;
Maya Chen (platform PM) and Devon Park (platform EM) will review.
We want to build a dashboard that shows current SLO state per
service, with drill-down to recent breach events. Success means
on-call gets to root cause in under 10 minutes p75 within one
quarter of launch. Roll out behind a flag to platform first, then
the rest of engineering two weeks later.

Please draft the spec.

## Pre-supplied answers (do not park; proceed straight through)

- **Stop 0 (output location):** `output_path: docs/specs/sla-dashboard.md, spec_kind: technical`
- **Stop A (structure approval):** `APPROVE` (first ask)

Proceed end-to-end without waiting for further user input.
"""


def _section(text: str, name: str, max_chars: int = 800) -> str:
    """Return up to ``max_chars`` of the body of section ``## name``."""
    pattern = re.compile(
        rf"##\s+{re.escape(name)}\s*\n([\s\S]{{0,{max_chars}}})", re.IGNORECASE
    )
    m = pattern.search(text)
    return m.group(1) if m else ""


@pytest.mark.pack
@pytest.mark.slow
def test_upper_section_isolation(agent_pack):
    ws = agent_pack("spec-author")
    result = ws.run_agent(prompt=PROMPT, agent="spec-author", timeout=900)
    if not result.usable:
        pytest.skip(result.unavailable_reason())
    assert result.ok, f"spec-author failed; see {result.log_path}"

    spec = ws.find_one("docs/specs/sla-dashboard.md")
    assert spec, f"spec missing; see {result.log_path}"
    text = spec.read_text(encoding="utf-8")

    sol = _section(text, "Solution Summary")
    for leak in ("drowning", "12 hours/week", "no single view"):
        assert leak not in sol, (
            f"Solution Summary leaks problem-narrative phrase {leak!r}; "
            f"see {result.log_path}"
        )
    for owner in ("Maya", "Devon", "platform PM", "platform EM"):
        assert owner not in sol, (
            f"Solution Summary names owner {owner!r}; see {result.log_path}"
        )

    prob = _section(text, "Problem Statement")
    for sol_word in ("dashboard", "drill-down"):
        assert sol_word not in prob.lower(), (
            f"Problem Statement preempts solution with {sol_word!r}; "
            f"see {result.log_path}"
        )
    for owner in ("Maya", "Devon"):
        assert owner not in prob, (
            f"Problem Statement names owner {owner!r}; "
            f"see {result.log_path}"
        )

    goals = _section(text, "Goals & Success Metrics")
    for owner in ("Maya", "Devon", "platform PM", "platform EM"):
        assert owner not in goals, (
            f"Goals names owner {owner!r}; see {result.log_path}"
        )
    for rollout in ("behind a flag", "two weeks later"):
        assert rollout not in goals.lower(), (
            f"Goals describes rollout with {rollout!r}; "
            f"see {result.log_path}"
        )

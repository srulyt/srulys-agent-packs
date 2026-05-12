"""Smoke coverage for the 8 styled archetype recipes added in session
``2026-05-04-c8d3b2a1``. Each parametrised case asks
``@story-orchestrator`` to build a deck featuring one specific
archetype, then asserts that the resulting ``deck-spec.json`` actually
selects that ``style_recipe`` and that the deck/QA artefacts exist.

Ported from legacy ``cases/smoke-archetype-*/``. The 8 archetypes:
``funnel``, ``waterfall``, ``risk_heatmap``, ``flywheel``,
``priority_matrix``, ``decision_options``, ``footer_source``,
``appendix_dense``.
"""
from __future__ import annotations

import json

import pytest

ARCHETYPES = [
    pytest.param(
        "funnel",
        """\
# Smoke -- Funnel

## Audience & Decision

Q3 sales-pipeline review. Audience: CRO + sales ops. Decision needed:
where to invest in conversion. Stages (4): Leads (1000) -> MQL (400)
-> SQL (120) -> Closed Won (30). The largest leak (Leads->MQL, 60%
drop) gets called out.

## Tone

Professional, data-led, decision-forcing.

## Approval gate

When you reach the proposal, I will reply ``APPROVED``. When the deck
is built and QA-passed, return the path to ``output.pptx``.

## Renderer expectation

Use the ``funnel`` styled recipe (function ``_styled_funnel``) for the
relevant slide. Set ``style: "styled"`` and ``style_recipe: "funnel"``
and populate ``funnel_stages[]`` (3-6 entries, with optional ``rate``).
""",
        id="funnel",
    ),
    pytest.param(
        "waterfall",
        """\
# Smoke -- Waterfall / Value Bridge

## Audience & Decision

FY26 revenue-bridge for the CFO. Decompose FY25 revenue ($10M) ->
FY26 plan ($14M) into 3-4 contributing components: pricing increase
(+$2M), Q2 churn (-$1M), new logos (+$3M). Show the running total.

## Tone

Professional, data-led, decision-forcing.

## Approval gate

When you reach the proposal, I will reply ``APPROVED``. When the deck
is built and QA-passed, return the path to ``output.pptx``.

## Renderer expectation

Use the ``waterfall`` styled recipe (function ``_styled_waterfall``).
Set ``style: "styled"`` and ``style_recipe: "waterfall"`` and populate
``waterfall.{start,steps[],end,units}``.
""",
        id="waterfall",
    ),
    pytest.param(
        "risk_heatmap",
        """\
# Smoke -- Risk Heatmap

## Audience & Decision

Quarterly enterprise-risk register for the COO. Decision needed: which
3 risks get owners + mitigation funding this quarter. Risks (5):
vendor SLA failure (high/high), spec drift (high/med), hiring slip
(low/low), data-loss event (low/high), tooling outage (med/med).

## Tone

Professional, data-led, decision-forcing.

## Approval gate

When you reach the proposal, I will reply ``APPROVED``. When the deck
is built and QA-passed, return the path to ``output.pptx``.

## Renderer expectation

Use the ``risk_heatmap`` styled recipe (function
``_styled_risk_heatmap``). Set ``style: "styled"`` and
``style_recipe: "risk_heatmap"`` and populate ``risks[]`` (>=3) and
``axes.{x_label,y_label}``.
""",
        id="risk_heatmap",
    ),
    pytest.param(
        "flywheel",
        """\
# Smoke -- Flywheel

## Audience & Decision

Growth-loop pitch for new investors. Audience: Series-B prospects.
Decision needed: investor confidence in the compounding mechanism.
Stages (4): more users -> more data -> better recommendations -> more
users return. Centre label: 'Compounding network effect'.

## Tone

Professional, data-led, decision-forcing.

## Approval gate

When you reach the proposal, I will reply ``APPROVED``. When the deck
is built and QA-passed, return the path to ``output.pptx``.

## Renderer expectation

Use the ``flywheel`` styled recipe (function ``_styled_flywheel``).
Set ``style: "styled"`` and ``style_recipe: "flywheel"`` and populate
``flywheel_stages[]`` (3-6) and ``center_label``.
""",
        id="flywheel",
    ),
    pytest.param(
        "priority_matrix",
        """\
# Smoke -- 2x2 / Priority Matrix

## Audience & Decision

Engineering backlog triage. Audience: VP Eng + product. Decision
needed: which initiatives to staff in H1. Plot 4-6 candidate
initiatives on effort (low/high) x value (low/high). Items: SSO
migration (high effort/high value), tooltip polish (low/low),
reporting v2 (high/high), error-page redesign (low/high). Mark the
chosen 'quick wins' quadrant.

## Tone

Professional, data-led, decision-forcing.

## Approval gate

When you reach the proposal, I will reply ``APPROVED``. When the deck
is built and QA-passed, return the path to ``output.pptx``.

## Renderer expectation

Use the ``priority_matrix`` styled recipe. Set
``style_recipe: "priority_matrix"`` and populate ``matrix_items[]``
(>=3, exactly one with ``recommended: true``), ``axes``, and
``quadrant_labels`` (length 4).
""",
        id="priority_matrix",
    ),
    pytest.param(
        "decision_options",
        """\
# Smoke -- Decision Options Table

## Audience & Decision

Vendor selection for production data warehouse. Decision needed: pick
a vendor. Compare 4 vendors (Acme, Globex, Initech, Umbra) across
criteria (Cost, Latency, Support, SOC2 compliance). Recommend Acme.

## Tone

Professional, data-led, decision-forcing.

## Approval gate

When you reach the proposal, I will reply ``APPROVED``. When the deck
is built and QA-passed, return the path to ``output.pptx``.

## Renderer expectation

Use the ``decision_options`` styled recipe (NOT the 3-column
``comparison-columns`` simple builder -- this case has >3 options).
Set ``style_recipe: "decision_options"`` and populate ``options[]``
(>=4), ``criteria[]``, and ``recommendation`` (one of the option
names).
""",
        id="decision_options",
    ),
    pytest.param(
        "footer_source",
        """\
# Smoke -- Footer Source

## Audience & Decision

Confidential Series-B pitch with cited research. Audience: VC
partners. Every chart slide cites its source; every slide carries a
'Confidential' marker; every slide has a 'page N / total' footer.
Use a regular content / data-callout slide and overlay the footer.

## Tone

Professional, data-led, decision-forcing.

## Approval gate

When you reach the proposal, I will reply ``APPROVED``. When the deck
is built and QA-passed, return the path to ``output.pptx``.

## Renderer expectation

Apply the ``footer_source`` partial (function
``_apply_footer_source``) on top of an existing slide builder (NOT
one of the new archetype recipes -- proves the partial composes).
At least one slide must have a non-null ``footer`` block populating
at least one of ``footer.{source,page,confidentiality}``.
""",
        id="footer_source",
    ),
    pytest.param(
        "appendix_dense",
        """\
# Smoke -- Appendix Dense

## Audience & Decision

Board pre-read for Q3 review. Audience: board of directors. The body
deck (5-7 slides) ends with one Appendix Dense slide carrying
methodology, cohort definition, raw data table, and caveats -- high
density is the point.

## Tone

Professional, data-led, decision-forcing.

## Approval gate

When you reach the proposal, I will reply ``APPROVED``. When the deck
is built and QA-passed, return the path to ``output.pptx``.

## Renderer expectation

Use the ``appendix_dense`` styled recipe. Set
``style_recipe: "appendix_dense"``, ``appendix: true``, and
``panels[]`` (length 2-4).
""",
        id="appendix_dense",
    ),
]


@pytest.mark.pack
@pytest.mark.slow
@pytest.mark.parametrize("recipe,prompt_body", ARCHETYPES)
def test_archetype_recipe(copilot_pack, recipe, prompt_body):
    ws = copilot_pack("story-telling-agent")
    prompt = "@story-orchestrator\n\n" + prompt_body
    result = ws.run_agent(prompt=prompt, agent="story-orchestrator", timeout=900)
    assert result.ok, f"story-orchestrator failed; see {result.log_path}"

    deck_specs = ws.glob(
        ".story-telling-stm/runs/*/agents/deck-builder/deck-spec.json"
    )
    assert deck_specs, f"deck-spec.json missing; see {result.log_path}"

    spec_text = deck_specs[0].read_text(encoding="utf-8")
    assert recipe in spec_text, (
        f"deck-spec.json does not reference recipe {recipe!r}; "
        f"see {result.log_path}\n--- deck-spec.json ---\n{spec_text[:2000]}"
    )

    pptx = ws.glob(
        ".story-telling-stm/runs/*/agents/deck-builder/output.pptx"
    )
    assert pptx and pptx[0].stat().st_size > 0, (
        f"output.pptx missing or empty; see {result.log_path}"
    )

    qa = ws.glob(
        ".story-telling-stm/runs/*/agents/deck-critic/qa-report.json"
    )
    assert qa, f"qa-report.json missing; see {result.log_path}"
    # The recipe-used should also appear in the deck-spec; sanity-check
    # the JSON is well-formed.
    json.loads(spec_text)

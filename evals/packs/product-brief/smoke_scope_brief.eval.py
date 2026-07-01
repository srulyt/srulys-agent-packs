"""Builder-style eval (``*.eval.py``) — fixtures + glob-count + judge example.

Shows how the fluent builder stages *individual* fixture files (the README
that documents the fixture is deliberately NOT fed to the agent), asserts an
exact artifact count with ``expect_glob_count``, adds a custom ``check()``
predicate over a produced file, and finishes with an LLM judge. Run it like a
Markdown eval::

    evalpilot run evals/packs/product-brief/smoke_scope_brief.eval.py
"""

from evalpilot import Eval

PROMPT = """\
@brief-orchestrator

I want a brief that describes the scope of our Data Products MVP so partner
teams understand what is in and out of scope. Source material is in
``inputs/``:

- A scope overview (``scope-overview.md``)
- The per-surface in/out-of-scope boundaries (``surfaces.md``)

Audience: partner engineering teams. This is NOT a decision brief -- the
team has already committed to building the MVP. No approval, funding, or
go/no-go is being requested. Please describe the scope; do not invent a
decision to ask for.
"""

_BRIEF = ".product-brief-agent-stm/runs/*/agents/brief-orchestrator/product-brief.md"
_MATURITY = (
    ".product-brief-agent-stm/runs/*/agents/brief-orchestrator/"
    "maturity-assessment.md"
)


def _records_scope_brief(ctx) -> tuple[bool, str]:
    """The maturity assessment must classify the brief as a scope-brief."""
    text = ctx.read(_MATURITY)
    if text is None:
        return False, "maturity-assessment.md missing"
    ok = "scope-brief" in text.lower()
    return ok, "" if ok else "maturity-assessment.md does not record 'scope-brief'"


eval = (
    Eval("product-brief-scope-brief", target="brief-orchestrator", kind="agent",
         tags=["pack", "slow", "judge"], timeout=600)
    .summarize(
        "A scope-description brief classifies as scope-brief and omits a "
        "manufactured decision ask."
    )
    .describe(
        "Smoke: scope-brief (Data Products MVP scope description).\n\n"
        "Exercises the Brief Type axis. The source describes the in/out-of-scope "
        "boundary of an MVP and asks for NO decision, approval, or funding. The "
        "orchestrator should classify the brief as a scope-brief, expand Problem "
        "Scope and Solution Scope, and omit a Call to Action / standalone Open "
        "Questions section rather than manufacturing a decision ask."
    )
    # Stage only the genuine source docs into inputs/. The fixture directory
    # also carries a README.md describing the fixture for harness maintainers;
    # feeding that commentary to the SUT would pollute its inputs, so it is
    # deliberately excluded (this is exactly why per-file staging is useful).
    .copy("fixtures/smoke_scope_brief/scope-overview.md", "inputs")
    .copy("fixtures/smoke_scope_brief/surfaces.md", "inputs")
    .prompt(PROMPT)
    .expect_glob_count(_BRIEF, equals=1, name="exactly one product-brief.md")
    .expect_file(_MATURITY)
    .check("maturity records scope-brief", _records_scope_brief)
    .judge(
        "Score 1.0 ONLY if the brief (a) is structured as a scope description "
        "with distinct Problem Scope and Solution Scope sections that carry "
        "explicit in-scope vs out-of-scope content (surface by surface for the "
        "solution), (b) contains NO decision/approval/funding/go-no-go ask and "
        "NO standalone Open Questions section, and (c) does not invent a Call "
        "to Action. Score 0.5 if the scope sections are present but an "
        "unsolicited decision ask or a standalone Open Questions section was "
        "added. Score 0.0 if it reads as a generic decision brief that asks the "
        "reader to decide.",
        artifact=_BRIEF,
        threshold=0.7,
    )
    .metric("judge_score", "$judge.score", direction="higher_is_better",
            baseline="rolling_mean", tolerance=0.1)
    .build()
)

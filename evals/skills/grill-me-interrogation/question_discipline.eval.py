"""Builder-style eval (``*.eval.py``) — custom ``check()`` predicate example.

The interesting bit is a Python ``check()`` predicate that counts questions
in the streamed output — a computation the declarative Markdown DSL cannot
express. It encodes the skill's contract that there is NO maximum question
count (the interrogation should ask *several* questions), which a fixed
assertion kind could not capture. Run it like a Markdown eval::

    evalpilot run evals/skills/grill-me-interrogation/question_discipline.eval.py
"""

from evalpilot import Eval

PROMPT = """\
Here is an under-specified feature brief: "We want to add a 'share
report' feature so users can share a generated report with people
outside their organization. It should be reasonably fast."

Grill me to close the requirement gaps before any PRD is drafted. Ask
your gap-closing questions now. (Note: the brief deliberately leaves the
authentication/sharing-access model unspecified, and leaves the
performance target as a vague 'reasonably fast'.) Do not draft a PRD;
just produce your interrogation questions.
"""


def _asks_several_questions(ctx) -> tuple[bool, str]:
    """No max question count — but a real interrogation asks several.

    Counts question lines in stdout (any line containing a '?', so it is
    robust to markdown formatting such as ``**1. [P0] ...?** (note)``) and
    passes when at least three are present. This is the kind of computed,
    threshold-based gate the Markdown DSL can't express, which is why it
    lives in a builder eval.
    """
    text = ctx.stdout or ""
    question_lines = [ln for ln in text.splitlines() if "?" in ln]
    n = len(question_lines)
    ok = n >= 3
    return ok, f"found {n} question line(s); expected >= 3"


eval = (
    Eval("grill-me-question-discipline", target="grill-me-interrogation",
         kind="skill", tags=["skill", "slow", "judge"], timeout=300)
    .summarize("Grill-me questions are well-formed, tagged, and MC-vs-freeform correct.")
    .describe(
        "Skill-in-isolation eval: grill-me-interrogation question discipline.\n\n"
        "Gives the skill an under-specified feature brief containing at least one "
        "enumerable-answer gap (auth model) and at least one open-ended gap "
        "(latency budget), and asks it to 'grill me' to close gaps. Judges "
        "question discipline: one gap per question, P0/P1/P2 tags, multiple-choice "
        "where applicable (with an escape) vs. freeform, and no invented answers.\n\n"
        "The judge does NOT assert any maximum question count — the skill removes "
        "the legacy cap deliberately."
    )
    .prompt(PROMPT)
    # Structural gate: priority tags must be present.
    .expect_stdout(["P0", "P1", "P2"], name="has a P0/P1/P2 priority tag")
    # Custom predicate: several questions, with no upper bound.
    .check("asks several questions (no max)", _asks_several_questions)
    .judge(
        "The response is a grill-me interrogation question set. It MUST "
        "satisfy ALL of:\n"
        "(a) Each question targets exactly ONE gap — no compound questions "
        "    bundling two decisions.\n"
        "(b) Every question is tagged with a P0/P1/P2 priority, with blockers "
        "    (P0) flagged first.\n"
        "(c) The enumerable gap (the auth / sharing-access model) is posed as "
        "    MULTIPLE-CHOICE with 2-6 sensible, mutually-distinct options PLUS "
        "    an escape such as 'Not sure / decide later' (or an explicit "
        "    freeform/'specify your own' affordance). It is acceptable for this "
        "    to be expressed via an ask_user-style call or inline option list.\n"
        "(d) The open-ended gap (the latency / performance budget) is posed as "
        "    a FREEFORM question, NOT as fabricated buckets like fast/medium/slow.\n"
        "(e) No answers are invented to fill the spec — the skill asks rather "
        "    than assuming.\n"
        "Do NOT penalise the response for asking 'too many' questions; there is "
        "no maximum question count. Score 1.0 only if all five (a-e) hold. "
        "Score 0.5 if 3-4 hold. Score 0.0 otherwise.",
        threshold=0.7,
    )
    .metric("judge_score", "$judge.score", direction="higher_is_better",
            baseline="rolling_mean", tolerance=0.1)
    .build()
)

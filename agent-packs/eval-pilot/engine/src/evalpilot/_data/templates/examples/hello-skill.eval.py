"""Builder-style eval — the power-user escape hatch.

Same capabilities as a ``*.eval.md`` file, but expressed in Python so you can
compute prompts, share fixtures, or register custom ``check`` predicates. Run
it exactly like a Markdown eval:

    evalpilot run examples/hello-skill.eval.py

Delete this file once you have real evals.
"""

from evalpilot import Eval

eval = (
    Eval("hello-skill", target="REPLACE-WITH-YOUR-SKILL", kind="skill",
         tags=["smoke"], timeout=600)
    .describe("A good result: the skill emits output that satisfies the criteria.")
    .prompt(
        "Replace with a prompt that exercises a real scenario for your skill. "
        "Do NOT include the expected answer."
    )
    .expect_stdout("REPLACE", ignore_case=True)   # cheap structural gate
    .judge(
        "Be strict: score 1.0 only if ALL criteria are met, 0.5 for partial, "
        "0.0 if off-topic.",
        threshold=0.7,
    )
    .metric("judge_score", "$judge.score",
            direction="higher_is_better", baseline="rolling_mean", tolerance=0.1)
    .build()
)

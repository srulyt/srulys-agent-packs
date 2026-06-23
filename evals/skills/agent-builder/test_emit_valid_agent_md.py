"""Skill-in-isolation eval for the ``agent-builder`` skill.

Demonstrates the first-class "evaluate a skill outside of any agent
pack" use case. The test stages only the single skill into the
workspace -- no agents, no other skills -- then asks Copilot CLI to use
it for a small task and judges the output.

If the skill's prompts are degraded (e.g. the YAML quoting rule is
removed), this eval should fail.
"""

from __future__ import annotations

import pytest


PROMPT = """\
Generate a minimal `.agent.md` file for a hypothetical agent named
`echo-bot`. The agent's only job is to echo back the user's message.

Constraints:
- Use proper YAML front-matter.
- Include a `description` field with a quoted string that contains the
  word "Echo" and at least one trigger keyword.
- Include a `tools` list.
- Add a short markdown body explaining the role.

Output the full file contents inside a single fenced code block. Do not
write anything to disk.
"""


@pytest.mark.skill
@pytest.mark.slow
@pytest.mark.judge
def test_agent_builder_emits_valid_agent_md(skill, judge):
    """Agent-builder skill produces a syntactically and semantically
    valid `.agent.md` for a trivial echo-bot specification."""
    ws = skill("agent-builder")

    result = ws.run_skill(
        skill="agent-builder",
        prompt=PROMPT,
        timeout=300,
        log_name="agent-builder",
    )
    if not result.usable:
        pytest.skip(result.unavailable_reason())
    assert result.ok, (
        f"copilot exited {result.returncode}; see {result.log_path}"
    )

    output = result.stdout
    assert "```" in output, "Expected the agent.md inside a fenced code block"

    # The skill's headline rule is "always quote the description". The
    # judge enforces it explicitly.
    verdict = judge(
        artifact=output,
        criteria=(
            "The assistant's response MUST contain a complete `.agent.md` "
            "file inside a fenced code block. The file MUST:\n"
            "1. Start with a YAML front-matter block delimited by `---`.\n"
            "2. Have a `description` field whose value is wrapped in "
            "   double quotes (the agent-builder skill's headline rule).\n"
            "3. Include the word 'Echo' (case-insensitive) in the "
            "   description.\n"
            "4. Include a `tools:` list.\n"
            "5. Have a non-empty markdown body after the front-matter.\n"
            "Score 1.0 only if all five are met. Score 0.6 if 3-4 met. "
            "Score 0.0 otherwise."
        ),
        threshold=0.7,
    )
    assert verdict.passed, (
        f"Judge rejected output (score={verdict.score:.2f}):\n{verdict.reasoning}"
    )

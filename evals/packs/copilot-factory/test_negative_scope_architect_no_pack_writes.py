"""Negative-scope smoke: when the user asks the factory to design (not build)
a 1-agent hello-world pack, the architect must produce ``architecture.md``
and stop -- no pack files written.

Ported from legacy ``cases/negative-scope-architect-no-pack-writes/``.
"""
from __future__ import annotations

import pytest

PROMPT = """\
Please design (architecture only -- do NOT build) a tiny single-agent
Copilot CLI pack that prints "hello, hello-world". One agent, no
skills, no state. Stop after the architecture review and present the
architecture for approval. Do not delegate to the engineer in this
turn.
"""


@pytest.mark.pack
@pytest.mark.slow
@pytest.mark.judge
def test_architect_does_not_write_pack_files(agent_pack, judge):
    ws = agent_pack("copilot-factory")

    result = ws.run_agent(prompt=PROMPT, agent="copilot-factory", timeout=900)
    if not result.usable:
        pytest.skip(result.unavailable_reason())
    assert result.ok, f"copilot-factory invocation failed; see {result.log_path}"

    arch_files = ws.glob(".copilot-factory/sessions/*/artifacts/architecture.md")
    assert arch_files, (
        f"expected an architecture.md to be produced; see {result.log_path}"
    )

    # Negative scope: no files under agent-packs/ should have been written.
    pack_writes = ws.glob("agent-packs/**/*.agent.md")
    assert not pack_writes, (
        f"architect must not write pack files in design-only mode; "
        f"unexpected writes: {pack_writes}; see {result.log_path}"
    )

    verdict = judge(
        artifact=arch_files[0].read_text(encoding="utf-8"),
        criteria=(
            "Score 1.0 only if the architecture document describes a single-agent "
            "Copilot CLI pack that prints 'hello, hello-world', is internally "
            "coherent (defines the agent's role, tools, and an output contract), "
            "and explicitly notes that this is the design phase only (no build "
            "delegation). Score 0.5 if the architecture is coherent but the "
            "scope-stop note is missing. Score 0.0 if the document fails to "
            "describe a single-agent hello-world pack."
        ),
        threshold=0.7,
    )
    assert verdict.passed, (
        f"architecture judge failed: {verdict.reasoning}; see {result.log_path}"
    )

"""Smoke evals for the ``copilot-factory`` agent pack.

Each test is a pytest function that:

1. Stages the pack (and shared skills/instructions) into a tmpdir
   workspace via the ``copilot_pack`` fixture.
2. Runs ``copilot -p ... --agent copilot-factory`` non-interactively.
3. Asserts on the artifacts the factory produces.
4. Optionally calls the LLM-as-judge helper (``judge`` fixture) to score
   the architecture document for semantic correctness.

These replace the legacy YAML cases under
``evals/packs/copilot-factory/cases/``. See
``evals/README.md`` for the authoring guide.
"""

from __future__ import annotations

import pytest


PROMPT_ISSUE_TRIAGE = """\
Please design and build a small Copilot CLI agent pack that helps a
maintainer triage incoming GitHub issues. The pack should have **two
agents**:

1. An orchestrator that receives an issue URL or number and returns a
   triage recommendation (label suggestions, priority, and a short
   summary of any duplicate or related issues it found).
2. A sub-agent specialised in searching the repository for related
   issues and prior discussion.

Treat this as a real production pack: it must include `agent-packs/<name>/`
with both agent definitions, a README, and explicit File Access Boundaries
on every agent. The triage feature is **issue triage** -- keep that
wording in your architecture document.

Use your standard four-phase workflow (architect -> engineer -> critic) and
land everything under your normal session directory.
"""


@pytest.mark.pack
@pytest.mark.slow
@pytest.mark.judge
def test_creates_two_agent_triage_pack(copilot_pack, judge):
    """Factory designs and builds a 2-agent issue-triage pack end-to-end."""
    ws = copilot_pack("copilot-factory")

    result = ws.run_agent(
        prompt=PROMPT_ISSUE_TRIAGE,
        agent="copilot-factory",
        timeout=900,
        log_name="copilot-factory",
    )

    # Run must complete cleanly. If it didn't, the log path tells the
    # operator (or @factory-engineer fix-loop) where to look.
    assert result.ok, (
        f"copilot-factory exited {result.returncode}; see {result.log_path}"
    )

    # 1) Architect produced an architecture artifact at the canonical path.
    arch_files = ws.glob(".copilot-factory/sessions/*/artifacts/architecture.md")
    assert len(arch_files) == 1, (
        f"expected exactly 1 architecture.md, got {len(arch_files)}: {arch_files}"
    )
    architecture = arch_files[0]

    # 2) Engineer produced a build manifest in the same session.
    manifests = ws.glob(".copilot-factory/sessions/*/artifacts/build-manifest.json")
    assert len(manifests) == 1, "expected exactly 1 build-manifest.json"

    # 3) Engineer wrote two .agent.md files for the new pack.
    agent_files = ws.glob("agent-packs/*/.github/agents/*.agent.md")
    assert len(agent_files) == 2, (
        f"expected 2 agents in the new pack, got {len(agent_files)}: {agent_files}"
    )

    # 4) Engineer wrote a README for the new pack.
    pack_readmes = ws.glob("agent-packs/*/README.md")
    assert len(pack_readmes) == 1, "new pack should have exactly one README.md"

    # 5) LLM judge: architecture document is on-topic and well-structured.
    verdict = judge(
        artifact=architecture.read_text(encoding="utf-8"),
        criteria=(
            "The architecture document MUST:\n"
            "1. Describe exactly two agents (an orchestrator + a search "
            "   sub-agent for finding related issues).\n"
            "2. Use the phrase 'issue triage' verbatim somewhere in the "
            "   document (the user requested this feature wording).\n"
            "3. Declare File Access Boundaries (read/write scopes) for "
            "   each of the two agents.\n"
            "4. Be coherent prose with named sections, not a stub.\n"
            "Score 1.0 only if all four are met. Score 0.5 if 2-3 are met. "
            "Score 0.0 if 0-1 are met."
        ),
        threshold=0.7,
    )
    assert verdict.passed, (
        f"Judge rejected architecture (score={verdict.score:.2f}):\n"
        f"{verdict.reasoning}"
    )

"""Req #3: prefer the `ask_user` tool per factory standard.

`ask_user` is a built-in Copilot CLI tool. The orchestrator
(`spec-author.agent.md`) surfaces user-facing prompts (Stop 0,
Stop V, Stop A, Stop B) via `ask_user(...)` calls rather than
verbatim-prose "reply with X / Y / Z" instructions.

This eval is a **static check** on the shipped orchestrator prompt
— it does not require a runtime tool-call trace from the harness.
It asserts:

- The agent prompt contains at least one `ask_user(` call.
- The agent prompt covers each of the four Stops (Stop 0, V, A, B)
  with at least one `ask_user` reference in the matching section.
- The `## How to Ask the User` conventions section is present.
- The prompt does NOT still ship the legacy "Reply with `KIND:`"
  verbatim Stop 0 instruction (regression guard — that prompt was
  rewritten to an `ask_user` call with `choices: ["product",
  "technical", "mixed"]`).

The check runs in the source tree (no agent invocation required),
so it is fast and harness-independent.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from evalpilot import assert_prose_not_contains


REPO_ROOT = Path(__file__).resolve().parents[3]
ORCHESTRATOR = (
    REPO_ROOT
    / "agent-packs"
    / "spec-author"
    / ".github"
    / "agents"
    / "spec-author.agent.md"
)


@pytest.mark.pack
def test_orchestrator_uses_ask_user_for_clarifications():
    assert ORCHESTRATOR.exists(), (
        f"orchestrator prompt not found at {ORCHESTRATOR}; "
        "cannot run static ask_user adoption check"
    )
    text = ORCHESTRATOR.read_text(encoding="utf-8")

    # At least one ask_user( invocation, and the conventions section.
    assert "ask_user(" in text, (
        "spec-author orchestrator must surface user-facing prompts "
        "via the built-in `ask_user` tool (factory standard, req #3)"
    )
    assert "## How to Ask the User" in text, (
        "orchestrator must include a `## How to Ask the User` "
        "conventions section documenting choices vs. freeform usage"
    )

    # Stop-by-stop coverage: each Stop section must contain an ask_user call.
    # The agent prompt uses H2 headings for stops; locate each section by
    # H2 heading and check the slice up to the next H2.
    def _section(heading: str) -> str:
        idx = text.find(heading)
        if idx < 0:
            return ""
        rest = text[idx + len(heading):]
        next_h2 = rest.find("\n## ")
        return rest if next_h2 < 0 else rest[:next_h2]

    stop_sections = {
        "Stop 0": "## Output Location & Spec-Kind Intake (Stop 0 — runs before context-discovery)",
        "Stop V": "## Stop V — Mode Decision",
        "Stop A": "## Stop A Protocol",
        "Stop B": "## Stop B Protocol",
    }

    # Stop 0 might be under a different heading; fall back to scanning for
    # the "Resolving `output_path`" + "Resolving `spec_kind`" body.
    for label, heading in stop_sections.items():
        sec = _section(heading)
        if not sec and label == "Stop 0":
            # Fallback: find the output_path resolution block.
            idx = text.find("### Resolving `output_path`")
            if idx >= 0:
                sec = text[idx : idx + 4000]
        assert "ask_user(" in sec, (
            f"{label} section must surface its user prompt via "
            f"`ask_user(...)` (factory standard, req #3); "
            f"heading searched: {heading!r}"
        )

    # Regression guard: legacy verbatim Stop 0 KIND prompt is gone.
    assert_prose_not_contains(
        text,
        "Reply with `KIND: product`, `KIND: technical`, or `KIND: mixed`",
        extra=(
            "legacy verbatim 'Reply with KIND:' Stop 0 prompt must be "
            "replaced by an ask_user(choices=[product, technical, mixed]) call"
        ),
    )

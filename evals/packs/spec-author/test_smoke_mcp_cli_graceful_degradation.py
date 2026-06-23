"""MCP/CLI graceful-degradation contract: zero MCP tools available
but the user prompt mentions "we usually have the GitHub MCP". The
detective must record an unmet expectation AND set
``graceful_degradation: true`` rather than hard-failing.

Ported from legacy ``cases/smoke-mcp-cli-graceful-degradation/``.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures" / "mcp_cli_graceful_degradation"

PROMPT = """\
@spec-author write a PRD for **Workspace activity digest** -- a daily
summary of changes in a product workspace.

We usually have the GitHub MCP available, so please use it for prior
art research if it's there.

Inputs available locally:
- `docs/personas.md` (PM and EM)
- `docs/spike-notes.md`

Treat as single-team, no new datastore, no security-surface change.

## Pre-supplied answers (do not park; proceed straight through)

- **Stop 0 (output location):** `output_path: docs/specs/digest.md, spec_kind: product`
- **Stop A (structure approval):** `APPROVE` (first ask)

Proceed end-to-end without waiting for further user input.
"""


@pytest.mark.pack
@pytest.mark.slow
def test_mcp_cli_graceful_degradation(agent_pack):
    ws = agent_pack("spec-author")
    ws.stage_files(FIXTURES, dest_subdir=".")

    result = ws.run_agent(prompt=PROMPT, agent="spec-author", timeout=900)
    if not result.usable:
        pytest.skip(result.unavailable_reason())
    assert result.ok, f"spec-author failed; see {result.log_path}"

    discoveries = ws.glob(
        ".spec-author/sessions/*/artifacts/discovery.json"
    )
    assert discoveries, f"discovery.json missing; see {result.log_path}"
    raw = discoveries[0].read_text(encoding="utf-8")
    discovery = json.loads(raw)

    assert discovery.get("graceful_degradation") is True, (
        f"discovery must set graceful_degradation: true; "
        f"got {discovery.get('graceful_degradation')!r}; "
        f"see {result.log_path}"
    )
    assert discovery.get("mcps_detected") in (None, [], {}), (
        f"mcps_detected must be empty when no MCPs are available; "
        f"got {discovery.get('mcps_detected')!r}; "
        f"see {result.log_path}"
    )
    assert "github" in raw.lower(), (
        f"discovery should record the unmet github-mcp expectation; "
        f"see {result.log_path}"
    )

    assert ws.find_one("docs/specs/digest.md"), (
        f"spec must still be drafted under graceful degradation; "
        f"see {result.log_path}"
    )

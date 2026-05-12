"""Smoke: orchestrator must NOT redirect the user back to ``@copilot-factory``
when the SUT itself is ``@copilot-factory``. Regression for the Layer-2
override of the self-redirect bug.

Ported from legacy ``cases/smoke-orchestrator-no-self-redirect/``.
"""
from __future__ import annotations

import re

import pytest

PROMPT = """\
Add a new versioning rule to the spec-author agent pack. The rule
should require every spec to declare a semver version field and
fail the build if the version doesn't increment on a breaking
change.
"""

FORBIDDEN_REDIRECT_PATTERNS = [
    re.compile(r"please\s+re-issue", re.I),
    re.compile(r"prefix\s+with\s+@?copilot-factory", re.I),
    re.compile(r"prepend\s+@?copilot-factory", re.I),
    re.compile(r"this\s+work\s+is\s+owned\s+by\s+@?copilot-factory", re.I),
]


@pytest.mark.pack
@pytest.mark.slow
def test_orchestrator_does_not_self_redirect(copilot_pack):
    ws = copilot_pack("copilot-factory")

    result = ws.run_agent(prompt=PROMPT, agent="copilot-factory", timeout=900)
    assert result.ok, f"copilot-factory invocation failed; see {result.log_path}"

    # Intake must produce a session with state.json and a captured
    # user-request.md. A redirect-only response would create neither.
    state_files = ws.glob(".copilot-factory/sessions/*/state.json")
    assert state_files, (
        f"expected a session state.json to be created; orchestrator likely "
        f"redirected instead of running intake; see {result.log_path}"
    )

    request_files = ws.glob(".copilot-factory/sessions/*/context/user-request.md")
    assert request_files, (
        f"expected user-request.md to be captured; see {result.log_path}"
    )

    captured = request_files[0].read_text(encoding="utf-8")
    assert any(needle in captured.lower() for needle in ("spec-author", "version")), (
        f"user-request.md does not contain the original prompt content; "
        f"see {result.log_path}"
    )
    for pattern in FORBIDDEN_REDIRECT_PATTERNS:
        assert not pattern.search(captured), (
            f"user-request.md contains a self-redirect phrase {pattern.pattern!r}; "
            f"see {result.log_path}"
        )

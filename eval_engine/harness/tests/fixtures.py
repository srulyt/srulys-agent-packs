"""Synthetic-fixture helpers used across assertion tests."""

from __future__ import annotations

from eval_engine.harness import models


def make_spec(*, agents: list[dict] | None = None,
              ordering: list[tuple[str, str]] | None = None) -> models.PackSpec:
    agents = agents or [
        {
            "name": "factory-architect",
            "allowed_tools": ["read", "search", "write"],
            "write_scope_allow": [r"\.copilot-factory/sessions/.+/architecture\.md$"],
            "scope_deny": [r"^\\.git/"],
            "invocations": models.InvocationExpectation(min=1, max=2),
            "prompt_contract": models.PromptContract(
                required_sections=["Inputs", "Constraints"],
                required_fields=["user-request"],
                forbidden_input=["INTERNAL_SECRET"],
                forbidden_downstream=[],
            ),
            "output_contract": models.OutputContract(
                must_contain_sections=["Architecture", "Risks"],
                forbidden=["TODO"],
            ),
            "token_budget_max": 60000,
            "no_subagent_reinvocation": True,
        },
        {
            "name": "factory-critic",
            "allowed_tools": ["read", "search"],
            "write_scope_allow": [],
            "scope_deny": [],
            "invocations": models.InvocationExpectation(min=1, max=2),
            "prompt_contract": models.PromptContract(),
            "output_contract": models.OutputContract(),
            "no_subagent_reinvocation": True,
        },
    ]
    return models.PackSpec(
        pack="copilot-factory",
        orchestrator="copilot-factory",
        agents=[
            models.AgentSpec(
                name=a["name"],
                allowed_tools=a["allowed_tools"],
                write_scope_allow=a.get("write_scope_allow", []),
                read_scope_allow=a.get("read_scope_allow", []),
                scope_deny=a.get("scope_deny", []),
                invocations=a.get("invocations", models.InvocationExpectation()),
                prompt_contract=a.get("prompt_contract", models.PromptContract()),
                output_contract=a.get("output_contract", models.OutputContract()),
                token_budget_max=a.get("token_budget_max"),
                no_subagent_reinvocation=a.get("no_subagent_reinvocation", True),
            )
            for a in agents
        ],
        flow=models.FlowConstraints(
            ordering=ordering or [("factory-architect", "factory-critic")],
            no_unexpected_agents=True,
        ),
    )


def make_case(spec: models.PackSpec) -> models.CaseSpec:
    return models.CaseSpec(
        id="smoke-1",
        pack=spec.pack,
        description="synthetic",
        prompt_file="prompt.md",
        prompt_template_vars={},
        workspace_isolation="copy-tree",
        inputs_dir="inputs/",
        golden_dir="golden/",
        steps=[],
        teardown=models.TeardownPolicy(),
        expected=models.CaseExpected(),
        case_dir="/tmp/case",
    )


def make_invocation(name: str, *, prompt: str = "", response: str = "",
                    mode: str = "sync", tokens: int = 1000,
                    invocation_id: str = "inv-1",
                    completed: bool = True) -> models.AgentInvocation:
    return models.AgentInvocation(
        invocation_id=invocation_id, name=name, mode=mode,
        prompt=prompt, response=response, tokens=tokens, completed=completed,
    )


def make_tool_call(name: str, *, agent: str, call_id: str = "c-1",
                   args: dict | None = None) -> models.ToolCall:
    return models.ToolCall(
        call_id=call_id, name=name,
        actor=models.Actor(kind="subagent", name=agent, invocation_id="inv-1"),
        arguments=args or {},
    )


def make_file_access(path: str, op: str, *, agent: str,
                     confidence: str = "high") -> models.FileAccess:
    return models.FileAccess(
        path=path, op=op,
        actor=models.Actor(kind="subagent", name=agent, invocation_id="inv-1"),
        confidence=confidence,
    )


def make_fixture(*, invocations, tool_calls=None, file_accesses=None,
                 background_reads=None) -> models.Fixture:
    return models.Fixture(
        schema_version="1.0.0",
        pack="copilot-factory",
        case_id="smoke-1",
        session_id="sess-1",
        run_id="run-1",
        workspace_root="/tmp/ws",
        captured_at="2026-04-28T00:00:00Z",
        cli_version="1.0.37",
        os="Windows_NT",
        models={"orchestrator": "claude-sonnet-4.6"},
        invocations=invocations,
        tool_calls=list(tool_calls or []),
        file_accesses=list(file_accesses or []),
        background_reads=list(background_reads or []),
    )

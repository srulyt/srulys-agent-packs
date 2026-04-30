"""Loaders for specs, cases, rubrics, and fixtures.

All file I/O for declarative inputs flows through this module so we have a
single place to enforce schema invariants and emit ``ConfigError`` with a
useful path-prefix when something is malformed. Loaders return the
dataclasses defined in :mod:`models` — the rest of the harness consumes
those, never raw dicts.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any

import yaml  # PyYAML

from . import models


class ConfigError(ValueError):
    """Raised on schema violations in spec/case/rubric/fixture files."""


def _read_yaml(path: str | os.PathLike[str]) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    if not isinstance(data, dict):
        raise ConfigError(f"{path}: top-level must be a mapping")
    return data


def _read_json(path: str | os.PathLike[str]) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _require(d: dict[str, Any], key: str, where: str) -> Any:
    if key not in d:
        raise ConfigError(f"{where}: missing required key {key!r}")
    return d[key]


# ---------- Pack spec ----------------------------------------------------


def load_spec(path: str | os.PathLike[str]) -> models.PackSpec:
    raw = _read_yaml(path)
    where = str(path)
    pack = _require(raw, "pack", where)
    orch = _require(raw, "orchestrator", where)
    agents = []
    for i, a in enumerate(_require(raw, "agents", where) or []):
        agents.append(_load_agent(a, where=f"{where}#agents[{i}]"))
    flow_raw = raw.get("flow", {}) or {}
    flow = models.FlowConstraints(
        ordering=[tuple(x) for x in flow_raw.get("ordering", []) or []],
        no_unexpected_agents=bool(flow_raw.get("no_unexpected_agents", True)),
    )
    rubrics = [_load_rubric_ref(r, where=where) for r in raw.get("rubrics", []) or []]
    return models.PackSpec(
        pack=pack,
        orchestrator=orch,
        agents=agents,
        flow=flow,
        rubrics=rubrics,
        models=raw.get("models", {}) or {},
        loops=raw.get("loops", {}) or {},
    )


def _load_agent(a: dict[str, Any], *, where: str) -> models.AgentSpec:
    name = _require(a, "name", where)
    inv_raw = a.get("invocations", {}) or {}
    inv = models.InvocationExpectation(
        min=int(inv_raw.get("min", 0)),
        max=int(inv_raw.get("max", 1)),
        must_complete=bool(inv_raw.get("must_complete", True)),
    )
    pc_raw = a.get("prompt_contract", {}) or {}
    pc = models.PromptContract(
        required_sections=list(pc_raw.get("required_sections", []) or []),
        required_fields=list(pc_raw.get("required_fields", []) or []),
        forbidden_input=list(pc_raw.get("forbidden_input", []) or []),
        forbidden_downstream=list(pc_raw.get("forbidden_downstream", []) or []),
    )
    oc_raw = a.get("output_contract", {}) or {}
    oc = models.OutputContract(
        must_contain_sections=list(oc_raw.get("must_contain_sections", []) or []),
        forbidden=list(oc_raw.get("forbidden", []) or []),
        schema_ref=oc_raw.get("schema_ref"),
    )
    return models.AgentSpec(
        name=name,
        invocations=inv,
        allowed_tools=list(a.get("allowed_tools", []) or []),
        write_scope_allow=list(a.get("write_scope_allow", []) or []),
        read_scope_allow=list(a.get("read_scope_allow", []) or []),
        scope_deny=list(a.get("scope_deny", []) or []),
        prompt_contract=pc,
        output_contract=oc,
        token_budget_max=a.get("token_budget_max"),
        no_subagent_reinvocation=bool(a.get("no_subagent_reinvocation", True)),
    )


def _load_rubric_ref(r: dict[str, Any], *, where: str) -> models.RubricRef:
    return models.RubricRef(
        id=_require(r, "id", where),
        apply_to=_require(r, "apply_to", where),
        severity=str(r.get("severity", "info")),
        threshold=r.get("threshold"),
    )


# ---------- Case + workspace --------------------------------------------


def load_case(path: str | os.PathLike[str]) -> models.CaseSpec:
    raw = _read_yaml(path)
    where = str(path)
    case_dir = os.path.dirname(os.path.abspath(path))
    ws = raw.get("workspace", {}) or {}
    steps = [
        models.WorkspaceStep(
            kind=_require(s, "kind", where=f"{where}#steps[{i}]"),
            args={k: v for k, v in s.items() if k != "kind"},
        )
        for i, s in enumerate(ws.get("steps", []) or [])
    ]
    td_raw = raw.get("teardown", {}) or {}
    td = models.TeardownPolicy(
        policy=str(td_raw.get("policy", "delete-on-pass")),
        hooks=[
            models.WorkspaceStep(kind=h["kind"], args={k: v for k, v in h.items() if k != "kind"})
            for h in td_raw.get("hooks", []) or []
        ],
    )
    exp_raw = raw.get("expected", {}) or {}
    artifacts = [
        models.ExpectedArtifact(
            id=_require(x, "id", where=f"{where}#expected.artifacts"),
            path_pattern=_require(x, "path_pattern", where=f"{where}#expected.artifacts"),
            required=bool(x.get("required", True)),
        )
        for x in exp_raw.get("artifacts", []) or []
    ]
    inv_overrides = {
        name: models.InvocationExpectation(
            min=int(v.get("min", 0)),
            max=int(v.get("max", 1)),
            must_complete=bool(v.get("must_complete", True)),
        )
        for name, v in (exp_raw.get("invocations", {}) or {}).items()
    }
    expected = models.CaseExpected(
        artifacts=artifacts,
        invocations=inv_overrides,
        allowed_agent_types=exp_raw.get("allowed_agent_types"),
        rubric_targets={k: v for k, v in (exp_raw.get("rubric_targets", {}) or {}).items()},
    )
    return models.CaseSpec(
        id=_require(raw, "id", where),
        pack=_require(raw, "pack", where),
        description=str(raw.get("description", "")),
        prompt_file=str(raw.get("prompt_file", "prompt.md")),
        prompt_template_vars=dict(raw.get("prompt_template_vars", {}) or {}),
        workspace_isolation=str(ws.get("isolation", "copy-tree")),
        inputs_dir=ws.get("inputs_dir"),
        golden_dir=ws.get("golden_dir"),
        steps=steps,
        teardown=td,
        expected=expected,
        case_dir=case_dir,
    )


# ---------- Rubric -------------------------------------------------------


def load_rubric(path: str | os.PathLike[str]) -> models.Rubric:
    """Rubric files are markdown with a YAML front-matter block."""
    text = Path(path).read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ConfigError(f"{path}: rubric must start with YAML front-matter (---)")
    end = text.find("\n---\n", 4)
    if end == -1:
        raise ConfigError(f"{path}: rubric front-matter not terminated")
    front = yaml.safe_load(text[4:end]) or {}
    body = text[end + len("\n---\n") :]
    where = str(path)
    return models.Rubric(
        id=_require(front, "id", where),
        description=str(front.get("description", "")),
        prompt_template=body,
        output_schema=front.get("output_schema") or {
            "type": "object",
            "required": ["score", "rationale"],
        },
        scoring_anchors=dict(front.get("scoring_anchors", {}) or {}),
        inputs=list(front.get("inputs", []) or []),
    )


# ---------- Fixture ------------------------------------------------------


def load_fixture(path: str | os.PathLike[str]) -> models.Fixture:
    raw = _read_json(path)
    where = str(path)
    sv = str(raw.get("schema_version", "0.0.0"))
    if not sv.startswith("1."):
        raise ConfigError(f"{path}: unsupported fixture schema_version {sv!r}; expected 1.x")
    invocations = [
        models.AgentInvocation(
            invocation_id=_require(i, "invocation_id", where=f"{where}#invocations"),
            name=_require(i, "name", where=f"{where}#invocations"),
            mode=str(i.get("mode", "sync")),
            started_at=i.get("started_at"),
            ended_at=i.get("ended_at"),
            completed=bool(i.get("completed", True)),
            prompt=str(i.get("prompt", "")),
            response=i.get("response"),
            parent_invocation_id=i.get("parent_invocation_id"),
            tokens=i.get("tokens"),
        )
        for i in raw.get("invocations", []) or []
    ]
    tool_calls = [
        models.ToolCall(
            call_id=_require(t, "call_id", where=f"{where}#tool_calls"),
            name=_require(t, "name", where=f"{where}#tool_calls"),
            actor=_load_actor(t.get("actor", {}) or {}),
            arguments=t.get("arguments", {}) or {},
            success=t.get("success"),
            started_at=t.get("started_at"),
            ended_at=t.get("ended_at"),
            result_summary=t.get("result_summary"),
        )
        for t in raw.get("tool_calls", []) or []
    ]
    file_accesses = [
        models.FileAccess(
            path=_require(f, "path", where=f"{where}#file_accesses"),
            op=_require(f, "op", where=f"{where}#file_accesses"),
            actor=_load_actor(f.get("actor", {}) or {}),
            confidence=str(f.get("confidence", "high")),
            call_id=f.get("call_id"),
        )
        for f in raw.get("file_accesses", []) or []
    ]
    return models.Fixture(
        schema_version=sv,
        pack=_require(raw, "pack", where),
        case_id=_require(raw, "case_id", where),
        session_id=_require(raw, "session_id", where),
        run_id=_require(raw, "run_id", where),
        workspace_root=_require(raw, "workspace_root", where),
        captured_at=str(raw.get("captured_at", "")),
        cli_version=raw.get("cli_version"),
        os=raw.get("os"),
        models=raw.get("models", {}) or {},
        invocations=invocations,
        tool_calls=tool_calls,
        file_accesses=file_accesses,
        background_reads=list(raw.get("background_reads", []) or []),
        session_store=raw.get("session_store", {}) or {},
        raw=raw,
    )


def _load_actor(a: dict[str, Any]) -> models.Actor:
    return models.Actor(
        kind=str(a.get("kind", "orchestrator")),
        name=a.get("name"),
        invocation_id=a.get("invocation_id"),
    )


# ---------- Hashing helpers ---------------------------------------------


def file_hash(path: str | os.PathLike[str]) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def text_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

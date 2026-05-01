"""Build a v2 fixture from a local Copilot CLI process log.

The local CLI's ``~/.copilot/session-store.db`` rolls up an entire session
into a single ``turns`` row, which is too coarse for evaluation. The richer
data — every model request/response, every tool call's full unredacted
arguments, every sub-agent dispatch — lives in the **process log** at
``~/.copilot/logs/process-<pid>-<launch>.log``.

This module parses that log into the v2 fixture schema documented in
``eval_engine/docs/02-fixture-schema.md``. The fixture is sufficient to
drive every L1/L2/L3 assertion the harness needs.

High-level strategy:

1. Locate the log file for a given Copilot CLI session by ``--name`` (the
   value passed to ``copilot --name <id>``). The log's session_id is the
   UUID copilot assigns; the human-readable name is in the
   ``session-store.db`` row.

2. Stream the log line-by-line and emit two kinds of structured records:

   * **Telemetry events** — JSON objects following ``[INFO] [Telemetry]
     cli.telemetry:`` headers. These give us session id, tool-call
     outcomes, sub-agent dispatch boundaries, per-turn token usage.

   * **Request groups** — bracketed by ``--- Start of group: Sending
     request to the AI model ---`` and ``--- End of group ---``. Each
     group contains two top-level JSON objects (request + response) with
     full unredacted content: system prompts, tool_use blocks (full
     ``input``), tool_result blocks (full ``content``).

3. Classify each request group as orchestrator-level vs sub-agent-level
   by checking whether its timestamp falls inside a
   ``subagent_started`` / ``subagent_completed`` window. The orchestrator
   sees only its own ``task`` tool calls; sub-agents have their own
   request groups inside the window.

4. Build the v2 fixture sections from the classified records.
"""
from __future__ import annotations

import json
import os
import re
import sqlite3
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterator

DEFAULT_LOG_DIR = Path(os.path.expanduser("~/.copilot/logs"))
DEFAULT_DB_PATH = Path(os.path.expanduser("~/.copilot/session-store.db"))

LOG_LINE_PREFIX = re.compile(
    r"^\d{4}-\d{2}-\d{2}T[\d:.]+Z?\s+\[(?:DEBUG|INFO|WARN|ERROR)\]"
)
TELEMETRY_HDR = re.compile(
    r"^(?P<ts>\d{4}-\d{2}-\d{2}T[\d:.]+Z)\s+\[INFO\]\s+\[Telemetry\]"
)
GROUP_START = re.compile(
    r"^(?P<ts>\d{4}-\d{2}-\d{2}T[\d:.]+Z)\s+\[INFO\]\s+--- Start of group:\s+"
    r"Sending request to the AI model\s*---"
)
GROUP_END = re.compile(
    r"^(?P<ts>\d{4}-\d{2}-\d{2}T[\d:.]+Z)\s+\[INFO\]\s+--- End of group ---"
)


# ---------------------------------------------------------------------------
# Low-level log streaming
# ---------------------------------------------------------------------------


@dataclass
class _RawTelemetry:
    timestamp: str
    payload: dict[str, Any]


@dataclass
class _RawGroup:
    started_at: str
    ended_at: str
    objects: list[dict[str, Any]] = field(default_factory=list)


def _parse_balanced_json(buf: list[str]) -> tuple[dict[str, Any] | None, int]:
    """Try to parse the leading top-level JSON object from ``buf``.

    Returns (parsed, line_count_consumed) or (None, 0) if no complete
    object is yet present. Skips blank lines and lines that look like
    log-line prefixes.
    """
    text_lines: list[str] = []
    i = 0
    started = False
    depth = 0
    in_string = False
    escape = False
    consumed = 0
    for line in buf:
        consumed += 1
        if not started:
            stripped = line.lstrip()
            if not stripped:
                continue
            if LOG_LINE_PREFIX.match(line):
                # Non-JSON noise, skip.
                continue
            if stripped[0] != "{":
                continue
            started = True
        text_lines.append(line)
        # Brace count, respecting strings.
        for ch in line:
            if escape:
                escape = False
                continue
            if ch == "\\":
                escape = True
                continue
            if ch == '"':
                in_string = not in_string
                continue
            if in_string:
                continue
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    candidate = "".join(text_lines)
                    try:
                        return json.loads(candidate), consumed
                    except json.JSONDecodeError:
                        return None, consumed
        i += 1
    return None, 0


def stream_log(log_path: Path) -> Iterator[_RawTelemetry | _RawGroup]:
    """Yield telemetry events and request groups in order from a process log."""
    with log_path.open(encoding="utf-8", errors="replace") as fh:
        lines = fh.readlines()

    n = len(lines)
    i = 0
    while i < n:
        line = lines[i]

        m = TELEMETRY_HDR.match(line)
        if m:
            payload, consumed = _parse_balanced_json(lines[i + 1 : i + 4000])
            if payload is not None:
                yield _RawTelemetry(timestamp=m.group("ts"), payload=payload)
                i = i + 1 + consumed
                continue
            i += 1
            continue

        m = GROUP_START.match(line)
        if m:
            started_at = m.group("ts")
            group = _RawGroup(started_at=started_at, ended_at=started_at)
            i += 1
            # Collect objects until we see the End of group line.
            while i < n:
                inner = lines[i]
                em = GROUP_END.match(inner)
                if em:
                    group.ended_at = em.group("ts")
                    i += 1
                    break
                if TELEMETRY_HDR.match(inner) or LOG_LINE_PREFIX.match(inner):
                    i += 1
                    continue
                stripped = inner.lstrip()
                if not stripped or stripped[0] != "{":
                    i += 1
                    continue
                payload, consumed = _parse_balanced_json(lines[i : i + 4000])
                if payload is not None:
                    group.objects.append(payload)
                    i += consumed
                else:
                    i += 1
            yield group
            continue

        i += 1


# ---------------------------------------------------------------------------
# Session resolution
# ---------------------------------------------------------------------------


@dataclass
class LocalSession:
    id: str
    cwd: str | None
    summary: str | None
    created_at: str
    updated_at: str
    name: str | None = None
    log_path: Path | None = None


def find_session_by_name(
    name: str, *, db_path: Path = DEFAULT_DB_PATH
) -> LocalSession | None:
    """Look up the most recent CLI session whose stored name matches ``name``.

    Copilot CLI's ``--name`` flag does not (currently) round-trip into the
    ``sessions`` table directly; the most reliable signal is that the
    session's cwd or summary contains the run-id we used as the name. The
    caller should pass either the run-id itself or a substring known to
    appear in the cwd.
    """
    if not db_path.exists():
        return None
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    try:
        rows = list(
            con.execute(
                """
                SELECT id, cwd, summary, created_at, updated_at
                FROM sessions
                WHERE cwd LIKE ? OR summary LIKE ?
                ORDER BY created_at DESC
                LIMIT 5
                """,
                (f"%{name}%", f"%{name}%"),
            )
        )
    finally:
        con.close()
    if not rows:
        return None
    r = rows[0]
    return LocalSession(
        id=r["id"],
        cwd=r["cwd"],
        summary=r["summary"],
        created_at=r["created_at"],
        updated_at=r["updated_at"],
        name=name,
    )


def find_log_for_session(
    session: LocalSession, *, log_dir: Path = DEFAULT_LOG_DIR
) -> Path | None:
    """Find the process log file that contains a given session id.

    Process logs are named ``process-<launch>-<pid>.log`` and the session
    id is recorded inside as ``session_start.session_id``. We search the
    most recent files first.
    """
    candidates = sorted(
        log_dir.glob("process-*.log"), key=lambda p: p.stat().st_mtime, reverse=True
    )
    needle = f'"session_id": "{session.id}"'
    for path in candidates:
        try:
            with path.open(encoding="utf-8", errors="replace") as fh:
                head = fh.read(2_000_000)
        except OSError:
            continue
        if needle in head or session.id in head:
            return path
    return None


# ---------------------------------------------------------------------------
# Fixture build
# ---------------------------------------------------------------------------


def _safe_get(d: Any, *path: str, default: Any = None) -> Any:
    cur = d
    for key in path:
        if isinstance(cur, dict) and key in cur:
            cur = cur[key]
        else:
            return default
    return cur


def _classify_groups(
    groups: list[_RawGroup],
    subagent_windows: list[tuple[str, str, str]],
) -> dict[int, str | None]:
    """Tag each group as ``orchestrator`` or a sub-agent ``tool_call_id``.

    A group is sub-agent-attributable iff its [started_at, ended_at] is
    fully contained within a subagent_started/completed window keyed by
    ``tool_call_id``.
    """
    tags: dict[int, str | None] = {}
    for idx, g in enumerate(groups):
        attribution: str | None = None
        for tcid, ws, we in subagent_windows:
            if ws <= g.started_at and g.ended_at <= we:
                attribution = tcid
                break
        tags[idx] = attribution
    return tags


def _iter_choices(response: dict[str, Any]) -> Iterator[dict[str, Any]]:
    """Yield choice-shaped dicts from a model response.

    The Copilot CLI process log emits each choice as its own top-level
    JSON object (``{index, message, finish_reason, logprobs}``) rather
    than wrapping them in ``{"choices": [...]}``. Handle both.
    """
    if "choices" in response and isinstance(response["choices"], list):
        for c in response["choices"]:
            if isinstance(c, dict):
                yield c
    elif "message" in response and "finish_reason" in response:
        yield response


def _extract_tool_uses_from_response(response: dict[str, Any]) -> list[dict[str, Any]]:
    """Pull tool_use blocks out of a model response (Anthropic OR OpenAI shape)."""
    out: list[dict[str, Any]] = []
    # Anthropic-style: content is a list of blocks at the top level.
    content = response.get("content")
    if isinstance(content, list):
        for blk in content:
            if isinstance(blk, dict) and blk.get("type") == "tool_use":
                out.append(
                    {
                        "tool_call_id": blk.get("id") or "",
                        "name": blk.get("name") or "",
                        "arguments_json": blk.get("input") or {},
                    }
                )
    # OpenAI-style: message.tool_calls[]
    for choice in _iter_choices(response):
        msg = choice.get("message") or {}
        for tc in msg.get("tool_calls") or []:
            fn = (tc or {}).get("function") or {}
            args_raw = fn.get("arguments")
            try:
                args_obj = (
                    json.loads(args_raw) if isinstance(args_raw, str) else (args_raw or {})
                )
            except json.JSONDecodeError:
                args_obj = {"_raw": args_raw}
            out.append(
                {
                    "tool_call_id": tc.get("id") or "",
                    "name": fn.get("name") or "",
                    "arguments_json": args_obj,
                }
            )
    return out


def _final_assistant_text(response: dict[str, Any]) -> str:
    """Extract any plain assistant text from a model response."""
    parts: list[str] = []
    content = response.get("content")
    if isinstance(content, list):
        for blk in content:
            if isinstance(blk, dict) and blk.get("type") == "text":
                parts.append(blk.get("text") or "")
    for choice in _iter_choices(response):
        msg = choice.get("message") or {}
        c = msg.get("content")
        if isinstance(c, str) and c.strip():
            parts.append(c)
        elif isinstance(c, list):
            for blk in c:
                if isinstance(blk, dict) and blk.get("type") == "text":
                    parts.append(blk.get("text") or "")
    return "\n".join(p for p in parts if p)


def _looks_like_response(obj: dict[str, Any]) -> bool:
    """True if a JSON object looks like a model RESPONSE (vs request)."""
    if not isinstance(obj, dict):
        return False
    if "choices" in obj:
        return True
    if obj.get("type") == "message" and "content" in obj:
        return True
    if "stop_reason" in obj or "finish_reason" in obj:
        return True
    if "usage" in obj and "messages" not in obj:
        return True
    return False


def _looks_like_request(obj: dict[str, Any]) -> bool:
    return isinstance(obj, dict) and "messages" in obj


# ----- file-write tracking -----

_WRITE_TOOLS = {"create", "edit", "str_replace_editor"}


def _file_path_from_args(name: str, args: dict[str, Any]) -> str | None:
    if not isinstance(args, dict):
        return None
    if name == "create":
        return args.get("path")
    if name == "edit":
        return args.get("path")
    if name == "str_replace_editor":
        return args.get("path")
    return None


# ----- main builder -----


@dataclass
class ExtractResult:
    fixture: dict[str, Any]
    warnings: list[str] = field(default_factory=list)


def build_fixture(
    *,
    log_path: Path,
    pack: str,
    case_id: str,
    workspace_root: str,
    run_id: str = "",
) -> ExtractResult:
    warnings: list[str] = []
    telemetries: list[_RawTelemetry] = []
    groups: list[_RawGroup] = []
    for rec in stream_log(log_path):
        if isinstance(rec, _RawTelemetry):
            telemetries.append(rec)
        else:
            groups.append(rec)

    # --- Resolve session metadata.
    session_id = None
    session_summary = None
    session_created_at = None
    session_repo = None
    session_branch = None
    for t in telemetries:
        if t.payload.get("kind") == "session_start":
            session_id = t.payload.get("session_id")
            session_created_at = t.payload.get("created_at") or t.timestamp
            client = t.payload.get("client") or {}
            session_repo = client.get("repository")
            session_branch = client.get("branch")
            break
    if session_id is None:
        # Fall back: any telemetry has session_id.
        for t in telemetries:
            sid = t.payload.get("session_id")
            if sid:
                session_id = sid
                session_created_at = t.timestamp
                break
    if session_id is None:
        raise ValueError(
            "Could not locate session_id in log. The log may be from a session "
            "that did not complete startup."
        )

    last_ts = telemetries[-1].timestamp if telemetries else session_created_at

    # --- Sub-agent windows: list of (tool_call_id, started_at, completed_at).
    started_at_by_tcid: dict[str, str] = {}
    windows: list[tuple[str, str, str]] = []
    for t in telemetries:
        kind = t.payload.get("kind")
        if kind == "subagent_started":
            tcid = (t.payload.get("properties") or {}).get("tool_call_id")
            if tcid:
                started_at_by_tcid[tcid] = t.timestamp
        elif kind == "subagent_completed":
            tcid = (t.payload.get("properties") or {}).get("tool_call_id")
            ws = started_at_by_tcid.get(tcid)
            if tcid and ws:
                windows.append((tcid, ws, t.timestamp))
    group_tags = _classify_groups(groups, windows)

    # --- Tool requests at the orchestrator level.
    tool_requests: list[dict[str, Any]] = []
    seen_tcids: set[str] = set()
    # Also build a complete map (orch + sub) of tool_call_id → unredacted arg
    # for file-path resolution and for the engineer's writes.
    all_tool_uses: dict[str, dict[str, Any]] = {}
    # And a list of sub-agent inner tool_uses keyed by parent_tcid → list.
    inner_tool_uses_by_parent: dict[str, list[dict[str, Any]]] = {}

    # Pre-build: for each sub-agent window, find groups inside it.
    groups_by_parent: dict[str, list[int]] = {}
    for idx, g in enumerate(groups):
        parent = group_tags[idx]
        if parent is not None:
            groups_by_parent.setdefault(parent, []).append(idx)

    for idx, g in enumerate(groups):
        for obj in g.objects:
            if not _looks_like_response(obj):
                continue
            for tu in _extract_tool_uses_from_response(obj):
                tcid = tu["tool_call_id"]
                if tcid:
                    all_tool_uses[tcid] = tu
                if group_tags[idx] is None:  # orchestrator
                    if tcid and tcid not in seen_tcids:
                        seen_tcids.add(tcid)
                        tool_requests.append(
                            {
                                "tool_call_id": tcid,
                                "name": tu["name"],
                                "timestamp": g.started_at,
                                "arguments_json": tu["arguments_json"],
                            }
                        )
                else:
                    inner_tool_uses_by_parent.setdefault(group_tags[idx], []).append(tu)

    # --- Events from tool_call_executed telemetry.
    events: list[dict[str, Any]] = []
    file_writes: list[dict[str, Any]] = []
    for t in telemetries:
        if t.payload.get("kind") != "tool_call_executed":
            continue
        props = t.payload.get("properties") or {}
        metrics = t.payload.get("metrics") or {}
        tcid = props.get("tool_call_id")
        tool_name = props.get("tool_name")
        success = props.get("result_type") == "SUCCESS"
        usage_model = props.get("model")
        # Decide if this execution was inside a sub-agent window.
        is_inner = False
        for parent_tcid, ws, we in windows:
            if ws <= t.timestamp <= we and parent_tcid != tcid:
                is_inner = True
                break
        ev: dict[str, Any] = {
            "timestamp": t.timestamp,
            "type": "tool.execution_complete",
            "tool_start_name": tool_name,
            "tool_complete_call_id": tcid,
            "tool_complete_success": success,
            "tool_complete_result_content": "",
            "usage_model": usage_model,
            "usage_input_tokens": 0,
            "usage_output_tokens": 0,
            "is_inner_to_subagent": is_inner,
        }
        events.append(ev)

        # File writes: pull unredacted path from the matching tool_use.
        if tool_name in _WRITE_TOOLS and tcid in all_tool_uses:
            args = all_tool_uses[tcid]["arguments_json"]
            path = _file_path_from_args(tool_name, args)
            if path:
                file_writes.append(
                    {
                        "file_path": path,
                        "tool_name": tool_name,
                        "turn_index": 0,
                        "first_seen_at": t.timestamp,
                    }
                )

    # Dedupe session_files by (file_path, tool_name) keeping earliest.
    _seen_paths: dict[tuple[str, str], dict[str, Any]] = {}
    for f in file_writes:
        key = (f["file_path"], f["tool_name"])
        prev = _seen_paths.get(key)
        if prev is None or f["first_seen_at"] < prev["first_seen_at"]:
            _seen_paths[key] = f
    file_writes = sorted(_seen_paths.values(), key=lambda x: x["first_seen_at"])

    # Supplement: walk the workspace filesystem to discover files created
    # by paths NOT explicitly captured as ``create``/``edit`` tool calls
    # (e.g., when an agent uses ``powershell`` to write files via
    # ``Out-File``, ``Set-Content``, ``New-Item``, etc.). Without this,
    # any file an agent writes through the shell is invisible to L3-files.
    # Only include files modified AFTER the session started -- otherwise
    # we'd sweep up every staged input fixture, drowning the real signal.
    explicit_paths = {
        os.path.normcase(os.path.abspath(f["file_path"]))
        for f in file_writes
    }
    # --- workspace-walk: capture all writable artifacts left in the workspace.
    # Some files are harness scaffolding (the operator's stdout capture, the
    # case staging files) and must NOT be attributed to the SUT. Skip them
    # by basename pattern; everything else goes to the orchestrator's bucket
    # via the workspace-walk path below.
    _HARNESS_INTERNAL_PREFIXES = ("_sut", "_runstate", "_eval")
    _HARNESS_INTERNAL_BASENAMES = {"plan.log", "judge-plan.log"}

    def _is_harness_internal(p: Path, ws: Path) -> bool:
        try:
            rel = p.resolve().relative_to(ws.resolve())
        except (ValueError, OSError):
            return False
        parts = rel.parts
        if not parts:
            return False
        if parts[0].startswith(_HARNESS_INTERNAL_PREFIXES):
            return True
        if rel.name in _HARNESS_INTERNAL_BASENAMES:
            return True
        return False

    ws_path = Path(workspace_root)
    session_start_epoch: float | None = None
    if session_created_at:
        try:
            from datetime import datetime
            ts = session_created_at.replace("Z", "+00:00")
            session_start_epoch = datetime.fromisoformat(ts).timestamp()
        except (ValueError, TypeError):
            session_start_epoch = None
    if ws_path.exists() and ws_path.is_dir():
        for p in ws_path.rglob("*"):
            if not p.is_file():
                continue
            try:
                rel_norm = os.path.normcase(str(p.resolve()))
                stat = p.stat()
            except OSError:
                continue
            if rel_norm in explicit_paths:
                continue
            if _is_harness_internal(p, ws_path):
                continue
            if session_start_epoch is not None and stat.st_mtime < session_start_epoch:
                continue
            file_writes.append(
                {
                    "file_path": str(p),
                    "tool_name": "workspace-walk",
                    "turn_index": 0,
                    "first_seen_at": last_ts,
                }
            )

    # --- agent_windows[].
    # The platform's `task` tool accepts:
    #   - agent_type: the registered agent identity (e.g. "Factory Architect"
    #     or a filename slug like "factory-architect"). This is the canonical
    #     name and matches the spec's `agents[].name` after normalization.
    #   - name:        a short invocation alias the caller chooses
    #                  (e.g. "design-architecture") — orchestrator-local only.
    #   - description: a 3-5 word UI label.
    # We must prefer ``agent_type`` for spec matching; ``name`` is the alias.
    def _normalize_agent_slug(value: str) -> str:
        # Canonicalize display names ("Factory Architect") to filename slugs
        # ("factory-architect") so they line up with how packs key their
        # agents in spec.yaml. Idempotent for already-slug values.
        if not value:
            return value
        s = value.strip()
        if not s:
            return s
        # If any whitespace is present, treat as a display name.
        if any(c.isspace() for c in s):
            s = "-".join(s.lower().split())
        # Lowercase trailing pass; keep hyphens/underscores/dots as-is.
        return s.lower()

    # Built-in Copilot CLI agent_types that are not pack sub-agents:
    # the orchestrator can dispatch generic shell/research subtasks via these.
    # They must NOT be reported as pack sub-agent invocations.
    _BUILTIN_AGENT_TYPES = {
        "task", "explore", "general-purpose", "rubber-duck",
        "code-review", "configure-copilot",
    }

    agent_windows: list[dict[str, Any]] = []
    for tcid, ws, we in windows:
        tu = all_tool_uses.get(tcid)
        args = (tu or {}).get("arguments_json") or {}
        raw_agent_type = args.get("agent_type") or args.get("name") or "unknown"
        agent_type = _normalize_agent_slug(raw_agent_type)
        if agent_type in _BUILTIN_AGENT_TYPES:
            continue
        agent_name = args.get("name") or args.get("description") or ""
        prompt = args.get("prompt") or ""
        # Pull the sub-agent's final assistant message as final_response:
        # it's the last response (no tool_uses, just text) inside the
        # window's groups, OR the last response with content.
        final_response = ""
        model_used: str | None = None
        for gi in groups_by_parent.get(tcid, []):
            for obj in groups[gi].objects:
                if not _looks_like_response(obj):
                    continue
                txt = _final_assistant_text(obj)
                if txt:
                    final_response = txt
                model_used = obj.get("model") or model_used
        agent_windows.append(
            {
                "tool_call_id": tcid,
                "agent_type": agent_type,
                "agent_name": agent_name,
                "started_at": ws,
                "completed_at": we,
                "success": True,
                "input_prompt": prompt,
                "final_response": final_response,
                "input_tokens": 0,
                "output_tokens": 0,
                "model_used": model_used or "",
            }
        )

    # --- Final assistant message: last response in an orchestrator group.
    final_msg = ""
    for idx in range(len(groups) - 1, -1, -1):
        if group_tags[idx] is not None:
            continue
        for obj in groups[idx].objects:
            if not _looks_like_response(obj):
                continue
            txt = _final_assistant_text(obj)
            if txt:
                final_msg = txt
                break
        if final_msg:
            break

    # --- Usage aggregate (best-effort).
    # assistant_usage records are emitted INSIDE request groups (not as
    # separate ``[INFO] [Telemetry]`` lines), so collect them by walking
    # the group object stream as well as standalone telemetry.
    by_model: dict[str, dict[str, int]] = {}
    by_agent: dict[str, dict[str, int]] = {}
    total_in = total_out = 0

    def _record_usage(payload: dict[str, Any]) -> None:
        nonlocal total_in, total_out
        props = payload.get("properties") or {}
        metrics = payload.get("metrics") or {}
        model = props.get("model") or "unknown"
        ti = int(metrics.get("input_tokens") or 0)
        to = int(metrics.get("output_tokens") or 0)
        bucket = by_model.setdefault(model, {"input_tokens": 0, "output_tokens": 0})
        bucket["input_tokens"] += ti
        bucket["output_tokens"] += to
        total_in += ti
        total_out += to

    for t in telemetries:
        if t.payload.get("kind") == "assistant_usage":
            _record_usage(t.payload)
    for g in groups:
        for obj in g.objects:
            if isinstance(obj, dict) and obj.get("kind") == "assistant_usage":
                _record_usage(obj)
    for win in agent_windows:
        bucket = by_agent.setdefault(
            win["agent_type"],
            {"input_tokens": 0, "output_tokens": 0, "invocations": 0},
        )
        bucket["invocations"] += 1
        bucket["input_tokens"] += win["input_tokens"]
        bucket["output_tokens"] += win["output_tokens"]

    if not tool_requests:
        warnings.append(
            "No orchestrator-level tool calls extracted from log. The log may "
            "be malformed, truncated, or its 'Sending request' groups may use "
            "an unrecognized format."
        )

    # ------------------------------------------------------------------
    # Assemble v1 fixture (matches eval_engine.harness.models.Fixture).
    # ------------------------------------------------------------------

    # Build invocations.
    orch_iid = "orchestrator"
    # The orchestrator's "prompt" is its own system prompt — i.e. the
    # `.github/agents/{pack}.agent.md` file content visible to the model.
    # L2-prompt-sections asserts required sections appear there; without
    # this the orchestrator always trivially fails.
    orch_prompt = ""
    try:
        orch_md = Path(workspace_root) / ".github" / "agents" / f"{pack}.agent.md"
        if orch_md.is_file():
            orch_prompt = orch_md.read_text(encoding="utf-8")
    except OSError:
        orch_prompt = ""
    invocations: list[dict[str, Any]] = [
        {
            "invocation_id": orch_iid,
            "name": pack,
            "mode": "sync",
            "started_at": session_created_at,
            "ended_at": last_ts,
            "completed": True,
            "prompt": orch_prompt,
            "response": final_msg,
            "parent_invocation_id": None,
        }
    ]
    for win in agent_windows:
        invocations.append(
            {
                "invocation_id": win["tool_call_id"],
                "name": win["agent_type"],
                "mode": "sync",
                "started_at": win["started_at"],
                "ended_at": win["completed_at"],
                "completed": True,
                "prompt": win["input_prompt"],
                "response": win["final_response"],
                "parent_invocation_id": orch_iid,
                "tokens": (win["input_tokens"] or 0) + (win["output_tokens"] or 0),
            }
        )

    # Build tool_calls (one per tool_use) -- both orchestrator and sub-agent.
    # We iterate through groups in order to preserve sequence and assign
    # actors based on the group's classification.
    tool_calls: list[dict[str, Any]] = []
    seen_call_ids: set[str] = set()
    # Build a quick map: tcid -> result content from a later tool_result.
    tool_results_by_id: dict[str, str] = {}
    for g in groups:
        for obj in g.objects:
            if isinstance(obj, dict) and obj.get("type") == "tool_result":
                tcid = obj.get("tool_use_id") or ""
                content = obj.get("content")
                if isinstance(content, list):
                    text_parts = []
                    for c in content:
                        if isinstance(c, dict) and c.get("type") == "text":
                            text_parts.append(c.get("text") or "")
                        elif isinstance(c, str):
                            text_parts.append(c)
                    content_str = "\n".join(text_parts)
                else:
                    content_str = str(content) if content is not None else ""
                if tcid and tcid not in tool_results_by_id:
                    tool_results_by_id[tcid] = content_str[:2000]
            elif isinstance(obj, dict) and "role" in obj and isinstance(obj.get("content"), list):
                # Sometimes tool_results are nested inside a user-message object.
                for c in obj["content"]:
                    if isinstance(c, dict) and c.get("type") == "tool_result":
                        tcid = c.get("tool_use_id") or ""
                        content = c.get("content")
                        if isinstance(content, list):
                            content_str = "\n".join(
                                (b.get("text") or "") if isinstance(b, dict) else str(b)
                                for b in content
                            )
                        else:
                            content_str = str(content) if content is not None else ""
                        if tcid and tcid not in tool_results_by_id:
                            tool_results_by_id[tcid] = content_str[:2000]

    # tool_call_executed lookup by id -> outcome / timing.
    exec_by_id: dict[str, _RawTelemetry] = {}
    for t in telemetries:
        if t.payload.get("kind") == "tool_call_executed":
            tcid = (t.payload.get("properties") or {}).get("tool_call_id")
            if tcid and tcid not in exec_by_id:
                exec_by_id[tcid] = t

    for idx, g in enumerate(groups):
        parent = group_tags[idx]  # None=orch, else parent task tcid
        for obj in g.objects:
            if not _looks_like_response(obj):
                continue
            for tu in _extract_tool_uses_from_response(obj):
                tcid = tu["tool_call_id"]
                if not tcid or tcid in seen_call_ids:
                    continue
                seen_call_ids.add(tcid)
                if parent is None:
                    actor = {"kind": "orchestrator", "name": pack, "invocation_id": orch_iid}
                else:
                    parent_win = next(
                        (w for w in agent_windows if w["tool_call_id"] == parent),
                        None,
                    )
                    actor = {
                        "kind": "subagent",
                        "name": (parent_win or {}).get("agent_type", "unknown"),
                        "invocation_id": parent,
                    }
                exec_t = exec_by_id.get(tcid)
                started_at = g.started_at
                ended_at = exec_t.timestamp if exec_t else g.ended_at
                success = None
                if exec_t:
                    success = (
                        (exec_t.payload.get("properties") or {}).get("result_type")
                        == "SUCCESS"
                    )
                tool_calls.append(
                    {
                        "call_id": tcid,
                        "name": tu["name"],
                        "actor": actor,
                        "arguments": tu["arguments_json"]
                        if isinstance(tu["arguments_json"], dict)
                        else {"_raw": tu["arguments_json"]},
                        "success": success,
                        "started_at": started_at,
                        "ended_at": ended_at,
                        "result_summary": tool_results_by_id.get(tcid, "")[:500] or None,
                    }
                )

    # Build file_accesses from session_files (writes). Match each to its
    # tool_call (when explicit) so the actor can be propagated.
    tool_call_index = {tc["call_id"]: tc for tc in tool_calls}
    file_accesses: list[dict[str, Any]] = []
    # Try to also link each explicit file write back to its tool_call id
    # by re-walking tool_uses.
    paths_to_call: dict[str, str] = {}
    for tc in tool_calls:
        if tc["name"] in _WRITE_TOOLS:
            args = tc.get("arguments") or {}
            p = args.get("path") if isinstance(args, dict) else None
            if p and p not in paths_to_call:
                paths_to_call[p] = tc["call_id"]

    seen_file_paths: set[str] = set()
    for f in file_writes:
        path = f["file_path"]
        if path in seen_file_paths:
            continue
        seen_file_paths.add(path)
        call_id = paths_to_call.get(path)
        if call_id and call_id in tool_call_index:
            actor = tool_call_index[call_id]["actor"]
            confidence = "high"
        else:
            actor = {"kind": "orchestrator", "name": pack, "invocation_id": orch_iid}
            confidence = "medium" if f["tool_name"] == "workspace-walk" else "high"
        # Make path workspace-relative if possible (POSIX-style).
        try:
            rel = Path(path).resolve().relative_to(Path(workspace_root).resolve())
            posix = rel.as_posix()
        except (ValueError, OSError):
            posix = Path(path).as_posix()
        file_accesses.append(
            {
                "path": posix,
                "op": "write",
                "actor": actor,
                "confidence": confidence,
                "call_id": call_id,
            }
        )

    # models dict: surface what we know.
    models_dict: dict[str, str] = {}
    if by_model:
        # Pick the heaviest-used model as orchestrator default.
        primary = max(
            by_model.items(),
            key=lambda kv: kv[1]["input_tokens"] + kv[1]["output_tokens"],
        )[0]
        models_dict["orchestrator"] = primary
    for win in agent_windows:
        if win["model_used"]:
            models_dict[win["agent_type"]] = win["model_used"]

    fixture: dict[str, Any] = {
        "schema_version": "1.0.0",
        "pack": pack,
        "case_id": case_id,
        "session_id": session_id,
        "run_id": run_id,
        "workspace_root": str(Path(workspace_root).resolve()),
        "captured_at": last_ts,
        "cli_version": None,
        "os": None,
        "models": models_dict,
        "invocations": invocations,
        "tool_calls": tool_calls,
        "file_accesses": file_accesses,
        "background_reads": [],
        "session_store": {
            "captured_by": "local_extractor@v0",
            "log_path": None,
            "telemetry_kinds": _kind_counts(telemetries),
            "usage_aggregate": {
                "by_model": by_model,
                "by_agent": by_agent,
                "total_input_tokens": total_in,
                "total_output_tokens": total_out,
            },
            "agent_windows": agent_windows,
        },
    }
    return ExtractResult(fixture=fixture, warnings=warnings)


def _kind_counts(telemetries: list[_RawTelemetry]) -> dict[str, int]:
    out: dict[str, int] = {}
    for t in telemetries:
        k = t.payload.get("kind") or "_unknown"
        out[k] = out.get(k, 0) + 1
    return out


def write_fixture(
    fixture: dict[str, Any], dest: Path, *, indent: int = 2
) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(
        json.dumps(fixture, indent=indent, ensure_ascii=False), encoding="utf-8"
    )

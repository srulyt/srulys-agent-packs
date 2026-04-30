"""Canonical tool taxonomy + runtime-name resolver.

See ``eval_engine/docs/00-tool-taxonomy.md`` for the authoritative vocabulary.

Specs declare ``allowed_tools`` using canonical category names
(``read``, ``search``, ``write``, ``execute``, ``agent``, ``data``, ``web``,
``mcp:<server>``, ``unknown``). Fixtures record the raw runtime tool name
the CLI surfaced (e.g., ``view``, ``grep``, ``task``,
``github-mcp-server-search_code``). The L3-tools assertion calls
:func:`resolve` to translate runtime names to categories before checking
membership of the spec's allow-list.

If a runtime name is not in the table, :func:`resolve` returns
``"unknown"``. Specs may explicitly list ``"unknown"`` to permit calls the
taxonomy does not yet know about; otherwise unknown calls fail L3-tools.
"""

from __future__ import annotations

from typing import Iterable

# Runtime tool name -> canonical category.
# Add new mappings here as new tools appear. Keep this table small,
# explicit, and lower-cased.
_RUNTIME_TO_CATEGORY: dict[str, str] = {
    # read
    "view": "read",
    "show_file": "read",
    "ide-get_diagnostics": "read",
    "ide-get_selection": "read",
    # search
    "grep": "search",
    "glob": "search",
    "github-mcp-server-search_code": "search",
    "github-mcp-server-search_users": "search",
    "web_search": "search",
    "web_fetch": "search",
    # write
    "create": "write",
    "edit": "write",
    # execute
    "powershell": "execute",
    "bash": "execute",
    "shell": "execute",
    "read_powershell": "execute",
    "write_powershell": "execute",
    "stop_powershell": "execute",
    "list_powershell": "execute",
    # agent
    "task": "agent",
    "read_agent": "agent",
    "write_agent": "agent",
    "list_agents": "agent",
    "skill": "agent",
    "ask_user": "agent",
    "report_intent": "agent",
    "task_complete": "agent",
    # data
    "sql": "data",
    "session_store_sql": "data",
    "store_memory": "data",
    "vote_memory": "data",
    # mcp aliases handled below by prefix
}

# Tools whose names are namespaced ``<server>-<verb>`` map to ``mcp:<server>``.
_MCP_PREFIXES: tuple[str, ...] = (
    "github-mcp-server-",
    "playwright-browser_",
    "workiq-",
    "extensions_",
)

_MCP_SERVER_FOR_PREFIX = {
    "github-mcp-server-": "mcp:github",
    "playwright-browser_": "mcp:playwright",
    "workiq-": "mcp:workiq",
    "extensions_": "mcp:extensions",
}

UNKNOWN = "unknown"

CANONICAL_CATEGORIES = frozenset(
    {"read", "search", "write", "execute", "agent", "data", "web", UNKNOWN}
)


def resolve(runtime_name: str) -> str:
    """Map a runtime tool name to its canonical category."""
    if not runtime_name:
        return UNKNOWN
    name = str(runtime_name).strip()
    if not name:
        return UNKNOWN
    # Direct hit in the table.
    if name in _RUNTIME_TO_CATEGORY:
        return _RUNTIME_TO_CATEGORY[name]
    # MCP-style namespaced tools collapse to ``mcp:<server>``.
    for prefix, server_cat in _MCP_SERVER_FOR_PREFIX.items():
        if name.startswith(prefix):
            return server_cat
    return UNKNOWN


def resolve_all(runtime_names: Iterable[str]) -> list[str]:
    return [resolve(n) for n in runtime_names]


def is_allowed(runtime_name: str, allowed: Iterable[str]) -> bool:
    """True iff ``runtime_name`` resolves to a category in ``allowed``."""
    cat = resolve(runtime_name)
    allowed_set = set(allowed)
    if cat in allowed_set:
        return True
    # An entry like ``mcp:github`` only allows that specific MCP server.
    # An entry of just ``mcp`` (without ``:``) is shorthand for any MCP server.
    if cat.startswith("mcp:") and "mcp" in allowed_set:
        return True
    return False

"""Runner subpackage: pluggable SUT backends."""

from .base import RunResult, SUTRunner, SUTUnavailable, get_runner, register_runner

__all__ = [
    "RunResult",
    "SUTRunner",
    "SUTUnavailable",
    "get_runner",
    "register_runner",
]

"""
Run Mode
========

Controls whether DeepTutor is running as a CLI application or an API server.
Modules can check the mode to conditionally import server-only dependencies.
"""

from enum import Enum
import os

from deeptutor.runtime.env import get_prefixed_env, set_prefixed_env


class RunMode(str, Enum):
    CLI = "cli"
    SERVER = "server"


_current_mode: RunMode | None = None


def _resolve_mode() -> RunMode:
    raw = get_prefixed_env("MODE").strip().lower()
    if raw == RunMode.SERVER.value:
        return RunMode.SERVER
    return RunMode.CLI


def get_mode() -> RunMode:
    global _current_mode
    if _current_mode is None:
        _current_mode = _resolve_mode()
    return _current_mode


def set_mode(mode: RunMode) -> None:
    """Explicitly set the run mode (call early in entry points)."""
    global _current_mode
    _current_mode = mode
    set_prefixed_env("MODE", mode.value)


def is_cli() -> bool:
    return get_mode() == RunMode.CLI


def is_server() -> bool:
    return get_mode() == RunMode.SERVER

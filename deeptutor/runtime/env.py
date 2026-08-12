"""NexaTutor environment names with one-way DeepTutor compatibility."""

from __future__ import annotations

import os


def get_prefixed_env(name: str, default: str = "") -> str:
    """Read NEXATUTOR_<name> first, then the legacy DEEPTUTOR_<name>."""
    return os.environ.get(f"NEXATUTOR_{name}", os.environ.get(f"DEEPTUTOR_{name}", default))


def set_prefixed_env(name: str, value: str) -> None:
    """Export only the NexaTutor spelling."""
    os.environ[f"NEXATUTOR_{name}"] = value

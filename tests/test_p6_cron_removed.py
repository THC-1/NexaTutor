from __future__ import annotations

import importlib.util
from pathlib import Path

from deeptutor.agents._shared.tool_composition import ToolMountFlags, compose_enabled_tools
from deeptutor.tools.builtin import BUILTIN_TOOL_NAMES, CONFIGURABLE_BUILTIN_TOOL_NAMES


ROOT = Path(__file__).resolve().parents[1]


class _Registry:
    def get_enabled(self, names: list[str]):
        return [type("Tool", (), {"name": name})() for name in names if name in BUILTIN_TOOL_NAMES]


def test_cron_cannot_be_registered_or_mounted_from_legacy_requests() -> None:
    assert "cron" not in BUILTIN_TOOL_NAMES
    assert "cron" not in CONFIGURABLE_BUILTIN_TOOL_NAMES
    composed = compose_enabled_tools(
        registry=_Registry(),
        requested_tools=["cron"],
        optional_whitelist=["cron"],
        mount_flags=ToolMountFlags(),
    )
    assert "cron" not in composed


def test_cron_lifecycle_implementation_and_dependencies_are_removed() -> None:
    sources = [
        ROOT / "deeptutor" / "api" / "main.py",
        ROOT / "deeptutor_cli" / "chat.py",
        ROOT / "deeptutor" / "agents" / "chat" / "agentic_pipeline.py",
    ]
    assert all("get_cron_service" not in path.read_text(encoding="utf-8") for path in sources)
    assert importlib.util.find_spec("deeptutor.services.cron.service") is None
    assert importlib.util.find_spec("deeptutor.tools.cron_tool") is None

    dependency_files = [
        ROOT / "pyproject.toml",
        ROOT / "requirements" / "server.txt",
        ROOT / ".pre-commit-config.yaml",
    ]
    dependency_text = "\n".join(path.read_text(encoding="utf-8") for path in dependency_files)
    assert "croniter" not in dependency_text.lower()

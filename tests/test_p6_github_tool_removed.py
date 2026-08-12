from __future__ import annotations

import importlib.util
from pathlib import Path

from deeptutor.agents._shared.tool_composition import ToolMountFlags, compose_enabled_tools
from deeptutor.tools.builtin import BUILTIN_TOOL_NAMES, CONFIGURABLE_BUILTIN_TOOL_NAMES


ROOT = Path(__file__).resolve().parents[1]


class _Registry:
    def get_enabled(self, names: list[str]):
        return [type("Tool", (), {"name": name})() for name in names if name in BUILTIN_TOOL_NAMES]


def test_github_tool_cannot_be_registered_or_mounted_from_legacy_requests() -> None:
    assert "github" not in BUILTIN_TOOL_NAMES
    assert "github" not in CONFIGURABLE_BUILTIN_TOOL_NAMES
    composed = compose_enabled_tools(
        registry=_Registry(),
        requested_tools=["github"],
        optional_whitelist=["github"],
        mount_flags=ToolMountFlags(),
    )
    assert "github" not in composed


def test_github_tool_implementation_and_ui_are_removed() -> None:
    assert importlib.util.find_spec("deeptutor.tools.github_query") is None
    trace = (ROOT / "web" / "components" / "chat" / "home" / "TracePanels.tsx").read_text(
        encoding="utf-8"
    )
    assert 'case "github"' not in trace
    for locale in ("en", "zh"):
        text = (ROOT / "web" / "locales" / locale / "app.json").read_text(encoding="utf-8")
        assert "Querying GitHub" not in text


def test_github_tool_and_copilot_removal_preserves_codex_oauth() -> None:
    assert not (
        ROOT / "deeptutor" / "services" / "llm" / "provider_core" / "github_copilot_provider.py"
    ).exists()
    assert (ROOT / "deeptutor" / "services" / "codex_auth" / "service.py").is_file()
    assert (ROOT / "deeptutor" / "api" / "routers" / "codex_callback.py").is_file()

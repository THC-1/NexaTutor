"""Registration contracts for the removed extension ecosystem."""

from __future__ import annotations

from deeptutor.api.main import app
from deeptutor.runtime.registry.tool_registry import get_tool_registry


def test_extension_management_routes_are_not_registered() -> None:
    paths = {route.path for route in app.routes}

    assert not any(path.startswith("/api/v1/settings/mcp") for path in paths)
    assert not any(path.startswith("/api/v1/space/mcp") for path in paths)
    assert not any(path.startswith("/api/v1/space/cli-apps") for path in paths)
    assert not any(path.startswith("/api/v1/plugins") for path in paths)
    assert not any(path.startswith("/api/v1/skills/hub") for path in paths)
    assert "/api/v1/skills/install" not in paths


def test_load_tools_is_not_registered_but_core_tools_remain() -> None:
    names = set(get_tool_registry().list_tools())

    assert "load_tools" not in names
    assert {"rag", "read_source", "read_memory", "consult_subagent"} <= names

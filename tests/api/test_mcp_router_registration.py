"""Route contracts for staged removal of MCP management APIs."""

from __future__ import annotations

from deeptutor.api.main import app


def test_main_app_does_not_register_mcp_management_routers() -> None:
    paths = {route.path for route in app.routes}

    assert not any(path.startswith("/api/v1/settings/mcp") for path in paths)
    assert not any(path.startswith("/api/v1/space/mcp") for path in paths)


def test_mcp_router_removal_preserves_core_learning_routes() -> None:
    paths = {route.path for route in app.routes}

    assert "/api/v1/chat" in paths
    assert "/api/v1/ws" in paths
    assert "/api/v1/knowledge/health" in paths
    assert "/api/v1/subagents/connections" in paths

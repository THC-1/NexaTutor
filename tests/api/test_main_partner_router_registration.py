"""Route contracts for staged removal of the Partner API surface."""

from __future__ import annotations

from deeptutor.api.main import app


def test_main_app_does_not_register_partner_api_router() -> None:
    paths = [route.path for route in app.routes]

    assert not any(path.startswith("/api/v1/partners") for path in paths)


def test_partner_router_removal_preserves_core_routes() -> None:
    paths = {route.path for route in app.routes}

    assert "/api/v1/subagents/partners" not in paths
    assert "/" in paths
    assert "/api/v1/chat" in paths
    assert "/api/v1/ws" in paths
    assert "/api/v1/knowledge/health" in paths

from __future__ import annotations

from deeptutor.api.main import app


def test_account_and_multi_user_routes_are_not_registered() -> None:
    paths = {route.path for route in app.routes}
    assert {path for path in paths if path.startswith("/api/v1/auth/")} == {
        "/api/v1/auth/openai-codex/callback"
    }
    assert not any(path.startswith("/api/v1/multi-user/") for path in paths)


def test_codex_oauth_callback_and_core_routes_remain_registered() -> None:
    paths = {route.path for route in app.routes}
    assert "/api/v1/auth/openai-codex/callback" in paths
    assert "/api/v1/ws" in paths
    assert "/api/v1/subagents/connections" in paths
    assert "/api/v1/skills/list" in paths

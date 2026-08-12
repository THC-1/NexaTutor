"""The local workspace may drive the retained Codex OAuth lifecycle."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from deeptutor.api.routers import settings as settings_router

CODEX_ROUTES = [
    ("post", "/api/v1/settings/providers/openai-codex/oauth/start"),
    ("get", "/api/v1/settings/providers/openai-codex/oauth/status"),
    ("post", "/api/v1/settings/providers/openai-codex/oauth/cancel"),
    ("post", "/api/v1/settings/providers/openai-codex/oauth/logout"),
    ("post", "/api/v1/settings/providers/openai-codex/models/refresh"),
]


class _Service:
    """Stand-in for the single local ``CodexOAuthService``."""

    def __init__(self) -> None:
        self.calls: list[str] = []

    async def start_login(self) -> dict[str, Any]:
        self.calls.append("start")
        return {"operation_id": "op-1"}

    def public_status(self) -> dict[str, Any]:
        self.calls.append("status")
        return {"connection": "disconnected"}

    async def cancel_login(self) -> dict[str, Any]:
        self.calls.append("cancel")
        return {"connection": "disconnected"}

    async def logout(self) -> dict[str, Any]:
        self.calls.append("logout")
        return {"connection": "disconnected"}

    async def refresh_models(self) -> dict[str, Any]:
        self.calls.append("refresh")
        return {"connection": "connected"}


@pytest.fixture
def client(monkeypatch) -> tuple[TestClient, _Service]:
    service = _Service()
    monkeypatch.setattr(settings_router, "get_codex_oauth_service", lambda: service)

    app = FastAPI()
    app.include_router(settings_router.router, prefix="/api/v1/settings")
    return TestClient(app), service


@pytest.mark.parametrize(("method", "path"), CODEX_ROUTES)
def test_local_workspace_drives_codex_lifecycle(client, method, path) -> None:
    test_client, service = client

    response = getattr(test_client, method)(path)

    assert response.status_code == 200
    assert service.calls, "the request must reach the local Codex service"

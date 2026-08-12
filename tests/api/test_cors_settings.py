"""Tests for FastAPI CORS settings."""

from __future__ import annotations

from fastapi.testclient import TestClient

from deeptutor.api import main as api_main


def test_cors_rejects_unconfigured_remote_origins(
    monkeypatch,
) -> None:
    monkeypatch.delenv("AUTH_ENABLED", raising=False)
    monkeypatch.delenv("CORS_ORIGIN", raising=False)
    monkeypatch.delenv("CORS_ORIGINS", raising=False)
    monkeypatch.setenv("FRONTEND_PORT", "3782")

    settings = api_main._build_cors_settings()

    assert settings["allow_origin_regex"] is None
    assert settings["mode"] == "explicit"
    assert "http://localhost:3782" in settings["allow_origins"]
    assert "http://127.0.0.1:3782" in settings["allow_origins"]
    assert "https://unconfigured.example.com" not in settings["allow_origins"]


def test_legacy_remote_origins_are_ignored(monkeypatch) -> None:
    monkeypatch.setenv("AUTH_ENABLED", "true")
    monkeypatch.setenv("CORS_ORIGIN", "https://app.example.com/")
    monkeypatch.setenv(
        "CORS_ORIGINS",
        "https://foo.example.com, https://bar.example.com\nhttps://foo.example.com",
    )

    settings = api_main._build_cors_settings()

    assert settings["allow_origin_regex"] is None
    assert "https://app.example.com" not in settings["allow_origins"]
    assert "https://foo.example.com" not in settings["allow_origins"]
    assert "https://bar.example.com" not in settings["allow_origins"]


def test_cors_does_not_accept_lan_or_public_origins(monkeypatch) -> None:
    monkeypatch.setenv("AUTH_ENABLED", "true")
    monkeypatch.setenv(
        "CORS_ORIGIN",
        "172.26.0.10:3782; https://learn.example.com/app/",
    )
    monkeypatch.setenv("CORS_ORIGINS", "http://localhost:3000;api.example.com")

    settings = api_main._build_cors_settings()

    assert settings["allow_origin_regex"] is None
    assert "http://172.26.0.10:3782" not in settings["allow_origins"]
    assert "https://learn.example.com" not in settings["allow_origins"]
    assert "http://api.example.com" not in settings["allow_origins"]


def test_cors_preflight_allows_configured_local_patch() -> None:
    client = TestClient(api_main.app)

    response = client.options(
        "/api/v1/settings",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "PATCH",
            "Access-Control-Request-Headers": "content-type",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"
    allowed_methods = {
        method.strip() for method in response.headers["access-control-allow-methods"].split(",")
    }
    assert "PATCH" in allowed_methods

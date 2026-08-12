"""P5 guardrails for removed public-deployment runtime settings."""

from __future__ import annotations

import json
from pathlib import Path

from deeptutor.services.config.runtime_settings import RuntimeSettingsService


REMOVED_KEYS = {
    "next_public_api_base_external",
    "public_api_base",
    "cors_origin",
    "cors_origins",
}


def test_legacy_public_settings_and_env_are_ignored(tmp_path: Path) -> None:
    settings_dir = tmp_path / "settings"
    settings_dir.mkdir()
    (settings_dir / "system.json").write_text(
        json.dumps(
            {
                "backend_port": 8123,
                "next_public_api_base_external": "https://remote.invalid",
                "cors_origins": ["https://remote.invalid"],
            }
        ),
        encoding="utf-8",
    )
    service = RuntimeSettingsService(
        settings_dir=settings_dir,
        process_env={
            "NEXT_PUBLIC_API_BASE_EXTERNAL": "https://env.invalid",
            "PUBLIC_API_BASE": "https://alias.invalid",
            "CORS_ORIGIN": "https://cors.invalid",
            "CORS_ORIGINS": "https://cors-list.invalid",
        },
    )

    system = service.load_system()
    rendered = service.render_environment()

    assert REMOVED_KEYS.isdisjoint(system)
    assert "NEXT_PUBLIC_API_BASE_EXTERNAL" not in rendered
    assert "CORS_ORIGIN" not in rendered
    assert "CORS_ORIGINS" not in rendered
    assert rendered["DEEPTUTOR_API_BASE_URL"] == "http://127.0.0.1:8123"

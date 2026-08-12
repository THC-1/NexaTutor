"""P5 guardrails for retired PocketBase runtime settings."""

from __future__ import annotations

from pathlib import Path

from deeptutor.services.config.runtime_settings import RuntimeSettingsService


def test_runtime_defaults_do_not_create_or_rewrite_integrations_file(tmp_path: Path) -> None:
    settings_dir = tmp_path / "settings"
    settings_dir.mkdir()
    integrations = settings_dir / "integrations.json"
    legacy = '{"pocketbase_url":"http://legacy.invalid","custom":"keep"}\n'
    integrations.write_text(legacy, encoding="utf-8")
    service = RuntimeSettingsService(settings_dir=settings_dir)

    service.ensure_defaults()

    assert integrations.read_text(encoding="utf-8") == legacy


def test_runtime_environment_ignores_legacy_pocketbase_values(tmp_path: Path) -> None:
    settings_dir = tmp_path / "settings"
    service = RuntimeSettingsService(
        settings_dir=settings_dir,
        process_env={
            "POCKETBASE_URL": "http://legacy.invalid",
            "POCKETBASE_PORT": "8090",
            "POCKETBASE_ADMIN_PASSWORD": "legacy-secret",
        },
    )

    rendered = service.render_environment()

    assert not any("POCKETBASE" in key for key in rendered)
    assert not (settings_dir / "integrations.json").exists()

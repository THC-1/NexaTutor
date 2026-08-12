from __future__ import annotations

import json

from deeptutor.services.settings import interface_settings
from deeptutor.services.path_service import PathService


def test_interface_settings_read_only_the_local_user_file(tmp_path, monkeypatch) -> None:
    service = PathService(workspace_root=tmp_path / "data")
    monkeypatch.setattr(interface_settings, "get_path_service", lambda: service)
    settings_file = service.get_settings_file("interface")
    settings_file.parent.mkdir(parents=True)
    settings_file.write_text(
        json.dumps({"theme": "dark", "language": "zh", "response_language": "en"})
    )

    assert interface_settings.get_ui_language() == "zh"
    assert interface_settings.get_response_language() == "en"
    assert interface_settings.get_ui_settings()["theme"] == "dark"


def test_interface_settings_default_when_local_file_is_missing(tmp_path, monkeypatch) -> None:
    service = PathService(workspace_root=tmp_path / "data")
    monkeypatch.setattr(interface_settings, "get_path_service", lambda: service)

    assert interface_settings.get_ui_settings() == interface_settings.DEFAULT_UI_SETTINGS

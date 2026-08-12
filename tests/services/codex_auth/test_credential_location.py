"""The Codex login belongs to the single local workspace."""

from __future__ import annotations

from pathlib import Path

import pytest

from deeptutor.services.codex_auth import service as service_module
from deeptutor.services.codex_auth.storage import CodexCredentialStore

@pytest.fixture
def isolated_user_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    from deeptutor.services import local_workspace
    from deeptutor.services.local_workspace import LocalWorkspace
    from deeptutor.services.path_service import PathService

    data_root = (tmp_path / "data").resolve()
    workspace = LocalWorkspace(PathService(workspace_root=data_root))
    monkeypatch.setattr(local_workspace, "get_local_workspace", lambda: workspace)
    monkeypatch.setattr(service_module, "_SERVICE_INSTANCES", {})
    return data_root / "user"


def test_credentials_land_in_local_user_private_root(isolated_user_root: Path) -> None:
    store = CodexCredentialStore(service_module._codex_secrets_root())

    assert store.credentials_path == (
        isolated_user_root / "private" / "openai-codex" / "credentials.v1.json"
    )
    assert "users" not in store.credentials_path.parts
    assert "system" not in store.credentials_path.parts


def test_legacy_auth_state_cannot_redirect_local_credentials(
    isolated_user_root: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Old identity paths and Auth environment cannot reactivate owner storage."""
    legacy_user = isolated_user_root.parent / "users" / "u_bob"
    legacy_user.mkdir(parents=True)
    (isolated_user_root.parent / "system" / "users.json").parent.mkdir(parents=True)
    (isolated_user_root.parent / "system" / "users.json").write_text("{}")
    monkeypatch.setenv("AUTH_ENABLED", "true")
    monkeypatch.setenv("NEXT_PUBLIC_AUTH_ENABLED", "true")
    monkeypatch.setenv("DEEPTUTOR_AUTH_ENABLED", "true")

    assert service_module._codex_secrets_root() == isolated_user_root

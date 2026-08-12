from __future__ import annotations

from pathlib import Path
import importlib.util
import re


ROOT = Path(__file__).resolve().parents[1]


def test_core_does_not_import_multi_user_knowledge_or_path_access() -> None:
    offenders: list[str] = []
    for path in (ROOT / "deeptutor").rglob("*.py"):
        relative = path.relative_to(ROOT).as_posix()
        if relative.startswith("deeptutor/multi_user/"):
            continue
        source = path.read_text(encoding="utf-8")
        if "deeptutor.multi_user.knowledge_access" in source:
            offenders.append(relative)
        if "deeptutor.multi_user.paths import get_current_path_service" in source:
            offenders.append(relative)
    assert offenders == []


def test_removed_account_auth_and_multi_user_modules_are_absent() -> None:
    assert importlib.util.find_spec("deeptutor.multi_user") is None
    assert importlib.util.find_spec("deeptutor.api.routers.auth") is None
    assert importlib.util.find_spec("deeptutor.services.auth") is None

    offenders: list[str] = []
    for path in (ROOT / "deeptutor").rglob("*.py"):
        relative = path.relative_to(ROOT).as_posix()
        source = path.read_text(encoding="utf-8")
        if re.search(r"(?:from|import)\s+deeptutor\.multi_user", source):
            offenders.append(relative)
    assert offenders == []

    main_source = (ROOT / "deeptutor" / "api" / "main.py").read_text(encoding="utf-8")
    assert "auth.router" not in main_source
    assert "codex_callback.router" in main_source


def test_retained_subagent_router_does_not_import_account_auth() -> None:
    source = (ROOT / "deeptutor" / "api" / "routers" / "subagents.py").read_text(
        encoding="utf-8"
    )
    assert "deeptutor.api.routers.auth" not in source
    assert "require_admin" not in source


def test_local_workspace_contract_targets_data_user() -> None:
    from deeptutor.services.local_workspace import get_local_user, get_local_workspace

    user = get_local_user()
    workspace = get_local_workspace()
    assert user.id == "local"
    assert user.is_admin is True
    assert workspace.path_service.get_user_root().name == "user"

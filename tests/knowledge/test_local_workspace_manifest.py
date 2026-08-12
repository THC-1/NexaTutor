from __future__ import annotations

from pathlib import Path

import pytest

from deeptutor.knowledge.manager import KnowledgeBaseManager
from deeptutor.services import local_workspace
from deeptutor.services.local_workspace import LocalWorkspace
from deeptutor.services.path_service import PathService


@pytest.fixture
def isolated_local_workspace(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> LocalWorkspace:
    workspace = LocalWorkspace(PathService(workspace_root=tmp_path / "data"))
    monkeypatch.setattr(local_workspace, "get_local_workspace", lambda: workspace)
    local_workspace.current_kb_manager.cache_clear()
    yield workspace
    local_workspace.current_kb_manager.cache_clear()


def _make_kb(manager: KnowledgeBaseManager, name: str, *files: str) -> None:
    raw = Path(manager.base_dir) / name / "raw"
    raw.mkdir(parents=True, exist_ok=True)
    for filename in files:
        (raw / filename).write_bytes(b"x" * 512)
    manager.register_knowledge_base(name, description=f"test KB {name}")


def test_local_workspace_resolves_its_kb_manifest(isolated_local_workspace) -> None:
    _make_kb(local_workspace.current_kb_manager(), "local-kb", "a.pdf", "b.pdf")

    manifest = local_workspace.resolve_kb_manifest("local-kb")

    assert manifest is not None
    assert manifest.total == 2
    assert [document.name for document in manifest.documents] == ["a.pdf", "b.pdf"]


def test_manifest_pattern_and_limit_reach_filesystem(isolated_local_workspace) -> None:
    _make_kb(
        local_workspace.current_kb_manager(),
        "local-kb",
        "a.pdf",
        "b.pdf",
        "notes.md",
    )

    manifest = local_workspace.resolve_kb_manifest("local-kb", pattern="*.pdf", limit=1)

    assert manifest is not None
    assert (manifest.total, manifest.matched, manifest.omitted) == (3, 2, 1)


def test_missing_or_empty_kb_has_no_manifest(isolated_local_workspace) -> None:
    assert local_workspace.resolve_kb_manifest("does-not-exist") is None
    assert local_workspace.resolve_kb_manifest("") is None
    assert local_workspace.resolve_kb_manifest(None) is None


def test_legacy_scope_prefixes_cannot_redirect_outside_local_workspace(
    isolated_local_workspace: LocalWorkspace,
) -> None:
    _make_kb(local_workspace.current_kb_manager(), "shared-name", "local.pdf")
    legacy_root = isolated_local_workspace.user_root.parent / "users" / "u_alice"
    _make_kb(KnowledgeBaseManager(base_dir=str(legacy_root / "knowledge_bases")), "shared-name", "secret.pdf")

    for reference in ("admin:kb:shared-name", "user:kb:shared-name", "local:kb:shared-name"):
        manifest = local_workspace.resolve_kb_manifest(reference)
        assert manifest is not None
        assert [document.name for document in manifest.documents] == ["local.pdf"]

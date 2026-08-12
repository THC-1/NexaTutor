from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _source(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def test_pageindex_is_not_registered_or_routable() -> None:
    factory = _source("deeptutor/services/rag/factory.py")
    router = _source("deeptutor/api/routers/knowledge.py")

    assert "PAGEINDEX_PROVIDER" not in factory
    assert "/rag-pipelines/pageindex/config" not in router
    assert "PageIndexConfigUpdate" not in router
    assert "_assert_provider_ready" not in router
    assert "_enforce_provider_formats" not in router


def test_pageindex_runtime_settings_are_inert() -> None:
    source = _source("deeptutor/services/config/runtime_settings.py")

    for token in (
        "DEFAULT_PAGEINDEX_SETTINGS",
        "load_pageindex",
        "save_pageindex",
        "_normalize_pageindex",
        "_apply_pageindex_process_overrides",
        "PAGEINDEX_API_KEY",
        "PAGEINDEX_API_BASE_URL",
    ):
        assert token not in source


def test_pageindex_backend_implementation_is_deleted() -> None:
    module_dir = ROOT / "deeptutor/services/rag/pipelines/pageindex"
    assert not module_dir.exists() or not list(module_dir.glob("*.py"))


def test_pageindex_frontend_surface_is_deleted() -> None:
    assert not (ROOT / "web/components/knowledge/PageIndexSettingsModal.tsx").exists()
    for relative in (
        "web/components/knowledge/CreateKbModal.tsx",
        "web/components/knowledge/KnowledgeHome.tsx",
        "web/components/knowledge/KnowledgePage.tsx",
        "web/lib/knowledge-api.ts",
    ):
        assert "pageindex" not in _source(relative).lower()


def test_pageindex_test_file_is_valid_python() -> None:
    ast.parse(Path(__file__).read_text(encoding="utf-8"))

from __future__ import annotations

from pathlib import Path

from fastapi.routing import APIRoute


ROOT = Path(__file__).resolve().parents[1]


def _text(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def test_p7_lightrag_server_registration_removed() -> None:
    from deeptutor.api.main import app
    from deeptutor.services.rag.factory import KNOWN_PROVIDERS, list_pipelines

    assert "lightrag-server" not in KNOWN_PROVIDERS
    assert "lightrag-server" not in {item["id"] for item in list_pipelines()}
    paths = {route.path for route in app.routes if isinstance(route, APIRoute)}
    assert "/api/v1/knowledge/probe-lightrag-server" not in paths
    assert "/api/v1/knowledge/connect-lightrag-server" not in paths


def test_p7_lightrag_server_calls_and_ui_removed() -> None:
    backend = "\n".join(
        _text(path)
        for path in (
            "deeptutor/services/rag/factory.py",
            "deeptutor/knowledge/manager.py",
            "deeptutor/knowledge/manifest.py",
        )
    ).lower()
    assert "pipelines.lightrag_server" not in backend
    assert "register_lightrag_server_kb" not in backend
    ui = "\n".join(
        _text(path)
        for path in (
            "web/components/knowledge/CreateKbModal.tsx",
            "web/components/knowledge/KnowledgeHome.tsx",
            "web/components/knowledge/KnowledgePage.tsx",
            "web/hooks/useKnowledgeBases.ts",
            "web/lib/knowledge-api.ts",
            "web/locales/en/app.json",
            "web/locales/zh/app.json",
        )
    ).lower()
    assert "lightrag-server" not in ui
    assert "lightragserver" not in ui


def test_p7_lightrag_server_implementation_removed() -> None:
    module_dir = ROOT / "deeptutor/services/rag/pipelines/lightrag_server"
    assert not any(module_dir.glob("*.py"))


def test_p7_lightrag_server_legacy_pointer_is_inert_but_protected() -> None:
    from deeptutor.knowledge.kb_types import is_connected_kb
    from deeptutor.services.rag.factory import normalize_provider_name

    legacy = {"type": "lightrag_server", "rag_provider": "lightrag-server"}
    assert is_connected_kb(legacy) is True
    assert normalize_provider_name(legacy["rag_provider"]) == "llamaindex"

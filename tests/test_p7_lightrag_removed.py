from __future__ import annotations

from pathlib import Path

from fastapi.routing import APIRoute


ROOT = Path(__file__).resolve().parents[1]


def _text(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def test_p7_lightrag_registration_removed() -> None:
    from deeptutor.api.main import app
    from deeptutor.services.rag.factory import KNOWN_PROVIDERS, list_pipelines

    assert "lightrag" not in KNOWN_PROVIDERS
    assert "lightrag" not in {item["id"] for item in list_pipelines()}
    paths = {route.path for route in app.routes if isinstance(route, APIRoute)}
    assert "/api/v1/knowledge/rag-pipelines/lightrag/config" not in paths


def test_p7_lightrag_calls_and_settings_removed() -> None:
    files = (
        "deeptutor/services/rag/factory.py",
        "deeptutor/services/rag/index_probe.py",
        "deeptutor/services/rag/linked_kb.py",
        "deeptutor/services/rag/preflight.py",
        "deeptutor/services/rag/service.py",
        "deeptutor/api/utils/task_log_stream.py",
        "deeptutor/services/config/runtime_settings.py",
        "deeptutor/services/config/__init__.py",
    )
    production = "\n".join(_text(path) for path in files).lower()
    assert "pipelines.lightrag." not in production
    assert "lightrag_provider" not in production
    assert "load_lightrag" not in production


def test_p7_lightrag_ui_removed() -> None:
    assert not (ROOT / "web/components/knowledge/EngineDetail.tsx").exists()
    ui = "\n".join(
        _text(path)
        for path in (
            "web/components/knowledge/CreateKbModal.tsx",
            "web/components/knowledge/KnowledgeHome.tsx",
            "web/lib/knowledge-api.ts",
            "web/locales/en/app.json",
            "web/locales/zh/app.json",
        )
    ).lower()
    assert "rag-anything" not in ui
    assert '"lightrag"' not in ui


def test_p7_lightrag_implementation_removed() -> None:
    module_dir = ROOT / "deeptutor/services/rag/pipelines/lightrag"
    assert not any(module_dir.glob("*.py"))


def test_p7_lightrag_dependencies_removed() -> None:
    packaging = (_text("pyproject.toml") + _text("requirements/cli.txt")).lower()
    assert "rag-lightrag" not in packaging
    assert "raganything" not in packaging

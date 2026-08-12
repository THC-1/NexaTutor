from __future__ import annotations

import importlib.util
from pathlib import Path

from fastapi.routing import APIRoute


ROOT = Path(__file__).resolve().parents[1]


def _text(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def test_p7_graphrag_registration_removed() -> None:
    from deeptutor.api.main import app
    from deeptutor.services.rag.factory import KNOWN_PROVIDERS, list_pipelines

    assert "graphrag" not in KNOWN_PROVIDERS
    assert "graphrag" not in {item["id"] for item in list_pipelines()}
    paths = {route.path for route in app.routes if isinstance(route, APIRoute)}
    assert "/api/v1/knowledge/rag-pipelines/graphrag/config" not in paths


def test_p7_graphrag_calls_and_settings_removed() -> None:
    production = "\n".join(
        _text(path)
        for path in (
            "deeptutor/services/rag/factory.py",
            "deeptutor/services/rag/index_probe.py",
            "deeptutor/services/rag/linked_kb.py",
            "deeptutor/services/rag/preflight.py",
            "deeptutor/services/rag/service.py",
            "deeptutor/api/utils/task_log_stream.py",
            "deeptutor/services/config/runtime_settings.py",
            "deeptutor/services/config/__init__.py",
        )
    ).lower()
    assert "pipelines.graphrag" not in production
    assert "graphrag_provider" not in production
    assert "load_graphrag" not in production
    assert '"graphrag"' not in _text("deeptutor/services/rag/preflight.py").lower()


def test_p7_graphrag_ui_removed() -> None:
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
    assert "graphrag" not in ui


def test_p7_graphrag_implementation_removed() -> None:
    module_dir = ROOT / "deeptutor/services/rag/pipelines/graphrag"
    assert not any(module_dir.glob("*.py"))


def test_p7_graphrag_dependencies_removed() -> None:
    packaging = (_text("pyproject.toml") + _text("requirements/cli.txt")).lower()
    assert "graphrag" not in packaging
    assert "nest_asyncio" not in packaging

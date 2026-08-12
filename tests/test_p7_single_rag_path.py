from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _source(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def test_factory_only_exposes_llamaindex() -> None:
    from deeptutor.services.rag.factory import (
        DEFAULT_PROVIDER,
        KNOWN_PROVIDERS,
        list_pipelines,
        normalize_provider_name,
    )

    assert DEFAULT_PROVIDER == "llamaindex"
    assert KNOWN_PROVIDERS == frozenset({DEFAULT_PROVIDER})
    assert [entry["id"] for entry in list_pipelines()] == [DEFAULT_PROVIDER]
    for legacy in ("pageindex", "graphrag", "lightrag", "lightrag-server", "ima"):
        assert normalize_provider_name(legacy) == DEFAULT_PROVIDER


def test_create_and_upload_do_not_expose_provider_selection() -> None:
    tree = ast.parse(_source("deeptutor/api/routers/knowledge.py"))
    functions = {
        node.name: node
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    for name in ("create_knowledge_base", "upload_files"):
        params = {arg.arg for arg in functions[name].args.args}
        assert "rag_provider" not in params


def test_knowledge_ui_has_no_engine_picker_or_engine_deep_link() -> None:
    page = _source("web/components/knowledge/KnowledgePage.tsx")
    home = _source("web/components/knowledge/KnowledgeHome.tsx")
    modal = _source("web/components/knowledge/CreateKbModal.tsx")

    assert "EngineDetail" not in page
    assert 'searchParams.get("engine")' not in page
    assert "Retrieval engines" not in home
    assert "Index engine" not in modal
    assert "providers.map" not in modal


def test_standard_rag_components_remain_present() -> None:
    for relative in (
        "deeptutor/services/rag/pipelines/llamaindex/pipeline.py",
        "deeptutor/services/rag/pipelines/llamaindex/vector_store.py",
        "deeptutor/services/rag/pipelines/llamaindex/retrievers.py",
        "deeptutor/tools/rag_tool.py",
    ):
        assert (ROOT / relative).is_file(), relative

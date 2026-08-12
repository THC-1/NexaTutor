from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _source(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def test_ima_is_not_registered_or_routable() -> None:
    factory = _source("deeptutor/services/rag/factory.py")
    router = _source("deeptutor/api/routers/knowledge.py")
    manager = _source("deeptutor/knowledge/manager.py")

    assert "IMA_PROVIDER" not in factory
    assert "pipelines.ima" not in factory
    assert "/probe-ima" not in router
    assert "/connect-ima" not in router
    assert "register_ima_kb" not in manager


def test_ima_remote_implementation_is_deleted() -> None:
    module_dir = ROOT / "deeptutor/services/rag/pipelines/ima"
    assert not module_dir.exists() or not list(module_dir.glob("*.py"))


def test_ima_old_kb_type_is_only_an_inactive_data_sentinel() -> None:
    source = _source("deeptutor/knowledge/kb_types.py")
    assert "IMA_KB_TYPE" not in source
    assert "LEGACY_INACTIVE_KB_TYPES" in source
    assert '"ima"' in source


def test_ima_has_no_frontend_remote_client() -> None:
    for relative in (
        "web/components/knowledge/CreateKbModal.tsx",
        "web/components/knowledge/KnowledgePage.tsx",
        "web/hooks/useKnowledgeBases.ts",
        "web/lib/knowledge-api.ts",
    ):
        source = _source(relative)
        assert "probeIma" not in source
        assert "connectIma" not in source


def test_legacy_ima_pointer_is_preserved_without_activation(tmp_path: Path) -> None:
    from deeptutor.knowledge.manager import KnowledgeBaseManager

    config_path = tmp_path / "kb_config.json"
    original = {
        "knowledge_bases": {
            "old-ima": {
                "type": "ima",
                "rag_provider": "ima",
                "client_id": "historical-client",
                "api_key": "historical-secret",
                "knowledge_base_id": "historical-library",
                "status": "ready",
            }
        }
    }
    config_path.write_text(json.dumps(original), encoding="utf-8")

    manager = KnowledgeBaseManager(base_dir=tmp_path)
    assert "old-ima" in manager.list_knowledge_bases()
    assert json.loads(config_path.read_text(encoding="utf-8")) == original

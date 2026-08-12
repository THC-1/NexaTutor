"""P5 guardrails for removing PocketBase calls from Core Knowledge."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_knowledge_manager_has_no_pocketbase_mirror() -> None:
    source = (ROOT / "deeptutor" / "knowledge" / "manager.py").read_text(encoding="utf-8")

    assert "pocketbase" not in source.lower()
    assert "_sync_kb_to_pb" not in source
    assert "_pb_enabled" not in source


def test_knowledge_upload_has_no_pocketbase_mirror() -> None:
    source = (ROOT / "deeptutor" / "api" / "routers" / "knowledge.py").read_text(
        encoding="utf-8"
    )

    assert "pocketbase" not in source.lower()
    assert "_upload_file_to_pb" not in source
    assert "_pb_sync" not in source

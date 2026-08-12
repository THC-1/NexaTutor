"""Manager handling of local connected-subagent KB pointers."""

from __future__ import annotations

from pathlib import Path

from deeptutor.knowledge.manager import KnowledgeBaseManager


def test_register_cli_connection_round_trips_local_target(tmp_path: Path) -> None:
    manager = KnowledgeBaseManager(base_dir=str(tmp_path / "kbs"))

    entry = manager.register_subagent_connection("MyClaude", "claude_code", cwd="")
    assert entry["type"] == "subagent"
    assert entry["agent_kind"] == "claude_code"
    assert entry["cwd"] == ""
    assert "partner_id" not in entry
    assert not (manager.base_dir / "MyClaude").exists()

    meta = manager.get_metadata("MyClaude")
    assert meta["type"] == "subagent"
    assert meta["agent_kind"] == "claude_code"
    assert "partner_id" not in meta

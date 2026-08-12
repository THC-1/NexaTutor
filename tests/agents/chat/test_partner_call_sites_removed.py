"""Negative contracts for removed Partner-specific chat execution paths."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PIPELINE = ROOT / "deeptutor" / "agents" / "chat" / "agentic_pipeline.py"
PROMPTS = ROOT / "deeptutor" / "agents" / "chat" / "prompt_blocks.py"


def test_chat_pipeline_has_no_partner_turn_execution_branches() -> None:
    source = PIPELINE.read_text(encoding="utf-8")

    assert "PARTNER_BUILTIN_TOOL_NAMES" not in source
    assert "_PARTNER_SUPPRESSED_TOOLS" not in source
    assert "_is_partner_turn" not in source
    assert '"kind": "partner"' not in source


def test_chat_prompt_assembler_has_no_partner_identity_blocks() -> None:
    source = PROMPTS.read_text(encoding="utf-8")

    assert "partner_turn_policy" not in source
    assert "general_partner" not in source

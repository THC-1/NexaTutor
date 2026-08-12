"""Registry contracts for staged removal of Partner-only tools."""

from __future__ import annotations

from deeptutor.runtime.registry.tool_registry import get_tool_registry


def test_partner_tools_are_not_registered_and_core_tools_remain() -> None:
    tools = set(get_tool_registry().list_tools())

    assert {"partner_read", "partner_memorize", "partner_search"}.isdisjoint(tools)
    assert {"rag", "read_memory", "write_memory", "consult_subagent"} <= tools

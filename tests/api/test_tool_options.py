"""Contract tests for the configurable built-in tool surface."""

from __future__ import annotations

import pytest

from deeptutor.api.utils.tool_options import build_tool_options


@pytest.mark.asyncio
async def test_tool_options_only_exposes_builtin_surfaces() -> None:
    payload = await build_tool_options()
    assert set(payload) == {"tools", "builtin_tools"}
    assert all(row.get("name") for row in payload["tools"])
    assert all(row.get("name") for row in payload["builtin_tools"])
    assert "mcp_tools" not in payload

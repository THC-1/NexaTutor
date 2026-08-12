"""Negative contracts for removed extension runtime call sites."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_chat_pipeline_has_no_provider_or_deferred_tool_calls() -> None:
    source = (ROOT / "deeptutor" / "agents" / "chat" / "agentic_pipeline.py").read_text(
        encoding="utf-8"
    )
    forbidden = (
        "build_tool_view",
        "ProviderToolView",
        "DeferredToolLoader",
        "ToolScope",
        "CLI_APP_TOOL_PREFIX",
        'tool_name == "load_tools"',
        "mcp_tools_filter",
        "_prepare_deferred_tools",
    )

    assert [token for token in forbidden if token in source] == []


def test_retained_runtime_does_not_start_reload_or_stop_mcp_manager() -> None:
    retained = (
        ROOT / "deeptutor" / "api" / "main.py",
        ROOT / "deeptutor" / "api" / "routers" / "knowledge.py",
        ROOT / "deeptutor" / "api" / "utils" / "tool_options.py",
    )
    offenders = []
    for path in retained:
        source = path.read_text(encoding="utf-8")
        if "get_mcp_manager" in source:
            offenders.append(str(path.relative_to(ROOT)))

    assert offenders == []

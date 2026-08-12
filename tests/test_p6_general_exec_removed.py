from __future__ import annotations

import importlib.util


def test_general_shell_exec_has_no_runtime_or_implementation_surface() -> None:
    from deeptutor.agents._shared.tool_composition import ToolMountFlags
    from deeptutor.tools.builtin import BUILTIN_TOOL_NAMES, CONFIGURABLE_BUILTIN_TOOL_NAMES

    assert "exec" not in BUILTIN_TOOL_NAMES
    assert "exec" not in CONFIGURABLE_BUILTIN_TOOL_NAMES
    assert "has_exec" not in ToolMountFlags.__dataclass_fields__
    assert importlib.util.find_spec("deeptutor.tools.exec_tool") is None


def test_protected_execution_surfaces_remain() -> None:
    from deeptutor.services.sandbox import ResourceLimits, get_sandbox_service
    from deeptutor.services.subagent.codex import CodexBackend
    from deeptutor.tools.builtin import BUILTIN_TOOL_NAMES

    assert "code_execution" in BUILTIN_TOOL_NAMES
    assert ResourceLimits().timeout_s > 0
    assert get_sandbox_service is not None
    command = CodexBackend()._build_command("hello", session_id=None, config=__import__(
        "deeptutor.services.subagent.config", fromlist=["BackendConfig"]
    ).BackendConfig())
    assert command[:2] == ["codex", "exec"]

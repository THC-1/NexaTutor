from __future__ import annotations

import importlib.util


def test_brainstorm_has_no_runtime_or_implementation_surface() -> None:
    from deeptutor.tools.builtin import BUILTIN_TOOL_NAMES, USER_TOGGLEABLE_TOOL_NAMES

    assert "brainstorm" not in BUILTIN_TOOL_NAMES
    assert "brainstorm" not in USER_TOGGLEABLE_TOOL_NAMES
    assert importlib.util.find_spec("deeptutor.tools.brainstorm") is None

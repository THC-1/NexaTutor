from __future__ import annotations

import importlib.util


def test_dedicated_reason_tool_has_no_runtime_or_implementation_surface() -> None:
    from deeptutor.tools.builtin import BUILTIN_TOOL_NAMES, USER_TOGGLEABLE_TOOL_NAMES

    assert "reason" not in BUILTIN_TOOL_NAMES
    assert "reason" not in USER_TOGGLEABLE_TOOL_NAMES
    assert importlib.util.find_spec("deeptutor.tools.reason") is None


def test_reason_data_fields_remain_supported() -> None:
    from deeptutor.learning.policy import NextStep

    assert NextStep(action="complete", reason="done").reason == "done"

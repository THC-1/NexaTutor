"""P6 negative assertions for removed video-generation registrations."""

from deeptutor.services.config.model_catalog import _default_catalog
from deeptutor.tools.builtin import BUILTIN_TOOL_NAMES


def test_videogen_is_not_a_builtin_tool() -> None:
    assert "videogen" not in BUILTIN_TOOL_NAMES


def test_videogen_is_not_a_model_catalog_service() -> None:
    services = _default_catalog().get("services") or {}
    assert "videogen" not in services

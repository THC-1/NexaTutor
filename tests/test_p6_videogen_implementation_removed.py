"""P6 negative assertions for removed videogen implementation."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_videogen_service_and_tool_implementation_are_removed() -> None:
    assert not any((ROOT / "deeptutor/services/videogen").rglob("*.py"))
    source = (ROOT / "deeptutor/tools/media_gen_tool.py").read_text(encoding="utf-8")
    assert "VideogenTool" not in source
    assert "videogen" not in source.lower()

"""P6 negative assertions for removed videogen calls in retained services."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_chat_and_provider_runtime_do_not_call_videogen() -> None:
    for relative in (
        "deeptutor/agents/chat/agentic_pipeline.py",
        "deeptutor/services/config/provider_runtime.py",
        "deeptutor/services/config/test_runner.py",
        "deeptutor/api/routers/settings.py",
    ):
        source = (ROOT / relative).read_text(encoding="utf-8").lower()
        assert "videogen" not in source

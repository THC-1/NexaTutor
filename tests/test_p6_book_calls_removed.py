"""P6 negative assertions for removed Book calls in retained Core flows."""

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]


def test_retained_session_and_mastery_flows_do_not_call_book() -> None:
    for relative in (
        "deeptutor/services/session/turn_runtime.py",
        "deeptutor/services/session/source_inventory.py",
        "deeptutor/capabilities/mastery/capability.py",
    ):
        source = (ROOT / relative).read_text(encoding="utf-8")
        assert "deeptutor.book" not in source
        assert re.search(r"(?<!note)book_references", source) is None


def test_retained_frontend_transports_do_not_send_book_references() -> None:
    for relative in (
        "web/context/UnifiedChatContext.tsx",
        "web/context/QuizFollowupContext.tsx",
        "web/lib/unified-ws.ts",
    ):
        source = (ROOT / relative).read_text(encoding="utf-8")
        assert re.search(r"(?<!note)book_references", source) is None
        assert re.search(r"(?<![Nn]ote)bookReferences", source) is None

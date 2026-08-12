from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WEBSOCKET_ROUTERS = (
    "unified_ws.py",
    "quiz_judge.py",
    "chat.py",
    "question.py",
    "knowledge.py",
)


def test_websocket_entrypoints_do_not_call_account_auth_or_user_context() -> None:
    router_root = ROOT / "deeptutor" / "api" / "routers"
    for filename in WEBSOCKET_ROUTERS:
        source = (router_root / filename).read_text(encoding="utf-8")
        assert "ws_require_auth" not in source, filename
        assert "ws_auth_failed" not in source, filename
        assert "reset_current_user" not in source, filename


def test_account_auth_cannot_gate_registered_http_or_websocket_entrypoints() -> None:
    main_source = (ROOT / "deeptutor" / "api" / "main.py").read_text(encoding="utf-8")
    assert "require_auth" not in main_source
    assert "dependencies=_auth" not in main_source

"""P5 guardrails for removing PocketBase from the Core session path."""

from __future__ import annotations

from deeptutor.services import session as session_service


def test_session_backend_is_always_local_sqlite(monkeypatch) -> None:
    sqlite_store = object()
    monkeypatch.setattr(
        session_service,
        "get_sqlite_session_store",
        lambda: sqlite_store,
    )

    assert session_service.get_session_store() is sqlite_store

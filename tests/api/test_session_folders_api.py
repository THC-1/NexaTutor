"""API tests for session folder management.

Exercises the HTTP contract of /api/v1/session-folders and the folder
extensions of /api/v1/sessions (folder filter + single-session move) on a
standalone app backed by a temp-DB store — no real data tree involved.
"""

from __future__ import annotations

import importlib
from pathlib import Path

import pytest

try:
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
except Exception:  # pragma: no cover - optional dependency in lightweight envs
    FastAPI = None
    TestClient = None

pytestmark = pytest.mark.skipif(
    FastAPI is None or TestClient is None, reason="fastapi not installed"
)

if FastAPI is not None and TestClient is not None:
    folders_module = importlib.import_module("deeptutor.api.routers.session_folders")
    sessions_module = importlib.import_module("deeptutor.api.routers.sessions")
    from deeptutor.services.session.sqlite_store import SQLiteSessionStore
else:  # pragma: no cover
    folders_module = None
    sessions_module = None
    SQLiteSessionStore = None


class _FakeAttachmentStore:
    async def delete_session(self, session_id: str) -> None:
        return None


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    store = SQLiteSessionStore(db_path=tmp_path / "test.db")

    def _store():
        return store

    monkeypatch.setattr(folders_module, "get_sqlite_session_store", _store)
    monkeypatch.setattr(folders_module, "get_attachment_store", _FakeAttachmentStore)
    monkeypatch.setattr(sessions_module, "get_session_store", _store)
    monkeypatch.setattr(sessions_module, "get_sqlite_session_store", _store)
    monkeypatch.setattr(sessions_module, "get_attachment_store", _FakeAttachmentStore)

    app = FastAPI()
    app.include_router(folders_module.router, prefix="/api/v1/session-folders")
    app.include_router(sessions_module.router, prefix="/api/v1/sessions")
    return TestClient(app), store


def _create_session(store: SQLiteSessionStore, title: str = "chat") -> str:
    import asyncio

    return asyncio.run(store.create_session(title=title))["id"]


def test_folder_crud_lifecycle(client):
    client, store = client

    # create
    res = client.post("/api/v1/session-folders", json={"name": "School"})
    assert res.status_code == 200
    folder = res.json()["folder"]
    fid = folder["folder_id"]
    assert folder["name"] == "School" and folder["status"] == "active"

    # list
    res = client.get("/api/v1/session-folders")
    assert res.status_code == 200
    assert [f["name"] for f in res.json()["folders"]] == ["School"]

    # rename
    res = client.patch(f"/api/v1/session-folders/{fid}", json={"name": "Homework"})
    assert res.status_code == 200
    assert res.json()["folder"]["name"] == "Homework"

    # empty name rejected by validation
    res = client.patch(f"/api/v1/session-folders/{fid}", json={"name": "  "})
    assert res.status_code == 422

    # archive -> shows up only under the archived filter
    assert client.post(f"/api/v1/session-folders/{fid}/archive").status_code == 200
    active = client.get("/api/v1/session-folders?status=active").json()["folders"]
    assert active == []
    archived = client.get("/api/v1/session-folders?status=archived").json()["folders"]
    assert [f["id"] for f in archived] == [fid]
    # default (no status) lists everything
    assert [f["id"] for f in client.get("/api/v1/session-folders").json()["folders"]] == [fid]

    # restore
    assert client.post(f"/api/v1/session-folders/{fid}/restore").status_code == 200
    assert client.get("/api/v1/session-folders").json()["folders"][0]["status"] == "active"

    # 404s
    assert client.patch("/api/v1/session-folders/folder_missing", json={"name": "x"}).status_code == 404
    assert client.post("/api/v1/session-folders/folder_missing/archive").status_code == 404


def test_delete_requires_archived_and_cascades(client):
    client, store = client

    fid = client.post("/api/v1/session-folders", json={"name": "F"}).json()["folder"]["id"]
    s1 = _create_session(store)
    assert (
        client.put(f"/api/v1/sessions/{s1}/folder", json={"folder_id": fid}).status_code
        == 200
    )

    # active folder delete -> 409
    assert client.delete(f"/api/v1/session-folders/{fid}").status_code == 409

    # archived delete with default cascade
    client.post(f"/api/v1/session-folders/{fid}/archive")
    res = client.delete(f"/api/v1/session-folders/{fid}")
    assert res.status_code == 200
    body = res.json()
    assert body["deleted"] is True
    assert body["deleted_sessions"] == [s1]
    assert client.get("/api/v1/sessions").json()["sessions"] == []


def test_delete_releases_sessions_when_not_cascading(client):
    client, store = client

    fid = client.post("/api/v1/session-folders", json={"name": "F"}).json()["folder"]["id"]
    s1 = _create_session(store)
    client.put(f"/api/v1/sessions/{s1}/folder", json={"folder_id": fid})
    client.post(f"/api/v1/session-folders/{fid}/archive")

    res = client.delete(f"/api/v1/session-folders/{fid}?delete_sessions=false")
    assert res.status_code == 200
    assert res.json()["deleted_sessions"] == []
    unassigned = client.get("/api/v1/sessions?folder_id=").json()["sessions"]
    assert [s["session_id"] for s in unassigned] == [s1]


def test_session_folder_filter_and_move(client):
    client, store = client

    s1 = _create_session(store, "math")
    s2 = _create_session(store, "physics")
    fid = client.post("/api/v1/session-folders", json={"name": "Work"}).json()["folder"]["id"]

    # move one session in
    res = client.put(f"/api/v1/sessions/{s1}/folder", json={"folder_id": fid})
    assert res.status_code == 200
    assert res.json()["session"]["folder_id"] == fid

    # filter by folder / unassigned / all
    in_folder = client.get(f"/api/v1/sessions?folder_id={fid}").json()["sessions"]
    assert [s["session_id"] for s in in_folder] == [s1]
    unassigned = client.get("/api/v1/sessions?folder_id=").json()["sessions"]
    assert [s["session_id"] for s in unassigned] == [s2]
    assert len(client.get("/api/v1/sessions").json()["sessions"]) == 2

    # move to archived folder -> 409
    client.post(f"/api/v1/session-folders/{fid}/archive")
    res = client.put(f"/api/v1/sessions/{s2}/folder", json={"folder_id": fid})
    assert res.status_code == 409

    # move out of archived folder (individual recovery) -> unassigned
    res = client.put(f"/api/v1/sessions/{s1}/folder", json={"folder_id": ""})
    assert res.status_code == 200
    assert res.json()["session"]["folder_id"] == ""

    # missing session -> 404
    assert (
        client.put("/api/v1/sessions/session_missing/folder", json={"folder_id": ""}).status_code
        == 404
    )


def test_batch_move(client):
    client, store = client

    fid = client.post("/api/v1/session-folders", json={"name": "Batch"}).json()["folder"]["id"]
    ids = [_create_session(store, f"chat {i}") for i in range(3)]
    res = client.put(f"/api/v1/session-folders/{fid}/sessions", json={"session_ids": ids})
    assert res.status_code == 200
    assert res.json()["updated"] == 3
    listed = client.get(f"/api/v1/sessions?folder_id={fid}").json()["sessions"]
    assert len(listed) == 3
    # batch into archived folder -> 409
    client.post(f"/api/v1/session-folders/{fid}/archive")
    assert (
        client.put(f"/api/v1/session-folders/{fid}/sessions", json={"session_ids": ids}).status_code
        == 409
    )


def test_pin_unpin_lifecycle(client):
    client, store = client

    older = client.post("/api/v1/session-folders", json={"name": "Older"}).json()["folder"]
    newer = client.post("/api/v1/session-folders", json={"name": "Newer"}).json()["folder"]
    assert [f["name"] for f in client.get("/api/v1/session-folders").json()["folders"]] == [
        "Older",
        "Newer",
    ]

    # pin the newer folder -> it jumps to the top with pinned=1
    res = client.put(f"/api/v1/session-folders/{newer['id']}/pin")
    assert res.status_code == 200
    assert res.json()["folder"]["pinned"] == 1
    folders = client.get("/api/v1/session-folders").json()["folders"]
    assert [f["name"] for f in folders] == ["Newer", "Older"]
    assert folders[0]["pinned"] == 1

    # unpin restores creation order
    res = client.delete(f"/api/v1/session-folders/{newer['id']}/pin")
    assert res.status_code == 200
    assert res.json()["folder"]["pinned"] == 0
    folders = client.get("/api/v1/session-folders").json()["folders"]
    assert [f["name"] for f in folders] == ["Older", "Newer"]

    # archived folders cannot be pinned
    client.post(f"/api/v1/session-folders/{older['id']}/archive")
    assert client.put(f"/api/v1/session-folders/{older['id']}/pin").status_code == 409

    # missing folder -> 404
    assert client.put("/api/v1/session-folders/folder_missing/pin").status_code == 404
    assert client.delete("/api/v1/session-folders/folder_missing/pin").status_code == 404

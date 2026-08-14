"""Tests for session folder organization.

Lifecycle under test:

    active folder --archive--> archived folder --restore--> active folder
                                      |
                                      +--delete--> sessions deleted by
                                                   default (or released to
                                                   unassigned with
                                                   ``delete_sessions=false``)

Sessions never move *into* an archived folder; moving a session out of an
archived folder is the individual recovery path.
"""

from __future__ import annotations

import asyncio
from pathlib import Path

import pytest

from deeptutor.services.session.sqlite_store import SQLiteSessionStore


@pytest.fixture
def store(tmp_path: Path) -> SQLiteSessionStore:
    return SQLiteSessionStore(db_path=tmp_path / "test.db")


def _session(store: SQLiteSessionStore, title: str = "chat") -> str:
    return asyncio.run(store.create_session(title=title))["id"]


def test_folder_lifecycle_and_counts(store: SQLiteSessionStore) -> None:
    folder = asyncio.run(store.create_folder("School"))
    assert folder["status"] == "active"
    assert folder["session_count"] == 0

    s1 = _session(store)
    s2 = _session(store)
    assert asyncio.run(store.set_session_folder(s1, folder["id"])) is True
    assert asyncio.run(store.set_session_folder(s2, folder["id"])) is True

    folders = asyncio.run(store.list_folders())
    assert [(f["name"], f["session_count"], f["status"]) for f in folders] == [
        ("School", 2, "active")
    ]
    # folder_id alias mirrors the sessions payload convention
    assert folders[0]["folder_id"] == folders[0]["id"]


def test_list_sessions_folder_filter_and_unassigned(store: SQLiteSessionStore) -> None:
    s1 = _session(store, "math")
    s2 = _session(store, "physics")
    folder = asyncio.run(store.create_folder("Work"))
    asyncio.run(store.set_session_folder(s1, folder["id"]))

    in_folder = asyncio.run(store.list_sessions(folder_id=folder["id"]))
    unassigned = asyncio.run(store.list_sessions(folder_id=""))
    all_sessions = asyncio.run(store.list_sessions())
    assert [s["id"] for s in in_folder] == [s1]
    assert [s["id"] for s in unassigned] == [s2]
    assert len(all_sessions) == 2
    # summaries carry folder_id for client-side grouping
    by_id = {s["id"]: s["folder_id"] for s in all_sessions}
    assert by_id[s1] == folder["id"]
    assert by_id[s2] == ""


def test_rename_folder(store: SQLiteSessionStore) -> None:
    folder = asyncio.run(store.create_folder("Old"))
    renamed = asyncio.run(store.rename_folder(folder["id"], "New"))
    assert renamed is not None
    assert renamed["name"] == "New"
    assert asyncio.run(store.rename_folder("folder_missing", "X")) is None


def test_active_folder_cannot_be_deleted(store: SQLiteSessionStore) -> None:
    folder = asyncio.run(store.create_folder("Keep"))
    with pytest.raises(ValueError, match="archived"):
        asyncio.run(store.delete_folder(folder["id"]))
    # still there, still active
    assert asyncio.run(store.get_folder(folder["id"]))["status"] == "active"


def test_archive_restore_and_delete_with_sessions(store: SQLiteSessionStore) -> None:
    folder = asyncio.run(store.create_folder("Archive me"))
    s1 = _session(store)
    s2 = _session(store)
    asyncio.run(store.set_session_folder(s1, folder["id"]))
    asyncio.run(store.set_session_folder(s2, folder["id"]))

    assert asyncio.run(store.archive_folder(folder["id"])) is True
    assert asyncio.run(store.get_folder(folder["id"]))["status"] == "archived"
    # archived folders disappear from the active list (default lists all;
    # the active filter is what the sidebar uses for grouping)
    assert asyncio.run(store.list_folders(status="active")) == []
    assert [f["id"] for f in asyncio.run(store.list_folders(status="archived"))] == [
        folder["id"]
    ]
    # default (no status) returns every folder regardless of state
    assert [f["id"] for f in asyncio.run(store.list_folders())] == [folder["id"]]

    # restore brings folder + sessions back
    assert asyncio.run(store.restore_folder(folder["id"])) is True
    assert asyncio.run(store.get_folder(folder["id"]))["status"] == "active"

    # delete (archived, default) cascades sessions
    assert asyncio.run(store.archive_folder(folder["id"])) is True
    result = asyncio.run(store.delete_folder(folder["id"], delete_sessions=True))
    assert result == {"deleted": True, "deleted_sessions": [s1, s2]}
    assert asyncio.run(store.list_sessions()) == []
    assert asyncio.run(store.delete_folder(folder["id"])) == {
        "deleted": False,
        "deleted_sessions": [],
    }


def test_delete_archived_folder_releases_sessions(store: SQLiteSessionStore) -> None:
    folder = asyncio.run(store.create_folder("Release"))
    s1 = _session(store)
    asyncio.run(store.set_session_folder(s1, folder["id"]))
    asyncio.run(store.archive_folder(folder["id"]))

    result = asyncio.run(store.delete_folder(folder["id"], delete_sessions=False))
    assert result == {"deleted": True, "deleted_sessions": []}
    assert [s["id"] for s in asyncio.run(store.list_sessions(folder_id=""))] == [s1]


def test_session_cannot_move_into_archived_folder(store: SQLiteSessionStore) -> None:
    folder = asyncio.run(store.create_folder("Archived"))
    s1 = _session(store)
    asyncio.run(store.archive_folder(folder["id"]))
    with pytest.raises(ValueError, match="not active"):
        asyncio.run(store.set_session_folder(s1, folder["id"]))


def test_individual_recovery_from_archived_folder(store: SQLiteSessionStore) -> None:
    folder = asyncio.run(store.create_folder("Archive"))
    s1 = _session(store)
    s2 = _session(store)
    asyncio.run(store.set_session_folder(s1, folder["id"]))
    asyncio.run(store.set_session_folder(s2, folder["id"]))
    asyncio.run(store.archive_folder(folder["id"]))

    # recover s2 alone -> back to unassigned
    assert asyncio.run(store.set_session_folder(s2, "")) is True
    assert [s["id"] for s in asyncio.run(store.list_sessions(folder_id=""))] == [s2]
    assert asyncio.run(store.get_folder(folder["id"]))["session_count"] == 1
    # sessions in an archived folder can also move to an active folder
    other = asyncio.run(store.create_folder("Active"))
    assert asyncio.run(store.set_session_folder(s1, other["id"])) is True
    assert [s["id"] for s in asyncio.run(store.list_sessions(folder_id=other["id"]))] == [
        s1
    ]


def test_move_sessions_batch(store: SQLiteSessionStore) -> None:
    folder = asyncio.run(store.create_folder("Batch"))
    ids = [_session(store) for _ in range(3)]
    assert asyncio.run(store.move_sessions(folder["id"], ids)) == 3
    assert len(asyncio.run(store.list_sessions(folder_id=folder["id"]))) == 3
    # unknown folder rejected
    with pytest.raises(ValueError, match="not active"):
        asyncio.run(store.move_sessions("folder_missing", ids))


def test_pin_unpin_and_sorting(store: SQLiteSessionStore) -> None:
    older = asyncio.run(store.create_folder("Older"))
    newer = asyncio.run(store.create_folder("Newer"))
    assert older["pinned"] == 0

    # default order: creation order
    assert [f["id"] for f in asyncio.run(store.list_folders())] == [
        older["id"],
        newer["id"],
    ]

    # pin the newer folder -> it jumps to the top
    assert asyncio.run(store.set_folder_pinned(newer["id"], True)) is True
    folders = asyncio.run(store.list_folders())
    assert [f["id"] for f in folders] == [newer["id"], older["id"]]
    assert folders[0]["pinned"] == 1

    # pinning twice is idempotent
    assert asyncio.run(store.set_folder_pinned(newer["id"], True)) is True
    assert asyncio.run(store.list_folders())[0]["pinned"] == 1

    # unpin restores creation order
    assert asyncio.run(store.set_folder_pinned(newer["id"], False)) is True
    assert [f["id"] for f in asyncio.run(store.list_folders())] == [
        older["id"],
        newer["id"],
    ]

    # missing folder -> False
    assert asyncio.run(store.set_folder_pinned("folder_missing", True)) is False


def test_pin_rejected_for_archived_folders(store: SQLiteSessionStore) -> None:
    folder = asyncio.run(store.create_folder("Archive me"))
    asyncio.run(store.archive_folder(folder["id"]))
    with pytest.raises(ValueError, match="Only active folders"):
        asyncio.run(store.set_folder_pinned(folder["id"], True))
    # archiving a pinned folder keeps the flag so restore brings it back up
    pinned = asyncio.run(store.create_folder("Pin me"))
    asyncio.run(store.set_folder_pinned(pinned["id"], True))
    asyncio.run(store.archive_folder(pinned["id"]))
    asyncio.run(store.restore_folder(pinned["id"]))
    restored = asyncio.run(store.get_folder(pinned["id"]))
    assert restored is not None and restored["pinned"] == 1

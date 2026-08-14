"""
Session folder management API.

Folders organize native chat sessions. Lifecycle:

    active folder --archive--> archived folder --restore--> active folder
                                      |
                                      +--delete--> sessions deleted by
                                                   default (or released to
                                                   unassigned with
                                                   ``delete_sessions=false``)

Sessions never move *into* an archived folder; moving a session out of an
archived folder (to unassigned or an active folder) is the individual
recovery path.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field, field_validator

from deeptutor.services.session import get_sqlite_session_store
from deeptutor.services.storage.attachment_store import get_attachment_store

logger = logging.getLogger(__name__)

router = APIRouter()


class FolderNameRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=60)

    @field_validator("name")
    @classmethod
    def _reject_blank(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("Folder name must not be blank")
        return stripped


class FolderMoveRequest(BaseModel):
    session_ids: list[str] = Field(default_factory=list, max_length=500)


def _require_folder(folder: dict | None) -> dict:
    if folder is None:
        raise HTTPException(status_code=404, detail="Folder not found")
    return folder


@router.get("")
async def list_folders(
    status: str | None = Query(default=None, pattern="^(active|archived)$"),
):
    store = get_sqlite_session_store()
    folders = await store.list_folders(status=status)
    return {"folders": folders}


@router.post("")
async def create_folder(payload: FolderNameRequest):
    store = get_sqlite_session_store()
    folder = await store.create_folder(payload.name)
    return {"folder": folder}


@router.patch("/{folder_id}")
async def rename_folder(folder_id: str, payload: FolderNameRequest):
    store = get_sqlite_session_store()
    folder = await store.rename_folder(folder_id, payload.name)
    return {"folder": _require_folder(folder)}


@router.post("/{folder_id}/archive")
async def archive_folder(folder_id: str):
    store = get_sqlite_session_store()
    if not await store.archive_folder(folder_id):
        raise HTTPException(status_code=404, detail="Folder not found")
    return {"folder": _require_folder(await store.get_folder(folder_id))}


@router.post("/{folder_id}/restore")
async def restore_folder(folder_id: str):
    store = get_sqlite_session_store()
    if not await store.restore_folder(folder_id):
        raise HTTPException(status_code=404, detail="Folder not found")
    return {"folder": _require_folder(await store.get_folder(folder_id))}


@router.put("/{folder_id}/pin")
async def pin_folder(folder_id: str):
    """Pin an active folder so it stays at the top of the list."""
    store = get_sqlite_session_store()
    try:
        pinned = await store.set_folder_pinned(folder_id, True)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    if not pinned:
        raise HTTPException(status_code=404, detail="Folder not found")
    return {"folder": _require_folder(await store.get_folder(folder_id))}


@router.delete("/{folder_id}/pin")
async def unpin_folder(folder_id: str):
    store = get_sqlite_session_store()
    try:
        pinned = await store.set_folder_pinned(folder_id, False)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    if not pinned:
        raise HTTPException(status_code=404, detail="Folder not found")
    return {"folder": _require_folder(await store.get_folder(folder_id))}


@router.delete("/{folder_id}")
async def delete_folder(
    folder_id: str,
    delete_sessions: bool = Query(default=True),
):
    """Delete an archived folder. ``delete_sessions=true`` (default) also
    deletes its sessions; ``false`` releases them to unassigned."""
    store = get_sqlite_session_store()
    try:
        result = await store.delete_folder(folder_id, delete_sessions=delete_sessions)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    if not result["deleted"]:
        raise HTTPException(status_code=404, detail="Folder not found")
    attachment_store = get_attachment_store()
    for session_id in result["deleted_sessions"]:
        try:
            await attachment_store.delete_session(session_id)
        except Exception:
            logger.exception(
                "failed to clean up attachments for session %s", session_id
            )
    return result


@router.put("/{folder_id}/sessions")
async def move_sessions_to_folder(folder_id: str, payload: FolderMoveRequest):
    """Batch-move sessions into an active folder."""
    store = get_sqlite_session_store()
    try:
        updated = await store.move_sessions(folder_id, payload.session_ids)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return {"updated": updated, "folder_id": folder_id}

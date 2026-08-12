"""Single-user runtime context and workspace access.

This is the replacement boundary for the former multi-user context, grants,
and admin/user workspace selectors. Runtime business code should depend on
this module, not on ``deeptutor.multi_user``.
"""

from __future__ import annotations

from dataclasses import dataclass
from contextlib import contextmanager
from functools import lru_cache
from pathlib import Path
from typing import Any, Literal
from collections.abc import Iterator

from fastapi import HTTPException

from deeptutor.knowledge.manager import KnowledgeBaseManager
from deeptutor.knowledge.manifest import MANIFEST_NOTE_LIMIT, KbManifest, build_manifest
from deeptutor.services.path_service import PathService

DEFAULT_KB_ALIASES = {"", "default", "current", "selected", "默认", "默认知识库", "当前知识库"}


@dataclass(frozen=True, slots=True)
class LocalUserContext:
    id: str = "local"
    username: str = "local"

    @property
    def role(self) -> str:
        return "admin"

    @property
    def is_admin(self) -> bool:
        return True


@dataclass(frozen=True, slots=True)
class LocalKnowledgeResource:
    id: str
    name: str
    base_dir: Path
    source: Literal["admin", "user"] = "admin"
    assigned: bool = False
    read_only: bool = False
    metadata: dict[str, Any] | None = None

    @property
    def physical_name(self) -> str:
        return self.name


@dataclass(frozen=True, slots=True)
class LocalWorkspace:
    path_service: PathService

    @property
    def user_root(self) -> Path:
        return self.path_service.get_user_root()

    @property
    def knowledge_bases_root(self) -> Path:
        return self.path_service.get_knowledge_bases_root()

    @property
    def private_root(self) -> Path:
        path = self.user_root / "private"
        path.mkdir(parents=True, exist_ok=True)
        return path


_LOCAL_USER = LocalUserContext()


def get_local_user() -> LocalUserContext:
    return _LOCAL_USER


def get_local_workspace() -> LocalWorkspace:
    return LocalWorkspace(PathService.get_instance())


@contextmanager
def local_workspace_context() -> Iterator[None]:
    """Compatibility scope for background jobs in the single local workspace."""
    yield


@lru_cache(maxsize=1)
def current_kb_manager() -> KnowledgeBaseManager:
    return KnowledgeBaseManager(base_dir=str(current_kb_base_dir()))


def current_kb_base_dir() -> Path:
    return get_local_workspace().knowledge_bases_root


def _strip_legacy_prefix(value: str) -> str:
    raw = str(value or "").strip()
    for prefix in ("admin:kb:", "user:kb:", "local:kb:"):
        if raw.startswith(prefix):
            return raw[len(prefix) :]
    return raw


def _resolve_name(manager: KnowledgeBaseManager, requested: str) -> str:
    names = manager.list_knowledge_bases()
    if requested and requested in names:
        return requested
    if requested.lower() in DEFAULT_KB_ALIASES:
        default = manager.get_default()
        if default and default in names:
            return default
        raise HTTPException(status_code=404, detail="No default knowledge base is configured")
    raise HTTPException(status_code=404, detail=f"Knowledge base '{requested}' not found")


def resolve_kb(kb_ref: str, *, require_write: bool = False) -> LocalKnowledgeResource:
    del require_write
    name = _resolve_name(current_kb_manager(), _strip_legacy_prefix(kb_ref))
    return LocalKnowledgeResource(
        id=f"local:kb:{name}",
        name=name,
        base_dir=current_kb_base_dir(),
    )


def assert_writable(kb_ref: str) -> LocalKnowledgeResource:
    return resolve_kb(kb_ref, require_write=True)


def manager_for_resource(resource: LocalKnowledgeResource) -> KnowledgeBaseManager:
    return current_kb_manager()


def list_visible_knowledge_bases() -> list[dict[str, Any]]:
    return [
        {
            "id": f"local:kb:{name}",
            "name": name,
            "source": "local",
            "assigned": False,
            "read_only": False,
            "provenance_label": "Local workspace",
        }
        for name in current_kb_manager().list_knowledge_bases()
    ]


def resolve_for_rag(kb_ref: str | None) -> LocalKnowledgeResource | None:
    return resolve_kb(kb_ref) if kb_ref else None


def resolve_kb_metadata(kb_ref: str | None) -> dict[str, Any] | None:
    if not kb_ref:
        return None
    try:
        resource = resolve_kb(kb_ref)
    except HTTPException:
        return None
    return current_kb_manager().get_metadata(resource.name)


def resolve_kb_manifest(
    kb_ref: str | None,
    *,
    limit: int = MANIFEST_NOTE_LIMIT,
    pattern: str = "",
) -> KbManifest | None:
    if not kb_ref:
        return None
    try:
        resource = resolve_kb(kb_ref)
    except HTTPException:
        return None
    entry = current_kb_manager().get_kb_entry(resource.name)
    if entry is None:
        return None
    return build_manifest(
        name=resource.name,
        kb_dir=resource.base_dir / resource.name,
        entry=entry,
        limit=limit,
        pattern=pattern,
    )


__all__ = [
    "LocalKnowledgeResource",
    "LocalUserContext",
    "LocalWorkspace",
    "assert_writable",
    "current_kb_base_dir",
    "current_kb_manager",
    "get_local_user",
    "get_local_workspace",
    "list_visible_knowledge_bases",
    "local_workspace_context",
    "manager_for_resource",
    "resolve_for_rag",
    "resolve_kb",
    "resolve_kb_manifest",
    "resolve_kb_metadata",
]

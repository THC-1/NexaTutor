"""Knowledge-base kind discriminators.

A KB entry's ``type`` field tells the rest of the system how to treat it.
Most KBs are the default *indexed* kind (chunk → embed → retrieve via an RAG
provider) and carry no ``type``. *Connected* KBs are pointers: their content
lives outside ``data/knowledge_bases`` and we never copy or re-index it. These
flavours exist today:

* ``obsidian`` — a pointer (``vault_path``) to a folder of Markdown the user
  owns. No index at all; the Obsidian capability navigates the live files and
  the chat loop routes the KB to that capability instead of ``rag``.
* ``linked`` — a pointer (``external_path``) to a folder that already holds an
  engine index the user built elsewhere.
  Retrieval reads that index in place — the indexing step is skipped, and the
  KB is queried by its bound ``rag_provider`` exactly like an ordinary KB.
* ``subagent`` — a pointer to a connected agent the capability drives live
  through the ``consult_subagent`` tool. ``agent_kind`` names the backend: a
  local CLI (Claude Code / Codex and compatible agents), keyed by an optional
  ``cwd``. It has no path on disk and nothing to index or retrieve. See
  ``capabilities/subagent``.
Legacy ``lightrag_server`` and ``ima`` records are no longer active providers,
but remain data-safety sentinels so discovery never prunes or rewrites a user's
historical connection record.

All connected and inactive legacy flavours share the same lifecycle quirks: no on-disk folder under
``base_dir``, no embedding reconcile, and deletion must never touch the
external resource. The :func:`is_connected_kb` / :func:`external_root_of` helpers
let the manager treat them uniformly without sprinkling ``type`` literals
across the codebase. ``subagent``, legacy ``lightrag_server`` and legacy ``ima``
but point at no folder, so :func:`external_root_of` returns ``None`` for them — a
have no local document folder; none resolves to a local path.

Kept in its own low-level module so both :mod:`deeptutor.knowledge.manager`
and the capability layer can import it without a cycle.
"""

from __future__ import annotations

from typing import Any

# A connected Obsidian vault: a pointer (``vault_path``) to a folder of
# Markdown the user already owns. No index, no embeddings — the Obsidian
# capability navigates the live files. See ``capabilities/obsidian``.
OBSIDIAN_KB_TYPE = "obsidian"

# A linked engine index: a pointer (``external_path``) to a folder that already
# contains a self-contained index built by one of our local providers. We mount
# it in place and retrieve via the bound provider — no copy, no re-index.
LINKED_KB_TYPE = "linked"

# A connected subagent: a pointer to a local agent CLI (Claude Code / Codex).
# No path on disk — ``agent_kind`` names the backend, optional ``cwd`` is the
# working directory. Driven live via ``consult_subagent``; never indexed.
SUBAGENT_KB_TYPE = "subagent"

# Retained pointer types still available to create and use.
RETAINED_CONNECTED_KB_TYPES = frozenset(
    {OBSIDIAN_KB_TYPE, LINKED_KB_TYPE, SUBAGENT_KB_TYPE}
)

# Removed remote providers remain here only to preserve historical config. They
# are not registered, routable, or constructible and must never be contacted.
LEGACY_INACTIVE_KB_TYPES = frozenset({"lightrag_server", "ima"})

# Membership makes manager discovery skip index reconciliation and orphan
# pruning. It is deliberately broader than the set of active connected types.
CONNECTED_KB_TYPES = RETAINED_CONNECTED_KB_TYPES | LEGACY_INACTIVE_KB_TYPES


def is_connected_kb(entry: Any) -> bool:
    """True for pointer KBs whose data lives outside ``data/knowledge_bases``."""
    return isinstance(entry, dict) and entry.get("type") in CONNECTED_KB_TYPES


def external_root_of(entry: Any) -> str | None:
    """Absolute path a connected KB points at, or ``None`` for ordinary KBs.

    ``linked`` KBs store it under ``external_path``; ``obsidian`` vaults under
    the older ``vault_path`` field. One accessor so callers don't care which.
    """
    if not isinstance(entry, dict):
        return None
    return entry.get("external_path") or entry.get("vault_path")


__all__ = [
    "OBSIDIAN_KB_TYPE",
    "LINKED_KB_TYPE",
    "SUBAGENT_KB_TYPE",
    "RETAINED_CONNECTED_KB_TYPES",
    "LEGACY_INACTIVE_KB_TYPES",
    "CONNECTED_KB_TYPES",
    "is_connected_kb",
    "external_root_of",
]

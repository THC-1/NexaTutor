"use client";

import {
  Archive,
  Check,
  ChevronDown,
  ChevronRight,
  Folder,
  FolderMinus,
  FolderPlus,
  Inbox,
  ListChecks,
  Pencil,
  Pin,
  PinOff,
  Plus,
  Trash2,
  Undo2,
  X,
  type LucideIcon,
} from "lucide-react";
import { useMemo, useState } from "react";
import { useTranslation } from "react-i18next";
import {
  type SessionFolder,
  type SessionSummary,
} from "@/lib/session-api";
import { normalizeMessageContent, truncateText } from "@/lib/message-content";
import { SessionAvatar } from "@/components/sidebar/SessionAvatar";
import {
  formatRelativeTime,
  getDayGroupKey,
  type DayGroupKey,
} from "@/lib/relative-time";
import { isPlaceholderSessionTitle } from "@/lib/session-title";

type SessionRuntimeStatus =
  | "idle"
  | "running"
  | "completed"
  | "failed"
  | "cancelled"
  | "rejected";

interface SessionListProps {
  sessions: SessionSummary[];
  /** When provided, the list renders folder groups (active folders, the
   *  unassigned bucket, and an archived section) instead of day groups. */
  folders?: SessionFolder[];
  activeSessionId: string | null;
  loading?: boolean;
  compact?: boolean;
  onSelect: (sessionId: string) => void | Promise<void>;
  onRename: (sessionId: string, title: string) => void | Promise<void>;
  onDelete: (sessionId: string) => void | Promise<void>;
  onCreateFolder?: (name: string) => void | Promise<void>;
  onRenameFolder?: (folderId: string, name: string) => void | Promise<void>;
  onArchiveFolder?: (folderId: string) => void | Promise<void>;
  onRestoreFolder?: (folderId: string) => void | Promise<void>;
  onDeleteFolder?: (folderId: string) => void | Promise<void>;
  /** Pin/unpin an active folder (component picks the direction from the
   *  folder's current `pinned` state). */
  onPinFolder?: (folderId: string) => void | Promise<void>;
  /** Move a session to a folder; `folderId: ""` = unassigned (also the
   *  individual recovery path for sessions inside archived folders). */
  onMoveSession?: (sessionId: string, folderId: string) => void | Promise<void>;
  /** Batch-move several sessions at once (multi-select mode). */
  onBatchMove?: (
    sessionIds: string[],
    folderId: string,
  ) => void | Promise<void>;
}

function StatusIndicator({ status }: { status?: SessionRuntimeStatus }) {
  if (!status || status === "idle") return null;

  if (status === "running") {
    return (
      <span className="relative ml-1.5 inline-flex shrink-0">
        <span className="session-pulse absolute inline-flex h-2 w-2 rounded-full bg-blue-400/60" />
        <span className="relative inline-flex h-2 w-2 rounded-full bg-blue-500" />
      </span>
    );
  }

  if (status === "completed") {
    return (
      <span className="ml-1.5 inline-flex h-2 w-2 shrink-0 rounded-full bg-emerald-400/50 ring-1 ring-emerald-400/10" />
    );
  }

  if (status === "failed") {
    return (
      <span className="ml-1.5 inline-flex h-2 w-2 shrink-0 rounded-full bg-rose-500/80 ring-1 ring-rose-500/20" />
    );
  }

  if (status === "rejected") {
    return (
      <span className="ml-1.5 inline-flex h-2 w-2 shrink-0 rounded-full bg-fuchsia-500/80 ring-1 ring-fuchsia-500/20" />
    );
  }

  if (status === "cancelled") {
    return (
      <span className="ml-1.5 inline-flex h-2 w-2 shrink-0 rounded-full bg-amber-500/70 ring-1 ring-amber-500/20" />
    );
  }

  return null;
}

/** Sessions whose folder_id points at a folder we don't know about (stale
 *  refs) land in the unassigned bucket so nothing disappears from the list. */
function groupByFolder(
  sessions: SessionSummary[],
  folders: SessionFolder[],
): {
  activeGroups: Array<{ folder: SessionFolder; items: SessionSummary[] }>;
  archivedGroups: Array<{ folder: SessionFolder; items: SessionSummary[] }>;
  unassigned: SessionSummary[];
} {
  const active: Array<{ folder: SessionFolder; items: SessionSummary[] }> = [];
  const archived: Array<{ folder: SessionFolder; items: SessionSummary[] }> =
    [];
  const known = new Map<
    string,
    Array<{ folder: SessionFolder; items: SessionSummary[] }>
  >();
  const unassigned: SessionSummary[] = [];

  for (const folder of folders) {
    const group = { folder, items: [] as SessionSummary[] };
    if (folder.status === "archived") archived.push(group);
    else active.push(group);
    const list = known.get(folder.id) ?? [];
    list.push(group);
    known.set(folder.id, list);
  }

  for (const session of sessions) {
    const folderId = session.folder_id ?? "";
    const groups = folderId ? (known.get(folderId) ?? []) : [];
    if (groups.length > 0) groups[0].items.push(session);
    else unassigned.push(session);
  }

  return { activeGroups: active, archivedGroups: archived, unassigned };
}

export default function SessionList({
  sessions,
  folders,
  activeSessionId,
  loading = false,
  compact = false,
  onSelect,
  onRename,
  onDelete,
  onCreateFolder,
  onRenameFolder,
  onArchiveFolder,
  onRestoreFolder,
  onDeleteFolder,
  onPinFolder,
  onMoveSession,
  onBatchMove,
}: SessionListProps) {
  const { t, i18n } = useTranslation();
  const [editingId, setEditingId] = useState<string | null>(null);
  const [draftTitle, setDraftTitle] = useState("");
  const [creatingFolder, setCreatingFolder] = useState(false);
  const [folderDraft, setFolderDraft] = useState("");
  const [renamingFolderId, setRenamingFolderId] = useState<string | null>(null);
  const [folderNameDraft, setFolderNameDraft] = useState("");
  const [collapsedFolderIds, setCollapsedFolderIds] = useState<Set<string>>(
    () => new Set(),
  );
  const [archivedCollapsed, setArchivedCollapsed] = useState(false);
  const [unassignedCollapsed, setUnassignedCollapsed] = useState(false);
  const [moveMenuSessionId, setMoveMenuSessionId] = useState<string | null>(
    null,
  );
  // HTML5 drag & drop: the session being dragged and the folder header
  // currently hovered as a drop target ("" = the unassigned header).
  const [draggingSessionId, setDraggingSessionId] = useState<string | null>(
    null,
  );
  const [dragOverTarget, setDragOverTarget] = useState<string | null>(null);
  // Multi-select mode: rows toggle selection instead of navigating.
  const [selectMode, setSelectMode] = useState(false);
  const [selectedIds, setSelectedIds] = useState<Set<string>>(() => new Set());
  const [batchMoveMenuOpen, setBatchMoveMenuOpen] = useState(false);

  const folderUiEnabled = folders !== undefined;

  const groups = useMemo(() => {
    if (!folderUiEnabled || !folders) return null;
    const grouped = groupByFolder(sessions, folders);
    // Pinned folders stay at the top; within each tier the backend order
    // (creation order) is preserved. Stable sort keeps local updates in sync.
    grouped.activeGroups.sort(
      (a, b) => (b.folder.pinned ?? 0) - (a.folder.pinned ?? 0),
    );
    return grouped;
  }, [folderUiEnabled, folders, sessions]);

  // The sentinel the backend writes when a session is created and not
  // yet renamed by the LLM title generator. We swap it for a localized
  // "New chat" string with a breathing animation so the sidebar shows
  // something "alive" while the title is being generated in the
  // background instead of a literal English sentinel.
  const placeholderLabel = t("New chat");

  // The group-key tokens stay stable; only the translated labels change.
  const groupLabels = useMemo<Record<DayGroupKey, string>>(
    () => ({
      today: t("Today"),
      yesterday: t("Yesterday"),
      last_7_days: t("Last 7 days"),
      earlier: t("Earlier"),
    }),
    [t],
  );

  const dayGrouped = useMemo(() => {
    const buckets = new Map<DayGroupKey, SessionSummary[]>();
    for (const session of sessions) {
      const key = getDayGroupKey(session.updated_at);
      const current = buckets.get(key) ?? [];
      current.push(session);
      buckets.set(key, current);
    }
    return Array.from(buckets.entries());
  }, [sessions]);

  const startEdit = (session: SessionSummary) => {
    setEditingId(session.session_id);
    setDraftTitle(session.title);
  };

  const commitEdit = async () => {
    if (!editingId) return;
    const nextTitle = draftTitle.trim();
    if (!nextTitle) {
      setEditingId(null);
      setDraftTitle("");
      return;
    }
    await onRename(editingId, nextTitle);
    setEditingId(null);
    setDraftTitle("");
  };

  const commitCreateFolder = async () => {
    const name = folderDraft.trim();
    setCreatingFolder(false);
    setFolderDraft("");
    if (!name || !onCreateFolder) return;
    await onCreateFolder(name);
  };

  const commitRenameFolder = async (folderId: string) => {
    const name = folderNameDraft.trim();
    setRenamingFolderId(null);
    setFolderNameDraft("");
    if (!name || !onRenameFolder) return;
    await onRenameFolder(folderId, name);
  };

  const toggleFolderCollapsed = (folderId: string) => {
    setCollapsedFolderIds((prev) => {
      const next = new Set(prev);
      if (next.has(folderId)) next.delete(folderId);
      else next.add(folderId);
      return next;
    });
  };

  const closeMoveMenu = () => setMoveMenuSessionId(null);

  // ── HTML5 drag & drop helpers ────────────────────────────────────
  const handleDragStart = (event: React.DragEvent, sessionId: string) => {
    event.dataTransfer.setData("application/x-session-id", sessionId);
    event.dataTransfer.effectAllowed = "move";
    setDraggingSessionId(sessionId);
  };

  const handleDragEnd = () => {
    setDraggingSessionId(null);
    setDragOverTarget(null);
  };

  const handleDropTargetDragOver = (
    event: React.DragEvent,
    target: string,
  ) => {
    if (!draggingSessionId) return;
    event.preventDefault();
    event.dataTransfer.dropEffect = "move";
    setDragOverTarget(target);
  };

  const handleDropTargetDragLeave = (
    event: React.DragEvent,
    target: string,
  ) => {
    // Dragging over children fires dragleave with the child as relatedTarget;
    // ignore those so the highlight only clears when leaving the header.
    if (event.currentTarget.contains(event.relatedTarget as Node)) return;
    setDragOverTarget((prev) => (prev === target ? null : prev));
  };

  const handleDropOnTarget = (event: React.DragEvent, target: string) => {
    event.preventDefault();
    setDragOverTarget(null);
    const sessionId = event.dataTransfer.getData("application/x-session-id");
    if (!sessionId || !onMoveSession) return;
    void onMoveSession(sessionId, target);
  };

  // ── Multi-select helpers ─────────────────────────────────────────
  const enterSelectMode = () => {
    setSelectMode(true);
    setSelectedIds(new Set());
  };

  const exitSelectMode = () => {
    setSelectMode(false);
    setSelectedIds(new Set());
    setBatchMoveMenuOpen(false);
  };

  const toggleSelected = (sessionId: string) => {
    setSelectedIds((prev) => {
      const next = new Set(prev);
      if (next.has(sessionId)) next.delete(sessionId);
      else next.add(sessionId);
      return next;
    });
  };

  if (loading) {
    if (compact) {
      return (
        <div className="space-y-1.5 px-2 py-1">
          {[1, 2, 3].map((i) => (
            <div
              key={i}
              className="h-4 w-3/4 animate-pulse rounded bg-[var(--muted)]/40"
            />
          ))}
        </div>
      );
    }
    return (
      <div className="space-y-2 px-1.5 py-2">
        {[1, 2, 3].map((i) => (
          <div
            key={i}
            className="h-10 animate-pulse rounded-md bg-[var(--muted)]/60"
          />
        ))}
      </div>
    );
  }

  if (sessions.length === 0 && !folderUiEnabled) {
    return (
      <div className="px-3 py-4 text-center text-[11px] text-[var(--muted-foreground)]/70">
        {t("No conversations yet")}
      </div>
    );
  }

  /* ================================================================
   * Folder-organized mode (sidebar + space, when folders are passed)
   * ================================================================ */
  if (folderUiEnabled && groups) {
    const { activeGroups, archivedGroups, unassigned } = groups;
    const renderSessionRow = (
      session: SessionSummary,
      inArchivedFolder: boolean,
    ) => {
      const active = activeSessionId === session.session_id;
      const isEditing = editingId === session.session_id;
      const moveMenuOpen = moveMenuSessionId === session.session_id;
      const selected = selectedIds.has(session.session_id);
      const rowClick = () => {
        if (selectMode) {
          toggleSelected(session.session_id);
          return;
        }
        void onSelect(session.session_id);
      };
      return (
        <div
          key={session.session_id}
          onClick={rowClick}
          onKeyDown={(event) => {
            if (event.key === "Enter" || event.key === " ") {
              event.preventDefault();
              rowClick();
            }
          }}
          role="button"
          tabIndex={0}
          draggable={!selectMode && !!onMoveSession}
          onDragStart={
            !selectMode && onMoveSession
              ? (event) => handleDragStart(event, session.session_id)
              : undefined
          }
          onDragEnd={handleDragEnd}
          className={`group relative flex items-center gap-2 rounded-lg px-2.5 py-1.5 transition-colors ${
            selectMode
              ? selected
                ? "bg-[var(--primary)]/15 text-[var(--foreground)]"
                : "text-[var(--muted-foreground)] hover:bg-[var(--background)]/40"
              : active
                ? "bg-[var(--background)]/50 text-[var(--foreground)]"
                : "text-[var(--muted-foreground)] hover:bg-[var(--background)]/40 hover:text-[var(--foreground)]"
          } ${draggingSessionId === session.session_id ? "opacity-50" : ""}`}
        >
          {selectMode ? (
            <span
              role="checkbox"
              aria-checked={selected}
              aria-label={t("Select")}
              className={`flex h-4 w-4 shrink-0 items-center justify-center rounded border transition-colors ${
                selected
                  ? "border-[var(--primary)] bg-[var(--primary)] text-white"
                  : "border-[var(--border)] text-transparent"
              }`}
            >
              <Check size={10} strokeWidth={3} />
            </span>
          ) : null}
          <SessionAvatar
            sessionId={session.session_id}
            running={session.status === "running"}
            className={
              session.status === "running" ? "text-blue-500" : "opacity-70"
            }
          />
          {isEditing ? (
            <input
              value={draftTitle}
              autoFocus
              onChange={(event) => setDraftTitle(event.target.value)}
              onBlur={() => void commitEdit()}
              onKeyDown={(event) => {
                if (event.key === "Enter") void commitEdit();
                if (event.key === "Escape") {
                  setEditingId(null);
                  setDraftTitle("");
                }
              }}
              onClick={(event) => event.stopPropagation()}
              className="min-w-0 flex-1 rounded border border-[var(--border)] bg-[var(--background)] px-1.5 py-px text-[12px] text-[var(--foreground)] outline-none focus:ring-1 focus:ring-[var(--primary)]/40"
            />
          ) : isPlaceholderSessionTitle(session.title) ? (
            <span
              className={`dt-breathing-text min-w-0 flex-1 truncate text-[13px] italic text-[var(--muted-foreground)] ${
                active ? "font-medium" : ""
              }`}
            >
              {placeholderLabel}
            </span>
          ) : (
            <span
              className={`min-w-0 flex-1 truncate text-[13px] ${
                active ? "font-medium" : ""
              }`}
            >
              {session.title}
            </span>
          )}
          {!selectMode ? (
            <div className="flex shrink-0 items-center gap-px opacity-0 transition-opacity group-hover:opacity-100">
              {isEditing ? (
                <button
                  onClick={(event) => {
                    event.stopPropagation();
                    void commitEdit();
                  }}
                  className="rounded p-0.5 text-[var(--muted-foreground)] hover:text-[var(--foreground)]"
                  aria-label={t("Save title")}
                >
                  <Check size={10} />
                </button>
              ) : (
                <button
                  onClick={(event) => {
                    event.stopPropagation();
                    startEdit(session);
                  }}
                  className="rounded p-0.5 text-[var(--muted-foreground)] hover:text-[var(--foreground)]"
                  aria-label={t("Rename chat")}
                >
                  <Pencil size={10} />
                </button>
              )}
              {inArchivedFolder && onMoveSession ? (
                <button
                  onClick={(event) => {
                    event.stopPropagation();
                    void onMoveSession(session.session_id, "");
                  }}
                  className="rounded p-0.5 text-[var(--muted-foreground)] hover:text-[var(--primary)]"
                  aria-label={t("Recover session")}
                  title={t("Recover session")}
                >
                  <Undo2 size={10} />
                </button>
              ) : null}
              {!inArchivedFolder && session.folder_id && onMoveSession ? (
                <button
                  onClick={(event) => {
                    event.stopPropagation();
                    void onMoveSession(session.session_id, "");
                  }}
                  className="rounded p-0.5 text-[var(--muted-foreground)] hover:text-[var(--primary)]"
                  aria-label={t("Remove from folder")}
                  title={t("Remove from folder")}
                >
                  <FolderMinus size={10} />
                </button>
              ) : null}
              {onMoveSession ? (
                <button
                  onClick={(event) => {
                    event.stopPropagation();
                    setMoveMenuSessionId(
                      moveMenuOpen ? null : session.session_id,
                    );
                  }}
                  className="rounded p-0.5 text-[var(--muted-foreground)] hover:text-[var(--foreground)]"
                  aria-label={t("Move to folder")}
                  title={t("Move to folder")}
                >
                  <FolderPlus size={10} />
                </button>
              ) : null}
              <button
                onClick={(event) => {
                  event.stopPropagation();
                  void onDelete(session.session_id);
                }}
                className="rounded p-0.5 text-[var(--muted-foreground)] hover:text-[var(--destructive)]"
                aria-label={t("Delete chat")}
              >
                <Trash2 size={10} />
              </button>
            </div>
          ) : null}
          {moveMenuOpen && onMoveSession ? (
            <>
              <div
                className="fixed inset-0 z-20"
                onClick={(event) => {
                  event.stopPropagation();
                  closeMoveMenu();
                }}
              />
              <MoveFolderMenu
                folders={folders ?? []}
                currentFolderId={session.folder_id}
                onPick={(folderId) => {
                  closeMoveMenu();
                  void onMoveSession(session.session_id, folderId);
                }}
              />
            </>
          ) : null}
        </div>
      );
    };

    const renderFolderHeader = (
      folder: SessionFolder,
      archived: boolean,
    ) => {
      const collapsed = collapsedFolderIds.has(folder.id);
      const renaming = renamingFolderId === folder.id;
      // Active folder headers are drop targets for dragged sessions; the
      // archived section never is (sessions cannot move into archives).
      const dropTarget = !archived && !!onMoveSession;
      const dropHovered = dropTarget && dragOverTarget === folder.id;
      return (
        <div
          className={`group/folder flex items-center gap-1 rounded-md px-1.5 py-1 text-[var(--muted-foreground)] hover:bg-[var(--background)]/40 ${
            dropHovered
              ? "bg-[var(--primary)]/15 ring-1 ring-[var(--primary)]/40"
              : ""
          }`}
          role="button"
          tabIndex={0}
          onClick={() => toggleFolderCollapsed(folder.id)}
          onKeyDown={(event) => {
            if (event.key === "Enter" || event.key === " ") {
              event.preventDefault();
              toggleFolderCollapsed(folder.id);
            }
          }}
          onDragOver={
            dropTarget
              ? (event) => handleDropTargetDragOver(event, folder.id)
              : undefined
          }
          onDragLeave={
            dropTarget
              ? (event) => handleDropTargetDragLeave(event, folder.id)
              : undefined
          }
          onDrop={
            dropTarget
              ? (event) => handleDropOnTarget(event, folder.id)
              : undefined
          }
        >
          {renaming ? (
            <input
              value={folderNameDraft}
              autoFocus
              onChange={(event) => setFolderNameDraft(event.target.value)}
              onClick={(event) => event.stopPropagation()}
              onBlur={() => void commitRenameFolder(folder.id)}
              onKeyDown={(event) => {
                if (event.key === "Enter") void commitRenameFolder(folder.id);
                if (event.key === "Escape") {
                  setRenamingFolderId(null);
                  setFolderNameDraft("");
                }
              }}
              className="min-w-0 flex-1 rounded border border-[var(--border)] bg-[var(--background)] px-1.5 py-px text-[12px] text-[var(--foreground)] outline-none focus:ring-1 focus:ring-[var(--primary)]/40"
            />
          ) : (
            <>
              {collapsed ? (
                <ChevronRight size={12} className="shrink-0" />
              ) : (
                <ChevronDown size={12} className="shrink-0" />
              )}
              {archived ? (
                <Archive size={12} className="shrink-0 opacity-80" />
              ) : (
                <Folder size={12} className="shrink-0 opacity-80" />
              )}
              <span className="min-w-0 flex-1 truncate text-[12px] font-medium">
                {folder.name}
              </span>
              <span className="shrink-0 text-[10px] opacity-70">
                {folder.session_count}
              </span>
              <div className="flex shrink-0 items-center gap-px opacity-0 transition-opacity group-hover/folder:opacity-100">
                {onRenameFolder && !archived ? (
                  <button
                    onClick={(event) => {
                      event.stopPropagation();
                      setRenamingFolderId(folder.id);
                      setFolderNameDraft(folder.name);
                    }}
                    className="rounded p-0.5 hover:text-[var(--foreground)]"
                    aria-label={t("Rename folder")}
                    title={t("Rename folder")}
                  >
                    <Pencil size={10} />
                  </button>
                ) : null}
                {onPinFolder && !archived ? (
                  <button
                    onClick={(event) => {
                      event.stopPropagation();
                      void onPinFolder(folder.id);
                    }}
                    className={`rounded p-0.5 hover:text-[var(--foreground)] ${
                      folder.pinned
                        ? "text-[var(--primary)]"
                        : "text-[var(--muted-foreground)]"
                    }`}
                    aria-label={
                      folder.pinned ? t("Unpin folder") : t("Pin folder")
                    }
                    title={folder.pinned ? t("Unpin folder") : t("Pin folder")}
                  >
                    {folder.pinned ? (
                      <PinOff size={10} />
                    ) : (
                      <Pin size={10} />
                    )}
                  </button>
                ) : null}
                {onArchiveFolder && !archived ? (
                  <button
                    onClick={(event) => {
                      event.stopPropagation();
                      void onArchiveFolder(folder.id);
                    }}
                    className="rounded p-0.5 hover:text-[var(--foreground)]"
                    aria-label={t("Archive folder")}
                    title={t("Archive folder")}
                  >
                    <Archive size={10} />
                  </button>
                ) : null}
                {onRestoreFolder && archived ? (
                  <button
                    onClick={(event) => {
                      event.stopPropagation();
                      void onRestoreFolder(folder.id);
                    }}
                    className="rounded p-0.5 hover:text-[var(--foreground)]"
                    aria-label={t("Restore folder")}
                    title={t("Restore folder")}
                  >
                    <Undo2 size={10} />
                  </button>
                ) : null}
                {onDeleteFolder && archived ? (
                  <button
                    onClick={(event) => {
                      event.stopPropagation();
                      void onDeleteFolder(folder.id);
                    }}
                    className="rounded p-0.5 hover:text-[var(--destructive)]"
                    aria-label={t("Delete folder")}
                    title={t("Delete folder")}
                  >
                    <Trash2 size={10} />
                  </button>
                ) : null}
              </div>
            </>
          )}
        </div>
      );
    };

    const renderGroupHeader = (
      icon: LucideIcon,
      label: string,
      count: number,
      options?: {
        collapsed?: boolean;
        onToggle?: () => void;
        /** When set, the header is a drop target for dragged sessions;
         *  the string is the folder id to move into ("" = unassigned). */
        dropTarget?: string | null;
        onDragOver?: (event: React.DragEvent) => void;
        onDragLeave?: (event: React.DragEvent) => void;
        onDrop?: (event: React.DragEvent) => void;
      },
    ) => {
      const Icon = icon;
      const { collapsed, onToggle, dropTarget, onDragOver, onDragLeave, onDrop } =
        options ?? {};
      const dropHovered =
        dropTarget !== undefined &&
        dropTarget !== null &&
        draggingSessionId !== null &&
        dragOverTarget === dropTarget;
      const content = (
        <>
          {onToggle ? (
            collapsed ? (
              <ChevronRight size={12} className="shrink-0" />
            ) : (
              <ChevronDown size={12} className="shrink-0" />
            )
          ) : null}
          <Icon size={12} strokeWidth={1.8} />
          <span className="min-w-0 flex-1 truncate">{label}</span>
          <span className="shrink-0 text-[10px] font-normal opacity-70">
            {count}
          </span>
        </>
      );
      const dropClasses = dropHovered
        ? "bg-[var(--primary)]/15 ring-1 ring-[var(--primary)]/40"
        : "";
      if (onToggle) {
        return (
          <button
            type="button"
            onClick={onToggle}
            className={`flex w-full items-center gap-1.5 rounded-md px-2 py-1 text-left text-[11px] font-semibold uppercase tracking-widest text-[var(--muted-foreground)]/80 transition-colors hover:bg-[var(--background)]/40 hover:text-[var(--muted-foreground)] ${dropClasses}`}
            aria-expanded={!collapsed}
            onDragOver={onDragOver}
            onDragLeave={onDragLeave}
            onDrop={onDrop}
          >
            {content}
          </button>
        );
      }
      return (
        <div
          className={`flex items-center gap-1.5 px-2 py-1 text-[11px] font-semibold uppercase tracking-widest text-[var(--muted-foreground)]/80 ${dropClasses}`}
          onDragOver={onDragOver}
          onDragLeave={onDragLeave}
          onDrop={onDrop}
        >
          {content}
        </div>
      );
    };

    return (
      <div className="space-y-1 py-0.5">
        {selectMode ? (
          <div className="relative mx-1.5 mb-1 flex items-center gap-1.5 rounded-md border border-[var(--border)] bg-[var(--background)] px-2 py-1.5">
            <span className="min-w-0 flex-1 truncate text-[11.5px] text-[var(--muted-foreground)]">
              {t("{{count}} selected", { count: selectedIds.size })}
            </span>
            <button
              type="button"
              onClick={() => setBatchMoveMenuOpen((prev) => !prev)}
              disabled={selectedIds.size === 0}
              className="inline-flex shrink-0 items-center gap-1 rounded-md border border-[var(--border)] px-1.5 py-0.5 text-[11px] text-[var(--muted-foreground)] transition-colors hover:text-[var(--foreground)] disabled:cursor-not-allowed disabled:opacity-40"
            >
              <FolderPlus size={11} />
              <span>{t("Move to folder")}</span>
            </button>
            <button
              type="button"
              onClick={exitSelectMode}
              className="shrink-0 rounded p-0.5 text-[var(--muted-foreground)] hover:text-[var(--foreground)]"
              aria-label={t("Cancel")}
              title={t("Cancel")}
            >
              <X size={12} />
            </button>
            {batchMoveMenuOpen ? (
              <>
                <div
                  className="fixed inset-0 z-20"
                  onClick={(event) => {
                    event.stopPropagation();
                    setBatchMoveMenuOpen(false);
                  }}
                />
                <MoveFolderMenu
                  folders={folders ?? []}
                  onPick={(folderId) => {
                    setBatchMoveMenuOpen(false);
                    const ids = Array.from(selectedIds);
                    exitSelectMode();
                    if (ids.length > 0 && onBatchMove) {
                      void onBatchMove(ids, folderId);
                    }
                  }}
                />
              </>
            ) : null}
          </div>
        ) : (
          <div className="flex items-center gap-1 px-1.5 pb-1">
            {onCreateFolder ? (
              <div className="min-w-0 flex-1">
                {creatingFolder ? (
                  <div className="flex items-center gap-1 rounded-md border border-[var(--border)] bg-[var(--background)] px-1.5 py-1">
                    <Folder size={12} className="shrink-0 opacity-70" />
                    <input
                      value={folderDraft}
                      autoFocus
                      placeholder={t("Folder name")}
                      onChange={(event) => setFolderDraft(event.target.value)}
                      onBlur={() => void commitCreateFolder()}
                      onKeyDown={(event) => {
                        if (event.key === "Enter") void commitCreateFolder();
                        if (event.key === "Escape") {
                          setCreatingFolder(false);
                          setFolderDraft("");
                        }
                      }}
                      className="min-w-0 flex-1 bg-transparent text-[12px] text-[var(--foreground)] outline-none placeholder:text-[var(--muted-foreground)]/50"
                    />
                  </div>
                ) : (
                  <button
                    onClick={() => {
                      setCreatingFolder(true);
                      setFolderDraft("");
                    }}
                    className="flex w-full items-center gap-1.5 rounded-md px-2 py-1 text-[11.5px] text-[var(--muted-foreground)]/80 transition-colors hover:bg-[var(--background)]/40 hover:text-[var(--foreground)]"
                  >
                    <Plus size={12} />
                    <span>{t("New folder")}</span>
                  </button>
                )}
              </div>
            ) : null}
            {onBatchMove ? (
              <button
                type="button"
                onClick={enterSelectMode}
                className="flex shrink-0 items-center gap-1.5 rounded-md px-2 py-1 text-[11.5px] text-[var(--muted-foreground)]/80 transition-colors hover:bg-[var(--background)]/40 hover:text-[var(--foreground)]"
                aria-label={t("Batch select")}
                title={t("Batch select")}
              >
                <ListChecks size={12} />
                <span>{t("Batch select")}</span>
              </button>
            ) : null}
          </div>
        )}

        {activeGroups.length === 0 && unassigned.length === 0 ? (
          <div className="px-3 py-3 text-center text-[11px] text-[var(--muted-foreground)]/70">
            {t("No conversations yet")}
          </div>
        ) : (
          <>
            {activeGroups.map(({ folder, items }) => (
              <div key={folder.id}>
                {renderFolderHeader(folder, false)}
                {!collapsedFolderIds.has(folder.id) ? (
                  <div className="space-y-0.5 pl-1.5">
                    {items.map((session) => renderSessionRow(session, false))}
                  </div>
                ) : null}
              </div>
            ))}
            <div className="pt-1">
              {renderGroupHeader(Inbox, t("Unassigned"), unassigned.length, {
                collapsed: unassignedCollapsed,
                onToggle: () => setUnassignedCollapsed((prev) => !prev),
                dropTarget: onMoveSession ? "" : null,
                onDragOver: onMoveSession
                  ? (event) => handleDropTargetDragOver(event, "")
                  : undefined,
                onDragLeave: onMoveSession
                  ? (event) => handleDropTargetDragLeave(event, "")
                  : undefined,
                onDrop: onMoveSession
                  ? (event) => handleDropOnTarget(event, "")
                  : undefined,
              })}
              {!unassignedCollapsed ? (
                <div className="space-y-0.5 pl-1.5">
                  {unassigned.map((session) =>
                    renderSessionRow(session, false),
                  )}
                </div>
              ) : null}
            </div>
          </>
        )}

        {archivedGroups.length > 0 ? (
          <div className="mt-2 border-t border-[var(--border)]/40 pt-1.5">
            <button
              onClick={() => setArchivedCollapsed((prev) => !prev)}
              className="flex w-full items-center gap-1.5 rounded-md px-2 py-1 text-left text-[11px] font-semibold uppercase tracking-widest text-[var(--muted-foreground)]/80 transition-colors hover:bg-[var(--background)]/40 hover:text-[var(--muted-foreground)]"
              aria-expanded={!archivedCollapsed}
            >
              {archivedCollapsed ? (
                <ChevronRight size={12} />
              ) : (
                <ChevronDown size={12} />
              )}
              <Archive size={12} strokeWidth={1.8} />
              <span className="min-w-0 flex-1 truncate">{t("Archived")}</span>
              <span className="shrink-0 text-[10px] font-normal opacity-70">
                {archivedGroups.length}
              </span>
            </button>
            {!archivedCollapsed ? (
              <div className="mt-1 space-y-0.5 pl-1.5">
                {archivedGroups.map(({ folder, items }) => (
                  <div key={folder.id}>
                    {renderFolderHeader(folder, true)}
                    <div className="space-y-0.5 pl-1.5">
                      {items.map((session) =>
                        renderSessionRow(session, true),
                      )}
                    </div>
                  </div>
                ))}
              </div>
            ) : null}
          </div>
        ) : null}
      </div>
    );
  }

  /* ---- Compact sidebar style (standalone chat history region) ---- */
  if (compact) {
    return (
      <div className="py-0.5">
        {sessions.map((session) => {
          const active = activeSessionId === session.session_id;
          const isEditing = editingId === session.session_id;
          return (
            <div
              key={session.session_id}
              onClick={() => void onSelect(session.session_id)}
              onKeyDown={(event) => {
                if (event.key === "Enter" || event.key === " ") {
                  event.preventDefault();
                  void onSelect(session.session_id);
                }
              }}
              role="button"
              tabIndex={0}
              className={`group flex items-center gap-2 rounded-lg px-2.5 py-1.5 transition-colors ${
                active
                  ? "bg-[var(--background)]/50 text-[var(--foreground)]"
                  : "text-[var(--muted-foreground)] hover:bg-[var(--background)]/40 hover:text-[var(--foreground)]"
              }`}
            >
              <SessionAvatar
                sessionId={session.session_id}
                running={session.status === "running"}
                className={
                  session.status === "running" ? "text-blue-500" : "opacity-70"
                }
              />
              {isEditing ? (
                <input
                  value={draftTitle}
                  autoFocus
                  onChange={(event) => setDraftTitle(event.target.value)}
                  onBlur={() => void commitEdit()}
                  onKeyDown={(event) => {
                    if (event.key === "Enter") void commitEdit();
                    if (event.key === "Escape") {
                      setEditingId(null);
                      setDraftTitle("");
                    }
                  }}
                  onClick={(event) => event.stopPropagation()}
                  className="min-w-0 flex-1 rounded border border-[var(--border)] bg-[var(--background)] px-1.5 py-px text-[12px] text-[var(--foreground)] outline-none focus:ring-1 focus:ring-[var(--primary)]/40"
                />
              ) : isPlaceholderSessionTitle(session.title) ? (
                <span
                  className={`dt-breathing-text min-w-0 flex-1 truncate text-[13px] italic text-[var(--muted-foreground)] ${active ? "font-medium" : ""}`}
                >
                  {placeholderLabel}
                </span>
              ) : (
                <span
                  className={`min-w-0 flex-1 truncate text-[13px] ${active ? "font-medium" : ""}`}
                >
                  {session.title}
                </span>
              )}
              <div className="flex shrink-0 items-center gap-px opacity-0 transition-opacity group-hover:opacity-100">
                {isEditing ? (
                  <button
                    onClick={(event) => {
                      event.stopPropagation();
                      void commitEdit();
                    }}
                    className="rounded p-0.5 text-[var(--muted-foreground)] hover:text-[var(--foreground)]"
                    aria-label={t("Save title")}
                  >
                    <Check size={10} />
                  </button>
                ) : (
                  <button
                    onClick={(event) => {
                      event.stopPropagation();
                      startEdit(session);
                    }}
                    className="rounded p-0.5 text-[var(--muted-foreground)] hover:text-[var(--foreground)]"
                    aria-label={t("Rename chat")}
                  >
                    <Pencil size={10} />
                  </button>
                )}
                <button
                  onClick={(event) => {
                    event.stopPropagation();
                    void onDelete(session.session_id);
                  }}
                  className="rounded p-0.5 text-[var(--muted-foreground)] hover:text-[var(--destructive)]"
                  aria-label={t("Delete chat")}
                >
                  <Trash2 size={10} />
                </button>
              </div>
            </div>
          );
        })}
      </div>
    );
  }

  /* ---- Classic style ---- */
  return (
    <div className="space-y-4">
      {dayGrouped.map(([key, items]) => (
        <div key={key}>
          <div className="mb-1.5 px-2 text-[11px] font-semibold uppercase tracking-widest text-[var(--muted-foreground)]">
            {groupLabels[key]}
          </div>
          <div className="divide-y divide-[var(--border)]/45 overflow-hidden rounded-lg border border-[var(--border)]/45 bg-[var(--card)]/50">
            {items.map((session) => {
              const active = activeSessionId === session.session_id;
              const isEditing = editingId === session.session_id;
              return (
                <div
                  key={session.session_id}
                  onClick={() => void onSelect(session.session_id)}
                  onKeyDown={(event) => {
                    if (event.key === "Enter" || event.key === " ") {
                      event.preventDefault();
                      void onSelect(session.session_id);
                    }
                  }}
                  role="button"
                  tabIndex={0}
                  className={`group relative w-full px-3 py-2.5 text-left transition-colors duration-150 ${
                    active
                      ? "bg-[var(--background)]/70 text-[var(--foreground)]"
                      : "text-[var(--muted-foreground)] hover:bg-[var(--background)]/50 hover:text-[var(--foreground)]"
                  }`}
                >
                  {active && (
                    <span className="absolute left-0 top-1/2 h-5 w-[3px] -translate-y-1/2 rounded-r-full bg-[var(--primary)]" />
                  )}
                  <div className="flex items-start gap-1.5">
                    <div className="min-w-0 flex-1">
                      {isEditing ? (
                        <input
                          value={draftTitle}
                          autoFocus
                          onChange={(event) =>
                            setDraftTitle(event.target.value)
                          }
                          onBlur={() => void commitEdit()}
                          onKeyDown={(event) => {
                            if (event.key === "Enter") void commitEdit();
                            if (event.key === "Escape") {
                              setEditingId(null);
                              setDraftTitle("");
                            }
                          }}
                          onClick={(event) => event.stopPropagation()}
                          className="w-full rounded border border-[var(--border)] bg-[var(--background)] px-2 py-0.5 text-[12px] text-[var(--foreground)] outline-none focus:ring-1 focus:ring-[var(--primary)]/40"
                        />
                      ) : (
                        <div className="flex items-center">
                          {isPlaceholderSessionTitle(session.title) ? (
                            <span
                              className={`dt-breathing-text line-clamp-1 min-w-0 flex-1 text-[12px] italic leading-snug text-[var(--muted-foreground)] ${
                                active ? "font-medium" : "font-normal"
                              }`}
                            >
                              {placeholderLabel}
                            </span>
                          ) : (
                            <span
                              className={`line-clamp-1 min-w-0 flex-1 text-[12px] leading-snug ${
                                active ? "font-medium" : "font-normal"
                              }`}
                            >
                              {session.title}
                            </span>
                          )}
                          <StatusIndicator status={session.status} />
                        </div>
                      )}
                      {!isEditing && (
                        <div className="mt-0.5 line-clamp-1 text-[11px] leading-tight text-[var(--muted-foreground)]">
                          {truncateText(
                            normalizeMessageContent(session.last_message),
                            120,
                          ) ||
                            formatRelativeTime(
                              session.updated_at,
                              i18n.language,
                            )}
                        </div>
                      )}
                    </div>
                    <div className="flex shrink-0 items-center gap-0.5 pt-px opacity-0 transition-opacity group-hover:opacity-100">
                      {isEditing ? (
                        <button
                          onClick={(event) => {
                            event.stopPropagation();
                            void commitEdit();
                          }}
                          className="rounded p-0.5 text-[var(--muted-foreground)] hover:bg-[var(--background)] hover:text-[var(--foreground)]"
                          aria-label={t("Save title")}
                        >
                          <Check size={12} />
                        </button>
                      ) : (
                        <button
                          onClick={(event) => {
                            event.stopPropagation();
                            startEdit(session);
                          }}
                          className="rounded p-0.5 text-[var(--muted-foreground)] hover:bg-[var(--background)] hover:text-[var(--foreground)]"
                          aria-label={t("Rename chat")}
                        >
                          <Pencil size={11} />
                        </button>
                      )}
                      <button
                        onClick={(event) => {
                          event.stopPropagation();
                          void onDelete(session.session_id);
                        }}
                        className="rounded p-0.5 text-[var(--muted-foreground)] hover:bg-[var(--background)] hover:text-[var(--destructive)]"
                        aria-label={t("Delete chat")}
                      >
                        <Trash2 size={11} />
                      </button>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      ))}
    </div>
  );
}

/** Popover listing the targets sessions can be moved to: unassigned plus
 *  every active folder (archived folders are never move targets). */
function MoveFolderMenu({
  folders,
  currentFolderId,
  onPick,
}: {
  folders: SessionFolder[];
  /** Optional: the session's current folder — shown with a checkmark and
   *  picking it again is a no-op. Omit for batch moves. */
  currentFolderId?: string;
  onPick: (folderId: string) => void;
}) {
  const { t } = useTranslation();
  const targets = folders.filter((folder) => folder.status === "active");
  const current = currentFolderId ?? "";

  const pick = (folderId: string) => {
    if (currentFolderId !== undefined && folderId === current) return;
    onPick(folderId);
  };

  return (
    <div
      className="absolute right-0 top-full z-30 mt-1 max-h-64 w-44 overflow-y-auto rounded-lg border border-[var(--border)] bg-[var(--card)] py-1 shadow-lg"
      onClick={(event) => event.stopPropagation()}
    >
      <div className="px-2.5 pb-1 pt-0.5 text-[10px] font-semibold uppercase tracking-widest text-[var(--muted-foreground)]/70">
        {t("Move to folder")}
      </div>
      <button
        onClick={() => pick("")}
        className={`flex w-full items-center gap-1.5 px-2.5 py-1 text-left text-[12px] transition-colors hover:bg-[var(--background)] ${
          current === "" ? "font-medium text-[var(--foreground)]" : ""
        }`}
      >
        <Inbox size={12} className="shrink-0 opacity-70" />
        <span className="min-w-0 flex-1 truncate">{t("Unassigned")}</span>
        {current === "" ? <Check size={12} /> : null}
      </button>
      {targets.map((folder) => (
        <button
          key={folder.id}
          onClick={() => pick(folder.id)}
          className={`flex w-full items-center gap-1.5 px-2.5 py-1 text-left text-[12px] transition-colors hover:bg-[var(--background)] ${
            current === folder.id ? "font-medium text-[var(--foreground)]" : ""
          }`}
        >
          <Folder size={12} className="shrink-0 opacity-70" />
          <span className="min-w-0 flex-1 truncate">{folder.name}</span>
          {current === folder.id ? <Check size={12} /> : null}
        </button>
      ))}
      {targets.length === 0 ? (
        <div className="px-2.5 py-1.5 text-[11px] text-[var(--muted-foreground)]/70">
          {t("No folders yet")}
        </div>
      ) : null}
    </div>
  );
}

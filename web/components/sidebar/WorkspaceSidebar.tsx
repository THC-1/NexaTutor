"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { useTranslation } from "react-i18next";
import { SidebarShell } from "@/components/sidebar/SidebarShell";
import { useUnifiedChat } from "@/context/UnifiedChatContext";
import {
  archiveSessionFolder,
  createSessionFolder,
  deleteSessionFolder,
  deleteSession,
  listSessionFolders,
  listSessions,
  moveSessionsToFolder,
  pinSessionFolder,
  renameSessionFolder,
  restoreSessionFolder,
  setSessionFolder,
  unpinSessionFolder,
  updateSessionTitle,
  type SessionFolder,
  type SessionSummary,
} from "@/lib/session-api";

export default function WorkspaceSidebar() {
  const { t } = useTranslation();
  const router = useRouter();
  const {
    newSession,
    cancelStreamingTurn,
    selectedSessionId,
    sessionStatuses,
    sidebarRefreshToken,
  } = useUnifiedChat();
  const [sessions, setSessions] = useState<SessionSummary[]>([]);
  const [folders, setFolders] = useState<SessionFolder[]>([]);
  const [loadingSessions, setLoadingSessions] = useState(false);
  const hasLoadedSessionsRef = useRef(false);

  const refreshSessions = useCallback(async () => {
    if (!hasLoadedSessionsRef.current) {
      setLoadingSessions(true);
    }
    try {
      setSessions(await listSessions(50, 0, { force: true }));
      setFolders(await listSessionFolders({ force: true }));
      hasLoadedSessionsRef.current = true;
    } catch (error) {
      console.error("Failed to load sessions", error);
    } finally {
      setLoadingSessions(false);
    }
  }, []);

  // First mount shows the skeleton; subsequent refreshes triggered by
  // ``sidebarRefreshToken`` (STREAM_END, server-side session bind,
  // turn deletion) silently swap in the new list. Resetting the ref
  // each refresh briefly re-renders the loading skeleton, which the
  // user perceives as a flicker on every message send / Answer Now.
  useEffect(() => {
    void refreshSessions();
  }, [refreshSessions, sidebarRefreshToken]);

  const orderedSessions = sessions
    .map((session, index) => {
      const runtime = sessionStatuses[session.session_id];
      return {
        index,
        session: runtime
          ? {
              ...session,
              status: runtime.status,
              active_turn_id: runtime.activeTurnId || session.active_turn_id,
            }
          : session,
      };
    })
    .sort((a, b) => {
      const aPriority = a.session.status === "running" ? 0 : 1;
      const bPriority = b.session.status === "running" ? 0 : 1;
      if (aPriority !== bPriority) return aPriority - bPriority;
      return a.index - b.index;
    })
    .map(({ session }) => session);

  // Cancel any in-flight streaming turn before starting a fresh session, so a
  // new chat never inherits a still-running turn (mirrors handleDeleteSession).
  const handleNewChat = useCallback(() => {
    cancelStreamingTurn();
    newSession();
    router.push("/home");
  }, [cancelStreamingTurn, newSession, router]);

  const handleSelectSession = useCallback(
    async (sessionId: string) => {
      router.push(`/home/${sessionId}`);
    },
    [router],
  );

  const handleRenameSession = useCallback(
    async (sessionId: string, title: string) => {
      const updated = await updateSessionTitle(sessionId, title);
      setSessions((prev) =>
        prev.map((session) =>
          session.session_id === sessionId
            ? {
                ...session,
                title: updated.title,
                updated_at: updated.updated_at,
              }
            : session,
        ),
      );
    },
    [],
  );

  const handleDeleteSession = useCallback(
    async (sessionId: string) => {
      if (!window.confirm(t("Delete this chat history?"))) return;
      await deleteSession(sessionId);
      setSessions((prev) =>
        prev.filter((session) => session.session_id !== sessionId),
      );
      if (selectedSessionId === sessionId) {
        cancelStreamingTurn();
        newSession();
        router.push("/home");
      }
    },
    [cancelStreamingTurn, newSession, router, selectedSessionId, t],
  );

  // ── Session folder management ────────────────────────────────────

  const refreshFolders = useCallback(async () => {
    try {
      setFolders(await listSessionFolders({ force: true }));
    } catch (error) {
      console.error("Failed to load session folders", error);
    }
  }, []);

  const handleCreateFolder = useCallback(
    async (name: string) => {
      await createSessionFolder(name);
      await refreshFolders();
      await refreshSessions();
    },
    [refreshFolders, refreshSessions],
  );

  const handleRenameFolder = useCallback(
    async (folderId: string, name: string) => {
      const renamed = await renameSessionFolder(folderId, name);
      setFolders((prev) =>
        prev.map((folder) => (folder.id === folderId ? renamed : folder)),
      );
    },
    [],
  );

  const handleArchiveFolder = useCallback(
    async (folderId: string) => {
      await archiveSessionFolder(folderId);
      await refreshFolders();
    },
    [refreshFolders],
  );

  const handleRestoreFolder = useCallback(
    async (folderId: string) => {
      await restoreSessionFolder(folderId);
      await refreshFolders();
    },
    [refreshFolders],
  );

  const handlePinFolder = useCallback(
    async (folderId: string) => {
      const folder = folders.find((item) => item.id === folderId);
      const updated = folder?.pinned
        ? await unpinSessionFolder(folderId)
        : await pinSessionFolder(folderId);
      setFolders((prev) =>
        prev.map((item) => (item.id === folderId ? updated : item)),
      );
    },
    [folders],
  );

  const handleDeleteFolder = useCallback(
    async (folderId: string) => {
      const folder = folders.find((item) => item.id === folderId);
      const count = folder?.session_count ?? 0;
      const message = count > 0
        ? t("Delete folder with sessions", { count, name: folder?.name ?? "" })
        : t("Delete folder", { name: folder?.name ?? "" });
      if (!window.confirm(message)) return;
      const result = await deleteSessionFolder(folderId, true);
      if (result.deleted_sessions.length > 0) {
        setSessions((prev) =>
          prev.filter(
            (session) => !result.deleted_sessions.includes(session.session_id),
          ),
        );
      }
      await refreshFolders();
    },
    [folders, refreshFolders, t],
  );

  const handleMoveSession = useCallback(
    async (sessionId: string, folderId: string) => {
      const prevFolderId =
        sessions.find((session) => session.session_id === sessionId)
          ?.folder_id ?? "";
      const updated = await setSessionFolder(sessionId, folderId);
      setSessions((prev) =>
        prev.map((session) =>
          session.session_id === sessionId
            ? { ...session, folder_id: updated.folder_id ?? "" }
            : session,
        ),
      );
      if (prevFolderId !== folderId) {
        setFolders((prev) =>
          prev.map((folder) => {
            let count = folder.session_count;
            if (folder.id === prevFolderId) {
              count = Math.max(0, count - 1);
            }
            if (folder.id === folderId) {
              count += 1;
            }
            return { ...folder, session_count: count };
          }),
        );
      }
    },
    [sessions],
  );

  const handleBatchMove = useCallback(
    async (sessionIds: string[], folderId: string) => {
      if (sessionIds.length === 0) return;
      await moveSessionsToFolder(folderId, sessionIds);
      const ids = new Set(sessionIds);
      setSessions((prev) =>
        prev.map((session) =>
          ids.has(session.session_id)
            ? { ...session, folder_id: folderId }
            : session,
        ),
      );
      // Re-count folders: subtract each moved session from its previous
      // folder, add the whole batch to the destination.
      const deltas = new Map<string, number>();
      for (const session of sessions) {
        if (!ids.has(session.session_id)) continue;
        const prevId = session.folder_id ?? "";
        deltas.set(prevId, (deltas.get(prevId) ?? 0) - 1);
      }
      deltas.set(folderId, (deltas.get(folderId) ?? 0) + sessionIds.length);
      setFolders((prev) =>
        prev.map((folder) => ({
          ...folder,
          session_count: Math.max(
            0,
            folder.session_count + (deltas.get(folder.id) ?? 0),
          ),
        })),
      );
    },
    [sessions],
  );

  return (
    <SidebarShell
      showSessions
      sessions={orderedSessions}
      folders={folders}
      activeSessionId={selectedSessionId}
      loadingSessions={loadingSessions}
      onNewChat={handleNewChat}
      onSelectSession={handleSelectSession}
      onRenameSession={handleRenameSession}
      onDeleteSession={handleDeleteSession}
      onCreateFolder={handleCreateFolder}
      onRenameFolder={handleRenameFolder}
      onArchiveFolder={handleArchiveFolder}
      onRestoreFolder={handleRestoreFolder}
      onDeleteFolder={handleDeleteFolder}
      onPinFolder={handlePinFolder}
      onMoveSession={handleMoveSession}
      onBatchMove={handleBatchMove}
    />
  );
}

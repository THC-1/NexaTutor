import { apiFetch, apiUrl } from "@/lib/api";
import { invalidateClientCache, withClientCache } from "@/lib/client-cache";
import type { LLMSelection, StreamEvent } from "@/lib/unified-ws";

export interface SessionMessage {
  id: number;
  session_id: string;
  role: "user" | "assistant" | "system";
  content: string;
  capability?: string;
  events: StreamEvent[];
  attachments: Array<{
    type: string;
    filename?: string;
    base64?: string;
    url?: string;
    mime_type?: string;
    id?: string;
    extracted_text?: string;
    generated?: boolean;
    size_bytes?: number;
  }>;
  metadata?: Record<string, unknown>;
  created_at: number;
  /** Edit-branching: id of the message this row continues. `null` for the
   *  first message in a session. Siblings share the same parent. */
  parent_message_id?: number | null;
}

export interface SessionFolder {
  id: string;
  folder_id: string;
  name: string;
  /** "active" folders are shown in the sidebar groups; "archived" folders
   *  must be restored before their sessions are manageable again. */
  status: "active" | "archived";
  /** 1 = pinned to the top of the active list (0/absent = normal order). */
  pinned?: number;
  created_at: number;
  updated_at: number;
  session_count: number;
}

export interface SessionSummary {
  id: string;
  session_id: string;
  title: string;
  created_at: number;
  updated_at: number;
  message_count: number;
  last_message: string;
  /** Folder this session belongs to; "" / absent = unassigned. */
  folder_id?: string;
  status?:
    | "idle"
    | "running"
    | "completed"
    | "failed"
    | "cancelled"
    | "rejected";
  active_turn_id?: string;
  preferences?: {
    capability?: string;
    tools?: string[];
    knowledge_bases?: string[];
    language?: string;
    llm_selection?: LLMSelection | null;
    /** Session-level persona preference; "" / absent = Default (no persona). */
    persona?: string;
    /** Edit-branching: maps a parent_message_id → the child id currently
     *  shown at that branch point. Missing keys default to the latest
     *  sibling (most recently created child). */
    selected_branches?: Record<string, number>;
  };
}

export interface ActiveTurnSummary {
  id: string;
  turn_id: string;
  session_id: string;
  capability: string;
  status: "running" | "completed" | "failed" | "cancelled" | "rejected";
  error: string;
  created_at: number;
  updated_at: number;
  finished_at?: number | null;
  last_seq: number;
}

export interface SessionDetail {
  id: string;
  session_id: string;
  title: string;
  created_at: number;
  updated_at: number;
  /** Folder this session belongs to; "" / absent = unassigned. */
  folder_id?: string;
  status?:
    | "idle"
    | "running"
    | "completed"
    | "failed"
    | "cancelled"
    | "rejected";
  active_turn_id?: string;
  compressed_summary?: string;
  summary_up_to_msg_id?: number;
  preferences?: {
    capability?: string;
    tools?: string[];
    knowledge_bases?: string[];
    language?: string;
    llm_selection?: LLMSelection | null;
    /** Session-level persona preference; "" / absent = Default (no persona). */
    persona?: string;
    /** Edit-branching: maps a parent_message_id → the child id currently
     *  shown at that branch point. Missing keys default to the latest
     *  sibling (most recently created child). */
    selected_branches?: Record<string, number>;
  };
  messages: SessionMessage[];
  active_turns?: ActiveTurnSummary[];
}

export interface QuizResultItem {
  question_id?: string;
  question: string;
  question_type?: string;
  options?: Record<string, string>;
  user_answer: string;
  correct_answer: string;
  explanation?: string;
  difficulty?: string;
  is_correct: boolean;
}

async function expectJson<T>(response: Response): Promise<T> {
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export async function listSessions(
  limit = 50,
  offset = 0,
  options?: { force?: boolean; folderId?: string },
): Promise<SessionSummary[]> {
  const qs = new URLSearchParams({
    limit: String(limit),
    offset: String(offset),
  });
  // `folderId: ""` filters to the unassigned bucket; absent = all sessions.
  if (options?.folderId !== undefined) {
    qs.set("folder_id", options.folderId);
  }
  const cacheKey = `sessions:${limit}:${offset}:${options?.folderId ?? "*"}`;
  return withClientCache<SessionSummary[]>(
    cacheKey,
    async () => {
      const response = await apiFetch(
        apiUrl(`/api/v1/sessions?${qs.toString()}`),
        {
          cache: "no-store",
        },
      );
      const data = await expectJson<{ sessions: SessionSummary[] }>(response);
      return data.sessions ?? [];
    },
    {
      force: options?.force,
      ttlMs: 15_000,
    },
  );
}

export async function getSession(
  sessionId: string,
  signal?: AbortSignal,
): Promise<SessionDetail> {
  const response = await apiFetch(apiUrl(`/api/v1/sessions/${sessionId}`), {
    cache: "no-store",
    signal,
  });
  return expectJson<SessionDetail>(response);
}

export async function updateSessionTitle(
  sessionId: string,
  title: string,
): Promise<SessionDetail> {
  const response = await apiFetch(apiUrl(`/api/v1/sessions/${sessionId}`), {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title }),
  });
  const data = await expectJson<{ session: SessionDetail }>(response);
  invalidateClientCache("sessions:");
  return data.session;
}

export async function deleteSession(sessionId: string): Promise<void> {
  const response = await apiFetch(apiUrl(`/api/v1/sessions/${sessionId}`), {
    method: "DELETE",
  });
  await expectJson<{ deleted: boolean }>(response);
  invalidateClientCache("sessions:");
}

export async function recordQuizResults(
  sessionId: string,
  answers: QuizResultItem[],
  turnId?: string | null,
): Promise<void> {
  const response = await apiFetch(
    apiUrl(`/api/v1/sessions/${sessionId}/quiz-results`),
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ answers, turn_id: turnId || "" }),
    },
  );
  await expectJson<{ recorded: boolean }>(response);
}

export async function deleteMessage(
  sessionId: string,
  messageId: number,
): Promise<void> {
  const response = await apiFetch(
    apiUrl(`/api/v1/sessions/${sessionId}/messages/${messageId}`),
    { method: "DELETE" },
  );
  await expectJson<{ deleted: boolean }>(response);
}

export async function updateBranchSelection(
  sessionId: string,
  selectedBranches: Record<string, number>,
): Promise<void> {
  const response = await apiFetch(
    apiUrl(`/api/v1/sessions/${sessionId}/branch-selection`),
    {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ selected_branches: selectedBranches }),
    },
  );
  await expectJson<{ selected_branches: Record<string, number> }>(response);
}

// ── Session folders ────────────────────────────────────────────────

/** Folder mutations change both the folder list and the sessions list. */
function invalidateSessionFolderCache(): void {
  invalidateClientCache("sessions:");
  invalidateClientCache("session-folders:");
}

export async function listSessionFolders(options?: {
  force?: boolean;
}): Promise<SessionFolder[]> {
  return withClientCache<SessionFolder[]>(
    "session-folders:all",
    async () => {
      const response = await apiFetch(apiUrl("/api/v1/session-folders"), {
        cache: "no-store",
      });
      const data = await expectJson<{ folders: SessionFolder[] }>(response);
      return data.folders ?? [];
    },
    { force: options?.force, ttlMs: 15_000 },
  );
}

async function expectFolder(response: Response): Promise<SessionFolder> {
  const data = await expectJson<{ folder: SessionFolder }>(response);
  return data.folder;
}

export async function createSessionFolder(name: string): Promise<SessionFolder> {
  const response = await apiFetch(apiUrl("/api/v1/session-folders"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name }),
  });
  const folder = await expectFolder(response);
  invalidateSessionFolderCache();
  return folder;
}

export async function renameSessionFolder(
  folderId: string,
  name: string,
): Promise<SessionFolder> {
  const response = await apiFetch(
    apiUrl(`/api/v1/session-folders/${folderId}`),
    {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name }),
    },
  );
  const folder = await expectFolder(response);
  invalidateSessionFolderCache();
  return folder;
}

export async function archiveSessionFolder(
  folderId: string,
): Promise<SessionFolder> {
  const response = await apiFetch(
    apiUrl(`/api/v1/session-folders/${folderId}/archive`),
    { method: "POST" },
  );
  const folder = await expectFolder(response);
  invalidateSessionFolderCache();
  return folder;
}

export async function restoreSessionFolder(
  folderId: string,
): Promise<SessionFolder> {
  const response = await apiFetch(
    apiUrl(`/api/v1/session-folders/${folderId}/restore`),
    { method: "POST" },
  );
  const folder = await expectFolder(response);
  invalidateSessionFolderCache();
  return folder;
}

export async function pinSessionFolder(folderId: string): Promise<SessionFolder> {
  const response = await apiFetch(
    apiUrl(`/api/v1/session-folders/${folderId}/pin`),
    { method: "PUT" },
  );
  const folder = await expectFolder(response);
  invalidateSessionFolderCache();
  return folder;
}

export async function unpinSessionFolder(
  folderId: string,
): Promise<SessionFolder> {
  const response = await apiFetch(
    apiUrl(`/api/v1/session-folders/${folderId}/pin`),
    { method: "DELETE" },
  );
  const folder = await expectFolder(response);
  invalidateSessionFolderCache();
  return folder;
}

export async function deleteSessionFolder(
  folderId: string,
  deleteSessions = true,
): Promise<{ deleted: boolean; deleted_sessions: string[] }> {
  const qs = new URLSearchParams({ delete_sessions: String(deleteSessions) });
  const response = await apiFetch(
    apiUrl(`/api/v1/session-folders/${folderId}?${qs.toString()}`),
    { method: "DELETE" },
  );
  const result = await expectJson<{
    deleted: boolean;
    deleted_sessions: string[];
  }>(response);
  invalidateSessionFolderCache();
  return result;
}

export async function moveSessionsToFolder(
  folderId: string,
  sessionIds: string[],
): Promise<number> {
  const response = await apiFetch(
    apiUrl(`/api/v1/session-folders/${folderId}/sessions`),
    {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_ids: sessionIds }),
    },
  );
  const data = await expectJson<{ updated: number }>(response);
  invalidateSessionFolderCache();
  return data.updated;
}

/** Move one session into a folder; `folderId: ""` = unassigned. */
export async function setSessionFolder(
  sessionId: string,
  folderId: string,
): Promise<SessionDetail> {
  const response = await apiFetch(
    apiUrl(`/api/v1/sessions/${sessionId}/folder`),
    {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ folder_id: folderId }),
    },
  );
  const data = await expectJson<{ session: SessionDetail }>(response);
  invalidateSessionFolderCache();
  return data.session;
}

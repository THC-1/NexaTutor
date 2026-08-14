"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import {
  Archive,
  Check,
  ChevronDown,
  Folder,
  History,
  Inbox,
  Loader2,
  RefreshCw,
  Search,
  type LucideIcon,
} from "lucide-react";
import { useTranslation } from "react-i18next";
import SessionList from "@/components/SessionList";
import SpaceSectionHeader from "@/components/space/SpaceSectionHeader";
import { useAppShell } from "@/context/AppShellContext";
import {
  deleteSession,
  listSessionFolders,
  listSessions,
  updateSessionTitle,
  type SessionFolder,
  type SessionSummary,
} from "@/lib/session-api";

const FILTER_ALL = "__all__";
const FILTER_UNASSIGNED = "__unassigned__";
const FILTER_ARCHIVED = "__archived__";

/**
 * Sessions list for chat history. Reopened sessions always route back to
 * the main chat surface. Supports filtering by session folder.
 */
export interface ChatHistorySectionProps {
  icon?: LucideIcon;
  title?: string;
  description?: string;
}

export default function ChatHistorySection({
  icon,
  title,
  description,
}: ChatHistorySectionProps = {}) {
  const basePath = "/home";
  const { t } = useTranslation();
  const router = useRouter();
  const { activeSessionId, setActiveSessionId } = useAppShell();
  const [sessions, setSessions] = useState<SessionSummary[]>([]);
  const [folders, setFolders] = useState<SessionFolder[]>([]);
  const [loading, setLoading] = useState(true);
  const [query, setQuery] = useState("");
  const [folderFilter, setFolderFilter] = useState<string>(FILTER_ALL);
  const [filterOpen, setFilterOpen] = useState(false);
  const filterRef = useRef<HTMLDivElement>(null);

  const load = useCallback(async (force = false) => {
    setLoading(true);
    try {
      const [sessionList, folderList] = await Promise.all([
        listSessions(200, 0, { force }),
        listSessionFolders({ force }),
      ]);
      setSessions(sessionList);
      setFolders(folderList);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load(true);
  }, [load]);

  const activeFolders = useMemo(
    () => folders.filter((folder) => folder.status === "active"),
    [folders],
  );
  const archivedFolderIds = useMemo(
    () =>
      new Set(
        folders.filter((folder) => folder.status === "archived").map((f) => f.id),
      ),
    [folders],
  );

  const filteredSessions = useMemo(() => {
    const needle = query.trim().toLowerCase();
    let base = sessions;
    if (needle) {
      base = base.filter((session) =>
        [session.title, session.last_message]
          .filter(Boolean)
          .some((value) => value.toLowerCase().includes(needle)),
      );
    }
    if (folderFilter === FILTER_UNASSIGNED) {
      return base.filter((session) => !session.folder_id);
    }
    if (folderFilter === FILTER_ARCHIVED) {
      return base.filter((session) =>
        archivedFolderIds.has(session.folder_id ?? ""),
      );
    }
    if (folderFilter !== FILTER_ALL) {
      return base.filter((session) => session.folder_id === folderFilter);
    }
    return base;
  }, [query, sessions, folderFilter, archivedFolderIds]);

  const handleSelect = useCallback(
    (sessionId: string) => {
      setActiveSessionId(sessionId);
      router.push(`${basePath}/${sessionId}`);
    },
    [basePath, router, setActiveSessionId],
  );

  const handleRename = useCallback(
    async (sessionId: string, title: string) => {
      await updateSessionTitle(sessionId, title);
      await load(true);
    },
    [load],
  );

  const handleDelete = useCallback(
    async (sessionId: string) => {
      if (!window.confirm(t("Delete this chat?"))) return;
      await deleteSession(sessionId);
      if (activeSessionId === sessionId) setActiveSessionId(null);
      setSessions((prev) =>
        prev.filter((session) => session.session_id !== sessionId),
      );
    },
    [activeSessionId, setActiveSessionId, t],
  );

  const pickFilter = (value: string) => {
    setFolderFilter(value);
    setFilterOpen(false);
  };

  const filterLabel = useMemo(() => {
    if (folderFilter === FILTER_ALL) return t("All conversations");
    if (folderFilter === FILTER_UNASSIGNED) return t("Unassigned");
    if (folderFilter === FILTER_ARCHIVED) return t("Archived");
    return folders.find((folder) => folder.id === folderFilter)?.name ?? t("All conversations");
  }, [folderFilter, folders, t]);

  const HeaderIcon = icon ?? History;
  const headerTitle = title ?? t("Chat History");
  const headerDescription =
    description ??
    t(
      "Browse, rename, delete, and reopen previous conversations from your learning space.",
    );

  return (
    <div className="space-y-6">
      <SpaceSectionHeader
        icon={HeaderIcon}
        title={headerTitle}
        description={headerDescription}
        meta={
          <span className="rounded-full border border-[var(--border)] bg-[var(--card)] px-2 py-0.5 text-[10.5px] font-medium text-[var(--muted-foreground)]">
            {sessions.length} {t("conversations")}
          </span>
        }
        action={
          <button
            type="button"
            onClick={() => void load(true)}
            disabled={loading}
            className="inline-flex items-center gap-1.5 rounded-lg border border-[var(--border)]/50 px-3 py-1.5 text-[12px] font-medium text-[var(--muted-foreground)] transition-colors hover:border-[var(--border)] hover:text-[var(--foreground)] disabled:opacity-40"
          >
            {loading ? (
              <Loader2 className="h-3 w-3 animate-spin" />
            ) : (
              <RefreshCw className="h-3 w-3" />
            )}
            {t("Refresh")}
          </button>
        }
      />

      <section className="rounded-2xl border border-[var(--border)] bg-[var(--card)] shadow-sm">
        <div className="flex flex-wrap items-center gap-2 border-b border-[var(--border)]/60 px-4 py-3">
          <label className="flex min-w-0 flex-1 items-center gap-2 rounded-xl border border-[var(--border)] bg-[var(--background)] px-3 py-2 text-[13px] text-[var(--muted-foreground)] focus-within:border-[var(--ring)]">
            <Search size={14} strokeWidth={1.7} />
            <input
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder={t("Search chat history...")}
              className="min-w-0 flex-1 bg-transparent text-[13px] text-[var(--foreground)] outline-none placeholder:text-[var(--muted-foreground)]/55"
            />
          </label>

          {/* Folder filter dropdown */}
          <div className="relative" ref={filterRef}>
            <button
              type="button"
              onClick={() => setFilterOpen((prev) => !prev)}
              className="inline-flex items-center gap-1.5 rounded-xl border border-[var(--border)] bg-[var(--background)] px-3 py-2 text-[12.5px] text-[var(--muted-foreground)] transition-colors hover:border-[var(--ring)] hover:text-[var(--foreground)]"
              aria-expanded={filterOpen}
              aria-label={t("Filter by folder")}
            >
              <Folder size={14} strokeWidth={1.7} />
              <span className="max-w-36 truncate">{filterLabel}</span>
              <ChevronDown
                size={13}
                strokeWidth={1.7}
                className={`transition-transform duration-150 ${
                  filterOpen ? "rotate-180" : ""
                }`}
              />
            </button>
            {filterOpen ? (
              <>
                <div
                  className="fixed inset-0 z-20"
                  onClick={() => setFilterOpen(false)}
                />
                <div className="absolute right-0 top-full z-30 mt-1 max-h-72 w-52 overflow-y-auto rounded-xl border border-[var(--border)] bg-[var(--card)] py-1 shadow-lg">
                  <FilterOption
                    icon={History}
                    label={t("All conversations")}
                    active={folderFilter === FILTER_ALL}
                    onClick={() => pickFilter(FILTER_ALL)}
                  />
                  <FilterOption
                    icon={Inbox}
                    label={t("Unassigned")}
                    active={folderFilter === FILTER_UNASSIGNED}
                    onClick={() => pickFilter(FILTER_UNASSIGNED)}
                  />
                  {activeFolders.map((folder) => (
                    <FilterOption
                      key={folder.id}
                      icon={Folder}
                      label={folder.name}
                      count={folder.session_count}
                      active={folderFilter === folder.id}
                      onClick={() => pickFilter(folder.id)}
                    />
                  ))}
                  {archivedFolderIds.size > 0 ? (
                    <FilterOption
                      icon={Archive}
                      label={t("Archived")}
                      active={folderFilter === FILTER_ARCHIVED}
                      onClick={() => pickFilter(FILTER_ARCHIVED)}
                    />
                  ) : null}
                </div>
              </>
            ) : null}
          </div>
        </div>

        <div className="px-3 py-3">
          <SessionList
            sessions={filteredSessions}
            folders={folders}
            activeSessionId={activeSessionId}
            loading={loading}
            onSelect={handleSelect}
            onRename={handleRename}
            onDelete={handleDelete}
          />
        </div>
      </section>
    </div>
  );
}

function FilterOption({
  icon: Icon,
  label,
  count,
  active,
  onClick,
}: {
  icon: LucideIcon;
  label: string;
  count?: number;
  active: boolean;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      className={`flex w-full items-center gap-2 px-3 py-1.5 text-left text-[12.5px] transition-colors hover:bg-[var(--background)] ${
        active
          ? "font-medium text-[var(--foreground)]"
          : "text-[var(--muted-foreground)]"
      }`}
    >
      <Icon size={13} strokeWidth={1.7} className="shrink-0 opacity-70" />
      <span className="min-w-0 flex-1 truncate">{label}</span>
      {count !== undefined ? (
        <span className="shrink-0 text-[10.5px] opacity-60">{count}</span>
      ) : null}
      {active ? <Check size={12} className="shrink-0" /> : null}
    </button>
  );
}

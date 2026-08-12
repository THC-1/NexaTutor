"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { useTranslation } from "react-i18next";
import { Cpu, Loader2, Plug, Plus, Trash2, X } from "lucide-react";

import { agentGlyph } from "@/components/agents/agent-icons";
import SpaceSectionHeader from "@/components/space/SpaceSectionHeader";
import {
  connectSubagent,
  detectSubagents,
  disconnectSubagent,
  listSubagentConnections,
  type SubagentBackendInfo,
  type SubagentConnection,
} from "@/lib/subagents-api";

type Lang = { zh: string; en: string };

function backendLabel(kind: string): string {
  const labels: Record<string, string> = {
    claude_code: "Claude Code",
    codex: "Codex",
    gemini: "Gemini CLI",
    kimi: "Kimi CLI",
    opencode: "opencode",
    mimo: "MiMo Code",
  };
  return labels[kind] ?? kind;
}

export default function ConnectedAgents() {
  const { i18n } = useTranslation();
  const zh = i18n.language?.toLowerCase().startsWith("zh");
  const tr = useCallback((text: Lang) => (zh ? text.zh : text.en), [zh]);
  const [backends, setBackends] = useState<SubagentBackendInfo[]>([]);
  const [connections, setConnections] = useState<SubagentConnection[]>([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [busyName, setBusyName] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const [detected, connected] = await Promise.all([
        detectSubagents().catch(() => [] as SubagentBackendInfo[]),
        listSubagentConnections().catch(() => [] as SubagentConnection[]),
      ]);
      setBackends(detected);
      setConnections(connected);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  const available = useMemo(() => backends.filter((backend) => backend.available), [backends]);

  const handleDisconnect = useCallback(
    async (name: string) => {
      if (
        !window.confirm(
          tr({
            zh: `断开「${name}」？这只会移除连接，不影响本机的智能体配置。`,
            en: `Disconnect “${name}”? This only removes the connection; your local agent is untouched.`,
          }),
        )
      ) {
        return;
      }
      setBusyName(name);
      try {
        await disconnectSubagent(name);
        await load();
      } finally {
        setBusyName(null);
      }
    },
    [load, tr],
  );

  return (
    <section className="space-y-4">
      <SpaceSectionHeader
        icon={Plug}
        title={tr({ zh: "连接的智能体", en: "Connected agents" })}
        description={tr({
          zh: "连接本机的 Claude Code、Codex、Gemini CLI、Kimi CLI、opencode 或 MiMo Code，在对话中直接咨询。",
          en: "Connect a local Claude Code, Codex, Gemini CLI, Kimi CLI, opencode, or MiMo Code and consult it directly in chat.",
        })}
        action={
          available.length > 0 ? (
            <button
              type="button"
              onClick={() => setModalOpen(true)}
              className="inline-flex items-center gap-1.5 rounded-lg bg-[var(--foreground)] px-3 py-1.5 text-[12px] font-medium text-[var(--background)] shadow-sm transition-opacity hover:opacity-90"
            >
              <Plus className="h-3.5 w-3.5" />
              {tr({ zh: "连接智能体", en: "Connect agent" })}
            </button>
          ) : null
        }
      />

      {loading ? (
        <div className="flex items-center gap-2 px-1 text-[12px] text-[var(--muted-foreground)]">
          <Loader2 className="h-3.5 w-3.5 animate-spin" />
          {tr({ zh: "检测本机智能体…", en: "Detecting local agents…" })}
        </div>
      ) : available.length === 0 ? (
        <div className="rounded-xl border border-dashed border-[var(--border)] bg-[var(--card)]/40 px-4 py-5 text-[12.5px] leading-relaxed text-[var(--muted-foreground)]">
          {tr({
            zh: "未检测到可用的本地智能体 CLI。请先安装并登录其中一个支持的 CLI。",
            en: "No supported local agent CLI was detected. Install and sign in to one first.",
          })}
        </div>
      ) : connections.length === 0 ? (
        <div className="rounded-xl border border-dashed border-[var(--border)] bg-[var(--card)]/40 px-4 py-5 text-[12.5px] leading-relaxed text-[var(--muted-foreground)]">
          {tr({
            zh: "尚未连接任何智能体。点击「连接智能体」添加检测到的本地 CLI。",
            en: "No agents connected yet. Click “Connect agent” to add a detected local CLI.",
          })}
        </div>
      ) : (
        <div className="grid gap-3 sm:grid-cols-2">
          {connections.map((connection) => {
            const Glyph = agentGlyph(connection.agent_kind);
            return (
              <div
                key={connection.name}
                className="group flex items-center gap-3 rounded-2xl border border-[var(--border)] bg-[var(--card)] px-4 py-3"
              >
                <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl border border-[var(--border)]/60 bg-[var(--background)] text-[var(--foreground)]">
                  {Glyph ? <Glyph size={20} /> : <Cpu size={18} strokeWidth={1.6} />}
                </span>
                <div className="min-w-0 flex-1">
                  <div className="truncate text-[13.5px] font-semibold tracking-tight text-[var(--foreground)]">
                    {connection.name}
                  </div>
                  <div className="mt-0.5 truncate text-[11.5px] text-[var(--muted-foreground)]">
                    {backendLabel(connection.agent_kind)}
                    {connection.cwd ? ` · ${connection.cwd}` : ""}
                  </div>
                </div>
                <button
                  type="button"
                  onClick={() => void handleDisconnect(connection.name)}
                  disabled={busyName === connection.name}
                  title={tr({ zh: "断开", en: "Disconnect" })}
                  aria-label={tr({ zh: "断开", en: "Disconnect" })}
                  className="rounded-lg border border-[var(--border)]/50 p-2 text-[var(--muted-foreground)] transition-colors hover:border-red-300 hover:text-red-600 disabled:opacity-50 dark:hover:border-red-900 dark:hover:text-red-400"
                >
                  {busyName === connection.name ? (
                    <Loader2 className="h-3.5 w-3.5 animate-spin" />
                  ) : (
                    <Trash2 className="h-3.5 w-3.5" />
                  )}
                </button>
              </div>
            );
          })}
        </div>
      )}

      {modalOpen ? (
        <ConnectModal
          backends={available}
          existingNames={connections.map((connection) => connection.name)}
          tr={tr}
          onClose={() => setModalOpen(false)}
          onConnected={() => {
            setModalOpen(false);
            void load();
          }}
        />
      ) : null}
    </section>
  );
}

function ConnectModal({
  backends,
  existingNames,
  tr,
  onClose,
  onConnected,
}: {
  backends: SubagentBackendInfo[];
  existingNames: string[];
  tr: (text: Lang) => string;
  onClose: () => void;
  onConnected: () => void;
}) {
  const [kind, setKind] = useState(backends[0]?.kind ?? "");
  const [name, setName] = useState("");
  const [cwd, setCwd] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const submit = useCallback(async () => {
    const trimmed = name.trim();
    if (!trimmed) {
      setError(tr({ zh: "请填写名称。", en: "Please enter a name." }));
      return;
    }
    if (existingNames.includes(trimmed)) {
      setError(tr({ zh: "已存在同名连接。", en: "A connection with this name already exists." }));
      return;
    }
    setSubmitting(true);
    setError("");
    try {
      await connectSubagent({ name: trimmed, agent_kind: kind, cwd: cwd.trim() });
      onConnected();
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : String(reason));
    } finally {
      setSubmitting(false);
    }
  }, [cwd, existingNames, kind, name, onConnected, tr]);

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/30 p-4 backdrop-blur-sm"
      onClick={onClose}
    >
      <div
        className="w-full max-w-md rounded-2xl border border-[var(--border)] bg-[var(--card)] p-5 shadow-2xl"
        onClick={(event) => event.stopPropagation()}
      >
        <div className="mb-4 flex items-center justify-between">
          <h2 className="font-serif text-[16px] font-semibold tracking-tight text-[var(--foreground)]">
            {tr({ zh: "连接智能体", en: "Connect an agent" })}
          </h2>
          <button type="button" onClick={onClose} aria-label={tr({ zh: "关闭", en: "Close" })}>
            <X size={16} />
          </button>
        </div>
        <div className="space-y-3.5">
          <div className="grid grid-cols-2 gap-2">
            {backends.map((backend) => {
              const Glyph = agentGlyph(backend.kind);
              return (
                <button
                  key={backend.kind}
                  type="button"
                  onClick={() => setKind(backend.kind)}
                  className={`flex items-center justify-center gap-1.5 rounded-lg border px-3 py-2 text-[12.5px] font-medium ${kind === backend.kind ? "border-[var(--primary)] text-[var(--foreground)]" : "border-[var(--border)] text-[var(--muted-foreground)]"}`}
                >
                  {Glyph ? <Glyph size={15} /> : null}
                  {backend.display_name}
                </button>
              );
            })}
          </div>
          <input
            autoFocus
            value={name}
            onChange={(event) => setName(event.target.value)}
            placeholder={tr({ zh: "连接名称", en: "Connection name" })}
            className="w-full rounded-lg border border-[var(--border)] bg-[var(--background)] px-3 py-2 text-[13px]"
          />
          <input
            value={cwd}
            onChange={(event) => setCwd(event.target.value)}
            placeholder={tr({ zh: "工作目录（可选）", en: "Working directory (optional)" })}
            className="w-full rounded-lg border border-[var(--border)] bg-[var(--background)] px-3 py-2 font-mono text-[12px]"
          />
          {error ? <p className="text-[12px] text-red-600 dark:text-red-400">{error}</p> : null}
        </div>
        <div className="mt-5 flex justify-end gap-2">
          <button type="button" onClick={onClose} className="px-3 py-1.5 text-[12.5px]">
            {tr({ zh: "取消", en: "Cancel" })}
          </button>
          <button
            type="button"
            onClick={() => void submit()}
            disabled={submitting || !kind}
            className="inline-flex items-center gap-1.5 rounded-lg bg-[var(--foreground)] px-3.5 py-1.5 text-[12.5px] font-medium text-[var(--background)] disabled:opacity-50"
          >
            {submitting ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Plug className="h-3.5 w-3.5" />}
            {tr({ zh: "连接", en: "Connect" })}
          </button>
        </div>
      </div>
    </div>
  );
}

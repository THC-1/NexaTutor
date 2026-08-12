"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { Loader2 } from "lucide-react";
import { useTranslation } from "react-i18next";

import {
  SettingRow,
  SettingSection,
  SettingsPageHeader,
  inputClass,
} from "@/components/settings/shared";
import { useSettings } from "@/components/settings/SettingsContext";
import {
  DEFAULT_CHAT_RESPONSE_TIMEOUT_SECONDS,
  MAX_CHAT_RESPONSE_TIMEOUT_SECONDS,
  MIN_CHAT_RESPONSE_TIMEOUT_SECONDS,
  clampChatResponseTimeout,
  writeStoredChatResponseTimeout,
} from "@/context/app-shell-storage";
import { apiFetch, apiUrl } from "@/lib/api";

type NetworkSettings = {
  backend_port: number;
  frontend_port: number;
};

type NetworkSettingsPayload = {
  settings: NetworkSettings;
  effective: {
    backend_url: string;
    frontend_url: string;
  };
  restart_required: boolean;
};

function normalizeDraft(payload: NetworkSettingsPayload): NetworkSettings {
  return {
    backend_port: payload.settings.backend_port,
    frontend_port: payload.settings.frontend_port,
  };
}

function DetailTile({
  label,
  value,
  tone = "neutral",
}: {
  label: string;
  value: string;
  tone?: "neutral" | "ok" | "warn";
}) {
  const dot =
    tone === "ok"
      ? "bg-emerald-500"
      : tone === "warn"
        ? "bg-amber-500"
        : "bg-[var(--border)]";
  return (
    <div className="rounded-xl border border-[var(--border)]/60 bg-[var(--card)] px-4 py-3">
      <div className="flex items-center gap-2 text-[11px] font-medium text-[var(--muted-foreground)]">
        <span className={`h-1.5 w-1.5 rounded-full ${dot}`} />
        {label}
      </div>
      <div
        className="mt-2 truncate text-[13px] font-medium text-[var(--foreground)]"
        title={value}
      >
        {value || "-"}
      </div>
    </div>
  );
}

/**
 * Per-user chat idle-timeout control. Self-contained (its own fetch + save via
 * the dedicated ``/settings/chat-response-timeout`` endpoint) and renders
 * independently of the admin network settings below, so any user can adjust it.
 * Mirrors the value to localStorage so the chat watchdog picks it up at once.
 */
function ChatResponseTimeoutSection() {
  const { t } = useTranslation();
  const { registerExtension } = useSettings();
  const [seconds, setSeconds] = useState<number>(
    DEFAULT_CHAT_RESPONSE_TIMEOUT_SECONDS,
  );
  const [initial, setInitial] = useState<number>(
    DEFAULT_CHAT_RESPONSE_TIMEOUT_SECONDS,
  );
  const [message, setMessage] = useState("");

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const response = await apiFetch(apiUrl("/api/v1/settings"));
        const data = (await response.json().catch(() => ({}))) as {
          ui?: { chat_response_timeout?: number };
        };
        const value = clampChatResponseTimeout(
          Number(data?.ui?.chat_response_timeout) ||
            DEFAULT_CHAT_RESPONSE_TIMEOUT_SECONDS,
        );
        if (cancelled) return;
        setSeconds(value);
        setInitial(value);
        writeStoredChatResponseTimeout(value);
      } catch {
        // keep the default
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  const dirty = seconds !== initial;

  // Flush through the global Apply (top toolbar) instead of a local button.
  const secondsRef = useRef(seconds);
  secondsRef.current = seconds;
  const save = useCallback(async () => {
    setMessage("");
    try {
      const value = clampChatResponseTimeout(secondsRef.current);
      const response = await apiFetch(
        apiUrl("/api/v1/settings/chat-response-timeout"),
        {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ chat_response_timeout: value }),
        },
      );
      if (!response.ok) throw new Error(t("Failed to save."));
      setSeconds(value);
      setInitial(value);
      writeStoredChatResponseTimeout(value);
    } catch (err) {
      setMessage(err instanceof Error ? err.message : String(err));
    }
  }, [t]);

  useEffect(() => {
    registerExtension("chat-timeout", { dirty, save });
    return () => registerExtension("chat-timeout", null);
  }, [dirty, save, registerExtension]);

  return (
    <SettingSection
      title={t("Chat response timeout")}
      description={t(
        "How long chat waits for a reply before showing a timeout error. Increase it for slow tools like image generation.",
      )}
    >
      <SettingRow
        title={t("Timeout (seconds)")}
        description={t(
          "Between {{min}} and {{max}} seconds. Takes effect immediately — no restart.",
          {
            min: MIN_CHAT_RESPONSE_TIMEOUT_SECONDS,
            max: MAX_CHAT_RESPONSE_TIMEOUT_SECONDS,
          },
        )}
        control={
          <input
            className={`${inputClass} w-28`}
            type="number"
            min={MIN_CHAT_RESPONSE_TIMEOUT_SECONDS}
            max={MAX_CHAT_RESPONSE_TIMEOUT_SECONDS}
            value={seconds}
            onChange={(event) => setSeconds(Number(event.target.value))}
          />
        }
      />
      {message && (
        <p className="px-1 pb-3 text-[11.5px] text-[var(--muted-foreground)]">
          {message}
        </p>
      )}
    </SettingSection>
  );
}

export default function NetworkSettingsPage() {
  const { t } = useTranslation();
  const { registerExtension } = useSettings();
  const [payload, setPayload] = useState<NetworkSettingsPayload | null>(null);
  const [draft, setDraft] = useState<NetworkSettings | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      setLoading(true);
      setError(null);
      try {
        const response = await apiFetch(apiUrl("/api/v1/settings/network"));
        const data = (await response.json().catch(() => ({}))) as
          | NetworkSettingsPayload
          | { detail?: string };
        if (!response.ok) {
          throw new Error(
            "detail" in data && data.detail
              ? data.detail
              : t("Failed to load network settings."),
          );
        }
        if (cancelled) return;
        const next = data as NetworkSettingsPayload;
        setPayload(next);
        setDraft(normalizeDraft(next));
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : String(err));
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    load();
    return () => {
      cancelled = true;
    };
  }, [t]);

  const dirty = useMemo(() => {
    if (!payload || !draft) return false;
    const current = normalizeDraft(payload);
    return (
      current.backend_port !== draft.backend_port ||
      current.frontend_port !== draft.frontend_port
    );
  }, [draft, payload]);

  // Flush through the global Apply (top toolbar) instead of a local button.
  // Refs keep the registered ``save`` closure reading the latest draft.
  const draftRef = useRef(draft);
  draftRef.current = draft;
  const save = useCallback(async () => {
    const current = draftRef.current;
    if (!current) return;
    setError(null);
    try {
      const response = await apiFetch(apiUrl("/api/v1/settings/network"), {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ...current,
        }),
      });
      const data = (await response.json().catch(() => ({}))) as
        | NetworkSettingsPayload
        | { detail?: string };
      if (!response.ok) {
        throw new Error(
          "detail" in data && data.detail
            ? data.detail
            : t("Failed to save network settings."),
        );
      }
      const next = data as NetworkSettingsPayload;
      setPayload(next);
      setDraft(normalizeDraft(next));
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    }
  }, [t]);

  useEffect(() => {
    registerExtension("network", { dirty, save });
    return () => registerExtension("network", null);
  }, [dirty, save, registerExtension]);

  return (
    <div data-tour="tour-network">
      <SettingsPageHeader
        title={t("Network")}
        description={t(
          "Manage the local ports used by the NexaTutor backend and Web UI.",
        )}
      />

      <p className="mb-7 text-[12px] text-[var(--muted-foreground)]">
        {t("Network changes take effect after restart.")}
      </p>

      <ChatResponseTimeoutSection />

      {loading && (
        <div className="flex items-center gap-2 text-[13px] text-[var(--muted-foreground)]">
          <Loader2 className="h-4 w-4 animate-spin" />
          {t("Loading network settings...")}
        </div>
      )}

      {!loading && error && (
        <div className="rounded-xl border border-red-500/30 bg-red-500/10 px-4 py-3 text-[13px] text-red-600 dark:text-red-300">
          {error}
        </div>
      )}

      {!loading && payload && draft && (
        <>
          <div className="mb-7 grid grid-cols-1 gap-3 md:grid-cols-2">
            <DetailTile
              label={t("Backend")}
              value={payload.effective.backend_url}
              tone="ok"
            />
            <DetailTile
              label={t("Web UI")}
              value={payload.effective.frontend_url}
              tone="ok"
            />
          </div>

          <SettingSection
            title={t("Runtime ports")}
            description={t(
              "These ports are read during startup. Docker port mappings must match the container-side values.",
            )}
          >
            <SettingRow
              title={t("Backend port")}
              description={t("FastAPI listens on this port.")}
              control={
                <input
                  className={`${inputClass} w-28`}
                  type="number"
                  min={1}
                  max={65535}
                  value={draft.backend_port}
                  onChange={(event) =>
                    setDraft((current) =>
                      current
                        ? {
                            ...current,
                            backend_port: Number(event.target.value),
                          }
                        : current,
                    )
                  }
                />
              }
            />
            <SettingRow
              title={t("Frontend port")}
              description={t("Next.js serves the Web UI on this port.")}
              control={
                <input
                  className={`${inputClass} w-28`}
                  type="number"
                  min={1}
                  max={65535}
                  value={draft.frontend_port}
                  onChange={(event) =>
                    setDraft((current) =>
                      current
                        ? {
                            ...current,
                            frontend_port: Number(event.target.value),
                          }
                        : current,
                    )
                  }
                />
              }
            />
          </SettingSection>

        </>
      )}
    </div>
  );
}

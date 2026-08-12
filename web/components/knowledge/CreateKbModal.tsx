"use client";

import { useEffect, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { FolderSearch, Link2, Loader2, Plus } from "lucide-react";
import Modal from "@/components/common/Modal";
import {
  probeLinkedFolder,
  type KnowledgeUploadPolicy,
  type LinkedFolderProbe,
} from "@/lib/knowledge-api";
import { validateFiles } from "@/lib/knowledge-helpers";
import FileDropZone from "./FileDropZone";

const OBSIDIAN_SOURCE = "obsidian";
type Mode = "new" | "link";

interface CreateKbModalProps {
  isOpen: boolean;
  onClose: () => void;
  uploadPolicy: KnowledgeUploadPolicy;
  onCreate: (params: { name: string; files: File[] }) => Promise<void>;
  onConnectLinkedFolder: (params: {
    name: string;
    folderPath: string;
    provider: string;
  }) => Promise<void>;
  onConnectObsidian: (params: { name: string; vaultPath: string }) => Promise<void>;
  initialMode?: Mode;
  initialSource?: string;
}

export default function CreateKbModal({
  isOpen,
  onClose,
  uploadPolicy,
  onCreate,
  onConnectLinkedFolder,
  onConnectObsidian,
  initialMode = "new",
  initialSource,
}: CreateKbModalProps) {
  const { t } = useTranslation();
  const [mode, setMode] = useState<Mode>("new");
  const [name, setName] = useState("");
  const [files, setFiles] = useState<File[]>([]);
  const [source, setSource] = useState(OBSIDIAN_SOURCE);
  const [folderPath, setFolderPath] = useState("");
  const [probe, setProbe] = useState<LinkedFolderProbe | null>(null);
  const [probing, setProbing] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const wasOpen = useRef(false);

  useEffect(() => {
    const justOpened = isOpen && !wasOpen.current;
    wasOpen.current = isOpen;
    if (!justOpened) return;
    setMode(initialMode);
    setSource(initialSource || OBSIDIAN_SOURCE);
    setName("");
    setFiles([]);
    setFolderPath("");
    setProbe(null);
    setError(null);
  }, [initialMode, initialSource, isOpen]);

  useEffect(() => setProbe(null), [folderPath, source]);

  const selection = validateFiles(files, uploadPolicy, t);
  const trimmedName = name.trim();
  const trimmedPath = folderPath.trim();
  const isObsidian = source === OBSIDIAN_SOURCE;
  const canSubmit =
    !submitting &&
    !!trimmedName &&
    (mode === "new"
      ? selection.validFiles.length > 0
      : !!trimmedPath && (isObsidian || !!probe?.ok));

  const handleProbe = async () => {
    if (!trimmedPath || isObsidian || probing) return;
    setProbing(true);
    setError(null);
    try {
      setProbe(
        await probeLinkedFolder({
          folderPath: trimmedPath,
          provider: "llamaindex",
        }),
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setProbing(false);
    }
  };

  const handleSubmit = async () => {
    if (!canSubmit) return;
    setSubmitting(true);
    setError(null);
    try {
      if (mode === "new") {
        await onCreate({ name: trimmedName, files: selection.validFiles });
      } else if (isObsidian) {
        await onConnectObsidian({ name: trimmedName, vaultPath: trimmedPath });
      } else {
        await onConnectLinkedFolder({
          name: trimmedName,
          folderPath: trimmedPath,
          provider: "llamaindex",
        });
      }
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={submitting ? () => {} : onClose}
      title={t("Create knowledge base")}
      titleIcon={<Plus size={16} />}
      width="lg"
      closeOnBackdrop={!submitting}
      closeOnEscape={!submitting}
      footer={
        <div className="flex items-center justify-end gap-2">
          <button type="button" onClick={onClose} disabled={submitting} className="rounded-md px-3 py-1.5 text-[12.5px] text-[var(--muted-foreground)] disabled:opacity-40">
            {t("Cancel")}
          </button>
          <button type="button" onClick={() => void handleSubmit()} disabled={!canSubmit} className="inline-flex items-center gap-1.5 rounded-md bg-[var(--primary)] px-3.5 py-1.5 text-[12.5px] font-medium text-[var(--primary-foreground)] disabled:opacity-40">
            {submitting ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : mode === "new" ? <Plus size={14} /> : <Link2 size={14} />}
            {mode === "new" ? t("Create") : t("Connect")}
          </button>
        </div>
      }
    >
      <div className="space-y-4 px-5 py-4">
        <div className="grid grid-cols-2 gap-2">
          {(["new", "link"] as Mode[]).map((item) => (
            <button key={item} type="button" disabled={submitting} onClick={() => setMode(item)} className={`rounded-xl border p-3 text-left text-[13px] font-medium ${mode === item ? "border-[var(--primary)] bg-[var(--primary)]/5" : "border-[var(--border)]"}`}>
              {item === "new" ? t("Create new") : t("Link existing")}
            </button>
          ))}
        </div>
        <div>
          <label className="mb-1 block text-[11px] font-medium uppercase tracking-wide text-[var(--muted-foreground)]">{t("Knowledge base name")}</label>
          <input value={name} onChange={(event) => setName(event.target.value)} autoFocus disabled={submitting} placeholder={t("e.g. project-papers")} className="w-full rounded-lg border border-[var(--border)] bg-[var(--background)] px-3 py-2 text-[13px] outline-none" />
        </div>
        {mode === "new" ? (
          <div>
            <label className="mb-2 block text-[11px] font-medium uppercase tracking-wide text-[var(--muted-foreground)]">{t("Initial documents")}</label>
            <FileDropZone files={files} onChange={setFiles} uploadPolicy={uploadPolicy} disabled={submitting} />
          </div>
        ) : (
          <>
            <div className="grid grid-cols-2 gap-2">
              <button type="button" onClick={() => setSource(OBSIDIAN_SOURCE)} className={`rounded-xl border p-3 text-left text-[12px] ${isObsidian ? "border-[var(--primary)]" : "border-[var(--border)]"}`}>{t("Obsidian vault")}</button>
              <button type="button" onClick={() => setSource("llamaindex")} className={`rounded-xl border p-3 text-left text-[12px] ${!isObsidian ? "border-[var(--primary)]" : "border-[var(--border)]"}`}>{t("Existing local index")}</button>
            </div>
            <div className="flex gap-2">
              <input value={folderPath} onChange={(event) => setFolderPath(event.target.value)} placeholder={isObsidian ? t("Vault folder path") : t("Index folder path")} className="min-w-0 flex-1 rounded-lg border border-[var(--border)] bg-[var(--background)] px-3 py-2 text-[13px] outline-none" />
              {!isObsidian && <button type="button" onClick={() => void handleProbe()} disabled={!trimmedPath || probing} className="inline-flex items-center gap-1 rounded-lg border border-[var(--border)] px-3 text-[12px] disabled:opacity-40">{probing ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <FolderSearch size={14} />}{t("Check")}</button>}
            </div>
            {probe && <p className={`text-[12px] ${probe.ok ? "text-emerald-600" : "text-red-600"}`}>{probe.ok ? t("Ready to link") : probe.error}</p>}
          </>
        )}
        {error && <pre className="whitespace-pre-wrap rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-[11px] text-red-700">{error}</pre>}
      </div>
    </Modal>
  );
}

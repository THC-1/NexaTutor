"use client";

import Link from "next/link";
import { Brain, Layers, Network } from "lucide-react";
import { useTranslation } from "react-i18next";

export default function MemorySettingsPage() {
  const { t } = useTranslation();
  return (
    <div className="space-y-6" data-tour="tour-memory">
      <header className="space-y-2">
        <div className="flex items-center gap-2">
          <Brain className="h-4 w-4 text-[var(--primary)]" />
          <h1 className="text-[18px] font-semibold text-[var(--foreground)]">{t("Memory")}</h1>
        </div>
        <p className="max-w-2xl text-[13px] leading-relaxed text-[var(--muted-foreground)]">
          {t("Memory is managed from the learning view. Your saved content stays local and can be reviewed there.")}
        </p>
      </header>
      <div className="grid gap-3 sm:grid-cols-3">
        <Link href="/memory" className="rounded-lg border border-[var(--border)] p-4 hover:border-[var(--primary)]/40">
          <Brain className="mb-2 h-4 w-4" />
          <div className="text-[13px] font-medium">{t("Open memory")}</div>
        </Link>
        <Link href="/memory/l1" className="rounded-lg border border-[var(--border)] p-4 hover:border-[var(--primary)]/40">
          <Layers className="mb-2 h-4 w-4" />
          <div className="text-[13px] font-medium">{t("L1 workspace mirror")}</div>
        </Link>
        <Link href="/memory/l3" className="rounded-lg border border-[var(--border)] p-4 hover:border-[var(--primary)]/40">
          <Network className="mb-2 h-4 w-4" />
          <div className="text-[13px] font-medium">{t("L3 knowledge")}</div>
        </Link>
      </div>
    </div>
  );
}

import { Bot } from "lucide-react";

/**
 * Vendor logos for LLM/embedding providers, keyed by binding name
 * (see deeptutor/services/provider_registry.py). SVGs are vendored from
 * @lobehub/icons-static-svg (MIT) into /public/provider-icons.
 *
 * `mono` icons are solid-fill brand marks that render black as <img>;
 * they get `dark:invert` so they stay visible on dark backgrounds.
 * Unknown/custom bindings fall back to the generic Bot icon.
 */
const PROVIDER_ICONS: Record<string, { file: string; mono?: boolean }> = {
  openai: { file: "openai.svg", mono: true },
  openai_codex: { file: "openai.svg", mono: true },
  anthropic: { file: "anthropic.svg", mono: true },
  custom_anthropic: { file: "anthropic.svg", mono: true },
  deepseek: { file: "deepseek-color.svg" },
  gemini: { file: "gemini-color.svg" },
  google: { file: "gemini-color.svg" },
  // Embedding providers remain independently configurable in P8.
  azure_openai: { file: "azure-color.svg" },
  openrouter: { file: "openrouter.svg", mono: true },
  siliconflow: { file: "siliconcloud-color.svg" },
  dashscope: { file: "qwen-color.svg" },
  aliyun: { file: "qwen-color.svg" },
  vllm: { file: "vllm-color.svg" },
  ollama: { file: "ollama.svg", mono: true },
  cohere: { file: "cohere-color.svg" },
  jina: { file: "jina.svg", mono: true },
  // Search providers (web/components/settings/shared.tsx). brave/duckduckgo/
  // searxng come from simple-icons with the brand color baked in.
  tavily: { file: "tavily-color.svg" },
  perplexity: { file: "perplexity-color.svg" },
  exa: { file: "exa-color.svg" },
  brave: { file: "brave.svg" },
  duckduckgo: { file: "duckduckgo.svg" },
  searxng: { file: "searxng.svg" },
  baidu: { file: "baidu-color.svg" },
};

export default function ProviderIcon({
  provider,
  size = 13,
  className = "",
}: {
  provider?: string | null;
  size?: number;
  className?: string;
}) {
  const spec = provider
    ? PROVIDER_ICONS[provider.trim().toLowerCase()]
    : undefined;
  if (!spec) {
    return (
      <Bot
        size={size}
        strokeWidth={1.7}
        className={`shrink-0 ${className}`.trim()}
      />
    );
  }
  return (
    // eslint-disable-next-line @next/next/no-img-element
    <img
      src={`/provider-icons/${spec.file}`}
      alt=""
      aria-hidden
      width={size}
      height={size}
      draggable={false}
      className={`shrink-0 select-none ${spec.mono ? "dark:invert" : ""} ${className}`.trim()}
    />
  );
}

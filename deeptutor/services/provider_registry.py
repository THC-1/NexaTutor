"""Product-scoped LLM provider registry for NexaTutor."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from pydantic.alias_generators import to_snake


@dataclass(frozen=True)
class ProviderSpec:
    name: str
    keywords: tuple[str, ...]
    env_key: str
    display_name: str = ""
    backend: str = "openai_compat"
    env_extras: tuple[tuple[str, str], ...] = ()
    is_gateway: bool = False
    is_local: bool = False
    detect_by_key_prefix: str = ""
    detect_by_base_keyword: str = ""
    default_api_base: str = ""
    strip_model_prefix: bool = False
    supports_max_completion_tokens: bool = False
    supports_prompt_caching: bool = False
    supports_stream_options: bool = True
    model_overrides: tuple[tuple[str, dict[str, Any]], ...] = ()
    is_oauth: bool = False
    is_direct: bool = False
    thinking_style: str = ""
    reasoning_model_patterns: tuple[str, ...] = ()

    @property
    def mode(self) -> str:
        if self.is_oauth:
            return "oauth"
        if self.is_direct:
            return "direct"
        if self.is_gateway:
            return "gateway"
        if self.is_local:
            return "local"
        return "standard"

    @property
    def auth_mode(self) -> str:
        return "oauth" if self.is_oauth else "api_key"

    @property
    def label(self) -> str:
        return self.display_name or self.name.title()


PROVIDER_ALIASES = {
    "google": "gemini",
    "google_genai": "gemini",
    "claude": "anthropic",
    "openai_compatible": "custom",
    "openai-compatible": "custom",
    "anthropic_compatible": "custom_anthropic",
    "anthropic-compatible": "custom_anthropic",
    "openai-codex": "openai_codex",
}

# Legacy bindings remain readable but no longer select a dedicated adapter.
# The catalog file itself is intentionally left untouched.
LEGACY_ANTHROPIC_COMPATIBLE_PROVIDERS = frozenset({"minimax_anthropic"})
LEGACY_OPENAI_COMPATIBLE_PROVIDERS = frozenset(
    {
        "azure",
        "azure_openai",
        "azureopenai",
        "openrouter",
        "edenai",
        "eden_ai",
        "aihubmix",
        "siliconflow",
        "novita",
        "novita_ai",
        "atlascloud",
        "atlas",
        "atlas_cloud",
        "volcengine",
        "volcengine_coding_plan",
        "volcenginecodingplan",
        "byteplus",
        "byteplus_coding_plan",
        "bytepluscodingplan",
        "github_copilot",
        "zhipu",
        "dashscope",
        "moonshot",
        "minimax",
        "mistral",
        "stepfun",
        "xiaomi_mimo",
        "vllm",
        "ollama",
        "lm_studio",
        "llama_cpp",
        "lemonade",
        "ovms",
        "nvidia_nim",
        "groq",
        "qianfan",
    }
)


def _normalized_name(name: str | None) -> str | None:
    if not name or not name.strip():
        return None
    return to_snake(name.strip().replace("-", "_"))


def canonical_provider_name(name: str | None) -> str | None:
    key = _normalized_name(name)
    return PROVIDER_ALIASES.get(key, key) if key else None


def compatibility_provider_name(name: str | None) -> str | None:
    """Map a removed binding to a protocol-level compatibility entry."""
    key = _normalized_name(name)
    if key in LEGACY_ANTHROPIC_COMPATIBLE_PROVIDERS:
        return "custom_anthropic"
    if key in LEGACY_OPENAI_COMPATIBLE_PROVIDERS:
        return "custom"
    return canonical_provider_name(name)


PROVIDERS: tuple[ProviderSpec, ...] = (
    ProviderSpec(
        name="custom",
        keywords=(),
        env_key="",
        display_name="OpenAI-compatible",
        backend="openai_compat",
        is_direct=True,
    ),
    ProviderSpec(
        name="custom_anthropic",
        keywords=(),
        env_key="",
        display_name="Anthropic-compatible",
        backend="anthropic",
        is_direct=True,
    ),
    ProviderSpec(
        name="anthropic",
        keywords=("anthropic", "claude"),
        env_key="ANTHROPIC_API_KEY",
        display_name="Anthropic",
        backend="anthropic",
        default_api_base="https://api.anthropic.com/v1",
        supports_prompt_caching=True,
    ),
    ProviderSpec(
        name="openai",
        keywords=("openai", "gpt"),
        env_key="OPENAI_API_KEY",
        display_name="OpenAI",
        default_api_base="https://api.openai.com/v1",
        supports_max_completion_tokens=True,
    ),
    ProviderSpec(
        name="openai_codex",
        keywords=("openai-codex",),
        env_key="",
        display_name="OpenAI Codex",
        backend="openai_codex",
        is_oauth=True,
        default_api_base="https://chatgpt.com/backend-api",
    ),
    ProviderSpec(
        name="deepseek",
        keywords=("deepseek",),
        env_key="DEEPSEEK_API_KEY",
        display_name="DeepSeek",
        default_api_base="https://api.deepseek.com",
        thinking_style="thinking_type",
        reasoning_model_patterns=("deepseek-v4-pro", "deepseek-reasoner"),
    ),
    ProviderSpec(
        name="gemini",
        keywords=("gemini",),
        env_key="GEMINI_API_KEY",
        display_name="Gemini",
        default_api_base="https://generativelanguage.googleapis.com/v1beta/openai/",
    ),
)

NANOBOT_LLM_PROVIDERS: tuple[str, ...] = tuple(spec.name for spec in PROVIDERS)


def find_by_name(name: str | None) -> ProviderSpec | None:
    canonical = canonical_provider_name(name)
    return next((spec for spec in PROVIDERS if spec.name == canonical), None)


def find_by_model(model: str | None) -> ProviderSpec | None:
    if not model:
        return None
    lower = model.lower()
    normalized = lower.replace("-", "_")
    prefix = lower.split("/", 1)[0].replace("-", "_") if "/" in lower else ""
    for spec in PROVIDERS:
        if spec.is_direct or spec.is_oauth:
            continue
        if prefix == spec.name or any(
            keyword in lower or keyword.replace("-", "_") in normalized
            for keyword in spec.keywords
        ):
            return spec
    return None


def find_gateway(
    provider_name: str | None = None,
    api_key: str | None = None,
    api_base: str | None = None,
) -> ProviderSpec | None:
    del api_key, api_base
    spec = find_by_name(provider_name)
    return spec if spec and (spec.is_gateway or spec.is_local) else None


def strip_provider_prefix(model: str, spec: ProviderSpec | None) -> str:
    if model and spec and spec.strip_model_prefix and "/" in model:
        return model.split("/", 1)[1]
    return model


__all__ = [
    "ProviderSpec",
    "PROVIDERS",
    "NANOBOT_LLM_PROVIDERS",
    "PROVIDER_ALIASES",
    "LEGACY_OPENAI_COMPATIBLE_PROVIDERS",
    "LEGACY_ANTHROPIC_COMPATIBLE_PROVIDERS",
    "canonical_provider_name",
    "compatibility_provider_name",
    "find_by_name",
    "find_by_model",
    "find_gateway",
    "strip_provider_prefix",
]

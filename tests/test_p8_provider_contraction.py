from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest

from deeptutor.api.routers import settings as settings_router
from deeptutor.services.config.provider_runtime import (
    EMBEDDING_PROVIDERS,
    SUPPORTED_SEARCH_PROVIDERS,
    resolve_llm_runtime_config,
)
from deeptutor.services.provider_registry import PROVIDERS, find_by_name
from deeptutor.services.subagent.registry import list_backend_kinds


PRODUCT_LLM_PROVIDERS = {
    "openai",
    "anthropic",
    "gemini",
    "deepseek",
    "custom",
    "custom_anthropic",
    "openai_codex",
}

REMOVED_LLM_PROVIDERS = {
    "azure_openai",
    "openrouter",
    "edenai",
    "aihubmix",
    "siliconflow",
    "novita",
    "atlascloud",
    "volcengine",
    "volcengine_coding_plan",
    "byteplus",
    "byteplus_coding_plan",
    "github_copilot",
    "zhipu",
    "dashscope",
    "moonshot",
    "minimax",
    "minimax_anthropic",
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


def _catalog(*, binding: str, model: str, base_url: str = "", api_key: str = "key") -> dict:
    return {
        "services": {
            "llm": {
                "active_profile_id": "p",
                "active_model_id": "m",
                "profiles": [
                    {
                        "id": "p",
                        "name": "Legacy",
                        "binding": binding,
                        "base_url": base_url,
                        "api_key": api_key,
                        "api_version": "",
                        "extra_headers": {},
                        "models": [{"id": "m", "name": model, "model": model}],
                    }
                ],
            }
        }
    }


def test_p8_llm_registry_contains_only_product_entries_and_codex_oauth() -> None:
    assert {spec.name for spec in PROVIDERS} == PRODUCT_LLM_PROVIDERS
    assert all(find_by_name(name) is None for name in REMOVED_LLM_PROVIDERS)


@pytest.mark.parametrize(
    ("binding", "model", "base_url", "api_key", "expected"),
    [
        ("ollama", "llama3.2", "http://localhost:11434/v1", "", "custom"),
        ("github_copilot", "copilot/gpt-4o", "https://api.githubcopilot.com", "", "custom"),
        ("openrouter", "openai/gpt-4o", "https://openrouter.ai/api/v1", "sk-or-old", "custom"),
        ("dashscope", "qwen-max", "https://dashscope.aliyuncs.com/compatible-mode/v1", "old", "custom"),
        ("minimax_anthropic", "claude-sonnet", "https://api.minimax.io/anthropic", "old", "custom_anthropic"),
    ],
)
def test_removed_llm_bindings_fall_back_to_explicit_compatibility_entry(
    binding: str,
    model: str,
    base_url: str,
    api_key: str,
    expected: str,
) -> None:
    resolved = resolve_llm_runtime_config(
        catalog=_catalog(binding=binding, model=model, base_url=base_url, api_key=api_key)
    )
    assert resolved.provider_name == expected
    assert resolved.binding == expected
    assert resolved.effective_url == base_url


def test_p8_provider_choices_match_product_contract() -> None:
    choices = settings_router._provider_choices()
    assert {item["value"] for item in choices["llm"]} == PRODUCT_LLM_PROVIDERS


def test_cli_init_wizard_only_offers_product_api_key_providers() -> None:
    from deeptutor_cli.init_wizard import FEATURED_LLM_PROVIDERS, LLM_FALLBACK_MODELS

    assert set(FEATURED_LLM_PROVIDERS) == PRODUCT_LLM_PROVIDERS - {"openai_codex"}
    assert set(LLM_FALLBACK_MODELS) <= PRODUCT_LLM_PROVIDERS - {"openai_codex"}


def test_p8_preserves_embedding_search_and_local_subagent_registries() -> None:
    assert {"openai", "gemini", "custom", "ollama", "vllm"} <= set(EMBEDDING_PROVIDERS)
    assert {"brave", "tavily", "duckduckgo", "none"} <= SUPPORTED_SEARCH_PROVIDERS
    assert set(list_backend_kinds()) == {
        "claude_code",
        "codex",
        "gemini",
        "kimi",
        "opencode",
        "mimo",
    }


class _CatalogService:
    def __init__(self, catalog: dict) -> None:
        self.catalog = deepcopy(catalog)

    def load(self) -> dict:
        return deepcopy(self.catalog)

    def public_catalog(self, catalog: dict | None = None) -> dict:
        result = deepcopy(catalog or self.catalog)
        for service in result.get("services", {}).values():
            for profile in service.get("profiles", []):
                profile["api_key_set"] = bool(profile.get("api_key"))
                profile["api_key"] = ""
        return result


@pytest.mark.asyncio
async def test_settings_response_never_contains_plaintext_provider_keys(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    catalog = _catalog(
        binding="openai",
        model="gpt-4o-mini",
        base_url="https://api.openai.com/v1",
        api_key="p8-plaintext-secret",
    )
    monkeypatch.setattr(settings_router, "get_model_catalog_service", lambda: _CatalogService(catalog))

    response = await settings_router.get_settings()

    assert "p8-plaintext-secret" not in str(response)
    profile = response["catalog"]["services"]["llm"]["profiles"][0]
    assert profile["api_key"] == ""
    assert profile["api_key_set"] is True


def test_catalog_secret_merge_preserves_replaces_and_clears_keys() -> None:
    from deeptutor.services.config.model_catalog import ModelCatalogService

    existing = _catalog(binding="openai", model="gpt-4o-mini", api_key="stored-secret")

    untouched = deepcopy(existing)
    untouched_profile = untouched["services"]["llm"]["profiles"][0]
    untouched_profile.update(api_key="", api_key_set=True)
    assert (
        ModelCatalogService.merge_catalog_secrets(untouched, existing)["services"]["llm"]
        ["profiles"][0]["api_key"]
        == "stored-secret"
    )

    replaced = deepcopy(untouched)
    replaced["services"]["llm"]["profiles"][0]["api_key"] = "replacement"
    assert (
        ModelCatalogService.merge_catalog_secrets(replaced, existing)["services"]["llm"]
        ["profiles"][0]["api_key"]
        == "replacement"
    )

    cleared = deepcopy(untouched)
    cleared["services"]["llm"]["profiles"][0]["api_key_clear"] = True
    assert (
        ModelCatalogService.merge_catalog_secrets(cleared, existing)["services"]["llm"]
        ["profiles"][0]["api_key"]
        == ""
    )


def test_removed_dedicated_llm_backends_are_not_importable() -> None:
    root = Path(__file__).resolve().parents[1]
    provider_core = root / "deeptutor" / "services" / "llm" / "provider_core"
    assert not (provider_core / "azure_openai_provider.py").exists()
    assert not (provider_core / "github_copilot_provider.py").exists()

    sources = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (
            root / "deeptutor" / "services" / "llm" / "provider_factory.py",
            provider_core / "__init__.py",
            root / "deeptutor" / "core" / "agentic" / "client.py",
        )
    )
    assert "azure_openai_provider" not in sources
    assert "github_copilot_provider" not in sources
    assert "GitHubCopilotProvider" not in sources
    assert "AzureOpenAIProvider" not in sources


def test_github_copilot_only_dependency_is_removed() -> None:
    root = Path(__file__).resolve().parents[1]
    dependency_files = (
        root / "pyproject.toml",
        root / "requirements" / "cli.txt",
        root / "packaging" / "deeptutor-cli" / "pyproject.toml",
    )
    assert all("oauth-cli-kit" not in path.read_text(encoding="utf-8") for path in dependency_files)

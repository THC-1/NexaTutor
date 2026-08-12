from deeptutor.services.provider_registry import (
    PROVIDERS,
    compatibility_provider_name,
    find_by_name,
)


def test_product_provider_registry_is_scoped() -> None:
    assert {spec.name for spec in PROVIDERS} == {
        "openai",
        "anthropic",
        "gemini",
        "deepseek",
        "custom",
        "custom_anthropic",
        "openai_codex",
    }


def test_compatibility_aliases_remain_protocol_level_only() -> None:
    assert find_by_name("openai-compatible").name == "custom"
    assert find_by_name("anthropic-compatible").name == "custom_anthropic"
    assert compatibility_provider_name("openrouter") == "custom"
    assert compatibility_provider_name("minimax_anthropic") == "custom_anthropic"
    assert find_by_name("openrouter") is None
    assert find_by_name("github-copilot") is None


def test_openai_codex_provider_is_oauth_backed() -> None:
    spec = find_by_name("openai_codex")
    assert spec is not None
    assert spec.auth_mode == "oauth"
    assert spec.env_key == ""

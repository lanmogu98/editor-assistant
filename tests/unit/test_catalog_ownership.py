"""Focused contract tests for the editor-owned LLM catalog."""

import argparse
import hashlib
import inspect
import warnings
from importlib.resources import files
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

import llm_exec_core
from llm_exec_core import LLMClient as CoreLLMClient
from llm_exec_core import config as core_config
from llm_exec_core.config import ModelDetails, ProviderSettings

pytestmark = pytest.mark.unit

EXPECTED_MODELS = [
    "deepseek-v4-flash-volc",
    "deepseek-v4-pro-volc",
    "deepseek-v4-flash",
    "deepseek-v4-pro",
    "gemini-3-flash",
    "gemini-3.1-flash-lite",
    "gemini-3.1-pro",
    "gemini-3.5-flash",
    "qwen3.6-flash",
    "glm-5.2",
    "glm-5",
    "glm-5.1",
    "glm-5.2-or",
    "glm-5-or",
    "glm-5.1-or",
    "glm-5-turbo-or",
    "doubao-seed-2.1-pro",
    "doubao-seed-1.6",
    "gpt-5.5-or",
    "claude-sonnet-5-or",
    "claude-opus-4.8-or",
]

RELEASE_CORE_CATALOG_SHA256 = (
    "490c5df6988c43b65badf28f75a8507e09c11505a2d4f47ecb2bda42984abfd4"
)

CUSTOM_CONFIG = {
    "custom-provider": {
        "api_key_env_var": "CUSTOM_TEST_API_KEY",
        "api_base_url": "https://example.invalid/v1/chat/completions",
        "temperature": 0.25,
        "max_tokens": 128,
        "context_window": 4096,
        "pricing_currency": "$",
        "models": {
            "custom-model": {
                "id": "custom/model",
                "pricing": {"input": 0.1, "output": 0.2},
            }
        },
    }
}


def _write_custom_config(tmp_path: Path) -> Path:
    config_path = tmp_path / "custom_llm_config.yml"
    config_path.write_text(yaml.safe_dump(CUSTOM_CONFIG), encoding="utf-8")
    return config_path


def test_app_catalog_is_owned_independently_from_core_041():
    from editor_assistant.config.constants import LLM_CONFIG_PATH

    core_catalog_path = Path(core_config.__file__).with_name("llm_config.yml")
    app_bytes = LLM_CONFIG_PATH.read_bytes()
    core_bytes = core_catalog_path.read_bytes()

    assert llm_exec_core.__version__ == "0.4.1"
    assert (
        hashlib.sha256(core_bytes).hexdigest() == RELEASE_CORE_CATALOG_SHA256
    )
    assert app_bytes != core_bytes
    assert yaml.safe_load(app_bytes) != yaml.safe_load(core_bytes)


def test_catalog_is_available_as_package_data():
    from editor_assistant.config.constants import LLM_CONFIG_PATH

    catalog = files("editor_assistant.config").joinpath("llm_config.yml")

    assert catalog.is_file()
    assert catalog.read_bytes() == LLM_CONFIG_PATH.read_bytes()
    assert (
        hashlib.sha256(catalog.read_bytes()).hexdigest()
        != RELEASE_CORE_CATALOG_SHA256
    )


def test_project_metadata_packages_catalog_and_constrains_core():
    pyproject = (
        Path(__file__)
        .parents[2]
        .joinpath("pyproject.toml")
        .read_text(encoding="utf-8")
    )

    assert '"llm-exec-core>=0.4.1,<0.5.0"' in pyproject
    assert '"config/llm_config.yml"' in pyproject
    assert 'path = "../llm-exec-core", editable = true' in pyproject


def test_default_discovery_uses_app_catalog_without_key_or_network(
    monkeypatch,
):
    from editor_assistant.config.constants import LLM_CONFIG_PATH
    from editor_assistant.llm_client import LLMClient

    app_catalog = yaml.safe_load(LLM_CONFIG_PATH.read_text(encoding="utf-8"))
    for provider_name, provider in app_catalog.items():
        if not provider_name.startswith("_"):
            monkeypatch.delenv(provider["api_key_env_var"], raising=False)
            for alias in provider.get("api_key_env_aliases", []):
                monkeypatch.delenv(alias, raising=False)

    with (
        patch(
            "llm_exec_core.client.httpx.AsyncClient",
            side_effect=AssertionError(
                "discovery must not create an HTTP client"
            ),
        ),
        warnings.catch_warnings(),
    ):
        warnings.simplefilter("error", DeprecationWarning)
        models = LLMClient.get_supported_models()

    assert models == EXPECTED_MODELS


def test_cli_parser_uses_exact_catalog_and_glm_52_default():
    from editor_assistant.cli import DEFAULT_MODEL, add_common_arguments

    parser = argparse.ArgumentParser(add_help=False)
    add_common_arguments(parser)
    args = parser.parse_args([])
    model_action = next(
        action for action in parser._actions if action.dest == "model"
    )

    assert DEFAULT_MODEL == "glm-5.2-or"
    assert args.model == "glm-5.2-or"
    assert list(model_action.choices) == EXPECTED_MODELS


def test_default_client_construction_uses_app_catalog(monkeypatch):
    from editor_assistant.llm_client import LLMClient

    monkeypatch.setenv("ZHIPU_API_KEY_OPENROUTER", "test-key")

    with warnings.catch_warnings():
        warnings.simplefilter("error", DeprecationWarning)
        client = LLMClient("glm-5.2-or")

    assert client.model_name == "glm-5.2-or"
    assert client.model == "z-ai/glm-5.2"
    assert client.provider_name == "zhipu-openrouter"


@pytest.mark.parametrize("source_kind", ["dict", "path"])
def test_explicit_client_construction_and_discovery_preserve_source(
    monkeypatch, tmp_path, source_kind
):
    from editor_assistant.llm_client import LLMClient

    config_source = CUSTOM_CONFIG
    if source_kind == "path":
        config_source = _write_custom_config(tmp_path)
    monkeypatch.setenv("CUSTOM_TEST_API_KEY", "test-key")

    client = LLMClient("custom-model", config_source=config_source)

    assert client.model == "custom/model"
    assert client.provider_name == "custom-provider"
    assert client.context_window == 4096
    assert LLMClient.get_supported_models(config_source) == ["custom-model"]


@pytest.mark.parametrize(
    "order", [("default", "explicit"), ("explicit", "default")]
)
def test_default_and_explicit_discovery_are_isolated_in_both_orders(
    order,
):
    from editor_assistant.llm_client import LLMClient

    results = {}

    for source_name in order:
        if source_name == "default":
            results[source_name] = LLMClient.get_supported_models()
        else:
            results[source_name] = LLMClient.get_supported_models(
                CUSTOM_CONFIG
            )

    assert results["default"] == EXPECTED_MODELS
    assert results["explicit"] == ["custom-model"]


def test_config_compatibility_api_defaults_and_explicit_override():
    from editor_assistant.config.llm_models import (
        get_model_details,
        get_provider_settings,
        get_supported_models,
        load_all_settings,
    )

    assert get_supported_models() == EXPECTED_MODELS
    settings = load_all_settings()
    assert list(settings) == [
        "deepseek-volcengine",
        "deepseek",
        "gemini",
        "qwen",
        "zhipu",
        "zhipu-openrouter",
        "doubao",
        "openai-openrouter",
        "anthropic-openrouter",
    ]
    assert (
        get_provider_settings("zhipu-openrouter")
        == settings["zhipu-openrouter"]
    )

    provider, model = get_model_details("glm-5.2-or")
    assert isinstance(provider, ProviderSettings)
    assert isinstance(model, ModelDetails)
    assert model.id == "z-ai/glm-5.2"

    assert get_supported_models(CUSTOM_CONFIG) == ["custom-model"]
    custom_provider, custom_model = get_model_details(
        "custom-model", CUSTOM_CONFIG
    )
    assert custom_provider.api_key_env_var == "CUSTOM_TEST_API_KEY"
    assert custom_model.id == "custom/model"


def test_llm_client_public_imports_and_async_contract():
    from editor_assistant.llm_client import (
        ExecutionMetadata,
        LLMClient,
        LLMResult,
        ResponseCache,
        StructuredOutputValidationError,
        TokenUsage,
    )

    assert LLMClient is not CoreLLMClient
    assert issubclass(LLMClient, CoreLLMClient)
    assert inspect.iscoroutinefunction(LLMClient.generate)
    assert inspect.iscoroutinefunction(LLMClient.generate_response)
    assert list(inspect.signature(LLMClient.__init__).parameters) == [
        "self",
        "model_name",
        "thinking_level",
        "config_source",
    ]
    assert all(
        symbol is not None
        for symbol in (
            ExecutionMetadata,
            LLMResult,
            ResponseCache,
            StructuredOutputValidationError,
            TokenUsage,
        )
    )


def test_removed_legacy_aliases_are_not_restored():
    from editor_assistant.llm_client import LLMClient

    models = LLMClient.get_supported_models()

    assert "glm-5.2-or" in models
    assert "glm-4.7-or" not in models
    assert "glm-4.6-or" not in models

"""Focused offline tests for the app-owned Qwen catalog policy."""

from pathlib import Path
from unittest.mock import patch

import pytest

from editor_assistant.config.llm_models import (
    get_model_details,
    get_supported_models,
)
from editor_assistant.llm_client import LLMClient

pytestmark = pytest.mark.unit

PRIMARY_KEY = "QWEN_API_KEY"
FALLBACK_KEY = "DASHSCOPE_API_KEY"
ENDPOINT_VARIABLE = "QWEN_API_BASE_URL"
STATIC_ENDPOINT = (
    "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
)
DECISION_RECORD = (
    Path(__file__).parents[2]
    / "docs"
    / "design_docs"
    / "issue_31_qwen_catalog_decision.md"
)


@pytest.fixture(autouse=True)
def _clear_qwen_environment(monkeypatch):
    for environment_name in (PRIMARY_KEY, FALLBACK_KEY, ENDPOINT_VARIABLE):
        monkeypatch.delenv(environment_name, raising=False)


def _client(monkeypatch, *, primary=None, fallback=None, endpoint=None):
    if primary is not None:
        monkeypatch.setenv(PRIMARY_KEY, primary)
    if fallback is not None:
        monkeypatch.setenv(FALLBACK_KEY, fallback)
    if endpoint is not None:
        monkeypatch.setenv(ENDPOINT_VARIABLE, endpoint)
    return LLMClient("qwen3.6-flash")


def test_qwen_catalog_has_exact_single_model_and_effective_policy(monkeypatch):
    qwen_models = [
        model_name
        for model_name in get_supported_models()
        if model_name.startswith("qwen")
    ]
    provider, model = get_model_details("qwen3.6-flash")
    client = _client(monkeypatch, primary="primary-test-key")

    assert qwen_models == ["qwen3.6-flash"]
    assert model.id == "qwen3.6-flash"
    assert client.context_window == 1_000_000
    assert client.max_tokens == 65_536
    assert client.output_token_field == "max_tokens"
    assert client.request_overrides == {"enable_thinking": False}
    assert provider.api_key_env_var == PRIMARY_KEY
    assert provider.api_key_env_aliases == [FALLBACK_KEY]
    assert provider.api_base_url_env_var == ENDPOINT_VARIABLE
    assert provider.api_base_url == STATIC_ENDPOINT


def test_qwen_capabilities_and_historical_pricing_are_exact():
    _, model = get_model_details("qwen3.6-flash")

    assert model.capabilities is not None
    assert model.capabilities.model_dump() == {
        "version": "qwen-bailian-2026-07-22",
        "source": "https://help.aliyun.com/en/model-studio/text-generation-model/",
        "source_date": "2026-07-22",
        "strict_response_schema": False,
        "json_object_response": True,
        "tools": True,
        "tool_streaming": True,
        "tool_choice": True,
        "parallel_tool_calls": True,
        "reasoning_controls": [],
        "openrouter_supported_parameters": [],
    }
    assert model.pricing.input == 0.30
    assert model.pricing.output == 0.60


def test_qwen_primary_key_precedes_fallback(monkeypatch):
    client = _client(
        monkeypatch,
        primary="primary-test-key",
        fallback="fallback-test-key",
    )

    assert client.api_key == "primary-test-key"
    assert client.headers["Authorization"] == "Bearer primary-test-key"


def test_qwen_falls_back_to_dashscope_key(monkeypatch):
    client = _client(monkeypatch, fallback="fallback-test-key")

    assert client.api_key == "fallback-test-key"
    assert client.headers["Authorization"] == "Bearer fallback-test-key"


def test_qwen_missing_keys_fail_without_http(monkeypatch):
    with patch("llm_exec_core.client.httpx.AsyncClient") as async_client:
        with pytest.raises(ValueError) as error:
            _client(monkeypatch)

    message = str(error.value)
    assert PRIMARY_KEY in message
    assert FALLBACK_KEY in message
    async_client.assert_not_called()


def test_qwen_invalid_key_does_not_leak_secret(monkeypatch):
    secret = "secret-prefix\nsecret-suffix"

    with pytest.raises(ValueError) as error:
        _client(monkeypatch, primary=secret, fallback="later-test-key")

    message = str(error.value)
    assert PRIMARY_KEY in message
    assert secret not in message
    assert "secret-prefix" not in message
    assert "secret-suffix" not in message
    assert "later-test-key" not in message


@pytest.mark.parametrize(
    ("endpoint", "expected"),
    [
        (
            "https://workspace.cn-beijing.maas.aliyuncs.com/"
            "compatible-mode/v1",
            "https://workspace.cn-beijing.maas.aliyuncs.com/"
            "compatible-mode/v1/chat/completions",
        ),
        (
            "https://workspace.cn-beijing.maas.aliyuncs.com/"
            "compatible-mode/v1/chat/completions",
            "https://workspace.cn-beijing.maas.aliyuncs.com/"
            "compatible-mode/v1/chat/completions",
        ),
    ],
)
def test_qwen_endpoint_override_accepts_sdk_and_full_forms(
    monkeypatch, endpoint, expected
):
    client = _client(
        monkeypatch,
        primary="primary-test-key",
        endpoint=endpoint,
    )

    assert client.api_url == expected


def test_qwen_static_endpoint_is_the_unset_override_fallback(monkeypatch):
    client = _client(monkeypatch, primary="primary-test-key")

    assert client.api_url == STATIC_ENDPOINT


def test_qwen_invalid_endpoint_fails_before_http(monkeypatch):
    with patch("llm_exec_core.client.httpx.AsyncClient") as async_client:
        with pytest.raises(ValueError) as error:
            _client(
                monkeypatch,
                primary="primary-test-key",
                endpoint="http://secret-host.invalid/v1",
            )

    message = str(error.value)
    assert ENDPOINT_VARIABLE in message
    assert "secret-host" not in message
    async_client.assert_not_called()


@pytest.mark.parametrize("stream", [False, True])
def test_qwen_exact_request_plan_forces_non_thinking(monkeypatch, stream):
    client = _client(monkeypatch, primary="primary-test-key")

    with patch(
        "llm_exec_core.client.httpx.AsyncClient",
        side_effect=AssertionError("request planning must not create HTTP"),
    ):
        payload, planning = client._build_request_plan(
            "Hello", stream, None, None
        )

    expected = {
        "model": "qwen3.6-flash",
        "messages": [{"role": "user", "content": "Hello"}],
        "temperature": 0.6,
        "stream": stream,
        "max_tokens": 65_536,
        "enable_thinking": False,
    }
    if stream:
        expected["stream_options"] = {"include_usage": True}

    assert payload == expected
    assert "reasoning_effort" not in payload
    assert planning["strategy"] == "raw"


def test_qwen_json_object_preference_uses_non_strict_fallback(monkeypatch):
    client = _client(monkeypatch, primary="primary-test-key")

    payload, planning = client._build_request_plan(
        "Return JSON",
        False,
        None,
        {
            "schema": {"type": "object"},
            "mode": "prefer",
        },
    )

    assert payload["response_format"] == {"type": "json_object"}
    assert payload["enable_thinking"] is False
    assert planning["strategy"] == "json_object"
    assert planning["fallback_reason"] == "strict_schema_not_supported"


def test_qwen_thinking_level_is_rejected_before_http(monkeypatch):
    monkeypatch.setenv(PRIMARY_KEY, "primary-test-key")

    with patch("llm_exec_core.client.httpx.AsyncClient") as async_client:
        with pytest.raises(
            ValueError, match="thinking_level.*reasoning_effort"
        ):
            LLMClient("qwen3.6-flash", thinking_level="high")

    async_client.assert_not_called()


def test_qwen_decision_record_covers_sources_candidates_and_limitations():
    record = DECISION_RECORD.read_text(encoding="utf-8")

    for required_text in (
        "2026-07-22",
        "https://github.com/lanmogu98/llm-exec-core/releases/tag/0.4.1",
        "qwen3.6-flash-2026-04-16",
        "qwen3.7",
        "qwen3.8",
        "qwen3.6-plus",
        "qwen3.6-max",
        "qwen3.5",
        "qwen3-max",
        "qwen-max",
        "qwen-plus",
        "qwen-turbo",
        "max_completion_tokens",
        "non-authoritative",
        "llm-exec-core/issues/23",
        "editor-assistant/issues/20",
        "Rollback",
    ):
        assert required_text in record

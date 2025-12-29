"""
Unit tests for LLMClient.

Note: These tests validate structure and basic functionality.
Integration tests with real APIs are in tests/integration/.
"""

import pytest


@pytest.fixture(autouse=True)
def _set_dummy_api_key_for_unit_tests(monkeypatch):
    """
    IMPORTANT (beginner note):
    `LLMClient.__init__()` *requires* an API key env var to exist, even if we never
    make a network call.

    For unit tests we set a dummy key so we can construct the object and test
    purely-local behavior (config loading, request overrides, token accounting).
    """
    monkeypatch.setenv("DEEPSEEK_API_KEY_VOLC", "test-key-volc")


class TestLLMClientImport:
    """Test that LLMClient can be imported."""
    
    @pytest.mark.unit
    def test_llm_client_can_be_imported(self):
        """Test that LLMClient class is importable."""
        from editor_assistant.llm_client import LLMClient
        assert LLMClient is not None


class TestLLMClientInit:
    """Test LLMClient initialization (requires API key)."""
    
    @pytest.mark.unit
    def test_client_initializes_with_valid_model(self):
        """Test client initializes with a valid model name."""
        from editor_assistant.llm_client import LLMClient
        client = LLMClient("deepseek-v3.2")
        
        assert client.model is not None
        assert client.context_window > 0
        assert client.max_tokens > 0
    
    @pytest.mark.unit
    def test_client_sets_thinking_level(self):
        """Test thinking_level is applied."""
        from editor_assistant.llm_client import LLMClient
        client = LLMClient("deepseek-v3.2", thinking_level="high")
        
        # thinking_level should be in request_overrides
        assert "reasoning_effort" in client.request_overrides
        assert client.request_overrides["reasoning_effort"] == "high"


class TestLLMClientTokenUsage:
    """Test token usage tracking."""
    
    @pytest.mark.unit
    def test_initial_token_usage_is_zero(self):
        """Test token usage starts at zero."""
        from editor_assistant.llm_client import LLMClient
        client = LLMClient("deepseek-v3.2")
        
        usage = client.get_token_usage()
        assert usage["total_input_tokens"] == 0
        assert usage["total_output_tokens"] == 0
        assert usage["cost"]["total_cost"] == 0
    
    @pytest.mark.unit
    def test_token_usage_structure(self):
        """Test token usage has expected structure."""
        from editor_assistant.llm_client import LLMClient
        client = LLMClient("deepseek-v3.2")
        
        usage = client.get_token_usage()
        assert "total_input_tokens" in usage
        assert "total_output_tokens" in usage
        assert "cost" in usage
        assert "input_cost" in usage["cost"]
        assert "output_cost" in usage["cost"]
        assert "total_cost" in usage["cost"]

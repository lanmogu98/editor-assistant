"""
Integration tests for LLM API calls.

These tests make real API calls and cost money.
Run sparingly and only when needed.

Beginner notes:
---------------
- These tests are *async* because `LLMClient.generate_response(...)` is async and must be awaited.
- We mark async tests using `@pytest.mark.asyncio` (provided by `pytest-asyncio`).
- We skip the entire module if the required API key env var is not set.
"""

import pytest
import os
from editor_assistant.llm_client import LLMClient


# Skip all tests in this module if no API key
pytestmark = pytest.mark.skipif(
    not os.getenv("DEEPSEEK_API_KEY_VOLC"),
    reason="DEEPSEEK_API_KEY_VOLC not set"
)


@pytest.mark.asyncio
class TestLLMClientRealAPI:
    """Test LLMClient with real API calls."""
    
    @pytest.fixture
    def client(self, budget_model_name):
        """
        Create a real LLM client.

        Beginner note:
        `budget_model_name` is a shared fixture from `tests/conftest.py`.
        It's intended to pick the cheapest model for smoke/integration testing.
        """
        return LLMClient(budget_model_name)
    
    @pytest.mark.integration
    @pytest.mark.slow
    async def test_generate_simple_response(self, client):
        """Test generating a simple response."""
        prompt = "What is 2+2? Answer with just the number."
        
        response, usage = await client.generate_response(prompt, request_name="test_simple")
        
        assert isinstance(response, str)
        assert len(response.strip()) > 0
        assert "4" in response
    
    @pytest.mark.integration
    @pytest.mark.slow
    async def test_generate_response_tracks_tokens(self, client):
        """Test that token usage is tracked."""
        prompt = "Say 'hello' in three languages."
        
        response, usage = await client.generate_response(prompt, request_name="test_tokens")
        token_usage = client.get_token_usage()
        
        assert token_usage["total_input_tokens"] > 0
        assert token_usage["total_output_tokens"] > 0
        assert token_usage["cost"]["total_cost"] > 0
    
    @pytest.mark.integration
    @pytest.mark.slow
    async def test_generate_response_streaming(self, client):
        """
        Test streaming response.

        Beginner note:
        In streaming mode, the client prints partial output chunks while receiving them,
        and still returns the final `(response_text, usage_dict)` tuple at the end.
        """
        prompt = "Count from 1 to 5."
        
        response, usage = await client.generate_response(
            prompt, 
            request_name="test_stream",
            stream=True
        )
        
        assert isinstance(response, str)
        assert len(response) > 0
    
    @pytest.mark.integration
    @pytest.mark.slow
    async def test_generate_response_non_streaming(self, client):
        """Test non-streaming response."""
        prompt = "What is the capital of France?"
        
        response, usage = await client.generate_response(
            prompt,
            request_name="test_no_stream",
            stream=False
        )
        
        assert isinstance(response, str)
        assert "Paris" in response


@pytest.mark.asyncio
class TestMultipleModels:
    """
    Test different model providers.

    Beginner notes:
    - These are still integration tests and may cost money.
    - We skip each test unless its specific provider API key is available.
    """
    
    @pytest.mark.integration
    @pytest.mark.slow
    @pytest.mark.skipif(
        not os.getenv("GEMINI_API_KEY"),
        reason="GEMINI_API_KEY not set"
    )
    async def test_gemini_model(self):
        """Test Gemini model works."""
        client = LLMClient("gemini-3-flash")
        
        try:
            response, usage = await client.generate_response(
                "What is 1+1?",
                request_name="test_gemini"
            )
        except Exception as exc:
            pytest.skip(f"Gemini API unavailable or SSL blocked: {exc}")
        
        assert "2" in response
    
    @pytest.mark.integration
    @pytest.mark.slow
    @pytest.mark.skipif(
        not os.getenv("OPENAI_API_KEY_OPENROUTER"),
        reason="OPENAI_API_KEY_OPENROUTER not set"
    )
    async def test_openrouter_model(self):
        """Test OpenRouter model works."""
        client = LLMClient("gpt-4.1-or")
        
        response, usage = await client.generate_response(
            "Say hello",
            request_name="test_openrouter"
        )
        
        assert isinstance(response, str)
        assert len(response) > 0

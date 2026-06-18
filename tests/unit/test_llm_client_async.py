"""
Unit tests for AsyncLLMClient (Async Refactor).
"""

import pytest
import httpx
from unittest.mock import MagicMock, AsyncMock, patch

pytestmark = pytest.mark.unit

@pytest.fixture
def mock_httpx_client():
    """Fixture to mock httpx.AsyncClient."""
    with patch("editor_assistant.llm_client.httpx.AsyncClient") as mock_cls:
        client_instance = AsyncMock()
        # Ensure __aenter__ returns the mock client instance
        client_instance.__aenter__.return_value = client_instance
        # Mock instance creation
        mock_cls.return_value = client_instance
        yield client_instance

@pytest.fixture
def mock_env_vars(monkeypatch):
    """Fixture to set environment variables for testing."""
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-key")
    monkeypatch.setenv("DEEPSEEK_API_KEY_VOLC", "test-key-volc")

@pytest.mark.asyncio
class TestAsyncLLMClient:
    
    async def test_generate_response_is_async(self, mock_env_vars, mock_httpx_client):
        """Test that generate_response is an async method returning tuple."""
        from editor_assistant.llm_client import LLMClient
        
        # Setup mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Test response"}}],
            "usage": {"prompt_tokens": 10, "completion_tokens": 20}
        }
        mock_response.raise_for_status = MagicMock()
        
        # client.post should be an async method (AsyncMock returns a coroutine)
        mock_httpx_client.post.return_value = mock_response
        
        # Initialize client
        client = LLMClient("deepseek-v3.2")
        
        # Execute (should be awaitable)
        response, usage = await client.generate_response("Hello")
        
        # Response is now a tuple (text, usage_dict)
        assert response == "Test response"
        assert isinstance(usage, dict)
        assert "total_input_tokens" in usage
        mock_httpx_client.post.assert_called_once()
    
    async def test_streaming_response(self, mock_env_vars, mock_httpx_client):
        """Test streaming response handling."""
        from editor_assistant.llm_client import LLMClient
        from contextlib import asynccontextmanager
        
        # Setup mock streaming response object
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        
        # Mock aiter_lines (async iterator)
        async def mock_lines():
            lines = [
                'data: {"choices": [{"delta": {"content": "Async"}}]}',
                'data: {"choices": [{"delta": {"content": " World"}}]}',
                'data: [DONE]'
            ]
            for line in lines:
                yield line
        
        # Configure aiter_lines to return the async generator
        mock_response.aiter_lines = mock_lines
        
        # Configure client.stream to be an async context manager
        # Use asynccontextmanager to create a proper async context manager
        @asynccontextmanager
        async def mock_stream(*args, **kwargs):
            yield mock_response
        
        mock_httpx_client.stream = mock_stream
        
        client = LLMClient("deepseek-v3.2")
        
        # Capture stdout to verify streaming print
        from io import StringIO
        import sys
        captured = StringIO()
        original_stdout = sys.stdout
        sys.stdout = captured
        
        try:
            response, usage = await client.generate_response("Hello", stream=True)
        finally:
            sys.stdout = original_stdout  # Restore stdout
        
        # Response is now a tuple (text, usage_dict)
        assert response == "Async World"
        assert isinstance(usage, dict)
        assert "Async World" in captured.getvalue()

    async def test_context_manager_support(self, mock_env_vars):
        """Test that client supports async context manager."""
        from editor_assistant.llm_client import LLMClient
        
        async with LLMClient("deepseek-v3.2") as client:
            assert client is not None
            # Internal client should be initialized
            assert client._async_client is not None
        
        # After exit, internal client should be None (closed)
        assert client._async_client is None

    async def test_http_error_includes_response_body(
        self, monkeypatch, mock_env_vars, mock_httpx_client
    ):
        """Final HTTP errors include the response body."""
        import editor_assistant.llm_client as llm_client_module
        from editor_assistant.llm_client import LLMClient

        monkeypatch.setattr(llm_client_module, "MAX_API_RETRIES", 1)

        client = LLMClient("deepseek-v3.2")
        request = httpx.Request("POST", client.api_url)
        mock_httpx_client.post.return_value = httpx.Response(
            404,
            request=request,
            content=b'{"error":"model not found"}',
        )

        with pytest.raises(Exception) as exc_info:
            await client.generate_response("Hello")

        assert (
            'Response body: {"error":"model not found"}'
            in str(exc_info.value)
        )

    async def test_openrouter_pinned_404_downshifts_max_tokens_and_retries(
        self, monkeypatch, mock_httpx_client
    ):
        """Pinned OpenRouter 404 can retry with a smaller output budget."""
        import editor_assistant.llm_client as llm_client_module
        from editor_assistant.llm_client import LLMClient

        monkeypatch.setenv("ZHIPU_API_KEY_OPENROUTER", "test-openrouter-key")
        monkeypatch.setattr(llm_client_module, "MAX_API_RETRIES", 2)
        monkeypatch.setattr(
            llm_client_module, "INITIAL_RETRY_DELAY_SECONDS", 0
        )

        client = LLMClient("glm-4.7-or")
        request = httpx.Request("POST", client.api_url)
        responses = [
            httpx.Response(
                404,
                request=request,
                content=(
                    b'{"error":"No allowed providers found for the request"}'
                ),
            ),
            httpx.Response(
                200,
                request=request,
                json={
                    "choices": [{"message": {"content": "Recovered"}}],
                    "usage": {"prompt_tokens": 3, "completion_tokens": 4},
                },
            ),
        ]
        payloads = []

        async def post_side_effect(*args, **kwargs):
            payloads.append(dict(kwargs["json"]))
            return responses.pop(0)

        mock_httpx_client.post.side_effect = post_side_effect

        response, usage = await client.generate_response("Hello")

        assert response == "Recovered"
        assert usage["total_output_tokens"] == 4
        assert payloads[0]["max_tokens"] == 65536
        assert payloads[1]["max_tokens"] == 8192

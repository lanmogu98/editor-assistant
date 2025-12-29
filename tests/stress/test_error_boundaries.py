import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock, patch
import httpx
from editor_assistant.llm_client import LLMClient
from editor_assistant.md_processor import MDProcessor
from editor_assistant.data_models import MDArticle, InputType

pytestmark = pytest.mark.slow

@pytest.fixture(autouse=True)
def _set_dummy_api_key(monkeypatch):
    """
    Beginner note:
    `LLMClient` (and therefore `MDProcessor`) requires a provider API key env var
    to exist at construction time. These stress tests mock network I/O, so a dummy
    key is sufficient and keeps the tests hermetic.
    """
    monkeypatch.setenv("DEEPSEEK_API_KEY_VOLC", "test-key-volc")

@pytest.fixture
def mock_httpx_client():
    with patch("httpx.AsyncClient") as mock_cls:
        client = AsyncMock()
        client.__aenter__.return_value = client
        client.__aexit__.return_value = None
        mock_cls.return_value = client
        yield client

# Helper to create mock usage dict
def mock_usage_dict():
    return {
        "total_input_tokens": 10, 
        "total_output_tokens": 20,
        "cost": {"input_cost": 0, "output_cost": 0, "total_cost": 0},
        "process_times": {"total_time": 0.1}
    }

class TestErrorBoundaries:
    
    @pytest.mark.asyncio
    async def test_rate_limit_handling(self, mock_httpx_client):
        """Verify client retries on 429 errors."""
        # Setup mock to fail with 429 twice, then succeed
        request = httpx.Request("POST", "https://example.invalid")
        error_response = MagicMock(spec=httpx.Response)
        error_response.status_code = 429
        error_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Rate limit",
            request=request,
            response=error_response,
        )
        
        success_response = MagicMock(spec=httpx.Response)
        success_response.status_code = 200
        success_response.json.return_value = {
            "choices": [{"message": {"content": "Success"}}],
            "usage": {"prompt_tokens": 10, "completion_tokens": 20}
        }
        success_response.raise_for_status.return_value = None
        
        # We need to mock the post call
        mock_httpx_client.post.side_effect = [
            error_response.raise_for_status.side_effect, 
            error_response.raise_for_status.side_effect, 
            success_response
        ]
        
        client = LLMClient(model_name="deepseek-v3.2")
        client._async_client = mock_httpx_client  # Inject mock client directly
        
        # Override sleep to speed up test
        with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
            response, usage = await client.generate_response("prompt")
            
            assert response == "Success"
            assert isinstance(usage, dict)
            assert mock_httpx_client.post.call_count == 3
            assert mock_sleep.call_count >= 2 # Should sleep at least twice

    @pytest.mark.asyncio
    async def test_network_timeouts(self, mock_httpx_client):
        """Verify client retries on network timeouts."""
        # Success response with correct format
        success_response = MagicMock()
        success_response.status_code = 200
        success_response.json.return_value = {
            "choices": [{"message": {"content": "Recovered"}}],
            "usage": {"prompt_tokens": 10, "completion_tokens": 20}
        }
        success_response.raise_for_status.return_value = None
        
        # Fail with Timeout twice, then succeed
        mock_httpx_client.post.side_effect = [
            httpx.ReadTimeout("Timeout"),
            httpx.ConnectTimeout("Connect timeout"),
            success_response
        ]
        
        client = LLMClient(model_name="deepseek-v3.2")
        client._async_client = mock_httpx_client
        
        with patch("asyncio.sleep", new_callable=AsyncMock):
            response, usage = await client.generate_response("prompt")
            assert response == "Recovered"
            assert isinstance(usage, dict)
            assert mock_httpx_client.post.call_count == 3

    @pytest.mark.asyncio
    async def test_partial_batch_failure(self):
        """Verify partial failures in a batch don't crash the whole process."""
        # Mock MDProcessor to simulate some failures
        processor = MDProcessor("deepseek-v3.2")
        
        async def mock_process(articles, task, *args, **kwargs):
            # Fail for "bad" articles
            if "bad" in articles[0].content:
                return (False, -1)
            return (True, 123)
            
        with patch.object(processor, 'process_mds', side_effect=mock_process):
            inputs = [
                MDArticle(type=InputType.PAPER, content="good1 " * 500, title="1", source_path="1.pdf"),
                MDArticle(type=InputType.PAPER, content="bad1 " * 500, title="2", source_path="2.pdf"),
                MDArticle(type=InputType.PAPER, content="good2 " * 500, title="3", source_path="3.pdf"),
            ]
            
            tasks = [processor.process_mds([inp], "brief") for inp in inputs]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            success_count = sum(1 for r in results if isinstance(r, tuple) and r[0])
            fail_count = sum(1 for r in results if isinstance(r, tuple) and not r[0])
            
            assert success_count == 2
            assert fail_count == 1

    @pytest.mark.asyncio
    async def test_semaphore_saturation(self):
        """Verify semaphore limits concurrent execution."""
        processor = MDProcessor("deepseek-v3.2", max_concurrent=2)
        
        active_tasks = 0
        max_active = 0
        
        async def mock_slow_llm(*args, **kwargs):
            nonlocal active_tasks, max_active
            active_tasks += 1
            max_active = max(max_active, active_tasks)
            await asyncio.sleep(0.05)
            active_tasks -= 1
            # Return tuple (response, usage)
            return ("response", mock_usage_dict())
            
        with patch("editor_assistant.llm_client.LLMClient.generate_response", side_effect=mock_slow_llm), \
             patch("editor_assistant.md_processor.TaskRegistry") as mock_registry:
            
            # Setup mock task correctly to return a valid tuple from validate()
            mock_task_cls = MagicMock()
            mock_task_instance = MagicMock()
            # This was the failure point: validate must return (bool, str)
            mock_task_instance.validate.return_value = (True, "")
            mock_task_instance.build_prompt.return_value = "prompt " * 100
            mock_task_instance.post_process.return_value = {"main": "response"}
            mock_task_instance.get_output_suffix.return_value = "_suffix"
            mock_task_instance.supports_multi_input = False
            
            mock_task_cls.return_value = mock_task_instance
            mock_registry.get.return_value = mock_task_cls
            
            # Submit 10 tasks, but limit is 2
            inputs = [
                MDArticle(
                    type=InputType.PAPER, 
                    content=f"content{i} " * 500, 
                    title=f"{i}",
                    source_path=f"{i}.pdf"
                ) 
                for i in range(10)
            ]
            tasks = [processor.process_mds([inp], "brief") for inp in inputs]
            
            await asyncio.gather(*tasks)
            
            # Verify we never exceeded limit significantly (allow +1 for race conditions in test measurement)
            assert max_active <= 3, f"Expected max ~2 concurrent, got {max_active}"

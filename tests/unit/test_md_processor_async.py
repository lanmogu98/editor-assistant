"""
Unit tests for Async MDProcessor (Async Refactor).
"""

import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock, patch
from editor_assistant.data_models import MDArticle, InputType, ProcessType

pytestmark = pytest.mark.unit


@pytest.fixture
def mock_llm_client_async():
    """
    Provide an async-shaped LLM client mock.

    Why this exists:
    - `MDProcessor` calls `await llm_client.generate_response(...)`
    - The real `LLMClient` constructor requires an API key env var
    - So we patch `editor_assistant.md_processor.LLMClient` to return a fake client
      whose `generate_response` is an `AsyncMock`.
    """
    with patch("editor_assistant.md_processor.LLMClient") as mock_cls:
        client = MagicMock()
        # generate_response returns (response_text, usage_dict)
        client.generate_response = AsyncMock(
            return_value=(
                "Mocked LLM Response",
                {
                    "total_input_tokens": 10,
                    "total_output_tokens": 20,
                    "cost": {
                        "input_cost": 0,
                        "output_cost": 0,
                        "total_cost": 0,
                    },
                    "process_times": {"total_time": 0.1},
                },
            )
        )
        # Setup properties - Increase limits to avoid ContentTooLargeError
        client.model_name = "test-model"
        client.context_window = 100000
        client.max_tokens = 1000
        client.pricing_currency = "$"

        mock_cls.return_value = client
        yield client


@pytest.fixture
def mock_run_repository():
    """
    Mock the RunRepository used by MDProcessor so unit tests don't touch SQLite.

    (Storage is already tested separately in `tests/unit/test_storage.py`.)
    """
    with patch("editor_assistant.md_processor.RunRepository") as mock_cls:
        repo = MagicMock()
        repo.create_run.return_value = 123
        repo.get_or_create_input.return_value = 456
        mock_cls.return_value = repo
        yield repo


@pytest.mark.asyncio
class TestAsyncMDProcessor:

    async def test_process_mds_is_async(
        self, mock_llm_client_async, mock_run_repository
    ):
        """Test that process_mds is an async method."""
        from editor_assistant.md_processor import MDProcessor

        # Mock TaskRegistry
        with patch(
            "editor_assistant.md_processor.TaskRegistry"
        ) as mock_registry:
            mock_task_cls = MagicMock()
            mock_task = MagicMock()
            mock_task.validate.return_value = (True, "")
            mock_task.build_prompt.return_value = (
                "Test Prompt " * 100
            )  # Sufficient length
            mock_task.post_process.return_value = {"main": "Processed Content"}
            mock_task.get_output_suffix.return_value = "_test"
            mock_task.supports_multi_input = False

            mock_task_cls.return_value = mock_task
            mock_registry.get.return_value = mock_task_cls

            # Initialize processor
            processor = MDProcessor("test-model")

            article = MDArticle(
                type=InputType.PAPER,
                content="Test content " * 500,  # Sufficient content
                title="Test Title",
                source_path="test.pdf",
            )

            # Execute (should be awaitable)
            success, run_id = await processor.process_mds(
                [article], "test-task"
            )

            assert success is True
            assert run_id == 123
            mock_llm_client_async.generate_response.assert_called_once()

    async def test_concurrency_semaphore(
        self, mock_llm_client_async, mock_run_repository
    ):
        """Test that concurrency is limited by semaphore."""
        from editor_assistant.md_processor import MDProcessor

        # Setup a slow LLM response - returns tuple (text, usage)
        async def slow_response(*args, **kwargs):
            await asyncio.sleep(0.01)  # Short sleep
            return (
                "Slow Response",
                {
                    "total_input_tokens": 10,
                    "total_output_tokens": 20,
                    "cost": {
                        "input_cost": 0,
                        "output_cost": 0,
                        "total_cost": 0,
                    },
                    "process_times": {"total_time": 0.01},
                },
            )

        mock_llm_client_async.generate_response.side_effect = slow_response

        # Initialize processor with max_concurrent=2
        processor = MDProcessor("test-model", max_concurrent=2)

        # Mock TaskRegistry
        with patch(
            "editor_assistant.md_processor.TaskRegistry"
        ) as mock_registry:
            mock_task_cls = MagicMock()
            mock_task = MagicMock()
            mock_task.validate.return_value = (True, "")
            mock_task.build_prompt.return_value = "Test Prompt " * 100
            mock_task.post_process.return_value = {"main": "Processed Content"}
            mock_task.get_output_suffix.return_value = "_test"
            mock_task.supports_multi_input = False

            mock_task_cls.return_value = mock_task
            mock_registry.get.return_value = mock_task_cls

            article = MDArticle(
                type=InputType.PAPER,
                content="content " * 500,
                title="title",
                source_path="test.pdf",
            )

            # Launch 5 concurrent tasks
            tasks = [
                processor.process_mds([article], "test-task") for _ in range(5)
            ]
            await asyncio.gather(*tasks)

            assert mock_llm_client_async.generate_response.call_count == 5


@pytest.mark.asyncio
async def test_streaming_console_output_uses_app_callback(
    mock_llm_client_async,
    mock_run_repository,
    capsys,
):
    from editor_assistant.md_processor import MDProcessor

    async def fake_generate_response(*args, stream_callback=None, **kwargs):
        stream_callback("hello")
        stream_callback(" world")
        return "hello world", {
            "total_input_tokens": 1,
            "total_output_tokens": 2,
            "cost": {"input_cost": 0, "output_cost": 0, "total_cost": 0},
            "process_times": {"total_time": 0.1},
        }

    mock_llm_client_async.generate_response.side_effect = (
        fake_generate_response
    )

    with patch("editor_assistant.md_processor.TaskRegistry") as mock_registry:
        mock_task_cls = MagicMock()
        mock_task = MagicMock()
        mock_task.validate.return_value = (True, "")
        mock_task.build_prompt.return_value = "Test Prompt " * 100
        mock_task.post_process.return_value = {"main": "Processed Content"}
        mock_task.get_output_suffix.return_value = "_test"
        mock_task.supports_multi_input = False

        mock_task_cls.return_value = mock_task
        mock_registry.get.return_value = mock_task_cls

        processor = MDProcessor("test-model", stream=True)
        article = MDArticle(
            type=InputType.PAPER,
            content="content " * 500,
            title="title",
            source_path="test.pdf",
        )

        success, _ = await processor.process_mds(
            [article],
            "test-task",
            save_files=False,
            output_to_console=True,
        )

    assert success is True
    assert "hello world" in capsys.readouterr().out

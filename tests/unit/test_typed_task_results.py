"""Focused tests for additive typed task execution results."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from llm_exec_core import ExecutionMetadata, LLMResult, TokenUsage

from editor_assistant import data_models
from editor_assistant.data_models import InputType, MDArticle
from editor_assistant.md_processor import MDProcessor
from editor_assistant.tasks.brief import BriefTask

pytestmark = pytest.mark.unit


def _core_result() -> LLMResult:
    return LLMResult(
        text="Typed response",
        structured={"title": "Typed title"},
        usage=TokenUsage(
            input_tokens=10,
            output_tokens=20,
            total_tokens=30,
            input_cost=0.1,
            output_cost=0.2,
            total_cost=0.3,
            currency="$",
            requests=[],
            process_times={"request_times": []},
        ),
        metadata=ExecutionMetadata(
            request_id="request-1",
            run_id="core-run-1",
            request_name="brief",
            model_name="test-model",
            model_id="test-model-id",
            provider_name="fake-provider",
            started_at="2026-07-22T00:00:00",
            finished_at="2026-07-22T00:00:01",
            duration_seconds=1.0,
            trace_context={"source": "unit-test"},
            planning={"validation_status": "client_validated"},
        ),
    )


def _legacy_usage() -> dict:
    return {
        "total_input_tokens": 10,
        "total_output_tokens": 20,
        "cost": {
            "input_cost": 0.1,
            "output_cost": 0.2,
            "total_cost": 0.3,
        },
        "process_times": {"total_time": 1.0},
    }


@pytest.fixture
def processor_dependencies():
    with (
        patch("editor_assistant.md_processor.LLMClient") as client_cls,
        patch("editor_assistant.md_processor.RunRepository") as repo_cls,
    ):
        client = MagicMock()
        client.model_name = "test-model"
        client.context_window = 100000
        client.max_tokens = 1000
        client.pricing_currency = "$"
        client.generate = AsyncMock(return_value=_core_result())
        client.generate_response = AsyncMock(
            return_value=("Legacy response", _legacy_usage())
        )
        client_cls.return_value = client

        repository = MagicMock()
        repository.get_or_create_input.return_value = 456
        repository.create_run.return_value = 123
        repo_cls.return_value = repository

        yield MDProcessor("test-model", stream=False), client, repository


@pytest.fixture
def valid_article() -> MDArticle:
    return MDArticle(
        type=InputType.PAPER,
        content="# Test\n\n" + "Content. " * 500,
        title="Test article",
        source_path="test.md",
    )


@pytest.mark.asyncio
async def test_execute_task_returns_artifacts_and_raw_core_result(
    processor_dependencies, valid_article
):
    processor, client, _ = processor_dependencies
    raw_result = _core_result()
    client.generate.return_value = raw_result

    result = await processor.execute_task(
        [valid_article], "brief", output_to_console=False
    )

    assert isinstance(result, data_models.TaskExecutionResult)
    assert result.task_name == "brief"
    assert result.run_id == 123
    assert result.outputs == {
        "main": data_models.OutputArtifact(
            value="Typed response",
            content_type="text/plain",
            serialized_text="Typed response",
        )
    }
    assert result.llm_result is raw_result
    assert result.llm_result.structured == {"title": "Typed title"}
    assert result.llm_result.usage.total_tokens == 30
    assert result.llm_result.metadata.planning == {
        "validation_status": "client_validated"
    }
    client.generate_response.assert_not_awaited()


@pytest.mark.asyncio
async def test_execute_task_propagates_provider_failure(
    processor_dependencies, valid_article
):
    processor, client, repository = processor_dependencies
    client.generate.side_effect = ConnectionError("provider unavailable")

    with pytest.raises(ConnectionError, match="provider unavailable"):
        await processor.execute_task(
            [valid_article], "brief", output_to_console=False
        )

    repository.update_run_status.assert_any_call(
        123, "failed", "provider unavailable"
    )


@pytest.mark.asyncio
async def test_execute_task_propagates_post_processing_failure(
    processor_dependencies, valid_article
):
    processor, _, repository = processor_dependencies

    with patch.object(
        BriefTask,
        "post_process",
        side_effect=RuntimeError("post-processing failed"),
    ):
        with pytest.raises(RuntimeError, match="post-processing failed"):
            await processor.execute_task(
                [valid_article], "brief", output_to_console=False
            )

    repository.update_run_status.assert_any_call(
        123, "failed", "post-processing failed"
    )


@pytest.mark.asyncio
async def test_execute_task_preserves_stream_callback(
    processor_dependencies, valid_article
):
    processor, client, _ = processor_dependencies
    processor.stream = True
    chunks = []

    async def generate_with_chunks(*args, stream_callback=None, **kwargs):
        stream_callback("first")
        stream_callback(" second")
        return _core_result()

    client.generate.side_effect = generate_with_chunks

    await processor.execute_task(
        [valid_article],
        "brief",
        output_to_console=False,
        stream_callback=chunks.append,
    )

    assert chunks == ["first", " second"]


@pytest.mark.asyncio
async def test_process_mds_translates_provider_failure_to_legacy_tuple(
    processor_dependencies, valid_article
):
    processor, client, repository = processor_dependencies
    client.generate_response.side_effect = ConnectionError(
        "provider unavailable"
    )

    result = await processor.process_mds(
        [valid_article], "brief", output_to_console=False
    )

    assert result == (False, 123)
    repository.update_run_status.assert_any_call(
        123,
        "failed",
        "Failed to connect to LLM service: provider unavailable",
    )
    client.generate.assert_not_awaited()

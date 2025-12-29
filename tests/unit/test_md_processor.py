"""
Unit tests for MDProcessor.

Uses mocks to avoid API calls where possible.
"""

import pytest
import os
from unittest.mock import patch, MagicMock, AsyncMock
from pathlib import Path

from editor_assistant.md_processor import MDProcessor
from editor_assistant.data_models import MDArticle, InputType, ProcessType, SaveType


class TestMDProcessorImport:
    """Test MDProcessor can be imported."""
    
    @pytest.mark.unit
    def test_md_processor_can_be_imported(self):
        """Test MDProcessor is importable."""
        from editor_assistant.md_processor import MDProcessor
        assert MDProcessor is not None


class TestMDProcessorInit:
    """Test MDProcessor initialization."""
    
    @pytest.mark.unit
    def test_processor_creates_llm_client(self, mock_llm_client):
        """Test that processor creates LLM client."""
        with patch('editor_assistant.md_processor.LLMClient') as MockClient, \
             patch('editor_assistant.md_processor.RunRepository') as MockRepo:
            MockClient.return_value = mock_llm_client
            MockRepo.return_value = MagicMock()
            
            processor = MDProcessor("test-model")
            
            MockClient.assert_called_once_with("test-model", thinking_level=None)
            assert processor.llm_client is mock_llm_client
            assert processor.model_name == "test-model"
    
    @pytest.mark.unit
    def test_processor_sets_thinking_level(self, mock_llm_client):
        """Test thinking_level is passed to LLM client."""
        with patch('editor_assistant.md_processor.LLMClient') as MockClient, \
             patch('editor_assistant.md_processor.RunRepository') as MockRepo:
            MockClient.return_value = mock_llm_client
            MockRepo.return_value = MagicMock()
            
            processor = MDProcessor("test-model", thinking_level="high")
            
            call_kwargs = MockClient.call_args[1]
            assert call_kwargs.get("thinking_level") == "high"
    
    @pytest.mark.unit
    def test_processor_sets_stream(self, mock_llm_client):
        """Test stream parameter is set."""
        with patch('editor_assistant.md_processor.LLMClient') as MockClient, \
             patch('editor_assistant.md_processor.RunRepository') as MockRepo:
            MockClient.return_value = mock_llm_client
            MockRepo.return_value = MagicMock()
            
            processor = MDProcessor("test-model", stream=False)
            
            assert processor.stream is False


class TestMDProcessorProcessMds:
    """Test MDProcessor.process_mds method (async)."""
    
    @pytest.fixture
    def processor(self, mock_llm_client):
        """
        Create a processor with:
        - LLM client mocked (no network)
        - Repository mocked (no SQLite IO in unit tests)

        Beginner note:
        We patch the *import location* used by MDProcessor:
        `editor_assistant.md_processor.LLMClient` and `editor_assistant.md_processor.RunRepository`.
        """
        with patch('editor_assistant.md_processor.LLMClient') as MockClient, \
             patch('editor_assistant.md_processor.RunRepository') as MockRepo:
            # Set up async mock for generate_response
            mock_llm_client.generate_response = AsyncMock(return_value=(
                "Test response",
                {"total_input_tokens": 10, "total_output_tokens": 20, 
                 "cost": {"input_cost": 0, "output_cost": 0, "total_cost": 0},
                 "process_times": {"total_time": 0.1}}
            ))
            MockClient.return_value = mock_llm_client
            repo = MagicMock()
            repo.get_or_create_input.return_value = 456
            repo.create_run.return_value = 123
            MockRepo.return_value = repo
            return MDProcessor("test-model")
    
    @pytest.fixture
    def valid_article(self, temp_dir):
        """Create a valid article for testing."""
        return MDArticle(
            type=InputType.PAPER,
            content="# Test Paper\n\n" + "Content. " * 500,  # Sufficient content
            title="Test Paper",
            source_path="/tmp/test.pdf",
            output_path=temp_dir
        )
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_process_mds_with_valid_article(self, processor, valid_article):
        """Test processing with valid article."""
        success, run_id = await processor.process_mds(
            [valid_article], 
            ProcessType.BRIEF
        )
        
        assert success is True
        assert run_id == 123
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_process_mds_with_string_task_type(self, processor, valid_article):
        """Test processing with string task type."""
        success, run_id = await processor.process_mds(
            [valid_article], 
            "brief"  # String instead of enum
        )
        
        assert success is True
        assert run_id == 123
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_process_mds_with_unknown_task(self, processor, valid_article):
        """Test that unknown task returns False."""
        success, run_id = await processor.process_mds(
            [valid_article], 
            "unknown_task"
        )
        
        assert success is False
        assert run_id == -1
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_process_mds_empty_articles_returns_false(self, processor):
        """Test that empty article list returns False."""
        success, run_id = await processor.process_mds([], ProcessType.BRIEF)
        assert success is False
        assert run_id == -1


class TestMDProcessorWithRealClient:
    """
    Unit test that exercises the *real* MDProcessor/LLMClient constructors.

    Beginner note:
    This does NOT call the network. It only verifies that:
    - model config exists
    - required env var is read
    - objects can be constructed
    """
    
    @pytest.mark.unit
    def test_processor_initializes_with_real_client(self, monkeypatch):
        """Test processor can initialize with real client."""
        monkeypatch.setenv("DEEPSEEK_API_KEY_VOLC", "test-key-volc")
        processor = MDProcessor("deepseek-v3.2", stream=False)
        assert processor.model_name == "deepseek-v3.2"
        assert processor.stream is False

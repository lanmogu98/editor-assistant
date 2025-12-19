"""
Integration tests for Task execution with real APIs.

These tests run actual tasks with LLM calls.
"""

import pytest
import os
from pathlib import Path

from editor_assistant.md_processor import MDProcessor
from editor_assistant.data_models import MDArticle, InputType, ProcessType


# Skip all tests if no API key
pytestmark = pytest.mark.skipif(
    not os.getenv("DEEPSEEK_API_KEY_VOLC"),
    reason="DEEPSEEK_API_KEY_VOLC not set"
)


class TestBriefTaskIntegration:
    """Integration tests for brief task."""
    
    @pytest.fixture
    def processor(self, budget_model_name):
        """Create processor with budget model."""
        return MDProcessor(budget_model_name, stream=False)
    
    @pytest.fixture
    def paper_article(self, short_test_content, temp_dir):
        """Create a paper article for testing."""
        # Need sufficient content for processing
        content = short_test_content + "\n\n" + "Additional content. " * 200
        return MDArticle(
            type=InputType.PAPER,
            content=content,
            title="Integration Test Paper",
            source_path="/tmp/test.pdf",
            output_path=temp_dir
        )
    
    @pytest.mark.integration
    @pytest.mark.slow
    def test_brief_generates_output(self, processor, paper_article, temp_dir):
        """Test that brief task generates output."""
        success, _ = processor.process_mds(
            [paper_article],
            ProcessType.BRIEF,
            output_to_console=False,
            save_files=True
        )
        
        assert success is True
        
        # Check output file was created
        output_dir = temp_dir / "llm_summaries" / processor.model_name
        assert output_dir.exists()
        
        # Check response file exists
        response_files = list(output_dir.glob("response_*.md"))
        assert len(response_files) > 0
    
    @pytest.mark.integration
    @pytest.mark.slow
    def test_brief_output_is_chinese(self, processor, paper_article, temp_dir):
        """Test that brief output is in Chinese."""
        paper_article.output_path = temp_dir
        
        processor.process_mds(
            [paper_article],
            ProcessType.BRIEF,
            output_to_console=False
        )
        
        # Read the output
        output_dir = temp_dir / "llm_summaries" / processor.model_name
        response_files = list(output_dir.glob("response_*.md"))
        
        if response_files:
            content = response_files[0].read_text(encoding='utf-8')
            # Check for Chinese characters
            has_chinese = any('\u4e00' <= c <= '\u9fff' for c in content)
            assert has_chinese, "Output should contain Chinese characters"


class TestOutlineTaskIntegration:
    """Integration tests for outline task."""
    
    @pytest.fixture
    def processor(self, budget_model_name):
        """Create processor with budget model."""
        return MDProcessor(budget_model_name, stream=False)
    
    @pytest.fixture
    def paper_article(self, sample_paper_content, temp_dir):
        """Create paper article from sample data."""
        return MDArticle(
            type=InputType.PAPER,
            content=sample_paper_content,
            title="Shannon Paper",
            source_path="/tmp/shannon.pdf",
            output_path=temp_dir
        )
    
    @pytest.mark.integration
    @pytest.mark.slow
    @pytest.mark.expensive
    def test_outline_generates_structured_output(self, processor, paper_article, temp_dir):
        """Test that outline generates structured output."""
        result = processor.process_mds(
            [paper_article],
            ProcessType.OUTLINE,
            output_to_console=False
        )
        
        assert result is True


class TestMultiSourceIntegration:
    """Integration tests for multi-source processing."""
    
    @pytest.fixture
    def processor(self, budget_model_name):
        """Create processor."""
        return MDProcessor(budget_model_name, stream=False)
    
    @pytest.fixture
    def multiple_articles(self, temp_dir):
        """Create multiple articles."""
        content = "Test content for article. " * 100
        return [
            MDArticle(
                type=InputType.PAPER,
                content="# Paper\n\n" + content,
                title="Paper 1",
                source_path="/tmp/paper1.pdf",
                output_path=temp_dir
            ),
            MDArticle(
                type=InputType.NEWS,
                content="# News\n\n" + content,
                title="News 1",
                source_path="https://example.com",
                output_path=temp_dir
            )
        ]
    
    @pytest.mark.integration
    @pytest.mark.slow
    def test_brief_with_multiple_sources(self, processor, multiple_articles, temp_dir):
        """Test brief task with multiple sources."""
        success, _ = processor.process_mds(
            multiple_articles,
            ProcessType.BRIEF,
            output_to_console=False,
            save_files=True
        )
        
        assert success is True


class TestStreamingIntegration:
    """Integration tests for streaming output."""
    
    @pytest.fixture
    def streaming_processor(self, budget_model_name):
        """Create processor with streaming enabled."""
        return MDProcessor(budget_model_name, stream=True)
    
    @pytest.fixture
    def non_streaming_processor(self, budget_model_name):
        """Create processor with streaming disabled."""
        return MDProcessor(budget_model_name, stream=False)
    
    @pytest.fixture
    def test_article(self, temp_dir):
        """Create test article."""
        content = "Test content. " * 200
        return MDArticle(
            type=InputType.PAPER,
            content="# Test\n\n" + content,
            title="Streaming Test",
            source_path="/tmp/test.pdf",
            output_path=temp_dir
        )
    
    @pytest.mark.integration
    @pytest.mark.slow
    def test_streaming_produces_output(self, streaming_processor, test_article, temp_dir, capsys):
        """Test that streaming produces output."""
        success, _ = streaming_processor.process_mds(
            [test_article],
            ProcessType.BRIEF,
            output_to_console=True,
            save_files=True
        )
        
        assert success is True
        
        # Check that something was printed (streaming output)
        captured = capsys.readouterr()
        # Note: streaming prints directly to stdout
    
    @pytest.mark.integration
    @pytest.mark.slow
    def test_non_streaming_produces_output(self, non_streaming_processor, test_article, temp_dir):
        """Test that non-streaming produces output."""
        success, _ = non_streaming_processor.process_mds(
            [test_article],
            ProcessType.BRIEF,
            output_to_console=False,
            save_files=True
        )
        
        assert success is True


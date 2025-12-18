"""
Unit tests for data models.
"""

import pytest
from editor_assistant.data_models import (
    InputType, Input, ProcessType, MDArticle, SaveType
)


class TestInputType:
    """Test InputType enum."""
    
    @pytest.mark.unit
    def test_input_type_values(self):
        """Test that InputType has expected values."""
        assert InputType.PAPER.value == "paper"
        assert InputType.NEWS.value == "news"
    
    @pytest.mark.unit
    def test_input_type_from_string(self):
        """Test creating InputType from string."""
        assert InputType("paper") == InputType.PAPER
        assert InputType("news") == InputType.NEWS


class TestInput:
    """Test Input model."""
    
    @pytest.mark.unit
    def test_input_creation(self):
        """Test creating Input object."""
        inp = Input(type=InputType.PAPER, path="/path/to/file.pdf")
        assert inp.type == InputType.PAPER
        assert inp.path == "/path/to/file.pdf"
    
    @pytest.mark.unit
    def test_input_with_url(self):
        """Test Input with URL path."""
        inp = Input(type=InputType.NEWS, path="https://example.com/article")
        assert inp.type == InputType.NEWS
        assert "https://" in inp.path


class TestProcessType:
    """Test ProcessType enum."""
    
    @pytest.mark.unit
    def test_process_type_values(self):
        """Test that ProcessType has expected values."""
        assert ProcessType.OUTLINE.value == "outline"
        assert ProcessType.BRIEF.value == "brief"
        assert ProcessType.TRANSLATE.value == "translate"
    
    @pytest.mark.unit
    def test_process_type_from_string(self):
        """Test creating ProcessType from string."""
        assert ProcessType("brief") == ProcessType.BRIEF


class TestMDArticle:
    """Test MDArticle model."""
    
    @pytest.mark.unit
    def test_md_article_minimal(self):
        """Test creating MDArticle with minimal fields."""
        article = MDArticle(type=InputType.PAPER)
        assert article.type == InputType.PAPER
        assert article.content is None
        assert article.title is None
    
    @pytest.mark.unit
    def test_md_article_full(self):
        """Test creating MDArticle with all fields."""
        article = MDArticle(
            type=InputType.PAPER,
            content="# Test Content",
            title="Test Paper",
            authors="Test Author",
            converter="markitdown",
            source_path="/path/to/source.pdf"
        )
        assert article.type == InputType.PAPER
        assert article.content == "# Test Content"
        assert article.title == "Test Paper"
        assert article.authors == "Test Author"
        assert article.converter == "markitdown"
    
    @pytest.mark.unit
    def test_md_article_content_update(self):
        """Test updating MDArticle content."""
        article = MDArticle(type=InputType.NEWS)
        article.content = "New content"
        assert article.content == "New content"


class TestSaveType:
    """Test SaveType enum."""
    
    @pytest.mark.unit
    def test_save_type_values(self):
        """Test that SaveType has expected values."""
        assert SaveType.PROMPT.value == "prompt"
        assert SaveType.RESPONSE.value == "response"


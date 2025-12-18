"""
Unit tests for the Task system.
"""

import pytest
from editor_assistant.data_models import MDArticle, InputType
from editor_assistant.tasks import TaskRegistry
from editor_assistant.tasks.base import Task
from editor_assistant.tasks.brief import BriefTask
from editor_assistant.tasks.outline import OutlineTask
from editor_assistant.tasks.translate import TranslateTask


class TestTaskRegistry:
    """Test TaskRegistry functionality."""
    
    @pytest.mark.unit
    def test_registry_has_builtin_tasks(self):
        """Test that built-in tasks are registered."""
        tasks = TaskRegistry.list_tasks()
        assert "brief" in tasks
        assert "outline" in tasks
        assert "translate" in tasks
    
    @pytest.mark.unit
    def test_registry_get_task(self):
        """Test getting task by name."""
        brief_task = TaskRegistry.get("brief")
        assert brief_task is not None
        assert issubclass(brief_task, Task)
    
    @pytest.mark.unit
    def test_registry_get_nonexistent(self):
        """Test getting non-existent task returns None."""
        task = TaskRegistry.get("nonexistent_task")
        assert task is None
    
    @pytest.mark.unit
    def test_registry_list_tasks(self):
        """Test listing all registered tasks."""
        tasks = TaskRegistry.list_tasks()
        assert isinstance(tasks, list)
        assert len(tasks) >= 3  # At least brief, outline, translate


class TestBriefTask:
    """Test BriefTask functionality."""
    
    @pytest.fixture
    def task(self):
        return BriefTask()
    
    @pytest.fixture
    def single_article(self):
        return [MDArticle(
            type=InputType.PAPER,
            content="# Test Paper\n\nThis is test content.",
            title="Test Paper"
        )]
    
    @pytest.fixture
    def multiple_articles(self):
        return [
            MDArticle(type=InputType.PAPER, content="# Paper 1", title="Paper 1"),
            MDArticle(type=InputType.NEWS, content="# News 1", title="News 1"),
        ]
    
    @pytest.mark.unit
    def test_brief_task_name(self, task):
        """Test task name is set correctly."""
        assert task.name == "brief"
    
    @pytest.mark.unit
    def test_brief_supports_multi_input(self, task):
        """Test brief supports multiple inputs."""
        assert task.supports_multi_input is True
    
    @pytest.mark.unit
    def test_brief_validate_single(self, task, single_article):
        """Test validation with single article."""
        is_valid, msg = task.validate(single_article)
        assert is_valid is True
        assert msg == ""
    
    @pytest.mark.unit
    def test_brief_validate_multiple(self, task, multiple_articles):
        """Test validation with multiple articles."""
        is_valid, msg = task.validate(multiple_articles)
        assert is_valid is True
    
    @pytest.mark.unit
    def test_brief_validate_empty(self, task):
        """Test validation fails for empty list."""
        is_valid, msg = task.validate([])
        assert is_valid is False
        assert "at least one" in msg.lower()
    
    @pytest.mark.unit
    def test_brief_build_prompt(self, task, single_article):
        """Test prompt building."""
        prompt = task.build_prompt(single_article)
        assert isinstance(prompt, str)
        assert len(prompt) > 0
    
    @pytest.mark.unit
    def test_brief_post_process(self, task, single_article):
        """Test post processing."""
        llm_response = "Generated news content"
        outputs = task.post_process(llm_response, single_article)  # Note: response first
        assert "main" in outputs
        assert outputs["main"] == llm_response


class TestOutlineTask:
    """Test OutlineTask functionality."""
    
    @pytest.fixture
    def task(self):
        return OutlineTask()
    
    @pytest.fixture
    def paper_article(self):
        return [MDArticle(
            type=InputType.PAPER,
            content="# Research Paper\n\nDetailed content here.",
            title="Research Paper"
        )]
    
    @pytest.fixture
    def news_article(self):
        return [MDArticle(
            type=InputType.NEWS,
            content="# News Article",
            title="News"
        )]
    
    @pytest.mark.unit
    def test_outline_task_name(self, task):
        """Test task name."""
        assert task.name == "outline"
    
    @pytest.mark.unit
    def test_outline_single_input_only(self, task):
        """Test outline requires single input."""
        assert task.supports_multi_input is False
    
    @pytest.mark.unit
    def test_outline_validate_paper(self, task, paper_article):
        """Test validation with paper."""
        is_valid, msg = task.validate(paper_article)
        assert is_valid is True
    
    @pytest.mark.unit
    def test_outline_validate_news_succeeds(self, task, news_article):
        """Test validation passes for any single article type."""
        # Outline only requires single article, doesn't check type
        is_valid, msg = task.validate(news_article)
        assert is_valid is True
    
    @pytest.mark.unit
    def test_outline_validate_multiple_fails(self, task, paper_article):
        """Test validation fails for multiple articles."""
        articles = paper_article + paper_article
        is_valid, msg = task.validate(articles)
        assert is_valid is False
        assert "exactly one" in msg.lower()
    
    @pytest.mark.unit
    def test_outline_build_prompt(self, task, paper_article):
        """Test prompt building."""
        prompt = task.build_prompt(paper_article)
        assert isinstance(prompt, str)
        assert len(prompt) > 0


class TestTranslateTask:
    """Test TranslateTask functionality."""
    
    @pytest.fixture
    def task(self):
        return TranslateTask()
    
    @pytest.fixture
    def article(self):
        return [MDArticle(
            type=InputType.PAPER,
            content="Line 1\nLine 2\nLine 3",
            title="Test"
        )]
    
    @pytest.mark.unit
    def test_translate_task_name(self, task):
        """Test task name."""
        assert task.name == "translate"
    
    @pytest.mark.unit
    def test_translate_single_input_only(self, task):
        """Test translate requires single input."""
        assert task.supports_multi_input is False
    
    @pytest.mark.unit
    def test_translate_validate_single(self, task, article):
        """Test validation with single article."""
        is_valid, msg = task.validate(article)
        assert is_valid is True
    
    @pytest.mark.unit
    def test_translate_validate_multiple_fails(self, task, article):
        """Test validation fails for multiple articles."""
        articles = article + article
        is_valid, msg = task.validate(articles)
        assert is_valid is False
    
    @pytest.mark.unit
    def test_translate_post_process_bilingual(self, task, article):
        """Test bilingual output generation."""
        llm_response = "第一行\n第二行\n第三行"
        outputs = task.post_process(llm_response, article)  # Note: response first
        assert "main" in outputs
        assert "bilingual" in outputs
        # Bilingual should interleave original and translated
        bilingual = outputs["bilingual"]
        assert "Line 1" in bilingual
        assert "第一行" in bilingual


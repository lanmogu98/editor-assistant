"""
Pytest configuration and shared fixtures for Editor Assistant.

Test Categories:
- unit: Fast tests with mocks, no API calls
- integration: Tests with real API calls (costs money)
- slow: Tests that take > 5 seconds

Usage:
    pytest tests/unit/              # Run unit tests only
    pytest tests/integration/       # Run integration tests
    pytest -m "not slow"           # Skip slow tests
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, MagicMock


# ============================================================================
# PYTEST CONFIGURATION
# ============================================================================

def pytest_addoption(parser):
    """Add custom pytest command-line options."""
    parser.addoption(
        "--integration-model",
        action="store",
        default="base",
        choices=["base", "advanced"],
        help="Model tier for integration tests: base (deepseek-v3.2) or advanced (gemini-2.5-flash-free)"
    )


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line("markers", "unit: Fast unit tests (mocked)")
    config.addinivalue_line("markers", "integration: Integration tests (real API)")
    config.addinivalue_line("markers", "slow: Slow running tests")
    config.addinivalue_line("markers", "expensive: Tests that cost money")
    config.addinivalue_line("markers", "advanced: Tests requiring advanced models (gemini)")


# ============================================================================
# DATABASE ISOLATION - CRITICAL SAFETY MEASURE
# ============================================================================
# This fixture runs automatically for ALL tests in the entire test session.
# It ensures that NO test can ever touch the production database.

@pytest.fixture(scope="session", autouse=True)
def isolate_database_from_production(tmp_path_factory):
    """
    CRITICAL: Force ALL tests to use a temporary database directory.
    
    Uses EDITOR_ASSISTANT_TEST_DB_DIR (separate from production env var).
    This prevents any test from accidentally touching ~/.editor_assistant/
    """
    # Create a session-wide temp directory for the database
    test_db_dir = tmp_path_factory.mktemp("test_editor_assistant")
    
    # Use the TEST-specific environment variable (not the production one)
    os.environ["EDITOR_ASSISTANT_TEST_DB_DIR"] = str(test_db_dir)
    
    yield test_db_dir
    
    # Clean up after all tests
    if "EDITOR_ASSISTANT_TEST_DB_DIR" in os.environ:
        del os.environ["EDITOR_ASSISTANT_TEST_DB_DIR"]


# ============================================================================
# PATH FIXTURES
# ============================================================================

@pytest.fixture
def project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent


@pytest.fixture
def sample_data_dir() -> Path:
    """Get the sample data directory."""
    return Path(__file__).parent / "fixtures" / "sample_data"


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test outputs."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


# ============================================================================
# SAMPLE DATA FIXTURES
# ============================================================================

@pytest.fixture
def sample_paper_content(sample_data_dir) -> str:
    """Load Shannon's paper as raw content."""
    paper_path = sample_data_dir / "A Mathematical Theory of Communication.md"
    if paper_path.exists():
        return paper_path.read_text(encoding='utf-8')
    return _get_fallback_paper_content()


@pytest.fixture
def sample_paper_article(sample_paper_content):
    """Create an MDArticle from the sample paper."""
    from editor_assistant.data_models import MDArticle, InputType
    return MDArticle(
        type=InputType.PAPER,
        content=sample_paper_content,
        title="A Mathematical Theory of Communication",
        authors="Claude Shannon",
        source_path="sample_data/shannon.pdf"
    )


@pytest.fixture
def sample_news_content() -> str:
    """Sample news article content for testing."""
    return """# New Breakthrough in Quantum Computing

Researchers have achieved a significant milestone in quantum error correction.

The team demonstrated 99.9% fidelity in quantum operations, marking a major 
step toward practical quantum computing applications.

"This breakthrough could accelerate quantum advantage by several years," 
said the lead researcher.

The findings were published in Nature today.
"""


@pytest.fixture
def sample_news_article(sample_news_content):
    """Create an MDArticle from sample news."""
    from editor_assistant.data_models import MDArticle, InputType
    return MDArticle(
        type=InputType.NEWS,
        content=sample_news_content,
        title="Quantum Computing Breakthrough",
        source_path="https://example.com/news"
    )


@pytest.fixture
def short_test_content() -> str:
    """Short content for quick tests."""
    return """# Test Document

This is a test document with minimal content.

## Section 1
Some test content here.

## Section 2  
More test content for validation.
"""


@pytest.fixture
def short_paper_article(short_test_content):
    """Create a minimal MDArticle for quick tests."""
    from editor_assistant.data_models import MDArticle, InputType
    return MDArticle(
        type=InputType.PAPER,
        content=short_test_content,
        title="Test Document",
        source_path="/tmp/test.md"
    )


# ============================================================================
# MOCK FIXTURES
# ============================================================================

@pytest.fixture
def mock_llm_response() -> str:
    """Standard mock LLM response."""
    return """**测试新闻标题**

这是一篇测试生成的新闻内容。研究团队在相关领域取得了重要进展。

该研究采用了创新的方法论，实验结果表明效果显著。这一发现对于未来的应用具有重要意义。

研究论文已发表于预印本平台。
"""


@pytest.fixture
def mock_llm_client(mock_llm_response):
    """Create a mock LLM client for unit tests."""
    mock = MagicMock()
    mock.model = "mock-model"
    mock.context_window = 128000
    mock.max_tokens = 8000
    mock.generate_response.return_value = mock_llm_response
    mock.get_token_usage.return_value = {
        "total_input_tokens": 1000,
        "total_output_tokens": 500,
        "cost": {"total_cost": 0.01}
    }
    mock.save_token_usage_report = MagicMock()
    return mock


@pytest.fixture
def mock_failing_llm_client():
    """Mock LLM client that raises errors."""
    mock = MagicMock()
    mock.model = "failing-model"
    mock.context_window = 128000
    mock.max_tokens = 8000
    mock.generate_response.side_effect = ConnectionError("API unavailable")
    return mock


# ============================================================================
# REAL CLIENT FIXTURES (for integration tests)
# ============================================================================

# Model constants for integration tests
INTEGRATION_MODELS = {
    "base": "deepseek-v3.2",              # Cheap, fast - default for integration tests
    "advanced": "gemini-2.5-flash-free"   # Free tier Gemini 2.5 - for advanced model testing
}


@pytest.fixture
def budget_model_name(request) -> str:
    """Return the model for integration testing based on --integration-model option."""
    tier = request.config.getoption("--integration-model")
    return INTEGRATION_MODELS.get(tier, INTEGRATION_MODELS["base"])


@pytest.fixture
def real_llm_client(budget_model_name):
    """Create a real LLM client for integration tests."""
    from editor_assistant.llm_client import LLMClient
    return LLMClient(budget_model_name)


@pytest.fixture
def advanced_model_name() -> str:
    """Return the advanced model name (gemini-2.5-flash-free)."""
    return INTEGRATION_MODELS["advanced"]


@pytest.fixture
def base_model_name() -> str:
    """Return the base model name (deepseek-v3.2)."""
    return INTEGRATION_MODELS["base"]


# ============================================================================
# SKIP CONDITIONS
# ============================================================================

@pytest.fixture
def skip_without_api_key():
    """Skip test if required API keys are not set."""
    # DeepSeek now only supported via Volcengine key.
    if not os.getenv("DEEPSEEK_API_KEY_VOLC"):
        pytest.skip("Missing API key: DEEPSEEK_API_KEY_VOLC")


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _get_fallback_paper_content() -> str:
    """Fallback paper content when file not available."""
    return """# A Mathematical Theory of Communication

## Abstract
This paper develops the mathematical foundations of information theory.

## Introduction
The fundamental problem of communication is reproducing at one point 
a message selected at another point.

## Methods
We introduce the concept of entropy and channel capacity.

## Results
The paper proves that reliable communication is possible at rates 
below channel capacity.

## Conclusion
Information theory provides a mathematical framework for 
understanding communication systems.
"""

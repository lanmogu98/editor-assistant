"""
Test URLs for integration testing.

These are real-world test cases for validating the full pipeline.
"""

# Long paper - HTML version (arxiv)
PAPER_HTML_LONG = "https://arxiv.org/html/2502.10517v1"

# Long paper - PDF version (arxiv)  
PAPER_PDF_LONG = "https://arxiv.org/pdf/2502.10517v1"

# News article - blog post
NEWS_BLOG = "https://simonguo.tech/blog/2025-10-automated-gpu-kernels.html"

# Short news - CRFM announcement
NEWS_SHORT = "https://crfm.stanford.edu/2025/05/28/fast-kernels.html"


# Grouped by type for easy access
TEST_PAPERS = {
    "html_long": PAPER_HTML_LONG,
    "pdf_long": PAPER_PDF_LONG,
}

TEST_NEWS = {
    "blog": NEWS_BLOG,
    "short": NEWS_SHORT,
}

# All test URLs
ALL_TEST_URLS = {
    **TEST_PAPERS,
    **TEST_NEWS,
}


def get_test_url(name: str) -> str:
    """Get a test URL by name."""
    return ALL_TEST_URLS.get(name)


def list_test_urls() -> dict:
    """List all available test URLs."""
    return ALL_TEST_URLS.copy()


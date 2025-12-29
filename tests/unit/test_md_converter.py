"""
Unit tests for `MarkdownConverter` (src/editor_assistant/md_converter.py).

Beginner-friendly notes:
-----------------------
These tests focus on *control flow* and *side effects*:
- Which converter is chosen (HTML converter vs MarkItDown)
- Whether conversion failures fall back correctly
- Whether a markdown output file is written to disk

We do NOT make real network calls:
- `_is_url_html()` normally does an HTTP HEAD request, so in unit tests we patch it.
"""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from editor_assistant.data_models import InputType, MDArticle
from editor_assistant.md_converter import MarkdownConverter


@pytest.fixture
def converter() -> MarkdownConverter:
    """
    Create a MarkdownConverter with a stubbed MarkItDown instance.

    Why we do this:
    - The property `MarkdownConverter.markitdown` imports `markitdown` lazily.
    - In tests we want to avoid importing external dependencies unless necessary.
    """
    c = MarkdownConverter()
    c._markitdown = MagicMock()
    return c


@pytest.mark.unit
def test_html_file_uses_clean_html_converter(monkeypatch, tmp_path: Path, converter: MarkdownConverter) -> None:
    """
    If the input is an HTML file, we prefer CleanHTML2Markdown.
    """
    html_path = tmp_path / "page.html"
    html_path.write_text("<html><body>Hello</body></html>", encoding="utf-8")

    # Avoid any URL HEAD logic — this is a local file test.
    monkeypatch.setattr(converter, "_is_url_html", lambda _: False)

    md_from_html = MDArticle(
        type=InputType.PAPER,
        title="A/B",  # Title contains '/', converter should sanitize it to 'A-B'
        content="# Title\n\nBody",
        source_path=str(html_path),
        converter="CleanHTML2Markdown",
    )

    # NOTE: MarkdownConverter imports CleanHTML2Markdown *inside* convert_content():
    #   from .clean_html_to_md import CleanHTML2Markdown
    # So we patch it at its defining module path.
    with patch("editor_assistant.clean_html_to_md.CleanHTML2Markdown") as MockClean:
        MockClean.return_value.convert.return_value = md_from_html

        result = converter.convert_content(str(html_path), type=InputType.PAPER)

    assert result is not None
    assert result.title == "A-B"  # '/' replaced
    assert result.output_path is not None
    assert Path(result.output_path).exists()

    # Since HTML conversion succeeded, we should NOT fall back to MarkItDown.
    converter._markitdown.convert.assert_not_called()


@pytest.mark.unit
def test_html_file_falls_back_to_markitdown_when_html_conversion_returns_none(
    monkeypatch, tmp_path: Path, converter: MarkdownConverter
) -> None:
    """
    If CleanHTML2Markdown returns None, we should fall back to MarkItDown.
    """
    html_path = tmp_path / "page.html"
    html_path.write_text("<html><body>Hello</body></html>", encoding="utf-8")

    monkeypatch.setattr(converter, "_is_url_html", lambda _: False)

    # MarkItDown.convert(...) returns an object with `.markdown` and `.title`.
    converter._markitdown.convert.return_value = SimpleNamespace(
        markdown="Converted markdown",
        title="From MarkItDown",
    )

    with patch("editor_assistant.clean_html_to_md.CleanHTML2Markdown") as MockClean:
        MockClean.return_value.convert.return_value = None

        result = converter.convert_content(str(html_path), type=InputType.NEWS)

    assert result is not None
    assert result.converter == "MarkItDown"
    assert result.type == InputType.NEWS
    converter._markitdown.convert.assert_called_once()
    assert Path(result.output_path).exists()


@pytest.mark.unit
def test_markitdown_failure_returns_none(monkeypatch, tmp_path: Path, converter: MarkdownConverter) -> None:
    """
    If MarkItDown conversion raises, convert_content should return None.
    """
    md_path = tmp_path / "paper.pdf"
    md_path.write_text("dummy", encoding="utf-8")

    # Make sure we go down the MarkItDown path (not HTML).
    monkeypatch.setattr(converter, "_is_url_html", lambda _: False)

    converter._markitdown.convert.side_effect = Exception("boom")
    result = converter.convert_content(str(md_path), type=InputType.PAPER)

    assert result is None


@pytest.mark.unit
def test_url_html_writes_output_under_webpage_dir(monkeypatch, tmp_path: Path, converter: MarkdownConverter) -> None:
    """
    For HTML URLs, MarkdownConverter writes outputs under a `webpage/` folder.

    The code uses a relative path like `webpage//example.com/...`, so we `chdir`
    into a temp directory to keep filesystem writes contained.
    """
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(converter, "_is_url_html", lambda _: True)

    url = "https://example.com/a/b"
    md_from_html = MDArticle(
        type=InputType.PAPER,
        title="My Title",
        content="Hello from URL",
        source_path=url,
        converter="CleanHTML2Markdown",
    )

    with patch("editor_assistant.clean_html_to_md.CleanHTML2Markdown") as MockClean:
        MockClean.return_value.convert.return_value = md_from_html
        result = converter.convert_content(url, type=InputType.PAPER)

    assert result is not None
    assert Path(result.output_path).exists()
    assert "webpage" in str(result.output_path)



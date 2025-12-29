"""
Unit tests for main.EditorAssistant.process_multiple covering partial/total conversion failure.
"""

import asyncio
from pathlib import Path
from unittest.mock import MagicMock, patch, AsyncMock

import pytest

from editor_assistant.main import EditorAssistant
from editor_assistant.data_models import Input, InputType
from editor_assistant.data_models import MDArticle


@pytest.mark.unit
@pytest.mark.asyncio
async def test_process_multiple_all_inputs_fail():
    """All inputs fail conversion -> no processing call."""
    with patch("editor_assistant.main.MarkdownConverter") as MockConverter, \
         patch("editor_assistant.main.MDProcessor") as MockProcessor:
        mock_converter = MockConverter.return_value
        mock_converter.convert_content.side_effect = Exception("boom")

        mock_processor = MockProcessor.return_value
        mock_processor.process_mds = AsyncMock()

        assistant = EditorAssistant("test-model", stream=False)
        inputs = [Input(type=InputType.PAPER, path="file1.pdf")]

        await assistant.process_multiple(inputs, "brief")

        mock_processor.process_mds.assert_not_called()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_process_multiple_partial_fail_warns_but_processes(tmp_path, capsys):
    """When some inputs fail conversion, processing continues without persisting failed inputs."""
    good_path = tmp_path / "good.pdf"
    good_path.write_text("dummy", encoding="utf-8")

    good_input = Input(type=InputType.PAPER, path=str(good_path))
    bad_input = Input(type=InputType.PAPER, path="bad.pdf")

    good_article = MDArticle(
        type=InputType.PAPER,
        content="ok " * 500,  # Sufficient content to pass validation
        title="good",
        source_path=str(good_path),
        output_path=str(good_path),
    )

    with patch("editor_assistant.main.MarkdownConverter") as MockConverter, \
         patch("editor_assistant.main.MDProcessor") as MockProcessor:
        mock_converter = MockConverter.return_value
        mock_converter.convert_content.side_effect = [
            good_article,  # for good input
            None,          # for bad input
        ]

        mock_processor = MockProcessor.return_value
        mock_processor.process_mds = AsyncMock(return_value=(True, 123))
        assistant = EditorAssistant("test-model", stream=False)

        await assistant.process_multiple([good_input, bad_input], "brief")

        mock_processor.process_mds.assert_called_once()
        # Ensure warning emitted for failed input (printed to stdout)
        captured = capsys.readouterr().out
        assert "failed" in captured.lower() or "Failed" in captured

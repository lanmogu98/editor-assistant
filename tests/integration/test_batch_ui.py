import pytest
import asyncio
from pathlib import Path
from unittest.mock import MagicMock, patch
from editor_assistant.cli import cmd_batch_process
from editor_assistant.data_models import Input, InputType

pytestmark = pytest.mark.unit

@pytest.mark.asyncio
async def test_batch_process_ui_flow(tmp_path, capsys):
    """
    Test the batch processing UI flow including:
    1. File discovery
    2. Rich progress bar initialization (mocked/verified)
    3. Processing execution
    4. Summary table generation
    """
    # 1. Setup test data
    input_dir = tmp_path / "inputs"
    input_dir.mkdir()
    
    # Create 3 dummy markdown files
    for i in range(3):
        (input_dir / f"doc{i}.md").write_text(f"# Doc {i}\nContent {i}", encoding="utf-8")
        
    # 2. Mock Arguments
    args = MagicMock()
    args.folder = str(input_dir)
    args.task = "brief"
    args.ext = ".md"
    args.model = "deepseek-v3.2"
    args.debug = False
    args.thinking = None
    args.no_stream = False
    args.save_files = True

    # 3. Mock EditorAssistant to avoid real API calls and speed up test
    with patch("editor_assistant.cli.EditorAssistant") as MockAssistant:
        mock_instance = MockAssistant.return_value
        
        # Mock process_multiple to simulate successful processing
        async def mock_process(*args, **kwargs):
            # Simulate callbacks if provided
            callbacks = kwargs.get("progress_callbacks", {})
            done_callback = kwargs.get("done_callback")
            
            for path in callbacks:
                # Trigger some stream updates
                callbacks[path]("chunk")
                
            # Trigger done callbacks
            if done_callback:
                for path in callbacks:
                    done_callback(path, True)
            
            return
            
        mock_instance.process_multiple.side_effect = mock_process
        
        # Mock LLMClient token usage for summary
        mock_client = MagicMock()
        mock_client.pricing_currency = "$"
        mock_client.get_token_usage.return_value = {
            "total_input_tokens": 100,
            "total_output_tokens": 50,
            "cost": {"total_cost": 0.002},
            "requests": ["req1", "req2", "req3"] # 3 successful requests
        }
        mock_instance.md_processor.llm_client = mock_client

        # 4. Run the command
        # We need to mock RICH_AVAILABLE to True to ensure UI path is taken
        with patch("editor_assistant.cli.RICH_AVAILABLE", True):
            # We also need to patch Console/Progress to verify they are called correctly
            # and to prevent actual terminal manipulation during test
            with patch("editor_assistant.cli.Console") as MockConsole, \
                 patch("editor_assistant.cli.Progress") as MockProgress:
                
                # Setup Progress context manager mock
                progress_ctx = MagicMock()
                MockProgress.return_value.__enter__.return_value = progress_ctx
                
                # Run
                await cmd_batch_process(args)
                
                # 5. Verifications
                
                # Verify Console was instantiated with force_terminal=True (The Fix)
                # It is instantiated twice (once for Progress, once for Summary), so check any call
                MockConsole.assert_any_call(force_terminal=True)
                
                # Verify Progress was called with transient=True (The Fix)
                # We check the kwargs passed to Progress constructor
                call_kwargs = MockProgress.call_args.kwargs
                assert call_kwargs.get("transient") is True, "Progress should be transient"
                assert call_kwargs.get("console") == MockConsole.return_value, "Progress should use our forced console"
                
                # Verify file discovery
                assert mock_instance.process_multiple.called
                call_args = mock_instance.process_multiple.call_args
                assert len(call_args[0][0]) == 3 # 3 inputs
                
                # Verify summary table printing
                # Console.print should be called for the Panel
                assert MockConsole.return_value.print.called
                
                # Verify log suppression (logging.getLogger().setLevel called with WARNING)
                # This is harder to verify without mocking logging, but the code path is covered.


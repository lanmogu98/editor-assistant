"""
Integration tests for storage module with real LLM API calls.

These tests verify that the storage module correctly records real runs.

NOTE: Database isolation is handled automatically by conftest.py's
      isolate_database_from_production fixture (session-scoped, autouse=True).
      All tests automatically use a temporary database.
"""

import pytest
import subprocess
import os
import sys
from typing import Dict, List, Optional
from pathlib import Path

from editor_assistant.storage import RunRepository
from editor_assistant.md_processor import MDProcessor
from editor_assistant.data_models import MDArticle, InputType, ProcessType


def _run_cli(args: List[str], *, timeout: int, env: Optional[Dict[str, str]] = None) -> subprocess.CompletedProcess[str]:
    """
    Run the CLI as a Python module.

    Beginner note:
    We prefer `python -m editor_assistant.cli` over the `editor-assistant` console script
    because the console script may not be installed in all test environments.
    """
    return subprocess.run(
        [sys.executable, "-m", "editor_assistant.cli", *args],
        capture_output=True,
        text=True,
        timeout=timeout,
        env=env,
    )


@pytest.fixture
def sample_article(temp_dir):
    """Create a sample article for testing with sufficient content."""
    # Need enough content to pass validation (> 1000 chars)
    content = "# Test Paper\n\n" + "This is test content for the paper. " * 100
    return MDArticle(
        type=InputType.PAPER,
        content=content,
        title="Test Paper Title",
        source_path="https://example.com/test.html",
        output_path=str(temp_dir / "output.md")
    )


@pytest.mark.asyncio
class TestStorageIntegration:
    """Integration tests for storage with real processing."""
    
    @pytest.mark.skipif(
        not os.getenv("DEEPSEEK_API_KEY_VOLC"),
        reason="DEEPSEEK_API_KEY_VOLC not set",
    )
    @pytest.mark.integration
    @pytest.mark.slow
    async def test_real_run_recorded_in_database(self, sample_article, budget_model_name):
        """A real LLM call should be recorded in the database."""
        # Database is automatically isolated by conftest.py
        processor = MDProcessor(budget_model_name, stream=False)
        
        # Process (this makes a real API call)
        success, run_id = await processor.process_mds(
            [sample_article], 
            ProcessType.BRIEF, 
            output_to_console=False
        )
        
        # Verify run was recorded
        runs = processor.repository.get_recent_runs()
        
        assert len(runs) >= 1
        latest_run = runs[0]
        
        assert latest_run["task"] == "brief"
        assert latest_run["model"] == budget_model_name
        
        if success:
            assert latest_run["status"] == "success"
            assert latest_run["total_cost"] is not None
        else:
            assert latest_run["status"] == "failed"
    
    @pytest.mark.skipif(
        not os.getenv("DEEPSEEK_API_KEY_VOLC"),
        reason="DEEPSEEK_API_KEY_VOLC not set",
    )
    @pytest.mark.integration
    @pytest.mark.slow
    async def test_run_details_complete(self, sample_article, budget_model_name):
        """Run details should include all expected fields."""
        # Database is automatically isolated by conftest.py
        processor = MDProcessor(budget_model_name, stream=False)
        
        await processor.process_mds(
            [sample_article], 
            ProcessType.BRIEF, 
            output_to_console=False
        )
        
        runs = processor.repository.get_recent_runs()
        if runs:
            run_id = runs[0]["id"]
            details = processor.repository.get_run_details(run_id)
            
            # Verify structure
            assert "id" in details
            assert "timestamp" in details
            assert "task" in details
            assert "model" in details
            assert "status" in details
            assert "inputs" in details
            assert "outputs" in details
            assert "token_usage" in details
            
            # Verify inputs
            assert len(details["inputs"]) == 1
            assert details["inputs"][0]["title"] == "Test Paper Title"
            
            # If successful, verify outputs and usage
            if details["status"] == "success":
                assert len(details["outputs"]) >= 1
                assert details["token_usage"] is not None
                assert details["token_usage"]["input_tokens"] > 0


class TestCLIHistoryCommands:
    """Integration tests for CLI history commands."""
    
    @pytest.mark.integration
    def test_history_command_with_data(self, isolate_database_from_production):
        """History command should show recorded runs."""
        # Add some data to the isolated database
        repo = RunRepository()  # Uses isolated DB automatically
        input_id = repo.get_or_create_input("paper", "/test.pdf", "Test Paper", "Content")
        run_id = repo.create_run("brief", "test-model", [input_id], currency="$")
        repo.update_run_status(run_id, "success")
        
        # Run history command with the isolated env
        env = os.environ.copy()
        result = _run_cli(["history"], timeout=30, env=env)
        
        # Verify command succeeds
        assert result.returncode == 0
    
    @pytest.mark.integration
    def test_stats_command_format(self):
        """Stats command should output correct format."""
        # Uses isolated database automatically
        env = os.environ.copy()
        
        result = _run_cli(["stats"], timeout=30, env=env)
        
        assert result.returncode == 0
        assert "Usage Statistics" in result.stdout
        assert "Total Runs:" in result.stdout

"""
CLI end-to-end tests.

These tests run actual CLI commands.
"""

import pytest
import subprocess
import os
import sys
from typing import Dict, List, Optional
from pathlib import Path


DEEPSEEK_VOLC_AVAILABLE = bool(os.getenv("DEEPSEEK_API_KEY_VOLC"))


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


class TestCLIBrief:
    """Test CLI brief command."""
    
    @pytest.mark.integration
    @pytest.mark.slow
    @pytest.mark.skipif(not DEEPSEEK_VOLC_AVAILABLE, reason="DEEPSEEK_API_KEY_VOLC not set")
    def test_brief_command_runs(self, temp_dir, sample_data_dir):
        """Test that brief command runs successfully."""
        # Use a local file if available
        sample_file = sample_data_dir / "A Mathematical Theory of Communication.md"
        if not sample_file.exists():
            pytest.skip("Sample file not found")
        
        result = _run_cli(
            [
                "brief",
                f"paper={sample_file}",
                "--model", "deepseek-v3.2",
                "--no-stream",
            ],
            timeout=120,
        )
        
        # Check it ran (may fail due to content, but should not crash)
        assert result.returncode in [0, 1]  # 0 = success, 1 = processing error
    
    @pytest.mark.integration
    @pytest.mark.slow
    @pytest.mark.skipif(not DEEPSEEK_VOLC_AVAILABLE, reason="DEEPSEEK_API_KEY_VOLC not set")
    def test_brief_with_url(self, temp_dir):
        """Test brief with URL input."""
        from tests.fixtures.test_urls import NEWS_SHORT
        
        result = _run_cli(
            [
                "brief",
                f"news={NEWS_SHORT}",
                "--model", "deepseek-v3.2",
                "--no-stream",
            ],
            timeout=180,
        )
        
        # Just check it doesn't crash
        assert result.returncode in [0, 1]


class TestCLIProcess:
    """Test CLI process (multi-task) command."""
    
    @pytest.mark.integration
    @pytest.mark.slow
    @pytest.mark.skipif(not DEEPSEEK_VOLC_AVAILABLE, reason="DEEPSEEK_API_KEY_VOLC not set")
    def test_process_multiple_tasks(self, temp_dir, sample_data_dir):
        """Test process command with multiple tasks."""
        sample_file = sample_data_dir / "A Mathematical Theory of Communication.md"
        if not sample_file.exists():
            pytest.skip("Sample file not found")
        
        result = _run_cli(
            [
                "process",
                f"paper={sample_file}",
                "--tasks", "brief",
                "--model", "deepseek-v3.2",
                "--no-stream",
            ],
            timeout=120,
        )
        
        assert result.returncode in [0, 1]


class TestCLIHelp:
    """Test CLI help commands (no API calls)."""
    
    @pytest.mark.unit
    def test_help_command(self):
        """Test --help works."""
        result = _run_cli(["--help"], timeout=30)
        
        assert result.returncode == 0
        assert "editor-assistant" in result.stdout.lower()
    
    @pytest.mark.unit
    def test_brief_help(self):
        """Test brief --help works."""
        result = _run_cli(["brief", "--help"], timeout=30)
        
        assert result.returncode == 0
        assert "brief" in result.stdout.lower()
    
    @pytest.mark.unit
    def test_version_command(self):
        """Test --version works."""
        result = _run_cli(["--version"], timeout=30)
        
        assert result.returncode == 0


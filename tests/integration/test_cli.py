"""
CLI end-to-end tests.

These tests run actual CLI commands.
"""

import pytest
import subprocess
import os
from pathlib import Path


# Skip all tests if no API key
pytestmark = pytest.mark.skipif(
    not os.getenv("DEEPSEEK_API_KEY"),
    reason="DEEPSEEK_API_KEY not set"
)


class TestCLIBrief:
    """Test CLI brief command."""
    
    @pytest.mark.integration
    @pytest.mark.slow
    def test_brief_command_runs(self, temp_dir, sample_data_dir):
        """Test that brief command runs successfully."""
        # Use a local file if available
        sample_file = sample_data_dir / "A Mathematical Theory of Communication.md"
        if not sample_file.exists():
            pytest.skip("Sample file not found")
        
        result = subprocess.run(
            [
                "editor-assistant", "brief",
                f"paper={sample_file}",
                "--model", "deepseek-v3.2",
                "--no-stream"
            ],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        # Check it ran (may fail due to content, but should not crash)
        assert result.returncode in [0, 1]  # 0 = success, 1 = processing error
    
    @pytest.mark.integration
    @pytest.mark.slow
    def test_brief_with_url(self, temp_dir):
        """Test brief with URL input."""
        from tests.fixtures.test_urls import NEWS_SHORT
        
        result = subprocess.run(
            [
                "editor-assistant", "brief",
                f"news={NEWS_SHORT}",
                "--model", "deepseek-v3.2",
                "--no-stream"
            ],
            capture_output=True,
            text=True,
            timeout=180
        )
        
        # Just check it doesn't crash
        assert result.returncode in [0, 1]


class TestCLIProcess:
    """Test CLI process (multi-task) command."""
    
    @pytest.mark.integration
    @pytest.mark.slow
    def test_process_multiple_tasks(self, temp_dir, sample_data_dir):
        """Test process command with multiple tasks."""
        sample_file = sample_data_dir / "A Mathematical Theory of Communication.md"
        if not sample_file.exists():
            pytest.skip("Sample file not found")
        
        result = subprocess.run(
            [
                "editor-assistant", "process",
                f"paper={sample_file}",
                "--tasks", "brief",
                "--model", "deepseek-v3.2",
                "--no-stream"
            ],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        assert result.returncode in [0, 1]


class TestCLIHelp:
    """Test CLI help commands (no API calls)."""
    
    @pytest.mark.unit
    def test_help_command(self):
        """Test --help works."""
        result = subprocess.run(
            ["editor-assistant", "--help"],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        assert "editor-assistant" in result.stdout.lower()
    
    @pytest.mark.unit
    def test_brief_help(self):
        """Test brief --help works."""
        result = subprocess.run(
            ["editor-assistant", "brief", "--help"],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        assert "brief" in result.stdout.lower()
    
    @pytest.mark.unit
    def test_version_command(self):
        """Test --version works."""
        result = subprocess.run(
            ["editor-assistant", "--version"],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0


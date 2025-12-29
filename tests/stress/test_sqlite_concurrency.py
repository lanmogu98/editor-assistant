"""
Stress test for SQLite concurrent writes.
Verifies if the database locks up under high concurrency from the async processor.
"""

import pytest
import asyncio
from editor_assistant.storage import RunRepository
from editor_assistant.md_processor import MDProcessor
from editor_assistant.data_models import MDArticle, InputType
from unittest.mock import MagicMock, AsyncMock, patch

@pytest.mark.asyncio
@pytest.mark.slow
async def test_sqlite_concurrent_writes_stress(monkeypatch):
    """
    Simulate 50 concurrent task completions trying to write to DB simultaneously.
    """
    # MDProcessor -> LLMClient constructor requires an API key env var to exist.
    # This stress test patches the *network call*, so a dummy key is sufficient.
    monkeypatch.setenv("DEEPSEEK_API_KEY_VOLC", "test-key-volc")

    repo = RunRepository()
    
    # Mock usage dict
    mock_usage = {
        "total_input_tokens": 100,
        "total_output_tokens": 50,
        "cost": {"input_cost": 0.001, "output_cost": 0.001, "total_cost": 0.002},
        "process_times": {"total_time": 0.1}
    }
    
    # Patch generate_response on the LLMClient class to avoid real API calls
    # We use a real model name to pass validation, but intercept the call
    with patch("editor_assistant.llm_client.LLMClient.generate_response", new_callable=AsyncMock) as mock_generate, \
         patch("editor_assistant.llm_client.LLMClient.get_token_usage") as mock_get_usage:
        
        # generate_response now returns tuple (response, usage)
        mock_generate.return_value = ("Stress test response", mock_usage)
        mock_get_usage.return_value = mock_usage

        # Initialize processor with high concurrency
        # Use a valid model name
        processor = MDProcessor("deepseek-v3.2", max_concurrent=50)
        
        # Create 50 inputs with sufficient content
        inputs = [
            MDArticle(
                type=InputType.PAPER, 
                content=f"Content {i} " * 500,  # Sufficient content
                title=f"Stress Test {i}", 
                source_path=f"stress_{i}.txt"
            ) 
            for i in range(50)
        ]
        
        # Run all 50 tasks
        # They will all hit the DB write phase roughly at the same time
        print("\nLaunching 50 concurrent tasks...")
        results = await asyncio.gather(
            *[processor.process_mds([inp], "brief", output_to_console=False) for inp in inputs]
        )
        
        # Verify results
        success_count = sum(1 for r in results if isinstance(r, tuple) and r[0])
        fail_count = 50 - success_count
        
        print(f"Success: {success_count}, Failed: {fail_count}")
        
        # Check DB consistency
        runs = repo.get_recent_runs(limit=100)
        stress_runs = [r for r in runs if r['model'] == 'deepseek-v3.2' and 'Stress Test' in str(r['input_titles'])]
        
        # Assertions
        # If we didn't optimize DB writes, this might fail with fewer records or errors
        assert success_count == 50, f"Expected 50 successes, got {success_count}"
        assert len(stress_runs) == 50, f"Expected 50 DB records, got {len(stress_runs)}"

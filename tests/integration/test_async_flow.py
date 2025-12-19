"""
Integration test for Async Flow (End-to-End).
"""

import pytest
import os
import asyncio
from editor_assistant.main import EditorAssistant
from editor_assistant.data_models import Input, InputType, ProcessType

# Skip if API keys are not set
pytestmark = pytest.mark.skipif(
    not os.getenv("DEEPSEEK_API_KEY_VOLC") and not os.getenv("DEEPSEEK_API_KEY"),
    reason="DEEPSEEK_API_KEY_VOLC or DEEPSEEK_API_KEY not set"
)

# Use cheap model for testing
TEST_MODEL = "deepseek-v3.2" 

@pytest.mark.integration
@pytest.mark.asyncio
async def test_async_process_multiple_real_api(tmp_path):
    """
    Test full async processing flow with real API.
    Process multiple 'papers' concurrently.
    """
    
    # Create dummy inputs
    inputs = []
    for i in range(3):
        # Create a dummy markdown file
        p = tmp_path / f"paper_{i}.md"
        p.write_text(f"# Paper {i}\n\nThis is the content of paper {i}. It discusses async processing.", encoding="utf-8")
        inputs.append(Input(type=InputType.PAPER, path=str(p)))

    # Initialize assistant
    # Note: debug_mode=True helps see logs
    assistant = EditorAssistant(TEST_MODEL, debug_mode=True, stream=False)
    
    # Run async processing
    # Using 'brief' task which is usually faster/cheaper
    await assistant.process_multiple(inputs, ProcessType.BRIEF, save_files=False)
    
    # Verification
    # Since process_multiple returns None, we verify side effects:
    # 1. Check database for runs
    from editor_assistant.storage import RunRepository
    repo = RunRepository()
    
    # We expect 3 runs to be created (one for each input)
    # Get recent runs and filter by our test model/task
    recent_runs = repo.get_recent_runs(limit=10)
    
    # Filter runs that match our test execution
    # This is a bit loose, but sufficient for basic integration check
    test_runs = [
        r for r in recent_runs 
        if r['model'] == TEST_MODEL and r['task'] == ProcessType.BRIEF.value
    ]
    
    # We should have at least 3 runs from this session (plus maybe previous ones)
    assert len(test_runs) >= 3
    
    # Check status of the latest 3 runs
    for run in test_runs[:3]:
        # They might be 'success' or 'failed' (if API error), but should not be 'pending' if awaited correctly
        assert run['status'] in ['success', 'failed']
        if run['status'] == 'failed':
            print(f"Run {run['id']} failed: {run.get('error_message')}")

if __name__ == "__main__":
    # Allow running directly for manual check
    asyncio.run(test_async_process_multiple_real_api(Path(".")))


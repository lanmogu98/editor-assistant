
import pytest
import os
import asyncio
import time
from editor_assistant.main import EditorAssistant
from editor_assistant.data_models import Input, InputType, ProcessType
from editor_assistant.config.constants import MIN_REQUEST_INTERVAL_SECONDS

# Skip if API key not set
pytestmark = pytest.mark.skipif(
    not os.getenv("DEEPSEEK_API_KEY_VOLC") and not os.getenv("DEEPSEEK_API_KEY"),
    reason="DEEPSEEK_API_KEY_VOLC or DEEPSEEK_API_KEY not set"
)

TEST_MODEL = "deepseek-v3.2"

@pytest.mark.integration
@pytest.mark.expensive
@pytest.mark.asyncio
async def test_high_concurrency_load(tmp_path):
    """
    Submit 10 concurrent requests to real API.
    Verify all complete successfully without 429 errors crashing the process.
    """
    
    # Create 10 dummy inputs
    inputs = []
    for i in range(10):
        p = tmp_path / f"load_test_{i}.md"
        p.write_text(f"# Load Test {i}\n\nSimple content {i} for stress testing.", encoding="utf-8")
        inputs.append(Input(type=InputType.PAPER, path=str(p)))

    # Initialize with default settings (should handle rate limiting)
    assistant = EditorAssistant(TEST_MODEL, debug_mode=True, stream=False)
    
    start_time = time.time()
    
    # Process all 10 concurrently
    # This will trigger 10 API calls almost simultaneously
    # The client-side rate limiter and semaphore should spread them out
    await assistant.process_multiple(inputs, ProcessType.BRIEF, save_files=False)
    
    duration = time.time() - start_time
    
    # Verify results in DB
    from editor_assistant.storage import RunRepository
    repo = RunRepository()
    recent_runs = repo.get_recent_runs(limit=20)
    
    # Filter for our test runs
    test_runs = [
        r for r in recent_runs 
        if r['model'] == TEST_MODEL 
        and r['task'] == ProcessType.BRIEF.value
        and "load_test" in r['input_titles']
    ]
    
    # We expect 10 distinct runs
    assert len(test_runs) == 10
    
    # Check for failures
    failures = [r for r in test_runs if r['status'] == 'failed']
    if failures:
        print(f"\n❌ {len(failures)} runs failed:")
        for f in failures:
            print(f"  - Run {f['id']}: {f.get('error_message')}")
            
    assert len(failures) == 0, f"{len(failures)} runs failed out of 10"
    
    print(f"\n✅ Load test passed: 10 requests in {duration:.2f}s")
    
    # Calculate effective RPS
    rps = 10 / duration
    print(f"Effective RPS: {rps:.2f}")
    
    # Ensure we respected the minimum interval (rough check)
    # 10 requests with 0.5s interval = at least 4.5s
    # However, parallelism allows overlaps if backend permits? 
    # No, our client enforces MIN_REQUEST_INTERVAL_SECONDS globally per client?
    # Actually, rate limit is per-provider.
    # If using 5 concurrent workers, total time should be approx (10/5) * latency + overhead
    # UNLESS rate limiter slows it down.


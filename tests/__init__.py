"""
Editor Assistant Test Suite.

Structure:
    tests/
    ├── conftest.py          # Shared fixtures and pytest config
    ├── fixtures/            # Test data and sample files
    │   ├── test_urls.py     # Real-world test URLs
    │   ├── md_input.py      # Sample MDArticle fixtures
    │   └── sample_data/     # PDF and MD files
    ├── unit/                # Fast tests with mocks
    │   ├── test_data_models.py
    │   ├── test_tasks.py
    │   ├── test_llm_client.py
    │   └── test_md_processor.py
    └── integration/         # Tests with real API calls
        ├── test_llm_api.py
        ├── test_tasks_api.py
        └── test_cli.py

Usage:
    # Run all unit tests (fast, no API calls)
    pytest tests/unit/ -v
    
    # Run integration tests (costs money!)
    pytest tests/integration/ -v
    
    # Run specific test file
    pytest tests/unit/test_tasks.py -v
    
    # Run with coverage
    pytest tests/unit/ --cov=src/editor_assistant
    
    # Use the test runner script
    python scripts/run_tests.py unit
    python scripts/run_tests.py integration
    python scripts/run_tests.py coverage
"""

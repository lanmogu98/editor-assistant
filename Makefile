# Editor Assistant Development Makefile

.PHONY: help install test test-unit test-integration test-budget test-all clean lint format

help:  ## Show this help message
	@echo "Editor Assistant Development Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "Test Categories:"
	@echo "  unit        - Fast tests with mocks (no API costs)"
	@echo "  budget      - Integration tests with cheaper models (low cost)"
	@echo "  integration - Full integration tests with premium models (expensive!)"

install:  ## Install package in development mode
	pip install -e .

install-dev:  ## Install with development dependencies
	pip install -e ".[dev]"

# Testing commands
test-unit:  ## Run fast unit tests (no API calls)
	python scripts/run_tests.py unit

test-budget:  ## Run integration tests with budget models
	python scripts/run_tests.py budget

test-integration:  ## Run full integration tests (expensive!)
	python scripts/run_tests.py integration

test-structure:  ## Run only code structure tests
	python scripts/run_tests.py structure

test-prompt:  ## Test prompt quality (very expensive!)
	python scripts/run_tests.py prompt

test-all:  ## Run all safe tests (unit + budget integration)
	python scripts/run_tests.py all

test-expensive:  ## Run ALL tests including expensive ones
	python scripts/run_tests.py expensive

test-coverage:  ## Run tests with coverage report
	python scripts/run_tests.py coverage

# Code quality
lint:  ## Run linting
	flake8 src/
	mypy src/

format:  ## Format code
	black src/ tests/
	isort src/ tests/

# Development helpers
clean:  ## Clean up generated files
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

dev-setup:  ## Set up development environment
	pip install -e ".[dev]"
	pre-commit install

# Quick development cycle
quick-test:  ## Quick test cycle for development
	@echo "Running quick development tests..."
	python -m pytest tests/unit/ -v --tb=short

# Multi-source development (for your planned feature)
test-multi-source:  ## Test multi-source functionality (budget models)
	python -m pytest tests/integration/test_multi_source_processing.py -v -m "budget_llm"

# Example usage
example-news:  ## Run example news generation
	editor-assistant news "https://example.com" --model deepseek-v3-latest --debug

example-outline:  ## Run example research outline
	editor-assistant outline example.pdf --model deepseek-r1-latest
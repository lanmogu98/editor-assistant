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

install:  ## Install package (production deps only)
	uv sync --no-dev

install-dev:  ## Install with development dependencies
	uv sync

# Testing commands
test-unit:  ## Run fast unit tests (no API calls)
	uv run python scripts/run_tests.py unit

test-budget:  ## Run integration tests with budget models
	uv run python scripts/run_tests.py budget

test-integration:  ## Run full integration tests (expensive!)
	uv run python scripts/run_tests.py integration

test-structure:  ## Run only code structure tests
	uv run python scripts/run_tests.py structure

test-prompt:  ## Test prompt quality (very expensive!)
	uv run python scripts/run_tests.py prompt

test-all:  ## Run all safe tests (unit + budget integration)
	uv run python scripts/run_tests.py all

test-expensive:  ## Run ALL tests including expensive ones
	uv run python scripts/run_tests.py expensive

test-coverage:  ## Run tests with coverage report
	uv run python scripts/run_tests.py coverage

# Code quality
lint:  ## Run linting
	uv run flake8 src/
	uv run mypy src/

format:  ## Format code
	uv run black src/ tests/
	uv run isort src/ tests/

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
	uv sync
	uv run pre-commit install

# Quick development cycle
quick-test:  ## Quick test cycle for development
	@echo "Running quick development tests..."
	uv run pytest tests/unit/ -v --tb=short

# Multi-source development
test-multi-source:  ## Test multi-source functionality (budget models)
	uv run pytest tests/integration/test_multi_source_processing.py -v -m "budget_llm"

# Bilingual translation development
test-bilingual:  ## Test bilingual translation functionality
	uv run pytest tests/integration/ -v -k "bilingual or translate" -m "budget_llm"

# Development workflow with different providers
dev-test-gemini:  ## Quick test with Gemini models
	uv run editor-assistant outline tests/fixtures/sample.pdf --model gemini-2.5-pro --debug

dev-test-deepseek:  ## Quick test with Deepseek models
	uv run editor-assistant brief news="https://example.com" --model deepseek-v3.1 --debug

dev-test-doubao:  ## Quick test with Doubao models
	uv run editor-assistant translate tests/fixtures/sample.pdf --model doubao-seed-1.6

# Example usage
example-brief:  ## Run example brief news generation (multi-source)
	uv run editor-assistant brief paper="https://example.com" --model deepseek-v3.1 --debug

example-news:  ## Alias for example-brief (backward compatibility)
	$(MAKE) example-brief

example-outline:  ## Run example research outline
	uv run editor-assistant outline example.pdf --model deepseek-r1

example-translate:  ## Run example bilingual translation
	uv run editor-assistant translate example.pdf --model gemini-2.5-pro --debug

example-translate-deepseek:  ## Run example translation with Deepseek
	uv run editor-assistant translate example.pdf --model deepseek-v3.1

example-translate-doubao:  ## Run example translation with Doubao
	uv run editor-assistant translate example.pdf --model doubao-seed-1.6

example-brief-multi-source:  ## Run example brief with different providers
	uv run editor-assistant brief news="https://example.com" paper=example.pdf --model deepseek-v3.1 --debug

example-outline-gemini:  ## Run example outline with Gemini
	uv run editor-assistant outline example.pdf --model gemini-2.5-pro --debug

example-convert:  ## Run example file conversion
	uv run editor-assistant convert example.pdf -o converted/

example-convert-multiple:  ## Convert multiple files
	uv run editor-assistant convert *.pdf *.docx -o converted/

example-clean:  ## Run example HTML cleaning
	uv run editor-assistant clean "https://example.com/article.html" -o clean.md

example-clean-local:  ## Clean local HTML file
	uv run editor-assistant clean example.html --stdout

# CLI validation helpers
validate-cli:  ## Test the new CLI syntax quickly
	@echo "Testing new CLI syntax..."
	uv run editor-assistant brief --help
	uv run editor-assistant outline --help
	uv run editor-assistant translate --help

models-list:  ## Show available models
	@uv run python -c "from src.editor_assistant.llm_client import LLMClient; print('Available models:'); [print(f'  {m}') for m in LLMClient.get_supported_models()]"

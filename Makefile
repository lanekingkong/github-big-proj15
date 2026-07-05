# OmniForge Makefile
# Provides convenient shortcuts for common development tasks

.PHONY: help install dev test lint format clean build

# Variables
PYTHON := python
PIP := pip
PYTEST := pytest
BLACK := black
RUFF := ruff
MYPY := mypy

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install production dependencies
	$(PIP) install -e .

dev: ## Install development dependencies
	$(PIP) install -e ".[dev]"
	pre-commit install

test: ## Run test suite
	$(PYTEST) tests/ -v

test-cov: ## Run tests with coverage
	$(PYTEST) tests/ -v --cov=omniforge --cov-report=html --cov-report=term

lint: ## Run linting
	$(RUFF) check omniforge/ tests/
	$(MYPY) omniforge/ --ignore-missing-imports

format: ## Format code
	$(BLACK) omniforge/ tests/
	$(RUFF) check --fix omniforge/ tests/

clean: ## Clean build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

build: ## Build distribution packages
	$(PYTHON) -m build

release: clean build ## Build and prepare for release
	$(PYTHON) -m twine check dist/*

check: lint test ## Run all quality checks
	@echo "All checks passed!"

run: ## Run CLI
	$(PYTHON) -m omniforge.cli $(ARGS)

shell: ## Open Python shell with omniforge imported
	$(PYTHON) -c "import omniforge; help(omniforge)"
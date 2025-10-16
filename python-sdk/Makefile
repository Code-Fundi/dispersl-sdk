# Dispersl Python SDK - Test Commands
# Comprehensive test suite with categorized commands

.PHONY: help test test-unit test-integration test-e2e test-all test-deploy test-deploy-ci
.PHONY: test-client test-http test-auth test-serializers test-agentic test-retry
.PHONY: test-workflows test-api test-complete test-watch test-coverage
.PHONY: lint format type-check clean build install-dev

# Default target
help:
	@echo "Dispersl Python SDK - Available Commands"
	@echo "========================================"
	@echo ""
	@echo "Test Commands:"
	@echo "  test              Run all tests"
	@echo "  test-unit         Run unit tests only"
	@echo "  test-integration  Run integration tests (requires localhost:3001/v1)"
	@echo "  test-e2e          Run end-to-end tests (requires localhost:3001/v1)"
	@echo "  test-all          Run all test categories"
	@echo "  test-deploy       Run integration + e2e tests (for deployment)"
	@echo "  test-deploy-ci    Run deployment tests in CI mode"
	@echo ""
	@echo "Individual Test Files:"
	@echo "  test-client       Run client tests"
	@echo "  test-http         Run HTTP client tests"
	@echo "  test-auth         Run authentication tests"
	@echo "  test-serializers  Run serializer tests"
	@echo "  test-agentic      Run agentic workflow tests"
	@echo "  test-retry        Run retry logic tests"
	@echo "  test-workflows    Run workflow integration tests"
	@echo "  test-api          Run API integration tests"
	@echo "  test-complete     Run complete workflow e2e tests"
	@echo ""
	@echo "Development Commands:"
	@echo "  test-watch        Run tests in watch mode"
	@echo "  test-coverage     Run tests with coverage report"
	@echo "  lint              Run linting"
	@echo "  format            Format code"
	@echo "  type-check        Run type checking"
	@echo "  clean             Clean build artifacts"
	@echo "  build             Build package"
	@echo "  install-dev       Install development dependencies"

# Test Commands
test:
	python run_tests.py all

test-unit:
	python run_tests.py unit

test-integration:
	python run_tests.py integration

test-e2e:
	python run_tests.py e2e

test-all:
	python run_tests.py all

test-deploy:
	python run_tests.py deploy

test-deploy-ci:
	python run_tests.py deploy-ci --ci

# Individual Test Files
test-client:
	python run_tests.py client

test-http:
	python run_tests.py http

test-auth:
	python run_tests.py auth

test-serializers:
	python run_tests.py serializers

test-agentic:
	python run_tests.py agentic

test-retry:
	python run_tests.py retry

test-workflows:
	python run_tests.py workflows

test-api:
	python run_tests.py api

test-complete:
	python run_tests.py complete

# Development Commands
test-watch:
	python run_tests.py unit --watch

test-coverage:
	python run_tests.py all --coverage

lint:
	python -m ruff check src/ tests/
	python -m pylint src/dispersl/

format:
	python -m black src/ tests/
	python -m isort src/ tests/

type-check:
	python -m mypy src/dispersl/

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf src/dispersl_sdk.egg-info/
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build:
	python -m build

install-dev:
	pip install -e ".[dev]"


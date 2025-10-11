"""
Test configuration and fixtures
Supports dynamic API URLs via environment variables
"""

import os
from collections.abc import Generator

import pytest

# Set default API URL for testing
DEFAULT_API_URL = "http://localhost:3000"
DEFAULT_API_KEY = "test_api_key"


def pytest_configure(config: pytest.Config) -> None:
    """Configure pytest with custom settings."""
    # Set default environment variables if not set
    os.environ.setdefault("DISPERSL_API_URL", DEFAULT_API_URL)
    os.environ.setdefault("DISPERSL_API_KEY", DEFAULT_API_KEY)

    # Log the API URL being used
    print(f"\nRunning tests against: {os.environ['DISPERSL_API_URL']}")


@pytest.fixture
def api_url() -> str:
    """Get the API URL for testing."""
    return os.environ.get("DISPERSL_API_URL", DEFAULT_API_URL)


@pytest.fixture
def api_key() -> str:
    """Get the API key for testing."""
    return os.environ.get("DISPERSL_API_KEY", DEFAULT_API_KEY)


@pytest.fixture
def is_integration_test() -> bool:
    """Check if integration tests should run."""
    return os.environ.get("RUN_INTEGRATION_TESTS", "false").lower() == "true"


@pytest.fixture(autouse=True)
def setup_test_env() -> Generator[None, None, None]:
    """Setup and teardown for each test."""
    # Setup: Set environment variables
    original_env = {
        "DISPERSL_API_URL": os.environ.get("DISPERSL_API_URL"),
        "DISPERSL_API_KEY": os.environ.get("DISPERSL_API_KEY"),
    }

    # Ensure defaults are set
    os.environ.setdefault("DISPERSL_API_URL", DEFAULT_API_URL)
    os.environ.setdefault("DISPERSL_API_KEY", DEFAULT_API_KEY)

    yield

    # Teardown: Restore original environment
    for key, value in original_env.items():
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value


# Pytest markers
def pytest_collection_modifyitems(config: pytest.Config, items: list) -> None:
    """Modify test collection to add markers."""
    for item in items:
        # Add marker based on test path
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
            # Skip integration tests unless explicitly enabled
            if not os.environ.get("RUN_INTEGRATION_TESTS", "false").lower() == "true":
                item.add_marker(pytest.mark.skip(reason="Integration tests disabled"))
        elif "e2e" in str(item.fspath):
            item.add_marker(pytest.mark.e2e)
            # Skip e2e tests unless explicitly enabled
            if not os.environ.get("RUN_E2E_TESTS", "false").lower() == "true":
                item.add_marker(pytest.mark.skip(reason="E2E tests disabled"))

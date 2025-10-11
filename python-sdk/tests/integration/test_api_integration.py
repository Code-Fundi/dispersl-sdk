"""
Integration tests for Dispersl SDK.

These tests require a running API server.
"""

import pytest

from dispersl import Client


@pytest.mark.integration
def test_client_initialization():
    """Test that client can be initialized."""
    client = Client(api_key="test_key")
    assert client is not None
    assert client.http is not None


@pytest.mark.integration
@pytest.mark.skip(reason="Requires live API server")
def test_models_list():
    """Test listing available models."""
    pass

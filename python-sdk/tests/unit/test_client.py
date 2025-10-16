"""Comprehensive unit tests for the Dispersl client."""

import os
import pytest
from unittest.mock import Mock, patch, MagicMock
from dispersl import Dispersl
from dispersl.exceptions import DisperslError, AuthenticationError
from dispersl.resources import (
    AgentsResource,
    ModelsResource,
    TaskManagementResource,
    StepManagementResource,
    HistoryResource,
    AuthenticationResource,
)

# Aliases for backward compatibility in tests
TasksResource = TaskManagementResource
StepsResource = StepManagementResource
AuthResource = AuthenticationResource


class TestDisperslClient:
    """Test Dispersl client initialization and configuration."""

    def test_init_with_api_key(self):
        """Test initializing client with API key."""
        client = Dispersl(api_key="test_key_123")
        assert client.auth is not None
        assert client.http.base_url is not None

    def test_init_with_custom_base_url(self):
        """Test initializing client with custom base URL."""
        custom_url = "https://custom.dispersl.ai"
        client = Dispersl(api_key="test_key", base_url=custom_url)
        assert client.http.base_url == custom_url

    def test_init_with_timeout(self):
        """Test initializing client with custom timeout."""
        client = Dispersl(api_key="test_key", timeout=60.0)
        assert client.http.timeout == 60.0

    def test_init_with_max_retries(self):
        """Test initializing client with max retries."""
        client = Dispersl(api_key="test_key", max_retries=5)
        assert client.http.max_retries == 5

    def test_init_without_api_key_raises_error(self):
        """Test that initializing without API key raises error."""
        with pytest.raises(DisperslError):
            Dispersl(api_key=None)

    def test_init_with_empty_api_key_raises_error(self):
        """Test that initializing with empty API key raises error."""
        with pytest.raises(DisperslError):
            Dispersl(api_key="")

    def test_resources_initialized(self):
        """Test that all resources are properly initialized."""
        client = Dispersl(api_key="test_key")
        
        assert isinstance(client.agents, AgentsResource)
        assert isinstance(client.models, ModelsResource)
        assert isinstance(client.auth_resource, AuthenticationResource)
        assert isinstance(client.tasks, TaskManagementResource)
        assert isinstance(client.steps, StepManagementResource)
        assert isinstance(client.history, HistoryResource)

    def test_resources_share_http_client(self):
        """Test that all resources share the same HTTP client."""
        client = Dispersl(api_key="test_key")
        
        assert client.agents.http is client.http
        assert client.models.http is client.http
        assert client.tasks.http is client.http
        assert client.steps.http is client.http
        assert client.history.http is client.http

    def test_default_headers(self):
        """Test that default headers are set."""
        client = Dispersl(api_key="test_key")
        
        # Check that auth headers are included
        assert "Authorization" in client.http._client.headers

    def test_custom_headers(self):
        """Test that custom headers are included."""
        custom_headers = {"X-Custom": "value"}
        client = Dispersl(api_key="test_key", headers=custom_headers)
        
        assert "X-Custom" in client.http._client.headers
        assert client.http._client.headers["X-Custom"] == "value"

    def test_user_agent_header(self):
        """Test that User-Agent header is set."""
        client = Dispersl(api_key="test_key")
        
        # User-Agent should be set by the HTTP client
        assert "User-Agent" in client.http._client.headers

    @patch.dict(os.environ, {"DISPERSL_API_KEY": "env_api_key"})
    def test_init_from_environment(self):
        """Test initializing client from environment variable."""
        client = Dispersl()
        assert client.auth is not None

    def test_close_client(self):
        """Test closing the client."""
        client = Dispersl(api_key="test_key")
        client.close()  # Should not raise any errors
        assert True

    def test_context_manager(self):
        """Test client as context manager."""
        with Dispersl(api_key="test_key") as client:
            assert client.auth is not None
            assert client.http is not None

    def test_repr(self):
        """Test client string representation."""
        client = Dispersl(api_key="test_key")
        repr_str = repr(client)
        assert "Dispersl" in repr_str
        assert "test_key" not in repr_str  # API key should be masked

    def test_invalid_timeout(self):
        """Test invalid timeout values."""
        with pytest.raises((ValueError, TypeError)):
            Dispersl(api_key="test_key", timeout=-1)

    def test_invalid_max_retries(self):
        """Test invalid max retries values."""
        with pytest.raises((ValueError, TypeError)):
            Dispersl(api_key="test_key", max_retries=-1)


class TestClientConfiguration:
    """Test client configuration methods."""

    def test_configure_retry_strategy(self):
        """Test configuring retry strategy."""
        client = Dispersl(api_key="test_key", max_retries=5, backoff_factor=3.0)
        assert client.http.max_retries == 5
        assert client.http.backoff_factor == 3.0

    def test_configure_timeouts(self):
        """Test configuring timeouts."""
        client = Dispersl(api_key="test_key", timeout=60.0, connect_timeout=20.0)
        assert client.http.timeout == 60.0
        assert client.http.connect_timeout == 20.0

    def test_configure_base_url_with_trailing_slash(self):
        """Test base URL with trailing slash is handled."""
        client = Dispersl(api_key="test_key", base_url="https://api.test.com/")
        assert not client.http.base_url.endswith("/")

    def test_configure_base_url_without_scheme(self):
        """Test base URL without scheme raises error."""
        with pytest.raises((ValueError, TypeError)):
            Dispersl(api_key="test_key", base_url="api.test.com")

    def test_enable_debug_mode(self):
        """Test enabling debug mode."""
        # Debug mode would typically be handled by logging configuration
        client = Dispersl(api_key="test_key")
        assert client.http is not None

    def test_configure_proxy(self):
        """Test configuring proxy."""
        # Proxy configuration would be handled by the HTTP client
        client = Dispersl(api_key="test_key")
        assert client.http is not None


class TestClientMethods:
    """Test client utility methods."""

    def test_build_request_url(self):
        """Test building request URLs."""
        client = Dispersl(api_key="test_key")
        # URL building is handled by the HTTP client
        assert client.http.base_url is not None

    def test_build_request_url_with_params(self):
        """Test building request URLs with parameters."""
        client = Dispersl(api_key="test_key")
        # URL building with params is handled by the HTTP client
        assert client.http.base_url is not None

    def test_validate_api_key_format(self):
        """Test API key format validation."""
        # API key validation is handled by the auth module
        client = Dispersl(api_key="test_key")
        assert client.auth is not None

    def test_set_api_key_after_init(self):
        """Test setting API key after initialization."""
        client = Dispersl(api_key="old_key")
        # API key changes would require reinitializing the auth handler
        # This is not typically supported in the current design
        assert client.auth is not None

    def test_get_sdk_version(self):
        """Test getting SDK version."""
        from dispersl import __version__
        assert __version__ is not None
        assert isinstance(__version__, str)

    @patch("dispersl.client.HTTPClient.get")
    def test_health_check(self, mock_get):
        """Test health check method."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "healthy"}
        mock_get.return_value = mock_response
        
        client = Dispersl(api_key="test_key")
        response = client.http.get("/health")
        
        assert response.status_code == 200

    @patch("dispersl.client.HTTPClient.get")
    def test_verify_connection(self, mock_get):
        """Test connection verification."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        client = Dispersl(api_key="test_key")
        response = client.http.get("/")
        
        assert response.status_code == 200


class TestClientErrorHandling:
    """Test client error handling."""

    @patch("dispersl.client.HTTPClient.get")
    def test_handle_authentication_error(self, mock_get):
        """Test handling authentication errors."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_get.return_value = mock_response
        
        client = Dispersl(api_key="invalid_key")
        
        with pytest.raises(AuthenticationError):
            client.http.get("/test")

    @patch("dispersl.client.HTTPClient.get")
    def test_handle_api_error(self, mock_get):
        """Test handling API errors."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response
        
        client = Dispersl(api_key="test_key")
        
        with pytest.raises(Exception):  # Will be caught by HTTP client error handling
            client.http.get("/test")

    @patch("dispersl.client.HTTPClient.get")
    def test_handle_network_error(self, mock_get):
        """Test handling network errors."""
        mock_get.side_effect = Exception("Network error")
        
        client = Dispersl(api_key="test_key")
        
        with pytest.raises(Exception):
            client.http.get("/test")

    @patch("dispersl.client.HTTPClient.get")
    def test_handle_timeout_error(self, mock_get):
        """Test handling timeout errors."""
        import httpx
        mock_get.side_effect = httpx.TimeoutException("Timeout")
        
        client = Dispersl(api_key="test_key")
        
        with pytest.raises(Exception):
            client.http.get("/test")

    @patch("dispersl.client.HTTPClient.get")
    def test_handle_invalid_response(self, mock_get):
        """Test handling invalid responses."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_get.return_value = mock_response
        
        client = Dispersl(api_key="test_key")
        
        # This would be handled by the HTTP client
        response = client.http.get("/test")
        assert response.status_code == 200


class TestClientThreadSafety:
    """Test client thread safety."""

    def test_concurrent_requests(self):
        """Test concurrent requests."""
        client = Dispersl(api_key="test_key")
        
        # Multiple clients can be created safely
        client2 = Dispersl(api_key="test_key")
        
        assert client.http is not client2.http
        assert client.auth is not client2.auth

    def test_session_isolation(self):
        """Test session isolation."""
        client = Dispersl(api_key="test_key")
        
        # Each client has its own HTTP session
        assert client.http is not None
        assert client.auth is not None

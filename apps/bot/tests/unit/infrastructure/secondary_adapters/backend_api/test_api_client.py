"""Tests for API Client."""

from src.infrastructure.api_client import APIClient


class TestAPIClient:
    """Test APIClient class."""

    def test_initialization_default(self):
        """Test APIClient initializes with default URL."""
        client = APIClient()
        assert client.base_url == "https://usipipo.duckdns.org"
        assert client.api_prefix == "/api/v1"

    def test_initialization_custom_url(self):
        """Test APIClient initializes with custom URL."""
        client = APIClient(base_url="http://localhost:8001")
        assert client.base_url == "http://localhost:8001"

    def test_initialization_custom_prefix(self):
        """Test APIClient initializes with custom prefix."""
        client = APIClient(api_prefix="/api/v2")
        assert client.api_prefix == "/api/v2"

    def test_url_trailing_slash_removed(self):
        """Test trailing slash is removed from base URL."""
        client = APIClient(base_url="http://localhost:8001/")
        assert client.base_url == "http://localhost:8001"

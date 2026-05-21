"""Tests for BackendHttpClient."""

import pytest
import httpx

from src.infrastructure.secondary_adapters.backend_api.http_client import (
    BackendHttpClient,
)


@pytest.mark.asyncio
async def test_http_client_creation():
    """Test de creación de cliente HTTP."""
    client = BackendHttpClient("http://localhost:8001")
    assert client.base_url == "http://localhost:8001"
    assert client.timeout == 30.0


@pytest.mark.asyncio
async def test_http_client_get_client():
    """Test de obtención de cliente."""
    client = BackendHttpClient("http://localhost:8001")
    httpx_client = await client.get_client()
    assert isinstance(httpx_client, httpx.AsyncClient)
    assert not httpx_client.is_closed


@pytest.mark.asyncio
async def test_http_client_close():
    """Test de cierre de cliente."""
    client = BackendHttpClient("http://localhost:8001")
    await client.get_client()
    await client.close()
    assert client._client is None or client._client.is_closed


@pytest.mark.asyncio
async def test_http_client_context_manager():
    """Test de context manager."""
    async with BackendHttpClient("http://localhost:8001") as client:
        httpx_client = await client.get_client()
        assert isinstance(httpx_client, httpx.AsyncClient)

    # After context, client should be closed
    assert client._client is None or client._client.is_closed

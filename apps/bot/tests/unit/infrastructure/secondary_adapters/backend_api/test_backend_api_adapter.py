"""Tests for BackendApiAdapter."""

import pytest
from unittest.mock import AsyncMock, patch
from uuid import uuid4

from src.infrastructure.secondary_adapters.backend_api.backend_api_adapter import (
    BackendApiAdapter,
)
from src.infrastructure.error_handling.exceptions import (
    BackendConnectionError,
)


@pytest.fixture
def backend_url() -> str:
    """URL base del backend para tests."""
    return "http://localhost:8001"


@pytest.fixture
def adapter(backend_url: str) -> BackendApiAdapter:
    """Crea un BackendApiAdapter para tests."""
    return BackendApiAdapter(backend_url)


class MockResponse:
    """Mock de respuesta HTTP (síncrono, como httpx.Response)."""

    def __init__(self, json_data: dict | list, status_code: int = 200):
        self._json_data = json_data
        self.status_code = status_code
        self.text = str(json_data)

    def json(self):
        """httpx.Response.json() es síncrono."""
        return self._json_data

    def raise_for_status(self):
        """httpx.Response.raise_for_status() es síncrono."""
        if self.status_code >= 400:
            import httpx

            raise httpx.HTTPStatusError(
                f"HTTP {self.status_code}",
                request=AsyncMock(),
                response=self,
            )


@pytest.mark.asyncio
async def test_auto_register_success(adapter: BackendApiAdapter):
    """Test de auto-registro exitoso."""
    user_id = str(uuid4())
    mock_response = MockResponse(
        {
            "access_token": "test_access",
            "refresh_token": "test_refresh",
            "expires_in": 1800,
            "user_id": user_id,
        }
    )

    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=mock_response)

    async def mock_get_client():
        return mock_client

    with patch.object(adapter.http_client, "get_client", mock_get_client):
        result = await adapter.auto_register(1058749165)

        assert result["access_token"] == "test_access"
        assert result["refresh_token"] == "test_refresh"
        assert result["expires_in"] == 1800
        assert result["user_id"] == user_id


@pytest.mark.asyncio
async def test_auto_register_backend_error(adapter: BackendApiAdapter):
    """Test de error del backend en auto-registro."""
    mock_response = MockResponse({"detail": "Internal server error"}, status_code=500)

    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=mock_response)

    async def mock_get_client():
        return mock_client

    with patch.object(adapter.http_client, "get_client", mock_get_client):
        with pytest.raises(BackendConnectionError):
            await adapter.auto_register(1058749165)


@pytest.mark.asyncio
async def test_refresh_tokens_success(adapter: BackendApiAdapter):
    """Test de refresh de tokens exitoso."""
    mock_response = MockResponse(
        {
            "access_token": "new_access",
            "refresh_token": "new_refresh",
            "expires_in": 1800,
        }
    )

    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=mock_response)

    async def mock_get_client():
        return mock_client

    with patch.object(adapter.http_client, "get_client", mock_get_client):
        result = await adapter.refresh_tokens("old_refresh")

        assert result["access_token"] == "new_access"
        assert result["refresh_token"] == "new_refresh"
        assert result["expires_in"] == 1800


@pytest.mark.asyncio
async def test_list_vpn_keys_success(adapter: BackendApiAdapter):
    """Test de listado de VPN keys exitoso."""
    mock_response = MockResponse(
        [
            {
                "id": str(uuid4()),
                "user_id": str(uuid4()),
                "name": "Test Key",
                "key_type": "wireguard",
                "status": "active",
                "key_data": "wg://...",
                "external_id": "ext_123",
                "created_at": "2026-03-24T00:00:00Z",
                "used_bytes": 0,
                "data_limit_bytes": 5368709120,
                "billing_reset_at": "2026-03-24T00:00:00Z",
            }
        ]
    )

    mock_client = AsyncMock()
    mock_client.get = AsyncMock(return_value=mock_response)

    async def mock_get_client():
        return mock_client

    with patch.object(adapter.http_client, "get_client", mock_get_client):
        keys = await adapter.list_vpn_keys("test_token")

        assert len(keys) == 1
        assert keys[0].name == "Test Key"


@pytest.mark.asyncio
async def test_delete_vpn_key_success(adapter: BackendApiAdapter):
    """Test de eliminación de VPN key exitoso."""
    mock_response = MockResponse({})

    mock_client = AsyncMock()
    mock_client.delete = AsyncMock(return_value=mock_response)

    async def mock_get_client():
        return mock_client

    with patch.object(adapter.http_client, "get_client", mock_get_client):
        result = await adapter.delete_vpn_key("test_token", uuid4())

        assert result is True


@pytest.mark.asyncio
async def test_get_key_config_success(adapter: BackendApiAdapter):
    """Test de obtención de configuración de VPN key."""
    mock_response = MockResponse({"config": "wg://config..."})

    mock_client = AsyncMock()
    mock_client.get = AsyncMock(return_value=mock_response)

    async def mock_get_client():
        return mock_client

    with patch.object(adapter.http_client, "get_client", mock_get_client):
        config = await adapter.get_key_config("test_token", uuid4())

        assert config == "wg://config..."


@pytest.mark.asyncio
async def test_get_referral_code_success(adapter: BackendApiAdapter):
    """Test de obtención de código de referido."""
    # Backend returns {"referral_code": "...", "total_referrals": N, ...}
    mock_response = MockResponse({"referral_code": "REFER123", "total_referrals": 5})

    mock_client = AsyncMock()
    mock_client.get = AsyncMock(return_value=mock_response)

    async def mock_get_client():
        return mock_client

    with patch.object(adapter.http_client, "get_client", mock_get_client):
        code = await adapter.get_referral_code("test_token")

        assert code == "REFER123"


@pytest.mark.asyncio
async def test_get_referral_stats_success(adapter: BackendApiAdapter):
    """Test de obtención de estadísticas de referidos."""
    mock_response = MockResponse(
        {
            "referrals_count": 5,
            "bonus_earned_gb": 10,
        }
    )

    mock_client = AsyncMock()
    mock_client.get = AsyncMock(return_value=mock_response)

    async def mock_get_client():
        return mock_client

    with patch.object(adapter.http_client, "get_client", mock_get_client):
        stats = await adapter.get_referral_stats("test_token")

        assert stats["referrals_count"] == 5
        assert stats["bonus_earned_gb"] == 10


@pytest.mark.asyncio
async def test_close_adapter(adapter: BackendApiAdapter):
    """Test de cierre del adaptador."""
    await adapter.http_client.get_client()
    await adapter.close()

    assert adapter.http_client._client is None or adapter.http_client._client.is_closed

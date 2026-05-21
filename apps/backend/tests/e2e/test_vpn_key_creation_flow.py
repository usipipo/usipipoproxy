"""
E2E tests for VPN key creation flow.

Tests the complete flow from API call → Backend → Agent (mocked) → VPN config generation.
"""

import pytest
from httpx import AsyncClient
from sqlalchemy import select

from src.infrastructure.persistence.models.user_model import UserModel
from src.infrastructure.persistence.models.vpn_key_model import VpnKeyModel
from src.infrastructure.persistence.models.vpn_server_model import VpnServerModel
from tests.e2e.conftest import TestSessionMaker


class TestVpnKeyCreationFlow:
    """Test VPN key creation operations."""

    @pytest.mark.asyncio
    async def test_create_wireguard_key_happy_path(
        self,
        client: AsyncClient,
        test_user: UserModel,
        test_vpn_server: VpnServerModel,
        mocked_agent_api,
        auth_headers: dict,
    ):
        """Test creating a WireGuard key - happy path."""
        # Arrange
        payload = {
            "name": "My-VPN-Key",
            "key_type": "wireguard",
            "data_limit_gb": 10.0,
            "server_id": str(test_vpn_server.id),
        }

        # Act
        response = await client.post("/api/v1/vpn/keys", json=payload, headers=auth_headers)

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "My-VPN-Key"
        assert data["key_type"] == "wireguard"
        assert "id" in data
        assert "config" in data

        # Verify database
        async with TestSessionMaker() as session:
            result = await session.execute(select(VpnKeyModel).where(VpnKeyModel.id == data["id"]))
            key = result.scalar_one()
            assert key is not None
            assert key.user_id == test_user.id
            assert key.server_id == test_vpn_server.id

    @pytest.mark.asyncio
    async def test_create_key_auto_select_server(
        self,
        client: AsyncClient,
        test_user: UserModel,
        test_vpn_server: VpnServerModel,
        mocked_agent_api,
        auth_headers: dict,
    ):
        """Test creating a key with auto-selected server."""
        # Arrange - don't specify server_id, let backend auto-select
        payload = {"name": "Auto-Server-Key", "key_type": "wireguard", "data_limit_gb": 10.0}

        # Act
        response = await client.post("/api/v1/vpn/keys", json=payload, headers=auth_headers)

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["server_id"] is not None

    @pytest.mark.asyncio
    async def test_create_key_invalid_name_too_short(
        self,
        client: AsyncClient,
        test_user: UserModel,
        test_vpn_server: VpnServerModel,
        mocked_agent_api,
        auth_headers: dict,
    ):
        """Test creating a key with name too short."""
        # Arrange
        payload = {
            "name": "Ab",  # Less than 3 chars
            "key_type": "wireguard",
            "data_limit_gb": 10.0,
            "server_id": str(test_vpn_server.id),
        }

        # Act
        response = await client.post("/api/v1/vpn/keys", json=payload, headers=auth_headers)

        # Assert
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    @pytest.mark.asyncio
    async def test_create_key_invalid_name_special_chars(
        self,
        client: AsyncClient,
        test_user: UserModel,
        test_vpn_server: VpnServerModel,
        mocked_agent_api,
        auth_headers: dict,
    ):
        """Test creating a key with invalid special characters."""
        # Arrange
        payload = {
            "name": "Test;rm -rf /",  # Shell injection attempt
            "key_type": "wireguard",
            "data_limit_gb": 10.0,
            "server_id": str(test_vpn_server.id),
        }

        # Act
        response = await client.post("/api/v1/vpn/keys", json=payload, headers=auth_headers)

        # Assert
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_key_duplicate_name_case_insensitive(
        self,
        client: AsyncClient,
        test_user: UserModel,
        test_vpn_server: VpnServerModel,
        mocked_agent_api,
        auth_headers: dict,
    ):
        """Test creating a key with duplicate name (case-insensitive)."""
        # Arrange - create first key
        payload1 = {
            "name": "Home",
            "key_type": "wireguard",
            "data_limit_gb": 10.0,
            "server_id": str(test_vpn_server.id),
        }

        await client.post("/api/v1/vpn/keys", json=payload1, headers=auth_headers)

        # Act - try to create with same name, different case
        payload2 = {
            "name": "home",  # Same as "Home" case-insensitive
            "key_type": "wireguard",
            "data_limit_gb": 10.0,
            "server_id": str(test_vpn_server.id),
        }

        response = await client.post("/api/v1/vpn/keys", json=payload2, headers=auth_headers)

        # Assert
        assert response.status_code == 409
        data = response.json()
        assert "VPN_KEY_NAME_EXISTS" in str(data)

    @pytest.mark.asyncio
    async def test_create_key_agent_offline(
        self,
        client: AsyncClient,
        test_user: UserModel,
        test_vpn_server: VpnServerModel,
        auth_headers: dict,
    ):
        """Test creating a key when agent is offline."""
        # Arrange - don't mock agent, let health check fail
        payload = {
            "name": "Offline-Key",
            "key_type": "wireguard",
            "data_limit_gb": 10.0,
            "server_id": str(test_vpn_server.id),
        }

        # Act
        response = await client.post("/api/v1/vpn/keys", json=payload, headers=auth_headers)

        # Assert
        assert response.status_code == 503

    @pytest.mark.asyncio
    async def test_create_key_rate_limit(
        self,
        client: AsyncClient,
        test_user: UserModel,
        test_vpn_server: VpnServerModel,
        mocked_agent_api,
        auth_headers: dict,
    ):
        """Test rate limiting on key creation (11th request returns 429)."""
        # Note: Rate limiting is disabled in test settings
        # This test documents the expected behavior
        pytest.skip("Rate limiting disabled in test environment")

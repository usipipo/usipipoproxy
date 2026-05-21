"""
E2E tests for VPN key list operations.

Tests listing and retrieving VPN keys.
"""

import pytest
from httpx import AsyncClient

from src.infrastructure.persistence.models.user_model import UserModel
from src.infrastructure.persistence.models.vpn_server_model import VpnServerModel


class TestVpnKeyListOperations:
    """Test VPN key list and retrieval operations."""

    @pytest.mark.asyncio
    async def test_list_user_keys(
        self,
        client: AsyncClient,
        test_user: UserModel,
        test_vpn_server: VpnServerModel,
        mocked_agent_api,
        auth_headers: dict,
    ):
        """Test listing user's VPN keys."""
        # Arrange - create multiple keys
        keys_data = [
            {"name": "Key-1", "key_type": "wireguard", "data_limit_gb": 10.0},
            {"name": "Key-2", "key_type": "wireguard", "data_limit_gb": 5.0},
            {"name": "Key-3", "key_type": "wireguard", "data_limit_gb": 20.0},
        ]

        for key_data in keys_data:
            payload = {**key_data, "server_id": str(test_vpn_server.id)}
            await client.post("/api/v1/vpn/keys", json=payload, headers=auth_headers)

        # Act - list keys
        response = await client.get("/api/v1/vpn/keys", headers=auth_headers)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 3
        assert all(key["user_id"] == str(test_user.id) for key in data)

    @pytest.mark.asyncio
    async def test_list_keys_multiple_types(
        self,
        client: AsyncClient,
        test_user: UserModel,
        test_vpn_server: VpnServerModel,
        mocked_agent_api,
        auth_headers: dict,
    ):
        """Test listing keys with multiple types."""
        # Arrange - create a wireguard key
        await client.post(
            "/api/v1/vpn/keys",
            json={
                "name": "WG-Key",
                "key_type": "wireguard",
                "data_limit_gb": 10.0,
                "server_id": str(test_vpn_server.id),
            },
            headers=auth_headers,
        )

        # Act
        response = await client.get("/api/v1/vpn/keys", headers=auth_headers)

        # Assert
        assert response.status_code == 200
        data = response.json()

        types = {key["key_type"] for key in data}
        assert "wireguard" in types

    @pytest.mark.asyncio
    async def test_list_keys_empty(
        self, client: AsyncClient, test_user: UserModel, auth_headers: dict
    ):
        """Test listing keys for new user (empty list)."""
        # Act
        response = await client.get("/api/v1/vpn/keys", headers=auth_headers)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    @pytest.mark.asyncio
    async def test_get_single_key(
        self,
        client: AsyncClient,
        test_user: UserModel,
        test_vpn_server: VpnServerModel,
        mocked_agent_api,
        auth_headers: dict,
    ):
        """Test retrieving a single VPN key."""
        # Arrange - create key
        create_payload = {
            "name": "Single-Key",
            "key_type": "wireguard",
            "data_limit_gb": 10.0,
            "server_id": str(test_vpn_server.id),
        }

        create_response = await client.post(
            "/api/v1/vpn/keys", json=create_payload, headers=auth_headers
        )

        key_id = create_response.json()["id"]

        # Act - get single key
        get_response = await client.get(f"/api/v1/vpn/keys/{key_id}", headers=auth_headers)

        # Assert
        assert get_response.status_code == 200
        data = get_response.json()
        assert data["id"] == key_id
        assert data["name"] == "Single-Key"
        assert data["key_type"] == "wireguard"
        assert "server_id" in data
        assert "server_name" in data

    @pytest.mark.asyncio
    async def test_get_key_includes_server_info(
        self,
        client: AsyncClient,
        test_user: UserModel,
        test_vpn_server: VpnServerModel,
        mocked_agent_api,
        auth_headers: dict,
    ):
        """Test that key details include server information."""
        # Arrange
        create_payload = {
            "name": "Server-Info-Key",
            "key_type": "wireguard",
            "data_limit_gb": 10.0,
            "server_id": str(test_vpn_server.id),
        }

        create_response = await client.post(
            "/api/v1/vpn/keys", json=create_payload, headers=auth_headers
        )

        key_id = create_response.json()["id"]

        # Act
        get_response = await client.get(f"/api/v1/vpn/keys/{key_id}", headers=auth_headers)

        # Assert
        assert get_response.status_code == 200
        data = get_response.json()
        assert data["server_id"] == str(test_vpn_server.id)
        assert data["server_name"] == test_vpn_server.name

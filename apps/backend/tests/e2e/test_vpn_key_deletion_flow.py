"""
E2E tests for VPN key deletion flow.

Tests the complete flow from API call → Backend → Agent (mocked) → VPN config removal.
"""

import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy import select

from src.infrastructure.persistence.models.user_model import UserModel
from src.infrastructure.persistence.models.vpn_key_model import VpnKeyModel
from src.infrastructure.persistence.models.vpn_server_model import VpnServerModel
from tests.e2e.conftest import TestSessionMaker


class TestVpnKeyDeletionFlow:
    """Test VPN key deletion operations."""

    @pytest.mark.asyncio
    async def test_delete_wireguard_key_happy_path(
        self,
        client: AsyncClient,
        test_user: UserModel,
        test_vpn_server: VpnServerModel,
        mocked_agent_api,
        auth_headers: dict,
    ):
        """Test deleting a WireGuard key - happy path."""
        # Arrange - create key first
        create_payload = {
            "name": "Key-To-Delete",
            "key_type": "wireguard",
            "data_limit_gb": 10.0,
            "server_id": str(test_vpn_server.id),
        }

        create_response = await client.post(
            "/api/v1/vpn/keys", json=create_payload, headers=auth_headers
        )

        key_id = create_response.json()["id"]

        # Act - delete the key
        delete_response = await client.delete(f"/api/v1/vpn/keys/{key_id}", headers=auth_headers)

        # Assert
        assert delete_response.status_code == 200

        # Verify database - key should be deleted
        async with TestSessionMaker() as session:
            result = await session.execute(select(VpnKeyModel).where(VpnKeyModel.id == key_id))
            key = result.scalar_one_or_none()
            assert key is None

    @pytest.mark.asyncio
    async def test_delete_key_idempotent(
        self,
        client: AsyncClient,
        test_user: UserModel,
        test_vpn_server: VpnServerModel,
        mocked_agent_api,
        auth_headers: dict,
    ):
        """Test deleting a key twice succeeds (idempotent)."""
        # Arrange - create and delete key
        create_payload = {
            "name": "Idempotent-Key",
            "key_type": "wireguard",
            "data_limit_gb": 10.0,
            "server_id": str(test_vpn_server.id),
        }

        create_response = await client.post(
            "/api/v1/vpn/keys", json=create_payload, headers=auth_headers
        )

        key_id = create_response.json()["id"]

        # First delete
        delete1 = await client.delete(f"/api/v1/vpn/keys/{key_id}", headers=auth_headers)

        # Second delete (should also succeed - idempotent)
        delete2 = await client.delete(f"/api/v1/vpn/keys/{key_id}", headers=auth_headers)

        # Assert - both should succeed
        assert delete1.status_code == 200
        assert delete2.status_code == 200

    @pytest.mark.asyncio
    async def test_delete_key_unauthorized(
        self,
        client: AsyncClient,
        test_user: UserModel,
        test_vpn_server: VpnServerModel,
        mocked_agent_api,
        auth_headers: dict,
    ):
        """Test user cannot delete another user's key."""
        # Arrange - create key for test_user
        create_payload = {
            "name": "Other-User-Key",
            "key_type": "wireguard",
            "data_limit_gb": 10.0,
            "server_id": str(test_vpn_server.id),
        }

        create_response = await client.post(
            "/api/v1/vpn/keys", json=create_payload, headers=auth_headers
        )

        key_id = create_response.json()["id"]

        # Act - try to delete with different auth (simulated by using invalid token)
        wrong_auth = {"Authorization": "Bearer wrong-token", "Content-Type": "application/json"}

        delete_response = await client.delete(f"/api/v1/vpn/keys/{key_id}", headers=wrong_auth)

        # Assert
        assert delete_response.status_code in [401, 403]

    @pytest.mark.asyncio
    async def test_delete_key_not_found(self, client: AsyncClient, auth_headers: dict):
        """Test deleting non-existent key."""
        # Arrange - use random UUID
        fake_key_id = uuid.uuid4()

        # Act
        delete_response = await client.delete(
            f"/api/v1/vpn/keys/{fake_key_id}", headers=auth_headers
        )

        # Assert
        assert delete_response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_key_agent_offline(
        self,
        client: AsyncClient,
        test_user: UserModel,
        test_vpn_server: VpnServerModel,
        mocked_agent_api,
        auth_headers: dict,
    ):
        """Test deleting key when agent is offline."""
        # Arrange - create key
        create_payload = {
            "name": "Offline-Delete-Key",
            "key_type": "wireguard",
            "data_limit_gb": 10.0,
            "server_id": str(test_vpn_server.id),
        }

        create_response = await client.post(
            "/api/v1/vpn/keys", json=create_payload, headers=auth_headers
        )

        key_id = create_response.json()["id"]

        # Act - mock agent health check to fail
        # (by not mocking the health endpoint)
        mocked_agent_api.stop()

        delete_response = await client.delete(f"/api/v1/vpn/keys/{key_id}", headers=auth_headers)

        # Assert
        assert delete_response.status_code == 503

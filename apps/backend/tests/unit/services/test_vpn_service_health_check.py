"""Unit tests for VpnService health check functionality."""

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from usipipo_commons.domain.entities.server import Server
from usipipo_commons.domain.enums.key_type import KeyType

from src.core.application.exceptions import AgentOfflineError
from src.core.application.services.vpn_service import VpnService


@pytest.fixture
def mock_repos():
    """Create mock repositories."""
    user_repo = AsyncMock()
    vpn_repo = AsyncMock()
    return {
        "user_repo": user_repo,
        "vpn_repo": vpn_repo,
    }


@pytest.fixture
def mock_server_registry():
    """Create mock server registry service."""
    registry = AsyncMock()
    registry.get_server = AsyncMock()
    registry.select_best_server = AsyncMock()
    return registry


@pytest.fixture
def mock_agent_client():
    """Create mock VPN agent client."""
    client = AsyncMock()
    client.create_wireguard_peer = AsyncMock(
        return_value={
            "public_key": "wg-pub-key-123",
            "config": "[Interface]\nPrivateKey = test\n[Peer]\nPublicKey = test",
        }
    )
    client.delete_wireguard_peer = AsyncMock(return_value=True)
    client.health_check = AsyncMock(return_value=True)
    return client


@pytest.fixture
def service(mock_repos, mock_server_registry, mock_agent_client):
    """Create VpnService instance with mocks."""
    vpn_service = VpnService(
        user_repo=mock_repos["user_repo"],
        vpn_repo=mock_repos["vpn_repo"],
        server_registry_service=mock_server_registry,
    )
    # Inject mock agent client
    vpn_service._agent_clients = {}
    vpn_service._get_agent_client = MagicMock(return_value=mock_agent_client)
    return vpn_service


@pytest.fixture
def sample_user():
    """Create sample user entity."""
    user = MagicMock()
    user.id = uuid.uuid4()
    user.telegram_id = 123456
    user.first_name = "Test"
    user.username = "testuser"
    return user


@pytest.fixture
def sample_server():
    """Create sample online server."""
    return Server(
        id=uuid.uuid4(),
        name="Test Server US",
        country_code="US",
        country_name="United States",
        city="New York",
        agent_url="https://test-server.example.com",
        agent_api_key="test-api-key",
        supports_wireguard=True,
        status="online",
        max_connections=1000,
        current_connections=100,
    )


class TestVpnServiceHealthCheckCreateKey:
    """Tests for health check in create_key operation."""

    @pytest.mark.asyncio
    async def test_create_key_health_check_passes(
        self, service, sample_user, sample_server, mock_agent_client
    ):
        """Test key creation when health check passes."""
        # Setup
        service.user_repo.get_by_id = AsyncMock(return_value=sample_user)
        service.vpn_repo.get_by_user_id = AsyncMock(return_value=[])
        service.server_registry.get_server = AsyncMock(return_value=sample_server)
        mock_agent_client.health_check = AsyncMock(return_value=True)

        # Execute
        result = await service.create_key(
            user_id=sample_user.id,
            name="test-key",
            vpn_type="wireguard",
            server_id=sample_server.id,
        )

        # Verify
        mock_agent_client.health_check.assert_called_once()
        mock_agent_client.create_wireguard_peer.assert_called_once()
        assert result is not None

    @pytest.mark.asyncio
    async def test_create_key_health_check_fails(
        self, service, sample_user, sample_server, mock_agent_client
    ):
        """Test key creation when health check fails."""
        # Setup
        service.user_repo.get_by_id = AsyncMock(return_value=sample_user)
        service.vpn_repo.get_by_user_id = AsyncMock(return_value=[])
        service.server_registry.get_server = AsyncMock(return_value=sample_server)
        mock_agent_client.health_check = AsyncMock(return_value=False)

        # Execute & Verify
        with pytest.raises(AgentOfflineError) as exc_info:
            await service.create_key(
                user_id=sample_user.id,
                name="test-key",
                vpn_type="wireguard",
                server_id=sample_server.id,
            )

        assert "offline" in str(exc_info.value.message).lower()
        assert sample_server.name in exc_info.value.message
        mock_agent_client.health_check.assert_called_once()
        mock_agent_client.create_wireguard_peer.assert_not_called()

    @pytest.mark.asyncio
    async def test_create_key_wireguard_health_check_passes(
        self, service, sample_user, sample_server, mock_agent_client
    ):
        """Test WireGuard key creation when health check passes."""
        # Setup
        service.user_repo.get_by_id = AsyncMock(return_value=sample_user)
        service.vpn_repo.get_by_user_id = AsyncMock(return_value=[])
        service.server_registry.get_server = AsyncMock(return_value=sample_server)
        mock_agent_client.health_check = AsyncMock(return_value=True)

        # Execute
        result = await service.create_key(
            user_id=sample_user.id,
            name="test-wg-key",
            vpn_type="wireguard",
            server_id=sample_server.id,
        )

        # Verify
        mock_agent_client.health_check.assert_called_once()
        mock_agent_client.create_wireguard_peer.assert_called_once()
        assert result is not None


class TestVpnServiceHealthCheckDeleteKey:
    """Tests for health check in delete_key operation."""

    @pytest.mark.asyncio
    async def test_delete_key_health_check_passes(
        self, service, sample_user, sample_server, mock_agent_client
    ):
        """Test key deletion when health check passes."""
        # Setup
        key_id = uuid.uuid4()
        mock_key = MagicMock()
        mock_key.id = str(key_id)
        mock_key.user_id = sample_user.id
        mock_key.server_id = sample_server.id
        mock_key.key_type = KeyType.WIREGUARD
        mock_key.external_id = "wg-pub-key-123"

        service.vpn_repo.get_by_id = AsyncMock(return_value=mock_key)
        service.server_registry.get_server = AsyncMock(return_value=sample_server)
        service.vpn_repo.delete = AsyncMock(return_value=True)
        mock_agent_client.health_check = AsyncMock(return_value=True)

        # Execute
        result = await service.delete_key(user_id=sample_user.id, key_id=key_id)

        # Verify
        mock_agent_client.health_check.assert_called_once()
        mock_agent_client.delete_wireguard_peer.assert_called_once_with("wg-pub-key-123")
        assert result is True

    @pytest.mark.asyncio
    async def test_delete_key_health_check_fails(
        self, service, sample_user, sample_server, mock_agent_client
    ):
        """Test key deletion when health check fails."""
        # Setup
        key_id = uuid.uuid4()
        mock_key = MagicMock()
        mock_key.id = str(key_id)
        mock_key.user_id = sample_user.id
        mock_key.server_id = sample_server.id
        mock_key.key_type = KeyType.WIREGUARD
        mock_key.external_id = "wg-pub-key-123"

        service.vpn_repo.get_by_id = AsyncMock(return_value=mock_key)
        service.server_registry.get_server = AsyncMock(return_value=sample_server)
        mock_agent_client.health_check = AsyncMock(return_value=False)

        # Execute & Verify
        with pytest.raises(AgentOfflineError) as exc_info:
            await service.delete_key(user_id=sample_user.id, key_id=key_id)

        assert "offline" in str(exc_info.value.message).lower()
        assert sample_server.name in exc_info.value.message
        mock_agent_client.health_check.assert_called_once()
        mock_agent_client.delete_wireguard_peer.assert_not_called()
        service.vpn_repo.delete.assert_not_called()

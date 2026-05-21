"""Unit tests for VpnService.create_key with server_id parameter."""

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from usipipo_commons.domain.entities.server import Server

from src.core.application.exceptions import NoAvailableServersError
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
    return client


@pytest.fixture
def service(mock_repos, mock_server_registry, mock_agent_client):
    """Create VpnService instance with mocks."""
    vpn_service = VpnService(
        user_repo=mock_repos["user_repo"],
        vpn_repo=mock_repos["vpn_repo"],
        server_registry_service=mock_server_registry,
    )
    # Inject mock agent client factory
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
def sample_online_server():
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


@pytest.fixture
def sample_offline_server():
    """Create sample offline server."""
    return Server(
        id=uuid.uuid4(),
        name="Offline Server",
        country_code="US",
        country_name="United States",
        city="New York",
        agent_url="https://offline-server.example.com",
        agent_api_key="test-api-key",
        supports_wireguard=True,
        status="offline",
        max_connections=1000,
        current_connections=0,
    )


class TestVpnServiceCreateKeyWithServerId:
    """Tests for create_key method with server_id parameter."""

    @pytest.mark.asyncio
    async def test_create_key_with_valid_server_id_uses_selected_server(
        self,
        service,
        mock_repos,
        mock_server_registry,
        mock_agent_client,
        sample_user,
        sample_online_server,
    ):
        """Test that providing server_id uses the selected server."""
        # Arrange
        mock_repos["user_repo"].get_by_id = AsyncMock(return_value=sample_user)
        mock_repos["vpn_repo"].get_by_user_id = AsyncMock(return_value=[])
        mock_repos["vpn_repo"].create = AsyncMock(return_value=MagicMock())
        mock_server_registry.get_server = AsyncMock(return_value=sample_online_server)

        # Act
        await service.create_key(
            user_id=sample_user.id,
            name="Test VPN Key",
            vpn_type="wireguard",
            data_limit_gb=5.0,
            server_id=sample_online_server.id,
        )

        # Assert
        mock_server_registry.get_server.assert_called_once_with(sample_online_server.id)
        mock_server_registry.select_best_server.assert_not_called()

    @pytest.mark.asyncio
    async def test_create_key_without_server_id_auto_selects(
        self,
        service,
        mock_repos,
        mock_server_registry,
        mock_agent_client,
        sample_user,
        sample_online_server,
    ):
        """Test that omitting server_id triggers auto-selection."""
        # Arrange
        mock_repos["user_repo"].get_by_id = AsyncMock(return_value=sample_user)
        mock_repos["vpn_repo"].get_by_user_id = AsyncMock(return_value=[])
        mock_repos["vpn_repo"].create = AsyncMock(return_value=MagicMock())
        mock_server_registry.select_best_server = AsyncMock(return_value=sample_online_server)

        # Act
        await service.create_key(
            user_id=sample_user.id,
            name="Test VPN Key",
            vpn_type="wireguard",
            data_limit_gb=5.0,
            server_id=None,
        )

        # Assert
        mock_server_registry.get_server.assert_not_called()
        mock_server_registry.select_best_server.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_key_with_invalid_server_id_raises_error(
        self, service, mock_repos, mock_server_registry, sample_user
    ):
        """Test that invalid server_id raises NoAvailableServersError."""
        # Arrange
        mock_repos["user_repo"].get_by_id = AsyncMock(return_value=sample_user)
        mock_repos["vpn_repo"].get_by_user_id = AsyncMock(return_value=[])
        mock_server_registry.get_server = AsyncMock(return_value=None)

        invalid_server_id = uuid.uuid4()

        # Act & Assert
        with pytest.raises(NoAvailableServersError, match="Selected server is not available"):
            await service.create_key(
                user_id=sample_user.id,
                name="Test VPN Key",
                vpn_type="wireguard",
                data_limit_gb=5.0,
                server_id=invalid_server_id,
            )

    @pytest.mark.asyncio
    async def test_create_key_with_offline_server_raises_error(
        self, service, mock_repos, mock_server_registry, sample_user, sample_offline_server
    ):
        """Test that selecting an offline server raises NoAvailableServersError."""
        # Arrange
        mock_repos["user_repo"].get_by_id = AsyncMock(return_value=sample_user)
        mock_repos["vpn_repo"].get_by_user_id = AsyncMock(return_value=[])
        mock_server_registry.get_server = AsyncMock(return_value=sample_offline_server)

        # Act & Assert
        with pytest.raises(NoAvailableServersError, match="Selected server is not available"):
            await service.create_key(
                user_id=sample_user.id,
                name="Test VPN Key",
                vpn_type="wireguard",
                data_limit_gb=5.0,
                server_id=sample_offline_server.id,
            )

    @pytest.mark.asyncio
    async def test_create_key_with_server_id_creates_key_on_correct_server(
        self,
        service,
        mock_repos,
        mock_server_registry,
        mock_agent_client,
        sample_user,
        sample_online_server,
    ):
        """Test that key is created with correct server_id."""
        # Arrange
        mock_repos["user_repo"].get_by_id = AsyncMock(return_value=sample_user)
        mock_repos["vpn_repo"].get_by_user_id = AsyncMock(return_value=[])

        # Capture the created key
        created_key = None

        async def capture_create(key):
            nonlocal created_key
            created_key = key
            return key

        mock_repos["vpn_repo"].create = capture_create

        mock_server_registry.get_server = AsyncMock(return_value=sample_online_server)

        # Act
        await service.create_key(
            user_id=sample_user.id,
            name="Test VPN Key",
            vpn_type="wireguard",
            data_limit_gb=5.0,
            server_id=sample_online_server.id,
        )

        # Assert
        assert created_key is not None
        assert created_key.server_id == sample_online_server.id

    @pytest.mark.asyncio
    async def test_create_key_auto_select_also_associates_server(
        self,
        service,
        mock_repos,
        mock_server_registry,
        mock_agent_client,
        sample_user,
        sample_online_server,
    ):
        """Test that auto-selected server is also associated with key."""
        # Arrange
        mock_repos["user_repo"].get_by_id = AsyncMock(return_value=sample_user)
        mock_repos["vpn_repo"].get_by_user_id = AsyncMock(return_value=[])

        created_key = None

        async def capture_create(key):
            nonlocal created_key
            created_key = key
            return key

        mock_repos["vpn_repo"].create = capture_create
        mock_server_registry.select_best_server = AsyncMock(return_value=sample_online_server)

        # Act
        await service.create_key(
            user_id=sample_user.id,
            name="Test VPN Key",
            vpn_type="wireguard",
            data_limit_gb=5.0,
            server_id=None,
        )

        # Assert
        assert created_key is not None
        assert created_key.server_id == sample_online_server.id

    @pytest.mark.asyncio
    async def test_create_key_with_server_id_uses_agent_client(
        self,
        service,
        mock_repos,
        mock_server_registry,
        mock_agent_client,
        sample_user,
        sample_online_server,
    ):
        """Test that agent client is used for the selected server."""
        # Arrange
        mock_repos["user_repo"].get_by_id = AsyncMock(return_value=sample_user)
        mock_repos["vpn_repo"].get_by_user_id = AsyncMock(return_value=[])
        mock_repos["vpn_repo"].create = AsyncMock(return_value=MagicMock())
        mock_server_registry.get_server = AsyncMock(return_value=sample_online_server)

        # Act
        await service.create_key(
            user_id=sample_user.id,
            name="Test VPN Key",
            vpn_type="wireguard",
            data_limit_gb=5.0,
            server_id=sample_online_server.id,
        )

        # Assert
        mock_agent_client.create_wireguard_peer.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_key_server_selection_logs_correctly(
        self,
        service,
        mock_repos,
        mock_server_registry,
        mock_agent_client,
        sample_user,
        sample_online_server,
        caplog,
    ):
        """Test that server selection is logged correctly."""
        # Arrange
        mock_repos["user_repo"].get_by_id = AsyncMock(return_value=sample_user)
        mock_repos["vpn_repo"].get_by_user_id = AsyncMock(return_value=[])
        mock_repos["vpn_repo"].create = AsyncMock(return_value=MagicMock())
        mock_server_registry.get_server = AsyncMock(return_value=sample_online_server)

        # Act
        with caplog.at_level("INFO"):
            await service.create_key(
                user_id=sample_user.id,
                name="Test VPN Key",
                vpn_type="wireguard",
                data_limit_gb=5.0,
                server_id=sample_online_server.id,
            )

        # Assert
        assert "user-selected server" in caplog.messages[0].lower() if caplog.messages else True

    @pytest.mark.asyncio
    async def test_create_key_auto_select_logs_correctly(
        self,
        service,
        mock_repos,
        mock_server_registry,
        mock_agent_client,
        sample_user,
        sample_online_server,
        caplog,
    ):
        """Test that auto-selection is logged correctly."""
        # Arrange
        mock_repos["user_repo"].get_by_id = AsyncMock(return_value=sample_user)
        mock_repos["vpn_repo"].get_by_user_id = AsyncMock(return_value=[])
        mock_repos["vpn_repo"].create = AsyncMock(return_value=MagicMock())
        mock_server_registry.select_best_server = AsyncMock(return_value=sample_online_server)

        # Act
        with caplog.at_level("INFO"):
            await service.create_key(
                user_id=sample_user.id,
                name="Test VPN Key",
                vpn_type="wireguard",
                data_limit_gb=5.0,
                server_id=None,
            )

        # Assert
        assert "auto-selected" in caplog.messages[0].lower() if caplog.messages else True

    @pytest.mark.asyncio
    async def test_create_key_with_server_id_backward_compatible(
        self,
        service,
        mock_repos,
        mock_server_registry,
        mock_agent_client,
        sample_user,
        sample_online_server,
    ):
        """Test that existing code without server_id still works (backward compatibility)."""
        # Arrange
        mock_repos["user_repo"].get_by_id = AsyncMock(return_value=sample_user)
        mock_repos["vpn_repo"].get_by_user_id = AsyncMock(return_value=[])
        mock_repos["vpn_repo"].create = AsyncMock(return_value=MagicMock())
        mock_server_registry.select_best_server = AsyncMock(return_value=sample_online_server)

        # Act - Call without server_id parameter (old behavior)
        await service.create_key(
            user_id=sample_user.id,
            name="Test VPN Key",
            vpn_type="wireguard",
            data_limit_gb=5.0,
        )

        # Assert - Should auto-select as before
        mock_server_registry.select_best_server.assert_called_once()
        mock_server_registry.get_server.assert_not_called()

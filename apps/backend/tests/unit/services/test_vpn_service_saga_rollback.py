"""Unit tests for VPN key saga pattern rollback mechanism.

Tests cover compensating transactions for partial failures in VPN key operations:
- Create: Agent succeeds + DB fails → Rollback agent
- Delete: Agent succeeds + DB fails → Log for manual cleanup
- Rollback failures: Cleanup also fails → VpnKeyRollbackError
"""

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from usipipo_commons.domain.entities.server import Server
from usipipo_commons.domain.entities.vpn_key import VpnKey
from usipipo_commons.domain.enums.key_status import KeyStatus
from usipipo_commons.domain.enums.key_type import KeyType

from src.core.application.exceptions import (
    VpnKeyRollbackError,
)
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
        agent_url="https://agent.example.com",
        agent_api_key="test-api-key",
        status="online",
        max_connections=1000,
        current_connections=100,
        supports_wireguard=True,
    )


@pytest.fixture
def sample_vpn_key():
    """Create sample VPN key entity."""
    return VpnKey(
        id=str(uuid.uuid4()),
        user_id=uuid.uuid4(),
        name="Test Key",
        key_type=KeyType.WIREGUARD,
        status=KeyStatus.ACTIVE,
        key_data="[Interface]\nPrivateKey = test",
        external_id="wg-pub-key-123",
        server_id=uuid.uuid4(),
        created_at=None,  # Will be set by service
        expires_at=None,
        used_bytes=0,
        data_limit_bytes=5 * 1024**3,
        billing_reset_at=None,
    )


class TestVpnServiceCreateKeyRollback:
    """Test saga pattern for VPN key creation with rollback."""

    @pytest.mark.asyncio
    async def test_create_key_success_no_rollback(
        self,
        service,
        mock_repos,
        mock_server_registry,
        mock_agent_client,
        sample_user,
        sample_server,
    ):
        """Test successful key creation without rollback."""
        # Arrange
        mock_repos["user_repo"].get_by_id = AsyncMock(return_value=sample_user)
        mock_repos["vpn_repo"].get_by_user_id = AsyncMock(return_value=[])
        mock_server_registry.select_best_server = AsyncMock(return_value=sample_server)

        created_key = MagicMock()
        created_key.id = str(uuid.uuid4())
        mock_repos["vpn_repo"].create = AsyncMock(return_value=created_key)

        # Act
        result = await service.create_key(
            user_id=sample_user.id,
            name="Test Key",
            vpn_type="wireguard",
            data_limit_gb=5.0,
        )

        # Assert
        assert result == created_key
        mock_agent_client.create_wireguard_peer.assert_called_once_with(name="Test Key")
        mock_repos["vpn_repo"].create.assert_called_once()
        mock_agent_client.delete_wireguard_peer.assert_not_called()

    @pytest.mark.asyncio
    async def test_create_key_db_failure_triggers_rollback(
        self,
        service,
        mock_repos,
        mock_server_registry,
        mock_agent_client,
        sample_user,
        sample_server,
    ):
        """Test that DB failure triggers agent rollback (saga pattern)."""
        # Arrange
        mock_repos["user_repo"].get_by_id = AsyncMock(return_value=sample_user)
        mock_repos["vpn_repo"].get_by_user_id = AsyncMock(return_value=[])
        mock_server_registry.select_best_server = AsyncMock(return_value=sample_server)

        # DB create fails
        db_error = Exception("Database connection timeout")
        mock_repos["vpn_repo"].create = AsyncMock(side_effect=db_error)

        # Act & Assert - rollback succeeds, original error is re-raised
        with pytest.raises(Exception) as exc_info:
            await service.create_key(
                user_id=sample_user.id,
                name="Test Key",
                vpn_type="wireguard",
                data_limit_gb=5.0,
            )

        # Verify original error is re-raised (not wrapped)
        assert exc_info.value == db_error

        # Verify rollback was attempted
        mock_agent_client.delete_wireguard_peer.assert_called_once_with("wg-pub-key-123")

        # Verify agent create was called
        mock_agent_client.create_wireguard_peer.assert_called_once_with(name="Test Key")

    @pytest.mark.asyncio
    async def test_create_key_rollback_failure_raises_vpnkeyrollbackerror(
        self,
        service,
        mock_repos,
        mock_server_registry,
        mock_agent_client,
        sample_user,
        sample_server,
    ):
        """Test that rollback failure raises VpnKeyRollbackError."""
        # Arrange
        mock_repos["user_repo"].get_by_id = AsyncMock(return_value=sample_user)
        mock_repos["vpn_repo"].get_by_user_id = AsyncMock(return_value=[])
        mock_server_registry.select_best_server = AsyncMock(return_value=sample_server)

        # DB create fails
        db_error = Exception("Database connection timeout")
        mock_repos["vpn_repo"].create = AsyncMock(side_effect=db_error)

        # Rollback also fails
        rollback_error = Exception("Agent connection refused")
        mock_agent_client.delete_wireguard_peer = AsyncMock(side_effect=rollback_error)

        # Act & Assert
        with pytest.raises(VpnKeyRollbackError) as exc_info:
            await service.create_key(
                user_id=sample_user.id,
                name="Test Key",
                vpn_type="wireguard",
                data_limit_gb=5.0,
            )

        # Verify exception details
        rollback_exc = exc_info.value
        assert rollback_exc.operation == "create"
        assert rollback_exc.key_name == "Test Key"
        assert rollback_exc.external_id == "wg-pub-key-123"
        assert rollback_exc.server_name == "Test Server US"
        assert rollback_exc.cleanup_status == "failed"
        assert rollback_exc.original_error == db_error
        assert rollback_exc.cleanup_error == rollback_error

    @pytest.mark.asyncio
    async def test_create_key_agent_failure_no_rollback_needed(
        self,
        service,
        mock_repos,
        mock_server_registry,
        mock_agent_client,
        sample_user,
        sample_server,
    ):
        """Test that agent failure doesn't trigger rollback (nothing to clean up)."""
        # Arrange
        mock_repos["user_repo"].get_by_id = AsyncMock(return_value=sample_user)
        mock_repos["vpn_repo"].get_by_user_id = AsyncMock(return_value=[])
        mock_server_registry.select_best_server = AsyncMock(return_value=sample_server)

        # Agent create fails
        agent_error = Exception("Agent timeout")
        mock_agent_client.create_wireguard_peer = AsyncMock(side_effect=agent_error)

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await service.create_key(
                user_id=sample_user.id,
                name="Test Key",
                vpn_type="wireguard",
                data_limit_gb=5.0,
            )

        assert exc_info.value == agent_error
        # DB should not be called
        mock_repos["vpn_repo"].create.assert_not_called()
        # No rollback needed
        mock_agent_client.delete_wireguard_peer.assert_not_called()


class TestVpnServiceDeleteKeyRollback:
    """Test saga pattern for VPN key deletion with partial failure handling."""

    @pytest.mark.asyncio
    async def test_delete_key_success_no_rollback(
        self,
        service,
        mock_repos,
        mock_server_registry,
        mock_agent_client,
        sample_user,
        sample_server,
        sample_vpn_key,
    ):
        """Test successful key deletion without rollback."""
        # Arrange
        sample_vpn_key.user_id = sample_user.id
        sample_vpn_key.server_id = sample_server.id
        mock_repos["vpn_repo"].get_by_id = AsyncMock(return_value=sample_vpn_key)
        mock_server_registry.get_server = AsyncMock(return_value=sample_server)
        mock_repos["vpn_repo"].delete = AsyncMock(return_value=True)

        # Act
        result = await service.delete_key(
            user_id=sample_user.id, key_id=uuid.UUID(sample_vpn_key.id)
        )

        # Assert
        assert result is True
        mock_agent_client.delete_wireguard_peer.assert_called_once_with("wg-pub-key-123")
        mock_repos["vpn_repo"].delete.assert_called_once_with(uuid.UUID(sample_vpn_key.id))

    @pytest.mark.asyncio
    async def test_delete_key_db_failure_raises_rollback_error(
        self,
        service,
        mock_repos,
        mock_server_registry,
        mock_agent_client,
        sample_user,
        sample_server,
        sample_vpn_key,
    ):
        """Test that DB failure after agent success raises VpnKeyRollbackError."""
        # Arrange
        sample_vpn_key.user_id = sample_user.id
        sample_vpn_key.server_id = sample_server.id
        mock_repos["vpn_repo"].get_by_id = AsyncMock(return_value=sample_vpn_key)
        mock_server_registry.get_server = AsyncMock(return_value=sample_server)

        # DB delete fails
        db_error = Exception("Database deadlock")
        mock_repos["vpn_repo"].delete = AsyncMock(side_effect=db_error)

        # Act & Assert
        with pytest.raises(VpnKeyRollbackError) as exc_info:
            await service.delete_key(user_id=sample_user.id, key_id=uuid.UUID(sample_vpn_key.id))

        # Verify exception details
        rollback_exc = exc_info.value
        assert rollback_exc.operation == "delete"
        assert rollback_exc.key_id == sample_vpn_key.id
        assert rollback_exc.external_id == "wg-pub-key-123"
        assert rollback_exc.server_name == "Test Server US"
        assert rollback_exc.cleanup_status == "partial"
        assert rollback_exc.original_error == db_error

        # Verify agent delete was called (can't rollback deletion)
        mock_agent_client.delete_wireguard_peer.assert_called_once_with("wg-pub-key-123")

    @pytest.mark.asyncio
    async def test_delete_key_agent_failure_prevents_db_delete(
        self,
        service,
        mock_repos,
        mock_server_registry,
        mock_agent_client,
        sample_user,
        sample_server,
        sample_vpn_key,
    ):
        """Test that agent failure prevents database deletion (no partial state)."""
        # Arrange
        sample_vpn_key.user_id = sample_user.id
        sample_vpn_key.server_id = sample_server.id
        mock_repos["vpn_repo"].get_by_id = AsyncMock(return_value=sample_vpn_key)
        mock_server_registry.get_server = AsyncMock(return_value=sample_server)

        # Agent delete fails
        agent_error = Exception("Agent connection refused")
        mock_agent_client.delete_wireguard_peer = AsyncMock(side_effect=agent_error)

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await service.delete_key(user_id=sample_user.id, key_id=uuid.UUID(sample_vpn_key.id))

        assert exc_info.value == agent_error
        # DB should NOT be called (prevents partial state)
        mock_repos["vpn_repo"].delete.assert_not_called()


class TestVpnKeyRollbackError:
    """Test VpnKeyRollbackError exception details."""

    def test_rollback_error_create_operation_message(self):
        """Test VpnKeyRollbackError message for create operation."""
        exc = VpnKeyRollbackError(
            operation="create",
            key_name="Test Key",
            external_id="wg-key-123",
            server_name="Test Server",
            cleanup_status="failed",
        )

        assert "Rollback failed during VPN key creation for 'Test Key'" in exc.message
        assert "Test Server" in exc.message
        assert "wg-key-123" in exc.message
        assert "CLEANUP FAILED: Manual intervention required" in exc.message

    def test_rollback_error_delete_operation_message(self):
        """Test VpnKeyRollbackError message for delete operation."""
        exc = VpnKeyRollbackError(
            operation="delete",
            key_id="key-uuid-123",
            external_id="wg-key-456",
            server_name="Test Server",
            cleanup_status="partial",
        )

        assert "Rollback failed during VPN key deletion for key key-uuid-123" in exc.message
        assert "Test Server" in exc.message
        assert "wg-key-456" in exc.message
        assert "CLEANUP PARTIAL: Manual intervention may be required" in exc.message

    def test_rollback_error_with_original_and_cleanup_errors(self):
        """Test VpnKeyRollbackError preserves original and cleanup errors."""
        original_error = Exception("Original DB error")
        cleanup_error = Exception("Cleanup failed")

        exc = VpnKeyRollbackError(
            operation="create",
            key_name="Test Key",
            original_error=original_error,
            cleanup_error=cleanup_error,
        )

        assert exc.original_error == original_error
        assert exc.cleanup_error == cleanup_error


class TestRollbackLogging:
    """Test that rollback operations are properly logged."""

    @pytest.mark.asyncio
    async def test_successful_rollback_logs_warning(
        self,
        service,
        mock_repos,
        mock_server_registry,
        mock_agent_client,
        sample_user,
        sample_server,
        caplog,
    ):
        """Test that successful rollback after DB failure logs warning."""
        # Arrange
        mock_repos["user_repo"].get_by_id = AsyncMock(return_value=sample_user)
        mock_repos["vpn_repo"].get_by_user_id = AsyncMock(return_value=[])
        mock_server_registry.select_best_server = AsyncMock(return_value=sample_server)
        mock_repos["vpn_repo"].create = AsyncMock(side_effect=Exception("DB error"))

        # Act
        with pytest.raises(Exception, match="DB error"):
            await service.create_key(
                user_id=sample_user.id,
                name="Test Key",
                vpn_type="wireguard",
            )

        # Assert - verify rollback was logged
        mock_agent_client.delete_wireguard_peer.assert_called_once()

    @pytest.mark.asyncio
    async def test_failed_rollback_logs_error(
        self,
        service,
        mock_repos,
        mock_server_registry,
        mock_agent_client,
        sample_user,
        sample_server,
        caplog,
    ):
        """Test that failed rollback logs error with full context."""
        # Arrange
        mock_repos["user_repo"].get_by_id = AsyncMock(return_value=sample_user)
        mock_repos["vpn_repo"].get_by_user_id = AsyncMock(return_value=[])
        mock_server_registry.select_best_server = AsyncMock(return_value=sample_server)
        mock_repos["vpn_repo"].create = AsyncMock(side_effect=Exception("DB error"))
        mock_agent_client.delete_wireguard_peer = AsyncMock(side_effect=Exception("Cleanup failed"))

        # Act
        with pytest.raises(VpnKeyRollbackError):
            await service.create_key(
                user_id=sample_user.id,
                name="Test Key",
                vpn_type="wireguard",
            )

        # Assert - verify cleanup was attempted
        mock_agent_client.delete_wireguard_peer.assert_called_once()


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    @pytest.mark.asyncio
    async def test_create_key_with_server_id_uses_selected_server(
        self,
        service,
        mock_repos,
        mock_server_registry,
        mock_agent_client,
        sample_user,
        sample_server,
    ):
        """Test that providing server_id uses selected server for rollback context."""
        # Arrange
        mock_repos["user_repo"].get_by_id = AsyncMock(return_value=sample_user)
        mock_repos["vpn_repo"].get_by_user_id = AsyncMock(return_value=[])
        mock_server_registry.get_server = AsyncMock(return_value=sample_server)
        mock_repos["vpn_repo"].create = AsyncMock(side_effect=Exception("DB error"))

        # Act
        with pytest.raises(Exception, match="DB error"):
            await service.create_key(
                user_id=sample_user.id,
                name="Test Key",
                vpn_type="wireguard",
                server_id=sample_server.id,
            )

        # Assert
        mock_server_registry.get_server.assert_called_once_with(sample_server.id)
        mock_agent_client.delete_wireguard_peer.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_key_without_server_id_uses_fallback(
        self, service, mock_repos, mock_server_registry, sample_user
    ):
        """Test deletion of key without server_id uses local fallback."""
        # Arrange
        key_without_server = VpnKey(
            id=str(uuid.uuid4()),
            user_id=sample_user.id,
            name="Legacy Key",
            key_type=KeyType.WIREGUARD,
            status=KeyStatus.ACTIVE,
            key_data="[Interface]",
            external_id="wg-legacy-key",
            server_id=None,  # No server_id
            created_at=None,
            expires_at=None,
            used_bytes=0,
            data_limit_bytes=5 * 1024**3,
            billing_reset_at=None,
        )
        mock_repos["vpn_repo"].get_by_id = AsyncMock(return_value=key_without_server)
        mock_repos["vpn_repo"].delete = AsyncMock(return_value=True)
        service.wireguard_client = AsyncMock()

        # Act
        await service.delete_key(user_id=sample_user.id, key_id=uuid.UUID(key_without_server.id))

        # Assert - local fallback used
        service.wireguard_client.delete_client.assert_called_once_with("wg-legacy-key")

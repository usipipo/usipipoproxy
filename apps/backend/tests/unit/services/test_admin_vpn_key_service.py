"""Unit tests for AdminVpnKeyService."""

import uuid
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest
from usipipo_commons.domain.entities.vpn_key import VpnKey
from usipipo_commons.domain.enums.key_status import KeyStatus
from usipipo_commons.domain.enums.key_type import KeyType

from src.core.application.services.admin_vpn_key_service import AdminVpnKeyService
from src.infrastructure.persistence.models.vpn_server_model import VpnServerModel


@pytest.fixture
def mock_repos():
    """Create mock repositories."""
    user_repo = AsyncMock()
    vpn_key_repo = AsyncMock()
    audit_log_repo = AsyncMock()
    return {
        "user_repo": user_repo,
        "vpn_key_repo": vpn_key_repo,
        "audit_log_repo": audit_log_repo,
    }


@pytest.fixture
def mock_session():
    """Create mock database session."""
    session = AsyncMock()
    session.execute = AsyncMock()
    return session


@pytest.fixture
def service(mock_session, mock_repos):
    """Create AdminVpnKeyService instance with mocks."""
    return AdminVpnKeyService(
        session=mock_session,
        user_repo=mock_repos["user_repo"],
        vpn_key_repo=mock_repos["vpn_key_repo"],
        audit_log_repo=mock_repos["audit_log_repo"],
    )


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
def sample_vpn_key():
    """Create sample VPN key entity."""
    return VpnKey(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        name="test-key",
        key_type=KeyType.WIREGUARD,
        status=KeyStatus.ACTIVE,
        key_data="config-data",
        external_id="ext-id-123",
        created_at=datetime.now(UTC),
        expires_at=datetime.now(UTC) + timedelta(days=30),
        used_bytes=1024**3,  # 1 GB
        data_limit_bytes=5 * 1024**3,  # 5 GB
        billing_reset_at=datetime.now(UTC),
    )


@pytest.fixture
def sample_server():
    """Create sample server model."""
    server = MagicMock(spec=VpnServerModel)
    server.id = uuid.uuid4()
    server.agent_url = "https://test-agent.example.com"
    server.agent_api_key = "test-api-key"
    server.country_code = "US"
    server.is_active = True
    return server


@pytest.mark.asyncio
async def test_list_keys_no_filters(service, mock_repos, sample_vpn_key):
    """Test listing keys without filters."""
    # Arrange
    mock_repos["vpn_key_repo"].get_all_keys = AsyncMock(return_value=[sample_vpn_key])

    # Act
    result = await service.list_keys({}, current_admin_id=999)

    # Assert
    assert result["total"] == 1
    assert len(result["keys"]) == 1
    assert result["page"] == 1
    assert result["page_size"] == 20
    mock_repos["vpn_key_repo"].get_all_keys.assert_called_once()


@pytest.mark.asyncio
async def test_list_keys_filter_by_user(service, mock_repos, sample_vpn_key, sample_user):
    """Test listing keys filtered by user UUID."""
    # Arrange
    # Make sure the vpn_key belongs to this user
    sample_vpn_key.user_id = sample_user.id
    mock_repos["vpn_key_repo"].get_all_keys = AsyncMock(return_value=[sample_vpn_key])

    # Act
    result = await service.list_keys(
        {"user_id": str(sample_user.id)},
        current_admin_id=uuid.uuid4(),
    )

    # Assert
    assert result["total"] == 1


@pytest.mark.asyncio
async def test_list_keys_filter_by_vpn_type(service, mock_repos, sample_vpn_key):
    """Test listing keys filtered by VPN type."""
    # Arrange
    mock_repos["vpn_key_repo"].get_all_keys = AsyncMock(return_value=[sample_vpn_key])

    # Act
    result = await service.list_keys(
        {"vpn_type": "wireguard"},
        current_admin_id=999,
    )

    # Assert
    assert result["total"] == 1
    assert len(result["keys"]) == 1


@pytest.mark.asyncio
async def test_list_keys_filter_by_status(service, mock_repos, sample_vpn_key):
    """Test listing keys filtered by status."""
    # Arrange
    mock_repos["vpn_key_repo"].get_all_keys = AsyncMock(return_value=[sample_vpn_key])

    # Act
    result = await service.list_keys(
        {"status": "active"},
        current_admin_id=999,
    )

    # Assert
    assert result["total"] == 1


@pytest.mark.asyncio
async def test_list_keys_pagination(service, mock_repos, sample_vpn_key):
    """Test listing keys with pagination."""
    # Arrange
    keys = [sample_vpn_key for _ in range(50)]
    mock_repos["vpn_key_repo"].get_all_keys = AsyncMock(return_value=keys)

    # Act
    result = await service.list_keys(
        {"page": 1, "page_size": 20},
        current_admin_id=999,
    )

    # Assert
    assert result["total"] == 50
    assert result["page"] == 1
    assert result["page_size"] == 20
    assert result["total_pages"] == 3
    assert result["has_next"] is True
    assert result["has_previous"] is False
    assert len(result["keys"]) == 20


@pytest.mark.asyncio
async def test_get_key_detail(service, mock_repos, sample_vpn_key):
    """Test getting key details."""
    # Arrange
    mock_repos["vpn_key_repo"].get_by_id = AsyncMock(return_value=sample_vpn_key)

    # Act
    result = await service.get_key_detail(sample_vpn_key.id, current_admin_id=999)

    # Assert
    assert result is not None
    assert result.id == sample_vpn_key.id
    mock_repos["vpn_key_repo"].get_by_id.assert_called_once_with(sample_vpn_key.id)


@pytest.mark.asyncio
async def test_get_key_detail_not_found(service, mock_repos):
    """Test getting key details when key doesn't exist."""
    # Arrange
    mock_repos["vpn_key_repo"].get_by_id = AsyncMock(return_value=None)
    key_id = uuid.uuid4()

    # Act
    result = await service.get_key_detail(key_id, current_admin_id=999)

    # Assert
    assert result is None


@pytest.mark.asyncio
async def test_get_user_keys(service, mock_repos, sample_user, sample_vpn_key):
    """Test getting all keys for a user."""
    # Arrange
    mock_repos["user_repo"].get_by_id = AsyncMock(return_value=sample_user)
    mock_repos["vpn_key_repo"].get_by_user_id = AsyncMock(return_value=[sample_vpn_key])

    # Act
    result = await service.get_user_keys(sample_user.id, current_admin_id=uuid.uuid4())

    # Assert
    assert len(result) == 1
    mock_repos["user_repo"].get_by_id.assert_called_once_with(sample_user.id)


@pytest.mark.asyncio
async def test_get_user_keys_user_not_found(service, mock_repos):
    """Test getting keys for non-existent user."""
    # Arrange
    mock_repos["user_repo"].get_by_id = AsyncMock(return_value=None)

    # Act
    result = await service.get_user_keys(uuid.uuid4(), current_admin_id=uuid.uuid4())

    # Assert
    assert len(result) == 0


@pytest.mark.asyncio
async def test_toggle_key_active_to_revoked(service, mock_repos, sample_vpn_key):
    """Test toggling key from active to revoked."""
    # Arrange
    mock_repos["vpn_key_repo"].get_by_id = AsyncMock(return_value=sample_vpn_key)
    mock_repos["vpn_key_repo"].update = AsyncMock()

    # Act
    result = await service.toggle_key(sample_vpn_key.id, current_admin_id=999)

    # Assert
    assert result is True
    assert sample_vpn_key.status == KeyStatus.REVOKED
    mock_repos["vpn_key_repo"].update.assert_called_once_with(sample_vpn_key)


@pytest.mark.asyncio
async def test_toggle_key_revoked_to_active(service, mock_repos, sample_vpn_key):
    """Test toggling key from revoked to active."""
    # Arrange
    sample_vpn_key.status = KeyStatus.REVOKED
    mock_repos["vpn_key_repo"].get_by_id = AsyncMock(return_value=sample_vpn_key)
    mock_repos["vpn_key_repo"].update = AsyncMock()

    # Act
    result = await service.toggle_key(sample_vpn_key.id, current_admin_id=999)

    # Assert
    assert result is True
    assert sample_vpn_key.status == KeyStatus.ACTIVE


@pytest.mark.asyncio
async def test_toggle_key_not_found(service, mock_repos):
    """Test toggling non-existent key."""
    # Arrange
    mock_repos["vpn_key_repo"].get_by_id = AsyncMock(return_value=None)
    key_id = uuid.uuid4()

    # Act & Assert
    with pytest.raises(ValueError, match=f"Key {key_id} not found"):
        await service.toggle_key(key_id, current_admin_id=999)


@pytest.mark.asyncio
async def test_update_data_limit(service, mock_repos, sample_vpn_key):
    """Test updating data limit."""
    # Arrange
    mock_repos["vpn_key_repo"].get_by_id = AsyncMock(return_value=sample_vpn_key)
    mock_repos["vpn_key_repo"].update = AsyncMock()

    # Act
    result = await service.update_data_limit(
        sample_vpn_key.id,
        data_limit_gb=10.0,
        reason="test upgrade",
        current_admin_id=999,
    )

    # Assert
    assert result is True
    assert sample_vpn_key.data_limit_bytes == int(10.0 * 1024**3)
    mock_repos["vpn_key_repo"].update.assert_called_once()


@pytest.mark.asyncio
async def test_reset_usage(service, mock_repos, sample_vpn_key):
    """Test resetting data usage."""
    # Arrange
    mock_repos["vpn_key_repo"].get_by_id = AsyncMock(return_value=sample_vpn_key)
    mock_repos["vpn_key_repo"].update = AsyncMock()

    # Act
    result = await service.reset_usage(
        sample_vpn_key.id,
        reason="billing cycle reset",
        current_admin_id=999,
    )

    # Assert
    assert result is True
    assert sample_vpn_key.used_bytes == 0
    mock_repos["vpn_key_repo"].update.assert_called_once()


@pytest.mark.asyncio
async def test_log_audit_with_repository(service, mock_repos):
    """Test logging audit with repository."""
    # Arrange
    target_id = uuid.uuid4()
    admin_id = uuid.uuid4()

    # Act
    await service.log_audit(
        operation="create_key",
        target_id=target_id,
        admin_id=admin_id,
        admin_username="testadmin",
        success=True,
        details={"user_id": str(uuid.uuid4())},
    )

    # Assert
    mock_repos["audit_log_repo"].create.assert_called_once()

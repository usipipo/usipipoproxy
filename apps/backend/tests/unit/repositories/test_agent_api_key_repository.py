"""Tests for AgentApiKeyRepository."""

from datetime import UTC

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.persistence.repositories.agent_api_key_repository import (
    AgentApiKeyRepository,
)


@pytest.fixture
def repository(test_session: AsyncSession) -> AgentApiKeyRepository:
    """Create repository instance."""
    return AgentApiKeyRepository(test_session)


@pytest.mark.asyncio
async def test_create_api_key(repository: AgentApiKeyRepository):
    """Test creating a new API key."""
    api_key = await repository.create(
        api_key_hash="test_hash_123",
        description="Test key",
    )

    assert api_key.api_key_hash == "test_hash_123"
    assert api_key.status == "active"
    assert api_key.description == "Test key"
    assert api_key.server_id is None
    assert api_key.used_at is None


@pytest.mark.asyncio
async def test_create_api_key_with_expiration(repository: AgentApiKeyRepository):
    """Test creating an API key with expiration."""
    from datetime import datetime, timedelta

    expires_at = datetime.now(UTC) + timedelta(days=30)

    api_key = await repository.create(
        api_key_hash="test_hash_expires",
        description="Key with expiration",
        expires_at=expires_at,
    )

    assert api_key.api_key_hash == "test_hash_expires"
    # Model stores naive datetime, compare naive versions
    assert api_key.expires_at.replace(tzinfo=UTC) == expires_at
    assert api_key.status == "active"


@pytest.mark.asyncio
async def test_get_by_hash(repository: AgentApiKeyRepository):
    """Test retrieving API key by hash."""
    # Create key
    created = await repository.create(api_key_hash="test_hash_456")

    # Retrieve
    retrieved = await repository.get_by_hash("test_hash_456")

    assert retrieved is not None
    assert retrieved.id == created.id
    assert retrieved.api_key_hash == "test_hash_456"


@pytest.mark.asyncio
async def test_get_by_hash_not_found(repository: AgentApiKeyRepository):
    """Test retrieving non-existent API key."""
    retrieved = await repository.get_by_hash("nonexistent_hash")
    assert retrieved is None


@pytest.mark.asyncio
async def test_mark_as_used(repository: AgentApiKeyRepository):
    """Test marking API key as used."""
    import uuid

    # Create key
    api_key = await repository.create(api_key_hash="test_hash_789")
    assert api_key.status == "active"
    assert api_key.used_at is None
    assert api_key.server_id is None

    # Mark as used
    server_id = uuid.uuid4()
    updated = await repository.mark_as_used(api_key, server_id)

    assert updated.status == "used"
    assert updated.server_id == server_id
    assert updated.used_at is not None


@pytest.mark.asyncio
async def test_revoke_api_key(repository: AgentApiKeyRepository):
    """Test revoking an API key."""
    # Create key
    api_key = await repository.create(api_key_hash="test_hash_revoke")
    assert api_key.status == "active"

    # Revoke
    updated = await repository.revoke(api_key)

    assert updated.status == "revoked"


@pytest.mark.asyncio
async def test_list_keys_all(repository: AgentApiKeyRepository):
    """Test listing all API keys."""
    # Create multiple keys
    await repository.create(api_key_hash="list_test_1")
    await repository.create(api_key_hash="list_test_2")
    await repository.create(api_key_hash="list_test_3")

    # List all
    keys = await repository.list_keys()

    assert len(keys) >= 3


@pytest.mark.asyncio
async def test_list_keys_by_status(repository: AgentApiKeyRepository):
    """Test listing API keys filtered by status."""
    import uuid

    # Create keys with different statuses
    await repository.create(api_key_hash="status_test_1")
    key2 = await repository.create(api_key_hash="status_test_2")

    # Mark one as used
    await repository.mark_as_used(key2, uuid.uuid4())

    # List active keys
    active_keys = await repository.list_keys(status="active")
    assert len(active_keys) >= 1
    assert all(k.status == "active" for k in active_keys)

    # List used keys
    used_keys = await repository.list_keys(status="used")
    assert len(used_keys) >= 1
    assert all(k.status == "used" for k in used_keys)


@pytest.mark.asyncio
async def test_list_keys_pagination(repository: AgentApiKeyRepository):
    """Test listing API keys with pagination."""
    # Create multiple keys
    for i in range(10):
        await repository.create(api_key_hash=f"pagination_test_{i}")

    # Get first page
    page1 = await repository.list_keys(limit=5, offset=0)
    assert len(page1) == 5

    # Get second page
    page2 = await repository.list_keys(limit=5, offset=5)
    assert len(page2) == 5

    # Ensure pages are different
    assert page1[0].id != page2[0].id

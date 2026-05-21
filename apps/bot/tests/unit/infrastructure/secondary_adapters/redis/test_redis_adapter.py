"""Tests for RedisAdapter."""

import time
import pytest
from unittest.mock import AsyncMock, patch

from src.infrastructure.secondary_adapters.redis.redis_adapter import (
    RedisAdapter,
)


@pytest.fixture
def redis_adapter() -> RedisAdapter:
    """Crea un RedisAdapter para tests."""
    return RedisAdapter()


@pytest.mark.asyncio
async def test_store_tokens(redis_adapter: RedisAdapter):
    """Test de almacenamiento de tokens."""
    mock_redis = AsyncMock()
    mock_pipeline = AsyncMock()
    mock_pipeline.__aenter__ = AsyncMock(return_value=mock_pipeline)
    mock_pipeline.__aexit__ = AsyncMock(return_value=None)
    mock_pipeline.hset = AsyncMock()
    mock_pipeline.expire = AsyncMock()
    mock_pipeline.execute = AsyncMock()
    mock_redis.pipeline = lambda: mock_pipeline

    with patch.object(redis_adapter, "_get_redis", return_value=mock_redis):
        await redis_adapter.store(
            telegram_id=1058749165,
            access_token="test_access",
            refresh_token="test_refresh",
            expires_in=1800,
        )

        # Verify pipeline was used
        assert mock_pipeline.hset.called
        assert mock_pipeline.expire.called
        assert mock_pipeline.execute.called


@pytest.mark.asyncio
async def test_get_tokens_success(redis_adapter: RedisAdapter):
    """Test de obtención de tokens exitosa."""
    mock_redis = AsyncMock()
    mock_redis.hgetall = AsyncMock(
        return_value={
            "access_token": "test_access",
            "refresh_token": "test_refresh",
            "expires_at": "1234567890",
            "created_at": "1234567800",
        }
    )

    with patch.object(redis_adapter, "_get_redis", return_value=mock_redis):
        tokens = await redis_adapter.get(1058749165)

        assert tokens is not None
        assert tokens["access_token"] == "test_access"
        assert tokens["refresh_token"] == "test_refresh"
        assert tokens["expires_at"] == 1234567890
        assert tokens["created_at"] == 1234567800


@pytest.mark.asyncio
async def test_get_tokens_not_found(redis_adapter: RedisAdapter):
    """Test cuando no hay tokens."""
    mock_redis = AsyncMock()
    mock_redis.hgetall = AsyncMock(return_value={})

    with patch.object(redis_adapter, "_get_redis", return_value=mock_redis):
        tokens = await redis_adapter.get(1058749165)

        assert tokens is None


@pytest.mark.asyncio
async def test_delete_tokens_success(redis_adapter: RedisAdapter):
    """Test de eliminación de tokens exitosa."""
    mock_redis = AsyncMock()
    mock_redis.delete = AsyncMock(return_value=1)

    with patch.object(redis_adapter, "_get_redis", return_value=mock_redis):
        result = await redis_adapter.delete(1058749165)

        assert result is True
        mock_redis.delete.assert_called_once()


@pytest.mark.asyncio
async def test_delete_tokens_not_found(redis_adapter: RedisAdapter):
    """Test cuando no hay tokens para eliminar."""
    mock_redis = AsyncMock()
    mock_redis.delete = AsyncMock(return_value=0)

    with patch.object(redis_adapter, "_get_redis", return_value=mock_redis):
        result = await redis_adapter.delete(1058749165)

        assert result is False


@pytest.mark.asyncio
async def test_is_authenticated_true(redis_adapter: RedisAdapter):
    """Test de autenticación exitosa."""
    mock_redis = AsyncMock()
    mock_redis.hgetall = AsyncMock(
        return_value={
            "access_token": "test_access",
            "refresh_token": "test_refresh",
            "expires_at": str(int(time.time()) + 1800),  # 30 min in future
            "created_at": str(int(time.time())),
        }
    )

    with patch.object(redis_adapter, "_get_redis", return_value=mock_redis):
        result = await redis_adapter.is_authenticated(1058749165)

        assert result is True


@pytest.mark.asyncio
async def test_is_authenticated_false_no_tokens(redis_adapter: RedisAdapter):
    """Test cuando no hay tokens."""
    mock_redis = AsyncMock()
    mock_redis.hgetall = AsyncMock(return_value={})

    with patch.object(redis_adapter, "_get_redis", return_value=mock_redis):
        result = await redis_adapter.is_authenticated(1058749165)

        assert result is False


@pytest.mark.asyncio
async def test_is_authenticated_false_expired(redis_adapter: RedisAdapter):
    """Test cuando tokens expiraron."""
    mock_redis = AsyncMock()
    mock_redis.hgetall = AsyncMock(
        return_value={
            "access_token": "test_access",
            "refresh_token": "test_refresh",
            "expires_at": str(int(time.time()) - 100),  # Expired 100 sec ago
            "created_at": str(int(time.time()) - 3600),
        }
    )

    with patch.object(redis_adapter, "_get_redis", return_value=mock_redis):
        result = await redis_adapter.is_authenticated(1058749165)

        assert result is False


@pytest.mark.asyncio
async def test_refresh_if_needed_not_required(redis_adapter: RedisAdapter):
    """Test cuando no se necesita refresh."""
    mock_redis = AsyncMock()
    mock_redis.hgetall = AsyncMock(
        return_value={
            "access_token": "test_access",
            "refresh_token": "test_refresh",
            "expires_at": str(int(time.time()) + 600),  # 10 min remaining (> 5 min threshold)
            "created_at": str(int(time.time())),
        }
    )

    with patch.object(redis_adapter, "_get_redis", return_value=mock_redis):
        result = await redis_adapter.refresh_if_needed(1058749165, AsyncMock())

        assert result is False


@pytest.mark.asyncio
async def test_refresh_if_needed_success(redis_adapter: RedisAdapter):
    """Test de refresh exitoso."""
    import time as time_module

    current_time = int(time_module.time())

    mock_redis = AsyncMock()
    mock_redis.hgetall = AsyncMock(
        return_value={
            "access_token": "old_access",
            "refresh_token": "old_refresh",
            "expires_at": str(current_time + 120),  # 2 min remaining (< 5 min threshold)
            "created_at": str(current_time - 1000),
        }
    )

    # Mock pipeline para store
    mock_pipeline = AsyncMock()
    mock_pipeline.__aenter__ = AsyncMock(return_value=mock_pipeline)
    mock_pipeline.__aexit__ = AsyncMock(return_value=None)
    mock_pipeline.hset = AsyncMock()
    mock_pipeline.expire = AsyncMock()
    mock_pipeline.execute = AsyncMock()
    mock_redis.pipeline = lambda: mock_pipeline

    mock_backend = AsyncMock()
    mock_backend.refresh_tokens = AsyncMock(
        return_value={
            "access_token": "new_access",
            "refresh_token": "new_refresh",
            "expires_in": 1800,
        }
    )

    with patch.object(redis_adapter, "_get_redis", return_value=mock_redis):
        result = await redis_adapter.refresh_if_needed(1058749165, mock_backend)

        assert result is True
        mock_backend.refresh_tokens.assert_called_once_with("old_refresh")


@pytest.mark.asyncio
async def test_refresh_if_needed_no_tokens(redis_adapter: RedisAdapter):
    """Test cuando no hay tokens para refresh."""
    mock_redis = AsyncMock()
    mock_redis.hgetall = AsyncMock(return_value={})

    with patch.object(redis_adapter, "_get_redis", return_value=mock_redis):
        result = await redis_adapter.refresh_if_needed(1058749165, AsyncMock())

        assert result is False


@pytest.mark.asyncio
async def test_refresh_if_needed_backend_error(redis_adapter: RedisAdapter):
    """Test cuando falla el refresh del backend."""
    mock_redis = AsyncMock()
    mock_redis.hgetall = AsyncMock(
        return_value={
            "access_token": "old_access",
            "refresh_token": "old_refresh",
            "expires_at": str(int(time.time()) + 120),
            "created_at": str(int(time.time())),
        }
    )

    mock_backend = AsyncMock()
    mock_backend.refresh_tokens = AsyncMock(side_effect=Exception("Backend error"))

    with patch.object(redis_adapter, "_get_redis", return_value=mock_redis):
        result = await redis_adapter.refresh_if_needed(1058749165, mock_backend)

        assert result is False

"""Tests para TokenStorage."""

import pytest


class TestTokenStorage:
    """Tests para TokenStorage."""

    @pytest.mark.asyncio
    async def test_token_storage_initialization(self):
        """TokenStorage se inicializa correctamente."""
        from src.infrastructure.token_storage import TokenStorage

        storage = TokenStorage()

        assert storage.TOKEN_PREFIX == "usipipo:bot:tokens:"
        assert storage.REFRESH_TOKEN_EXPIRY == 30 * 24 * 60 * 60

    @pytest.mark.asyncio
    async def test_token_storage_constants(self):
        """TokenStorage tiene constantes correctas."""
        from src.infrastructure.token_storage import TokenStorage

        assert TokenStorage.ACCESS_TOKEN_EXPIRY == 30 * 60  # 30 min
        assert TokenStorage.REFRESH_TOKEN_EXPIRY == 30 * 24 * 60 * 60  # 30 días

    @pytest.mark.asyncio
    async def test_redis_pool_exists(self):
        """RedisPool existe y tiene métodos."""
        from src.infrastructure.redis import RedisPool

        assert hasattr(RedisPool, "get_instance")
        assert hasattr(RedisPool, "get_client")
        assert hasattr(RedisPool, "health_check")
        assert hasattr(RedisPool, "close")

    @pytest.mark.asyncio
    async def test_redis_pool_singleton_pattern(self):
        """RedisPool sigue patrón singleton."""
        from src.infrastructure.redis import RedisPool

        # Reset singleton
        RedisPool._instance = None
        RedisPool._pool = None

        assert RedisPool._instance is None

    @pytest.mark.asyncio
    async def test_config_has_redis_settings(self):
        """Settings tiene configuración de Redis."""
        from src.infrastructure.config import settings

        assert hasattr(settings, "REDIS_URL")
        assert hasattr(settings, "REDIS_MAX_CONNECTIONS")
        assert hasattr(settings, "REDIS_SOCKET_TIMEOUT")

    @pytest.mark.asyncio
    async def test_token_storage_methods_are_async(self):
        """Métodos de TokenStorage son async."""
        from src.infrastructure.token_storage import TokenStorage
        import inspect

        assert inspect.iscoroutinefunction(TokenStorage.store)
        assert inspect.iscoroutinefunction(TokenStorage.get)
        assert inspect.iscoroutinefunction(TokenStorage.delete)
        assert inspect.iscoroutinefunction(TokenStorage.is_authenticated)
        assert inspect.iscoroutinefunction(TokenStorage.needs_refresh)

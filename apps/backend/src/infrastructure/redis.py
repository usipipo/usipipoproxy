"""Redis connection pool for uSipipo Backend."""

import logging
import redis.asyncio as redis
from typing import Optional

from src.shared.config import settings

logger = logging.getLogger(__name__)


class RedisPool:
    """
    Redis connection pool singleton.

    Manages async Redis connections for caching, sessions,
    rate limiting, and background job queues.
    """

    _instance: Optional["RedisPool"] = None
    _pool: Optional[redis.Redis] = None

    def __init__(
        self,
        redis_url: str,
        max_connections: int = 10,
    ):
        self.redis_url = redis_url
        self.max_connections = max_connections

    @classmethod
    async def get_instance(
        cls,
        redis_url: Optional[str] = None,
        max_connections: Optional[int] = None,
    ) -> "RedisPool":
        """
        Get RedisPool singleton instance.

        Args:
            redis_url: Redis URL (uses settings by default)
            max_connections: Max connections (uses settings by default)

        Returns:
            RedisPool: Singleton instance
        """
        if cls._instance is None:
            url = redis_url or settings.REDIS_URL
            connections = max_connections or settings.REDIS_MAX_CONNECTIONS

            cls._instance = cls(url, connections)
            cls._pool = redis.from_url(
                url,
                max_connections=connections,
                decode_responses=True,
                socket_timeout=settings.REDIS_SOCKET_TIMEOUT,
                socket_connect_timeout=settings.REDIS_SOCKET_TIMEOUT,
                retry_on_timeout=settings.REDIS_RETRY_ON_TIMEOUT,
            )
        return cls._instance

    @classmethod
    async def get_client(cls) -> redis.Redis:
        """
        Get Redis client from pool.

        Returns:
            redis.Redis: Redis client

        Raises:
            RuntimeError: If pool is not initialized
        """
        if cls._pool is None:
            # Auto-initialize with settings
            await cls.get_instance()

        if cls._pool is None:
            raise RuntimeError("Redis pool not initialized")

        return cls._pool

    @classmethod
    async def health_check(cls) -> bool:
        """
        Check Redis connection health.

        Returns:
            bool: True if connected, False otherwise
        """
        try:
            client = await cls.get_client()
            await client.ping()
            return True
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return False

    @classmethod
    async def close(cls) -> None:
        """Close Redis connection pool."""
        if cls._pool:
            await cls._pool.close()
            cls._pool = None
            cls._instance = None

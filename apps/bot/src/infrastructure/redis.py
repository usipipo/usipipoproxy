"""Redis connection pool para el bot uSipipo."""

import redis.asyncio as redis
from typing import Optional

from src.infrastructure.config import settings


class RedisPool:
    """
    Pool de conexiones Redis (singleton).

    Gestiona conexiones asíncronas a Redis para almacenamiento
    de tokens y sesiones.
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
        Obtiene instancia singleton del pool.

        Args:
            redis_url: URL de Redis (usa settings por defecto)
            max_connections: Máximo de conexiones (usa settings por defecto)

        Returns:
            RedisPool: Instancia singleton
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
        Obtiene cliente Redis del pool.

        Returns:
            redis.Redis: Cliente Redis

        Raises:
            RuntimeError: Si el pool no está inicializado
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
        Verifica conexión con Redis.

        Returns:
            bool: True si está conectado, False si no
        """
        try:
            client = await cls.get_client()
            await client.ping()  # type: ignore[misc]
            return True
        except Exception:
            return False

    @classmethod
    async def close(cls) -> None:
        """Cierra el pool de conexiones."""
        if cls._pool:
            await cls._pool.close()
            cls._pool = None
            cls._instance = None

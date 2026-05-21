"""Redis-based cache service for expensive database queries."""

import json
import logging
from typing import Any

import redis.asyncio as redis

from src.infrastructure.redis import RedisPool

logger = logging.getLogger(__name__)


class CacheService:
    """
    Servicio de cacheo utilizando Redis.

    Proporciona caching automático con TTL para consultas
    costosas como listados de usuarios, estadísticas, etc.
    """

    def __init__(
        self,
        redis_client: redis.Redis | None = None,
        default_ttl: int = 300,  # 5 minutes
    ):
        self.redis_client = redis_client
        self.default_ttl = default_ttl

    async def _get_client(self) -> redis.Redis:
        """Obtiene cliente Redis."""
        if self.redis_client:
            return self.redis_client
        return await RedisPool.get_client()

    def _make_key(self, prefix: str, *args: Any) -> str:
        """
        Genera una clave cache única.

        Args:
            prefix: Prefijo del tipo de dato
            *args: Argumentos para identificar la consulta

        Returns:
            str: Clave cache única
        """
        key_parts = [str(arg) for arg in args if arg is not None]
        key = f"usipipo:backend:cache:{prefix}:{':'.join(key_parts)}"
        return key

    async def get(self, prefix: str, *args: Any) -> Any | None:
        """
        Recupera valor del cache.

        Args:
            prefix: Prefijo del tipo de dato
            *args: Argumentos de la consulta

        Returns:
            Valor cacheado o None si no existe
        """
        key = self._make_key(prefix, *args)
        try:
            client = await self._get_client()
            value = await client.get(key)
            if value:
                logger.debug(f"Cache hit: {key}")
                return json.loads(value)
            logger.debug(f"Cache miss: {key}")
            return None
        except Exception as e:
            logger.warning(f"Cache get error for key {key}: {e}")
            return None

    async def set(
        self,
        prefix: str,
        value: Any,
        ttl: int | None = None,
        *args: Any,
    ) -> bool:
        """
        Almacena valor en cache.

        Args:
            prefix: Prefijo del tipo de dato
            value: Valor a cachear (serializable a JSON)
            ttl: Tiempo de vida en segundos (default: 300)
            *args: Argumentos para generar la clave

        Returns:
            True si se guardó correctamente
        """
        key = self._make_key(prefix, *args)
        ttl = ttl or self.default_ttl

        try:
            client = await self._get_client()
            serialized = json.dumps(value, default=str)
            await client.setex(key, ttl, serialized)
            logger.debug(f"Cache set: {key} (TTL: {ttl}s)")
            return True
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False

    async def delete(self, prefix: str, *args: Any) -> bool:
        """
        Elimina una entrada del cache.

        Args:
            prefix: Prefijo del tipo de dato
            *args: Argumentos de la consulta

        Returns:
            True si se eliminó
        """
        key = self._make_key(prefix, *args)
        try:
            client = await self._get_client()
            await client.delete(key)
            logger.debug(f"Cache delete: {key}")
            return True
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            return False

    async def clear_pattern(self, pattern: str) -> int:
        """
        Elimina todas las claves que coincidan con el patrón.

        Args:
            pattern: Patrón de claves (ej: "user:*")

        Returns:
            Número de claves eliminadas
        """
        try:
            client = await self._get_client()
            keys = []
            async for key in client.scan_iter(match=pattern):
                keys.append(key)

            if keys:
                deleted = await client.delete(*keys)
                logger.info(f"Cache clear pattern '{pattern}': {deleted} keys deleted")
                return deleted
            return 0
        except Exception as e:
            logger.error(f"Cache clear pattern error: {e}")
            return 0

    async def exists(self, prefix: str, *args: Any) -> bool:
        """Verifica si una clave existe en cache."""
        key = self._make_key(prefix, *args)
        try:
            client = await self._get_client()
            return await client.exists(key) > 0
        except Exception as e:
            logger.warning(f"Cache exists error for key {key}: {e}")
            return False

    async def ttl(self, prefix: str, *args: Any) -> int:
        """
        Obtiene el tiempo de vida restante de una clave.

        Returns:
            Segundos restantes (-1 si no expira, -2 si no existe)
        """
        key = self._make_key(prefix, *args)
        try:
            client = await self._get_client()
            return await client.ttl(key)
        except Exception as e:
            logger.warning(f"Cache TTL error for key {key}: {e}")
            return -2

    async def increment(self, prefix: str, field: str, amount: int = 1) -> int:
        """
        Incrementa un contador en cache.

        Útil para rate limiting y métricas en tiempo real.

        Args:
            prefix: Prefijo del contador
            field: Campo/identifier a incrementar
            amount: Cantidad a incrementar

        Returns:
            Nuevo valor del contador
        """
        key = self._make_key(prefix, field)
        try:
            client = await self._get_client()
            return await client.incrby(key, amount)
        except Exception as e:
            logger.error(f"Cache increment error for key {key}: {e}")
            return 0

    async def expire(self, prefix: str, ttl: int, *args: Any) -> bool:
        """
        Establece TTL para una clave existente.

        Args:
            prefix: Prefijo del tipo de dato
            ttl: Tiempo de vida en segundos
            *args: Argumentos para generar la clave

        Returns:
            True si se estableció correctamente
        """
        key = self._make_key(prefix, *args)
        try:
            client = await self._get_client()
            await client.expire(key, ttl)
            return True
        except Exception as e:
            logger.error(f"Cache expire error for key {key}: {e}")
            return False

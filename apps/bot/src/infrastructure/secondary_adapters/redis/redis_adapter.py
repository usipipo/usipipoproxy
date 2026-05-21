"""Redis Adapter - Implementation of TokenStoragePort."""

import logging
import time
from typing import TYPE_CHECKING, Optional

import redis.asyncio as redis

from ....application.ports.backend_api_port import BackendApiPort
from ....application.ports.token_storage_port import TokenStoragePort
from ...redis import RedisPool


if TYPE_CHECKING:
    from ....application.ports.backend_api_port import BackendApiPort


logger = logging.getLogger(__name__)


class RedisAdapter(TokenStoragePort):
    """
    Adaptador secundario para almacenamiento de tokens en Redis.

    Implementa el contrato TokenStoragePort usando Redis.
    """

    TOKEN_PREFIX = "usipipo:bot:tokens:"
    ACCESS_TOKEN_EXPIRY = 30 * 60  # 30 minutos
    REFRESH_TOKEN_EXPIRY = 30 * 24 * 60 * 60  # 30 días
    REFRESH_THRESHOLD = 5 * 60  # 5 minutos antes de expirar

    def __init__(self, redis_pool: Optional[redis.Redis] = None):
        """
        Inicializa el adaptador.

        Args:
            redis_pool: Pool de conexiones Redis (opcional, usa singleton si None)
        """
        self._redis_pool = redis_pool

    async def _get_redis(self) -> redis.Redis:
        """Obtiene cliente Redis del pool."""
        if self._redis_pool:
            return self._redis_pool
        return await RedisPool.get_client()

    async def store(
        self,
        telegram_id: int,
        access_token: str,
        refresh_token: str,
        expires_in: int,
    ) -> None:
        """
        Guarda tokens con expiración automática.

        Args:
            telegram_id: ID de Telegram del usuario
            access_token: JWT access token
            refresh_token: JWT refresh token
            expires_in: Segundos hasta expiración
        """
        key = f"{self.TOKEN_PREFIX}{telegram_id}"
        redis_client = await self._get_redis()

        async with redis_client.pipeline() as pipe:
            await pipe.hset(
                key,
                mapping={  # type: ignore[misc]
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "expires_at": str(int(time.time()) + expires_in),
                    "created_at": str(int(time.time())),
                },
            )
            await pipe.expire(key, self.REFRESH_TOKEN_EXPIRY)
            await pipe.execute()

        logger.debug(f"Tokens stored for user {telegram_id}")

    async def get(self, telegram_id: int) -> Optional[dict]:
        """
        Recupera tokens del usuario.

        Args:
            telegram_id: ID de Telegram del usuario

        Returns:
            dict con access_token y refresh_token, o None
        """
        key = f"{self.TOKEN_PREFIX}{telegram_id}"
        redis_client = await self._get_redis()
        data = await redis_client.hgetall(key)  # type: ignore[misc]

        if not data:
            return None

        return {
            "access_token": data["access_token"],
            "refresh_token": data["refresh_token"],
            "expires_at": int(data["expires_at"]),
            "created_at": int(data["created_at"]),
        }

    async def delete(self, telegram_id: int) -> bool:
        """
        Elimina tokens (unlink).

        Args:
            telegram_id: ID de Telegram del usuario

        Returns:
            True si se eliminó, False si no existía
        """
        key = f"{self.TOKEN_PREFIX}{telegram_id}"
        redis_client = await self._get_redis()
        deleted = await redis_client.delete(key)

        if deleted:
            logger.debug(f"Tokens deleted for user {telegram_id}")

        return deleted > 0

    async def is_authenticated(self, telegram_id: int) -> bool:
        """
        Verifica si el usuario tiene tokens válidos.

        Args:
            telegram_id: ID de Telegram del usuario

        Returns:
            True si tiene tokens válidos
        """
        tokens = await self.get(telegram_id)

        if not tokens:
            return False

        # Check if access token expired
        if time.time() > tokens["expires_at"]:
            logger.debug(f"Tokens expired for user {telegram_id}")
            return False

        return True

    async def refresh_if_needed(
        self,
        telegram_id: int,
        backend_api: "BackendApiPort",
    ) -> bool:
        """
        Auto-refresh si token está por expirar (5 min).

        Args:
            telegram_id: ID de Telegram del usuario
            backend_api: BackendApiPort para refresh

        Returns:
            True si se hizo refresh, False si no era necesario
        """
        tokens = await self.get(telegram_id)

        if not tokens:
            return False

        # Check if needs refresh (within 5 min of expiration)
        time_remaining = tokens["expires_at"] - int(time.time())

        if time_remaining > self.REFRESH_THRESHOLD:
            return False

        logger.debug(f"Refreshing tokens for user {telegram_id}")

        try:
            # Refresh tokens via backend
            new_tokens = await backend_api.refresh_tokens(tokens["refresh_token"])

            # Store new tokens
            await self.store(
                telegram_id,
                new_tokens["access_token"],
                new_tokens["refresh_token"],
                new_tokens["expires_in"],
            )

            logger.info(f"Tokens refreshed for user {telegram_id}")
            return True

        except Exception as e:
            logger.warning(f"Failed to refresh tokens for user {telegram_id}: {e}")
            return False

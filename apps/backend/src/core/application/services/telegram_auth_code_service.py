"""Servicio de códigos de autenticación vía Telegram."""

import logging
import random
import string

import redis.asyncio as redis

from src.infrastructure.api_clients.client_telegram_bot import get_telegram_bot_client
from src.shared.config import settings

logger = logging.getLogger(__name__)

# Redis keys
CODE_PREFIX = "auth_code:"
CODE_EXPIRY_SECONDS = 300  # 5 minutes


class TelegramAuthCodeService:
    """
    Servicio para generar y verificar códigos de autenticación vía Telegram.

    Los códigos se almacenan en Redis con expiración automática.
    """

    def __init__(self) -> None:
        self.redis_client: redis.Redis | None = None

    def _get_redis(self) -> redis.Redis:
        """Obtiene cliente Redis."""
        if self.redis_client is None:
            self.redis_client = redis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
            )
        return self.redis_client

    def _generate_code(self) -> str:
        """
        Genera código de 6 dígitos.

        Returns:
            str: Código de 6 dígitos
        """
        return "".join(random.choices(string.digits, k=6))

    def create_code(self, telegram_id: int) -> str:
        """
        Crea código de autenticación para un usuario.

        Args:
            telegram_id: ID de Telegram del usuario

        Returns:
            str: Código generado
        """
        code = self._generate_code()
        r = self._get_redis()

        # Store code with expiry
        key = f"{CODE_PREFIX}{telegram_id}"
        r.setex(key, CODE_EXPIRY_SECONDS, code)

        # Send code via Telegram bot
        bot_client = get_telegram_bot_client()
        bot_client.send_auth_code(telegram_id, code)

        logger.info(f"Auth code created and sent to telegram_id={telegram_id}")
        return code

    def verify_code(self, telegram_id: int, code: str) -> bool:
        """
        Verifica código de autenticación.

        Args:
            telegram_id: ID de Telegram del usuario
            code: Código a verificar

        Returns:
            bool: True si es válido, False si no
        """
        r = self._get_redis()
        key = f"{CODE_PREFIX}{telegram_id}"

        stored_code = r.get(key)

        if stored_code is None:
            logger.warning(f"Code expired or not found for telegram_id={telegram_id}")
            return False

        # Constant-time comparison to prevent timing attacks
        is_valid = stored_code == code

        if is_valid:
            # Delete code after successful verification (one-time use)
            r.delete(key)
            logger.info(f"Code verified for telegram_id={telegram_id}")
        else:
            logger.warning(f"Invalid code for telegram_id={telegram_id}")

        return is_valid

    def delete_code(self, telegram_id: int) -> bool:
        """
        Elimina código de autenticación (útil para logout o retry).

        Args:
            telegram_id: ID de Telegram del usuario

        Returns:
            bool: True si se eliminó, False si no existía
        """
        r = self._get_redis()
        key = f"{CODE_PREFIX}{telegram_id}"
        result = r.delete(key)
        return result > 0


# Singleton instance
_telegram_auth_code_service: TelegramAuthCodeService | None = None


def get_telegram_auth_code_service() -> TelegramAuthCodeService:
    """
    Obtiene instancia singleton del servicio.

    Returns:
        TelegramAuthCodeService: Instancia del servicio
    """
    global _telegram_auth_code_service
    if _telegram_auth_code_service is None:
        _telegram_auth_code_service = TelegramAuthCodeService()
    return _telegram_auth_code_service

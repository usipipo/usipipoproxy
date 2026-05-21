"""Token Storage Port - Contract for token caching."""

from typing import TYPE_CHECKING, Optional, Protocol

if TYPE_CHECKING:
    from .backend_api_port import BackendApiPort


class TokenStoragePort(Protocol):
    """
    Contrato para almacenamiento de tokens en Redis.

    Proporciona caché local de tokens JWT para evitar
    llamadas innecesarias al backend.
    """

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

    async def get(self, telegram_id: int) -> Optional[dict]:
        """
        Recupera tokens del usuario.

        Args:
            telegram_id: ID de Telegram del usuario

        Returns:
            dict con access_token y refresh_token, o None
        """

    async def delete(self, telegram_id: int) -> bool:
        """
        Elimina tokens (unlink).

        Args:
            telegram_id: ID de Telegram del usuario

        Returns:
            True si se eliminó, False si no existía
        """

    async def is_authenticated(self, telegram_id: int) -> bool:
        """
        Verifica si el usuario tiene tokens válidos.

        Args:
            telegram_id: ID de Telegram del usuario

        Returns:
            True si tiene tokens válidos
        """

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

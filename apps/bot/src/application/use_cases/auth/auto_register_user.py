"""AutoRegisterUser Use Case."""

from typing import NamedTuple

from ...ports.backend_api_port import BackendApiPort
from ...ports.token_storage_port import TokenStoragePort


class AutoRegisterUserResult(NamedTuple):
    """Resultado del caso de uso."""

    success: bool
    message: str
    user_id: str


class AutoRegisterUser:
    """
    Caso de uso: Auto-registrar usuario con Telegram ID.

    Flujo:
    1. Llama al backend para auto-registrar usuario
    2. Guarda tokens en Redis
    3. Retorna resultado
    """

    def __init__(
        self,
        backend_api: BackendApiPort,
        token_storage: TokenStoragePort,
    ):
        self.backend_api = backend_api
        self.token_storage = token_storage

    async def execute(self, telegram_id: int) -> AutoRegisterUserResult:
        """
        Ejecuta el caso de uso.

        Args:
            telegram_id: ID de Telegram del usuario

        Returns:
            AutoRegisterUserResult con el resultado

        Raises:
            BackendConnectionError: Si el backend no responde
        """
        # 1. Auto-registrar en backend
        tokens = await self.backend_api.auto_register(telegram_id)

        # 2. Guardar tokens en Redis
        await self.token_storage.store(
            telegram_id,
            tokens["access_token"],
            tokens["refresh_token"],
            tokens["expires_in"],
        )

        # 3. Retornar resultado
        return AutoRegisterUserResult(
            success=True,
            message=(
                "✅ ¡Bienvenido a uSipipo!\n\n"
                "Tu cuenta ha sido creada y estás autenticado.\n\n"
                "Usa /help para ver los comandos disponibles."
            ),
            user_id=tokens.get("user_id", "unknown"),
        )

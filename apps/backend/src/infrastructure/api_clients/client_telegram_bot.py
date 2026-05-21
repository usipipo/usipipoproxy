"""Cliente para enviar mensajes vía Telegram Bot API."""

import logging

import httpx

from src.shared.config import settings

logger = logging.getLogger(__name__)


class TelegramBotClient:
    """
    Cliente para enviar mensajes vía Telegram Bot.

    Usado para enviar códigos de autenticación y notificaciones.
    """

    def __init__(self, bot_token: str | None = None):
        self.bot_token = bot_token or settings.TELEGRAM_TOKEN
        self.base_url = "https://api.telegram.org"
        self.http_client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Obtiene cliente HTTP."""
        if self.http_client is None:
            self.http_client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=30.0,
            )
        return self.http_client

    async def send_message(
        self,
        chat_id: int,
        text: str,
        parse_mode: str = "HTML",
    ) -> bool:
        """
        Envía mensaje a un chat.

        Args:
            chat_id: ID del chat (telegram_id del usuario)
            text: Texto del mensaje
            parse_mode: Modo de parseo (HTML, Markdown, etc.)

        Returns:
            bool: True si se envió, False si falló
        """
        try:
            client = await self._get_client()
            response = await client.post(
                f"/bot{self.bot_token}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": text,
                    "parse_mode": parse_mode,
                },
            )
            response.raise_for_status()
            result = response.json()

            if result.get("ok"):
                logger.info(f"Telegram message sent to chat_id={chat_id}")
                return True
            else:
                logger.error(f"Telegram API error: {result}")
                return False

        except httpx.HTTPError as e:
            logger.error(f"HTTP error sending Telegram message: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending Telegram message: {e}")
            return False

    async def send_auth_code(self, telegram_id: int, code: str) -> bool:
        """
        Envía código de autenticación.

        Args:
            telegram_id: ID de Telegram del usuario
            code: Código de 6 dígitos

        Returns:
            bool: True si se envió, False si falló
        """
        text = (
            f"🔐 <b>Código de Autenticación uSipipo</b>\n\n"
            f"Tu código de verificación es:\n\n"
            f"<b>{code}</b>\n\n"
            f"⏰ Válido por 5 minutos.\n"
            f"⚠️ No compartas este código con nadie."
        )

        return await self.send_message(telegram_id, text)

    async def close(self) -> None:
        """Cierra el cliente HTTP."""
        if self.http_client:
            await self.http_client.aclose()


# Singleton instance
_telegram_bot_client: TelegramBotClient | None = None


def get_telegram_bot_client() -> TelegramBotClient:
    """
    Obtiene instancia singleton del cliente.

    Returns:
        TelegramBotClient: Instancia del cliente
    """
    global _telegram_bot_client
    if _telegram_bot_client is None:
        _telegram_bot_client = TelegramBotClient()
    return _telegram_bot_client

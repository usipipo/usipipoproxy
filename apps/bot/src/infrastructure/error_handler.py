"""
Manejo de errores centralizado para el bot uSipipo Telegram.

Author: uSipipo Team
Version: 1.0.0
"""

from typing import Optional

from telegram import Update
from telegram.ext import ContextTypes

from src.infrastructure.logger import get_logger

logger = get_logger("error_handler")


class BotError(Exception):
    """Excepción base para errores del bot."""

    def __init__(self, message: str, user_message: Optional[str] = None):
        super().__init__(message)
        self.user_message = user_message or "Ocurrió un error. Intenta de nuevo."


class APIError(BotError):
    """Error al comunicarse con el backend API."""

    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(
            message,
            user_message="Error de conexión con el servidor. Intenta más tarde.",
        )
        self.status_code = status_code


class ValidationError(BotError):
    """Error de validación de datos."""

    def __init__(self, message: str):
        super().__init__(message, user_message=message)


async def error_handler(update: Optional[Update], context: ContextTypes.DEFAULT_TYPE) -> None:
    """Maneja errores no capturados en los handlers del bot."""
    error = context.error

    if error is None:
        logger.error("Error desconocido en el bot")
        return

    logger.error(f"Exception while handling an update: {error}", exc_info=error)

    if update and update.effective_message:
        try:
            if isinstance(error, BotError):
                await update.effective_message.reply_text(f"❌ {error.user_message}")
            else:
                await update.effective_message.reply_text(
                    "❌ Ocurrió un error inesperado. Intenta de nuevo."
                )
        except Exception as e:
            logger.error(f"Error al enviar mensaje de error al usuario: {e}")

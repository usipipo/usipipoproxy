"""Custom exceptions for Telegram Bot."""

from typing import Optional


class BotError(Exception):
    """Excepción base del bot."""

    def __init__(self, message: str, original_exception: Optional[Exception] = None):
        super().__init__(message)
        self.message = message
        self.original_exception = original_exception


class AuthenticationError(BotError):
    """
    Error de autenticación.

    Se lanza cuando el usuario no está autenticado o
    los tokens son inválidos.
    """


class BackendConnectionError(BotError):
    """
    Error de conexión con el backend.

    Se lanza cuando no se puede conectar con el backend
    o la respuesta es inválida.
    """


class ValidationError(BotError):
    """
    Error de validación de datos.

    Se lanza cuando los datos de entrada son inválidos.
    """


class NotFoundError(BotError):
    """
    Recurso no encontrado.

    Se lanza cuando el backend retorna 404.
    """


class PermissionDeniedError(BotError):
    """
    Permiso denegado.

    Se lanza cuando el backend retorna 403.
    """


class RateLimitError(BotError):
    """
    Límite de tasa excedido.

    Se lanza cuando el backend retorna 429.
    """

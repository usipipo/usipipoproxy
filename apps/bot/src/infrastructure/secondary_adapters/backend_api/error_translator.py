"""HTTP to Domain Error Translator."""

import logging
from typing import Optional

from ...error_handling.exceptions import (
    BotError,
    AuthenticationError,
    BackendConnectionError,
    ValidationError,
    NotFoundError,
    PermissionDeniedError,
    RateLimitError,
)


logger = logging.getLogger(__name__)


class ErrorTranslator:
    """
    Traduce errores HTTP a mensajes amigables de Telegram.

    Mapea códigos de estado HTTP a excepciones de dominio
    con mensajes apropiados para usuarios de Telegram.
    """

    ERROR_MESSAGES = {
        400: "❌ Solicitud inválida. Verifica los datos e intenta nuevamente.",
        401: "❌ Sesión expirada. Por favor inicia sesión nuevamente.",
        403: "❌ Acceso denegado. No tienes permisos para esta acción.",
        404: "❌ No encontrado. El recurso solicitado no existe.",
        409: "❌ Conflicto. Ya existe un recurso con estos datos.",
        422: "❌ Datos inválidos. Verifica el formato e intenta nuevamente.",
        429: "⏳ Demasiadas solicitudes. Espera unos segundos e intenta nuevamente.",
        500: "❌ Error interno del servidor. Intenta nuevamente más tarde.",
        502: "❌ Servicio no disponible. Intenta nuevamente más tarde.",
        503: "❌ Servicio temporalmente no disponible. Intenta más tarde.",
    }

    @classmethod
    def translate(
        cls,
        status_code: int,
        detail: Optional[str] = None,
        original_exception: Optional[Exception] = None,
    ) -> BotError:
        """
        Traduce error HTTP a excepción de dominio.

        Args:
            status_code: Código de estado HTTP
            detail: Detalle opcional del error
            original_exception: Excepción original (opcional)

        Returns:
            Excepción de dominio apropiada
        """
        # Client errors (4xx)
        if status_code == 400:
            return ValidationError(
                cls.ERROR_MESSAGES[400],
                original_exception,
            )
        elif status_code == 401:
            return AuthenticationError(
                cls.ERROR_MESSAGES[401],
                original_exception,
            )
        elif status_code == 403:
            return PermissionDeniedError(
                cls.ERROR_MESSAGES[403],
                original_exception,
            )
        elif status_code == 404:
            return NotFoundError(
                cls.ERROR_MESSAGES[404],
                original_exception,
            )
        elif status_code == 409:
            return ValidationError(
                cls.ERROR_MESSAGES[409],
                original_exception,
            )
        elif status_code == 422:
            return ValidationError(
                cls.ERROR_MESSAGES[422],
                original_exception,
            )
        elif status_code == 429:
            return RateLimitError(
                cls.ERROR_MESSAGES[429],
                original_exception,
            )

        # Server errors (5xx)
        elif status_code >= 500:
            # Log detailed error for server errors
            logger.error(
                f"Backend server error {status_code}: {detail or 'No detail'}",
                exc_info=original_exception,
            )
            return BackendConnectionError(
                cls.ERROR_MESSAGES.get(
                    status_code,
                    f"❌ Error inesperado (código {status_code}). Intenta nuevamente.",
                ),
                original_exception,
            )

        # Unknown errors
        else:
            return BotError(
                f"❌ Error inesperado (código {status_code}). Intenta nuevamente.",
                original_exception,
            )

    @classmethod
    def translate_connection_error(
        cls,
        original_exception: Exception,
    ) -> BackendConnectionError:
        """
        Traduce error de conexión a excepción de dominio.

        Args:
            original_exception: Excepción original (httpx.ConnectError, etc.)

        Returns:
            BackendConnectionError
        """
        return BackendConnectionError(
            "❌ No se pudo conectar con el backend. Verifica tu conexión e intenta nuevamente.",
            original_exception,
        )

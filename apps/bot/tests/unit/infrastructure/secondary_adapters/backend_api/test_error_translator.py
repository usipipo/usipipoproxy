"""Tests for ErrorTranslator."""

from src.infrastructure.secondary_adapters.backend_api.error_translator import (
    ErrorTranslator,
)
from src.infrastructure.error_handling.exceptions import (
    AuthenticationError,
    BackendConnectionError,
    NotFoundError,
    PermissionDeniedError,
    RateLimitError,
    ValidationError,
)


def test_translate_400_validation_error():
    """Test de traducción de error 400."""
    error = ErrorTranslator.translate(400)
    assert isinstance(error, ValidationError)
    assert "Solicitud inválida" in error.message


def test_translate_401_authentication_error():
    """Test de traducción de error 401."""
    error = ErrorTranslator.translate(401)
    assert isinstance(error, AuthenticationError)
    assert "Sesión expirada" in error.message


def test_translate_403_permission_denied():
    """Test de traducción de error 403."""
    error = ErrorTranslator.translate(403)
    assert isinstance(error, PermissionDeniedError)
    assert "Acceso denegado" in error.message


def test_translate_404_not_found():
    """Test de traducción de error 404."""
    error = ErrorTranslator.translate(404)
    assert isinstance(error, NotFoundError)
    assert "No encontrado" in error.message


def test_translate_429_rate_limit():
    """Test de traducción de error 429."""
    error = ErrorTranslator.translate(429)
    assert isinstance(error, RateLimitError)
    assert "Demasiadas solicitudes" in error.message


def test_translate_500_server_error():
    """Test de traducción de error 500."""
    error = ErrorTranslator.translate(500)
    assert isinstance(error, BackendConnectionError)
    assert "Error interno" in error.message


def test_translate_with_detail():
    """Test de traducción con detalle."""
    error = ErrorTranslator.translate(400, detail="Email inválido")
    assert isinstance(error, ValidationError)
    # El mensaje base se muestra
    assert "Solicitud inválida" in error.message


def test_translate_unknown_error():
    """Test de traducción de error desconocido."""
    error = ErrorTranslator.translate(418)  # I'm a teapot
    assert isinstance(error, Exception)
    assert "418" in str(error)


def test_translate_connection_error():
    """Test de traducción de error de conexión."""
    original = ConnectionError("Network unreachable")
    error = ErrorTranslator.translate_connection_error(original)
    assert isinstance(error, BackendConnectionError)
    assert "No se pudo conectar" in error.message
    assert error.original_exception is original

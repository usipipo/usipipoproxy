"""Tests for custom exceptions."""

from src.infrastructure.error_handling.exceptions import (
    BotError,
    AuthenticationError,
    BackendConnectionError,
    ValidationError,
    NotFoundError,
    PermissionDeniedError,
    RateLimitError,
)


def test_bot_error_basic():
    """Test básico de BotError."""
    error = BotError("Test message")
    assert str(error) == "Test message"
    assert error.message == "Test message"
    assert error.original_exception is None


def test_bot_error_with_original():
    """Test de BotError con excepción original."""
    original = ValueError("Original error")
    error = BotError("Test message", original)
    assert error.message == "Test message"
    assert error.original_exception is original


def test_authentication_error():
    """Test de AuthenticationError."""
    error = AuthenticationError("Not authenticated")
    assert isinstance(error, BotError)
    assert "Not authenticated" in str(error)


def test_backend_connection_error():
    """Test de BackendConnectionError."""
    error = BackendConnectionError("Backend unavailable")
    assert isinstance(error, BotError)


def test_validation_error():
    """Test de ValidationError."""
    error = ValidationError("Invalid data")
    assert isinstance(error, BotError)


def test_not_found_error():
    """Test de NotFoundError."""
    error = NotFoundError("Resource not found")
    assert isinstance(error, BotError)


def test_permission_denied_error():
    """Test de PermissionDeniedError."""
    error = PermissionDeniedError("Access denied")
    assert isinstance(error, BotError)


def test_rate_limit_error():
    """Test de RateLimitError."""
    error = RateLimitError("Too many requests")
    assert isinstance(error, BotError)

"""Tests for logger and error handler."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from src.infrastructure.logger import setup_logger, get_logger
from src.infrastructure.error_handler import BotError, APIError, ValidationError, error_handler


class TestLogger:
    """Test logger setup and retrieval."""

    def test_setup_logger_returns_logger(self):
        """Test setup_logger returns a logger instance."""
        logger = setup_logger("test-logger")
        assert logger is not None
        assert logger.name == "test-logger"

    def test_setup_logger_with_level(self):
        """Test setup_logger with custom level."""
        logger = setup_logger("test-debug", level="DEBUG")
        assert logger.level == 10  # DEBUG = 10

    def test_get_logger_default(self):
        """Test get_logger returns default logger."""
        logger = get_logger()
        assert logger is not None

    def test_get_logger_with_name(self):
        """Test get_logger with custom name."""
        logger = get_logger("custom")
        assert logger is not None


class TestBotErrors:
    """Test custom error classes."""

    def test_bot_error_default_message(self):
        """Test BotError has default user message."""
        error = BotError("internal error")
        assert str(error) == "internal error"
        assert error.user_message == "Ocurrió un error. Intenta de nuevo."

    def test_bot_error_custom_user_message(self):
        """Test BotError with custom user message."""
        error = BotError("internal", user_message="Custom message")
        assert error.user_message == "Custom message"

    def test_api_error(self):
        """Test APIError initialization."""
        error = APIError("connection failed", status_code=500)
        assert error.status_code == 500
        assert "servidor" in error.user_message.lower()

    def test_validation_error(self):
        """Test ValidationError initialization."""
        error = ValidationError("Invalid input")
        assert error.user_message == "Invalid input"


class TestErrorHandler:
    """Test error handler function."""

    @pytest.mark.asyncio
    async def test_error_handler_with_bot_error(self):
        """Test error handler sends user-friendly message for BotError."""
        mock_update = MagicMock()
        mock_update.effective_message = MagicMock()
        mock_update.effective_message.reply_text = AsyncMock()

        mock_context = MagicMock()
        mock_context.error = BotError("internal", user_message="Error personalizado")

        await error_handler(mock_update, mock_context)

        mock_update.effective_message.reply_text.assert_called_once()
        call_args = mock_update.effective_message.reply_text.call_args[0][0]
        assert "Error personalizado" in call_args

    @pytest.mark.asyncio
    async def test_error_handler_with_generic_error(self):
        """Test error handler sends generic message for unknown errors."""
        mock_update = MagicMock()
        mock_update.effective_message = MagicMock()
        mock_update.effective_message.reply_text = AsyncMock()

        mock_context = MagicMock()
        mock_context.error = ValueError("some error")

        await error_handler(mock_update, mock_context)

        mock_update.effective_message.reply_text.assert_called_once()

    @pytest.mark.asyncio
    async def test_error_handler_with_no_error(self):
        """Test error handler does nothing when no error."""
        mock_context = MagicMock()
        mock_context.error = None

        # Should not raise
        await error_handler(None, mock_context)

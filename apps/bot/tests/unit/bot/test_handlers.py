"""Tests for bot handlers."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from src.bot.handlers.basic import BasicHandler
from src.bot.keyboards.main import BasicMessages


class TestBasicHandler:
    """Test BasicHandler class."""

    @pytest.fixture
    def handler(self):
        """Create handler instance."""
        return BasicHandler()

    @pytest.mark.asyncio
    async def test_start_handler_sends_welcome_message(self, handler):
        """Test start_handler sends welcome message."""
        mock_update = MagicMock()
        mock_update.effective_user = MagicMock(id=123)
        mock_update.message = MagicMock()
        mock_update.message.reply_text = AsyncMock()

        await handler.start_handler(mock_update, None)

        mock_update.message.reply_text.assert_called_once()
        call_args = mock_update.message.reply_text.call_args
        assert BasicMessages.START_TEXT in call_args[1].get("text", "")

    @pytest.mark.asyncio
    async def test_help_handler_sends_help_message(self, handler):
        """Test help_handler sends help message."""
        mock_update = MagicMock()
        mock_update.effective_user = MagicMock(id=123)
        mock_update.message = MagicMock()
        mock_update.message.reply_text = AsyncMock()

        await handler.help_handler(mock_update, None)

        # Help handler sends 2 messages: HELP_TEXT and SUPPORT_HELP
        assert mock_update.message.reply_text.call_count == 2

        # First call should be HELP_TEXT
        first_call_args = mock_update.message.reply_text.call_args_list[0]
        assert BasicMessages.HELP_TEXT in first_call_args[1].get("text", "")

        # Second call should be SUPPORT_HELP
        second_call_args = mock_update.message.reply_text.call_args_list[1]
        assert BasicMessages.SUPPORT_HELP in second_call_args[1].get("text", "")


class TestBasicMessages:
    """Test BasicMessages constants."""

    def test_start_text_defined(self):
        """Test START_TEXT is defined."""
        assert hasattr(BasicMessages, "START_TEXT")
        assert BasicMessages.START_TEXT is not None
        assert len(BasicMessages.START_TEXT) > 0

    def test_help_text_defined(self):
        """Test HELP_TEXT is defined."""
        assert hasattr(BasicMessages, "HELP_TEXT")
        assert BasicMessages.HELP_TEXT is not None
        assert len(BasicMessages.HELP_TEXT) > 0

    def test_start_text_contains_welcome(self):
        """Test START_TEXT contains welcome message."""
        assert (
            "bienvenido" in BasicMessages.START_TEXT.lower()
            or "welcome" in BasicMessages.START_TEXT.lower()
        )

    def test_help_text_contains_commands(self):
        """Test HELP_TEXT contains command list."""
        assert "/start" in BasicMessages.HELP_TEXT
        assert "/help" in BasicMessages.HELP_TEXT

"""Tests para Operations Handlers."""

import pytest
from unittest.mock import patch, AsyncMock


class TestOperationsHandler:
    """Tests para OperationsHandler."""

    @pytest.mark.asyncio
    async def test_operations_handler_initialization(self):
        """OperationsHandler se inicializa correctamente."""
        with (
            patch("src.bot.handlers.operations.APIClient"),
            patch("src.bot.handlers.operations.TokenStorage"),
        ):
            from src.bot.handlers.operations import OperationsHandler

            mock_api = AsyncMock()
            mock_storage = AsyncMock()

            handler = OperationsHandler(mock_api, mock_storage)

            assert handler.api == mock_api
            assert handler.tokens == mock_storage

    @pytest.mark.asyncio
    async def test_operations_messages_constants_exist(self):
        """OperationsMessages constants están definidas."""
        from src.bot.keyboards.messages_operations import OperationsMessages

        assert hasattr(OperationsMessages, "Menu")
        assert hasattr(OperationsMessages, "Credits")
        assert hasattr(OperationsMessages, "Shop")
        assert hasattr(OperationsMessages, "Transactions")
        assert hasattr(OperationsMessages, "Referrals")

    @pytest.mark.asyncio
    async def test_operations_messages_has_menu_messages(self):
        """OperationsMessages tiene mensajes de menú."""
        from src.bot.keyboards.messages_operations import OperationsMessages

        assert hasattr(OperationsMessages.Menu, "MAIN")
        assert hasattr(OperationsMessages.Menu, "MAIN_WITH_CREDITS")

    @pytest.mark.asyncio
    async def test_operations_messages_has_credits_messages(self):
        """OperationsMessages tiene mensajes de créditos."""
        from src.bot.keyboards.messages_operations import OperationsMessages

        assert hasattr(OperationsMessages.Credits, "DISPLAY")
        assert hasattr(OperationsMessages.Credits, "REDEEM_SUCCESS")
        assert hasattr(OperationsMessages.Credits, "INSUFFICIENT_CREDITS")

    @pytest.mark.asyncio
    async def test_operations_messages_has_shop_messages(self):
        """OperationsMessages tiene mensajes de tienda."""
        from src.bot.keyboards.messages_operations import OperationsMessages

        assert hasattr(OperationsMessages.Shop, "WELCOME")
        assert hasattr(OperationsMessages.Shop, "ITEMS_LIST")

    @pytest.mark.asyncio
    async def test_operations_messages_has_transactions_messages(self):
        """OperationsMessages tiene mensajes de transacciones."""
        from src.bot.keyboards.messages_operations import OperationsMessages

        assert hasattr(OperationsMessages.Transactions, "HISTORY_HEADER")
        assert hasattr(OperationsMessages.Transactions, "NO_TRANSACTIONS")
        assert hasattr(OperationsMessages.Transactions, "TRANSACTION_ITEM")

    @pytest.mark.asyncio
    async def test_operations_messages_has_referrals_messages(self):
        """OperationsMessages tiene mensajes de referidos."""
        from src.bot.keyboards.messages_operations import OperationsMessages

        assert hasattr(OperationsMessages.Referrals, "MENU")

    @pytest.mark.asyncio
    async def test_operations_messages_has_error_messages(self):
        """OperationsMessages tiene mensajes de error."""
        from src.bot.keyboards.messages_operations import OperationsMessages

        assert hasattr(OperationsMessages.Error, "SYSTEM_ERROR")
        assert hasattr(OperationsMessages.Error, "OPERATION_FAILED")
        assert hasattr(OperationsMessages.Error, "INVALID_OPTION")

    @pytest.mark.asyncio
    async def test_operations_messages_has_success_messages(self):
        """OperationsMessages tiene mensajes de éxito."""
        from src.bot.keyboards.messages_operations import OperationsMessages

        assert hasattr(OperationsMessages.Success, "OPERATION_COMPLETED")
        assert hasattr(OperationsMessages.Success, "CHANGES_SAVED")

    @pytest.mark.asyncio
    async def test_operations_messages_main_menu_has_placeholder(self):
        """El mensaje del menú principal tiene placeholder."""
        from src.bot.keyboards.messages_operations import OperationsMessages

        assert "{credits}" in OperationsMessages.Menu.MAIN_WITH_CREDITS

    @pytest.mark.asyncio
    async def test_operations_keyboard_main_menu_exists(self):
        """OperationsKeyboard.operations_menu existe."""
        from src.bot.keyboards.operations import OperationsKeyboard

        assert hasattr(OperationsKeyboard, "operations_menu")
        assert callable(getattr(OperationsKeyboard, "operations_menu"))

    @pytest.mark.asyncio
    async def test_operations_keyboard_main_menu_returns_inline_keyboard(self):
        """operations_menu retorna InlineKeyboardMarkup."""
        from telegram import InlineKeyboardMarkup
        from src.bot.keyboards.operations import OperationsKeyboard

        keyboard = OperationsKeyboard.operations_menu(credits=0)

        assert isinstance(keyboard, InlineKeyboardMarkup)

    @pytest.mark.asyncio
    async def test_operations_keyboard_main_menu_with_credits(self):
        """operations_menu muestra créditos correctamente."""
        from src.bot.keyboards.operations import OperationsKeyboard

        keyboard = OperationsKeyboard.operations_menu(credits=100)

        buttons = keyboard.inline_keyboard
        # Should have credits button with value
        assert any("Créditos (100)" in btn.text for row in buttons for btn in row)

    @pytest.mark.asyncio
    async def test_operations_keyboard_credits_menu_exists(self):
        """OperationsKeyboard.credits_menu existe."""
        from src.bot.keyboards.operations import OperationsKeyboard

        keyboard = OperationsKeyboard.credits_menu(credits=50)

        from telegram import InlineKeyboardMarkup

        assert isinstance(keyboard, InlineKeyboardMarkup)

    @pytest.mark.asyncio
    async def test_operations_keyboard_shop_menu_exists(self):
        """OperationsKeyboard.shop_menu existe."""
        from src.bot.keyboards.operations import OperationsKeyboard

        keyboard = OperationsKeyboard.shop_menu()

        from telegram import InlineKeyboardMarkup

        assert isinstance(keyboard, InlineKeyboardMarkup)

    @pytest.mark.asyncio
    async def test_operations_keyboard_transactions_history_exists(self):
        """OperationsKeyboard.transactions_history_menu existe."""
        from src.bot.keyboards.operations import OperationsKeyboard

        keyboard = OperationsKeyboard.transactions_history_menu(has_more=False, page=0)

        from telegram import InlineKeyboardMarkup

        assert isinstance(keyboard, InlineKeyboardMarkup)

    @pytest.mark.asyncio
    async def test_operations_keyboard_back_to_operations_exists(self):
        """OperationsKeyboard.back_to_operations existe."""
        from src.bot.keyboards.operations import OperationsKeyboard

        keyboard = OperationsKeyboard.back_to_operations()

        from telegram import InlineKeyboardMarkup

        assert isinstance(keyboard, InlineKeyboardMarkup)

    @pytest.mark.asyncio
    async def test_operations_handler_get_auth_headers(self):
        """_get_auth_headers retorna headers con token."""
        with (
            patch("src.bot.handlers.operations.APIClient"),
            patch("src.bot.handlers.operations.TokenStorage"),
        ):
            from src.bot.handlers.operations import OperationsHandler

            mock_api = AsyncMock()
            mock_storage = AsyncMock()
            mock_storage.get.return_value = {"access_token": "test-token-123"}

            handler = OperationsHandler(mock_api, mock_storage)

            headers = await handler._get_auth_headers(telegram_id=123)

            assert "Authorization" in headers
            assert headers["Authorization"] == "Bearer test-token-123"

    @pytest.mark.asyncio
    async def test_operations_handler_get_auth_headers_unauthenticated(self):
        """_get_auth_headers lanza error si no está autenticado."""
        with (
            patch("src.bot.handlers.operations.APIClient"),
            patch("src.bot.handlers.operations.TokenStorage"),
        ):
            from src.bot.handlers.operations import OperationsHandler

            mock_api = AsyncMock()
            mock_storage = AsyncMock()
            mock_storage.get.return_value = None

            handler = OperationsHandler(mock_api, mock_storage)

            with pytest.raises(PermissionError):
                await handler._get_auth_headers(telegram_id=123)

    @pytest.mark.asyncio
    async def test_get_operations_handlers_returns_list(self):
        """get_operations_handlers retorna una lista."""
        with (
            patch("src.bot.handlers.operations.APIClient"),
            patch("src.bot.handlers.operations.TokenStorage"),
        ):
            from src.bot.handlers.operations import get_operations_handlers

            mock_api = AsyncMock()
            mock_storage = AsyncMock()

            handlers = get_operations_handlers(mock_api, mock_storage)

            assert isinstance(handlers, list)
            assert len(handlers) > 0

    @pytest.mark.asyncio
    async def test_get_operations_callback_handlers_returns_list(self):
        """get_operations_callback_handlers retorna una lista."""
        with (
            patch("src.bot.handlers.operations.APIClient"),
            patch("src.bot.handlers.operations.TokenStorage"),
        ):
            from src.bot.handlers.operations import get_operations_callback_handlers

            mock_api = AsyncMock()
            mock_storage = AsyncMock()

            handlers = get_operations_callback_handlers(mock_api, mock_storage)

            assert isinstance(handlers, list)
            assert len(handlers) > 0

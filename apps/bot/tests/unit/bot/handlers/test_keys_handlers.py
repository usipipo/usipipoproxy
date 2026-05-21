"""Tests para VPN Keys Handlers."""

import pytest
from unittest.mock import patch, AsyncMock


class TestKeysHandler:
    """Tests para KeysHandler."""

    @pytest.mark.asyncio
    async def test_keys_handler_initialization(self):
        """KeysHandler se inicializa correctamente."""
        with patch("src.bot.handlers.keys.APIClient"), patch("src.bot.handlers.keys.TokenStorage"):
            from src.bot.handlers.keys import KeysHandler

            mock_api = AsyncMock()
            mock_storage = AsyncMock()

            handler = KeysHandler(mock_api, mock_storage)

            assert handler.api == mock_api
            assert handler.tokens == mock_storage

    @pytest.mark.asyncio
    async def test_keys_messages_constants_exist(self):
        """KeysMessages constants están definidas."""
        from src.bot.keyboards.messages_keys import KeysMessages

        assert hasattr(KeysMessages, "MAIN_MENU")
        assert hasattr(KeysMessages, "NO_KEYS")
        assert hasattr(KeysMessages, "KEY_DETAILS")
        assert hasattr(KeysMessages, "KEY_NOT_FOUND")

    @pytest.mark.asyncio
    async def test_keys_messages_has_action_messages(self):
        """KeysMessages tiene mensajes de acciones."""
        from src.bot.keyboards.messages_keys import KeysMessages

        assert hasattr(KeysMessages.Actions, "KEY_SUSPENDED")
        assert hasattr(KeysMessages.Actions, "KEY_REACTIVATED")
        assert hasattr(KeysMessages.Actions, "KEY_DELETED")
        assert hasattr(KeysMessages.Actions, "KEY_RENAMED")
        assert hasattr(KeysMessages.Actions, "KEY_CREATED")

    @pytest.mark.asyncio
    async def test_keys_messages_has_error_messages(self):
        """KeysMessages tiene mensajes de error."""
        from src.bot.keyboards.messages_keys import KeysMessages

        assert hasattr(KeysMessages.Error, "SYSTEM_ERROR")
        assert hasattr(KeysMessages.Error, "KEY_NOT_ACCESSIBLE")
        assert hasattr(KeysMessages.Error, "OPERATION_FAILED")
        assert hasattr(KeysMessages.Error, "MAX_KEYS_REACHED")

    @pytest.mark.asyncio
    async def test_keys_messages_has_success_messages(self):
        """KeysMessages tiene mensajes de éxito."""
        from src.bot.keyboards.messages_keys import KeysMessages

        assert hasattr(KeysMessages.Success, "OPERATION_COMPLETED")
        assert hasattr(KeysMessages.Success, "CHANGES_SAVED")

    @pytest.mark.asyncio
    async def test_keys_messages_main_menu_has_placeholders(self):
        """El mensaje del menú principal tiene placeholders."""
        from src.bot.keyboards.messages_keys import KeysMessages

        assert "{total_keys}" in KeysMessages.MAIN_MENU
        assert "{outline_count}" in KeysMessages.MAIN_MENU
        assert "{wireguard_count}" in KeysMessages.MAIN_MENU
        assert "{trusttunnel_count}" in KeysMessages.MAIN_MENU

    @pytest.mark.asyncio
    async def test_keys_messages_key_details_has_placeholders(self):
        """El mensaje de detalles de clave tiene placeholders."""
        from src.bot.keyboards.messages_keys import KeysMessages

        assert "{name}" in KeysMessages.KEY_DETAILS
        assert "{type}" in KeysMessages.KEY_DETAILS
        assert "{usage}" in KeysMessages.KEY_DETAILS
        assert "{limit}" in KeysMessages.KEY_DETAILS
        assert "{status}" in KeysMessages.KEY_DETAILS

    @pytest.mark.asyncio
    async def test_keys_keyboard_main_menu_exists(self):
        """KeysKeyboard.main_menu existe."""
        from src.bot.keyboards.keys import KeysKeyboard

        assert hasattr(KeysKeyboard, "main_menu")
        assert callable(getattr(KeysKeyboard, "main_menu"))

    @pytest.mark.asyncio
    async def test_keys_keyboard_main_menu_returns_inline_keyboard(self):
        """main_menu retorna InlineKeyboardMarkup."""
        from telegram import InlineKeyboardMarkup
        from src.bot.keyboards.keys import KeysKeyboard

        keyboard = KeysKeyboard.main_menu(total_keys=0, outline_count=0, wireguard_count=0)

        assert isinstance(keyboard, InlineKeyboardMarkup)

    @pytest.mark.asyncio
    async def test_keys_keyboard_main_menu_with_no_keys(self):
        """main_menu con 0 claves muestra opción de crear."""
        from src.bot.keyboards.keys import KeysKeyboard

        keyboard = KeysKeyboard.main_menu(total_keys=0, outline_count=0, wireguard_count=0)

        buttons = keyboard.inline_keyboard
        # Should have "Crear Nueva Clave" button
        assert any("Crear" in btn.text for row in buttons for btn in row)

    @pytest.mark.asyncio
    async def test_keys_keyboard_main_menu_with_keys(self):
        """main_menu con claves muestra opciones por tipo."""
        from src.bot.keyboards.keys import KeysKeyboard

        keyboard = KeysKeyboard.main_menu(total_keys=2, outline_count=1, wireguard_count=1)

        buttons = keyboard.inline_keyboard
        # Should have Outline and WireGuard buttons
        assert any("Outline" in btn.text for row in buttons for btn in row)
        assert any("WireGuard" in btn.text for row in buttons for btn in row)

    @pytest.mark.asyncio
    async def test_keys_keyboard_keys_list_exists(self):
        """KeysKeyboard.keys_list existe."""
        from src.bot.keyboards.keys import KeysKeyboard

        keys = [
            {"id": "uuid-1", "name": "Test Key", "status": "active"},
        ]
        keyboard = KeysKeyboard.keys_list(keys, key_type="outline")

        from telegram import InlineKeyboardMarkup

        assert isinstance(keyboard, InlineKeyboardMarkup)

    @pytest.mark.asyncio
    async def test_keys_keyboard_key_actions_exists(self):
        """KeysKeyboard.key_actions existe."""
        from src.bot.keyboards.keys import KeysKeyboard

        keyboard = KeysKeyboard.key_actions(key_id="uuid-1", is_active=True, key_type="wireguard")

        from telegram import InlineKeyboardMarkup

        assert isinstance(keyboard, InlineKeyboardMarkup)

    @pytest.mark.asyncio
    async def test_keys_keyboard_key_actions_wireguard_has_download(self):
        """key_actions para WireGuard muestra descarga de config."""
        from src.bot.keyboards.keys import KeysKeyboard

        keyboard = KeysKeyboard.key_actions(key_id="uuid-1", is_active=True, key_type="wireguard")

        buttons = keyboard.inline_keyboard
        assert any("Descargar" in btn.text or "📥" in btn.text for row in buttons for btn in row)

    @pytest.mark.asyncio
    async def test_keys_keyboard_key_actions_outline_has_link(self):
        """key_actions para Outline muestra enlace de acceso."""
        from src.bot.keyboards.keys import KeysKeyboard

        keyboard = KeysKeyboard.key_actions(key_id="uuid-1", is_active=True, key_type="outline")

        buttons = keyboard.inline_keyboard
        assert any(
            "Clave de Acceso" in btn.text or "🔗" in btn.text for row in buttons for btn in row
        )

    @pytest.mark.asyncio
    async def test_keys_keyboard_confirm_delete_exists(self):
        """KeysKeyboard.confirm_delete existe."""
        from src.bot.keyboards.keys import KeysKeyboard

        keyboard = KeysKeyboard.confirm_delete(key_id="uuid-1")

        from telegram import InlineKeyboardMarkup

        assert isinstance(keyboard, InlineKeyboardMarkup)

        buttons = keyboard.inline_keyboard
        assert any("Eliminar" in btn.text for row in buttons for btn in row)
        assert any("Cancelar" in btn.text for row in buttons for btn in row)

    @pytest.mark.asyncio
    async def test_keys_keyboard_cancel_rename_exists(self):
        """KeysKeyboard.cancel_rename existe."""
        from src.bot.keyboards.keys import KeysKeyboard

        keyboard = KeysKeyboard.cancel_rename()

        from telegram import InlineKeyboardMarkup

        assert isinstance(keyboard, InlineKeyboardMarkup)

    @pytest.mark.asyncio
    async def test_keys_keyboard_back_to_menu_exists(self):
        """KeysKeyboard.back_to_menu existe."""
        from src.bot.keyboards.keys import KeysKeyboard

        keyboard = KeysKeyboard.back_to_menu()

        from telegram import InlineKeyboardMarkup

        assert isinstance(keyboard, InlineKeyboardMarkup)

    @pytest.mark.asyncio
    async def test_keys_handler_get_auth_headers(self):
        """_get_auth_headers retorna headers con token."""
        with patch("src.bot.handlers.keys.APIClient"), patch("src.bot.handlers.keys.TokenStorage"):
            from src.bot.handlers.keys import KeysHandler

            mock_api = AsyncMock()
            mock_storage = AsyncMock()
            mock_storage.get.return_value = {"access_token": "test-token-123"}

            handler = KeysHandler(mock_api, mock_storage)

            headers = await handler._get_auth_headers(telegram_id=123)

            assert "Authorization" in headers
            assert headers["Authorization"] == "Bearer test-token-123"

    @pytest.mark.asyncio
    async def test_keys_handler_get_auth_headers_unauthenticated(self):
        """_get_auth_headers lanza error si no está autenticado."""
        with patch("src.bot.handlers.keys.APIClient"), patch("src.bot.handlers.keys.TokenStorage"):
            from src.bot.handlers.keys import KeysHandler

            mock_api = AsyncMock()
            mock_storage = AsyncMock()
            mock_storage.get.return_value = None

            handler = KeysHandler(mock_api, mock_storage)

            with pytest.raises(PermissionError):
                await handler._get_auth_headers(telegram_id=123)

    @pytest.mark.asyncio
    async def test_keys_handler_progress_bar_generation(self):
        """_generate_progress_bar genera barra correcta."""
        with patch("src.bot.handlers.keys.APIClient"), patch("src.bot.handlers.keys.TokenStorage"):
            from src.bot.handlers.keys import KeysHandler

            mock_api = AsyncMock()
            mock_storage = AsyncMock()

            handler = KeysHandler(mock_api, mock_storage)

            bar = handler._generate_progress_bar(50.0, width=10)

            # Format is "█████░░░░░ 50%" (bar + space + percentage)
            assert "50%" in bar
            assert "█" in bar
            assert "░" in bar

    @pytest.mark.asyncio
    async def test_keys_handler_progress_bar_full(self):
        """_generate_progress_bar con 100% está llena."""
        with patch("src.bot.handlers.keys.APIClient"), patch("src.bot.handlers.keys.TokenStorage"):
            from src.bot.handlers.keys import KeysHandler

            mock_api = AsyncMock()
            mock_storage = AsyncMock()

            handler = KeysHandler(mock_api, mock_storage)

            bar = handler._generate_progress_bar(100.0, width=10)

            assert bar == "██████████ 100%"

    @pytest.mark.asyncio
    async def test_keys_handler_progress_bar_empty(self):
        """_generate_progress_bar con 0% está vacía."""
        with patch("src.bot.handlers.keys.APIClient"), patch("src.bot.handlers.keys.TokenStorage"):
            from src.bot.handlers.keys import KeysHandler

            mock_api = AsyncMock()
            mock_storage = AsyncMock()

            handler = KeysHandler(mock_api, mock_storage)

            bar = handler._generate_progress_bar(0.0, width=10)

            assert bar == "░░░░░░░░░░ 0%"

    @pytest.mark.asyncio
    async def test_get_keys_handlers_returns_list(self):
        """get_keys_handlers retorna una lista."""
        with patch("src.bot.handlers.keys.APIClient"), patch("src.bot.handlers.keys.TokenStorage"):
            from src.bot.handlers.keys import get_keys_handlers

            mock_api = AsyncMock()
            mock_storage = AsyncMock()

            handlers = get_keys_handlers(mock_api, mock_storage)

            assert isinstance(handlers, list)
            assert len(handlers) > 0

    @pytest.mark.asyncio
    async def test_get_keys_callback_handlers_returns_list(self):
        """get_keys_callback_handlers retorna una lista."""
        with patch("src.bot.handlers.keys.APIClient"), patch("src.bot.handlers.keys.TokenStorage"):
            from src.bot.handlers.keys import get_keys_callback_handlers

            mock_api = AsyncMock()
            mock_storage = AsyncMock()

            handlers = get_keys_callback_handlers(mock_api, mock_storage)

            assert isinstance(handlers, list)
            assert len(handlers) > 0

"""Tests para Data Packages Handlers."""

import pytest
from unittest.mock import patch, AsyncMock


class TestPackagesHandler:
    """Tests para PackagesHandler."""

    @pytest.mark.asyncio
    async def test_packages_handler_initialization(self):
        """PackagesHandler se inicializa correctamente."""
        with (
            patch("src.bot.handlers.packages.APIClient"),
            patch("src.bot.handlers.packages.TokenStorage"),
        ):
            from src.bot.handlers.packages import PackagesHandler

            mock_api = AsyncMock()
            mock_storage = AsyncMock()

            handler = PackagesHandler(mock_api, mock_storage)

            assert handler.api == mock_api
            assert handler.tokens == mock_storage

    @pytest.mark.asyncio
    async def test_packages_messages_constants_exist(self):
        """PackagesMessages constants están definidas."""
        from src.bot.keyboards.messages_packages import PackagesMessages

        assert hasattr(PackagesMessages, "Menu")
        assert hasattr(PackagesMessages, "Payment")
        assert hasattr(PackagesMessages, "Summary")
        assert hasattr(PackagesMessages, "Slots")
        assert hasattr(PackagesMessages, "Error")

    @pytest.mark.asyncio
    async def test_packages_messages_has_menu_messages(self):
        """PackagesMessages tiene mensajes de menú."""
        from src.bot.keyboards.messages_packages import PackagesMessages

        assert hasattr(PackagesMessages.Menu, "PACKAGES_LIST")
        assert hasattr(PackagesMessages.Menu, "PACKAGE_ITEM")
        assert hasattr(PackagesMessages.Menu, "PACKAGE_DETAILS")
        assert hasattr(PackagesMessages.Menu, "NO_PACKAGES")
        assert hasattr(PackagesMessages.Menu, "INVALID_PACKAGE")

    @pytest.mark.asyncio
    async def test_packages_messages_has_payment_messages(self):
        """PackagesMessages tiene mensajes de pago."""
        from src.bot.keyboards.messages_packages import PackagesMessages

        assert hasattr(PackagesMessages.Payment, "SELECT_METHOD")
        assert hasattr(PackagesMessages.Payment, "STARS_PAYMENT_SENT")
        assert hasattr(PackagesMessages.Payment, "STARS_SUCCESS")
        assert hasattr(PackagesMessages.Payment, "STARS_FAILED")
        assert hasattr(PackagesMessages.Payment, "CRYPTO_PAYMENT")
        assert hasattr(PackagesMessages.Payment, "CRYPTO_PENDING")
        assert hasattr(PackagesMessages.Payment, "CRYPTO_SUCCESS")
        assert hasattr(PackagesMessages.Payment, "CRYPTO_EXPIRED")
        assert hasattr(PackagesMessages.Payment, "CRYPTO_PAYMENT_FAILED")

    @pytest.mark.asyncio
    async def test_packages_messages_has_summary_messages(self):
        """PackagesMessages tiene mensajes de resumen."""
        from src.bot.keyboards.messages_packages import PackagesMessages

        assert hasattr(PackagesMessages.Summary, "DATA_SUMMARY")
        assert hasattr(PackagesMessages.Summary, "NO_ACTIVE_PACKAGES")

    @pytest.mark.asyncio
    async def test_packages_messages_has_slots_messages(self):
        """PackagesMessages tiene mensajes de slots."""
        from src.bot.keyboards.messages_packages import PackagesMessages

        assert hasattr(PackagesMessages.Slots, "SLOTS_HEADER")
        assert hasattr(PackagesMessages.Slots, "SLOT_ITEM")
        assert hasattr(PackagesMessages.Slots, "NO_SLOTS")
        assert hasattr(PackagesMessages.Slots, "BUY_SLOT_PROMPT")
        assert hasattr(PackagesMessages.Slots, "SLOT_PURCHASED")
        assert hasattr(PackagesMessages.Slots, "SLOT_PURCHASE_FAILED")
        assert hasattr(PackagesMessages.Slots, "MAX_SLOTS_REACHED")

    @pytest.mark.asyncio
    async def test_packages_messages_has_error_messages(self):
        """PackagesMessages tiene mensajes de error."""
        from src.bot.keyboards.messages_packages import PackagesMessages

        assert hasattr(PackagesMessages.Error, "SYSTEM_ERROR")
        assert hasattr(PackagesMessages.Error, "NOT_AUTHENTICATED")
        assert hasattr(PackagesMessages.Error, "INVALID_PACKAGE")
        assert hasattr(PackagesMessages.Error, "PAYMENT_FAILED")
        assert hasattr(PackagesMessages.Error, "CRYPTO_PAYMENT_FAILED")
        assert hasattr(PackagesMessages.Error, "NETWORK_ERROR")
        assert hasattr(PackagesMessages.Error, "INSUFFICIENT_FUNDS")
        assert hasattr(PackagesMessages.Error, "TIMEOUT")

    @pytest.mark.asyncio
    async def test_packages_messages_menu_has_placeholders(self):
        """El mensaje de lista de paquetes tiene placeholders."""
        from src.bot.keyboards.messages_packages import PackagesMessages

        assert "{name}" in PackagesMessages.Menu.PACKAGE_ITEM
        assert "{data}" in PackagesMessages.Menu.PACKAGE_ITEM
        assert "{price_usd}" in PackagesMessages.Menu.PACKAGE_ITEM
        assert "{price_stars}" in PackagesMessages.Menu.PACKAGE_ITEM

    @pytest.mark.asyncio
    async def test_packages_messages_package_details_has_placeholders(self):
        """El mensaje de detalles de paquete tiene placeholders."""
        from src.bot.keyboards.messages_packages import PackagesMessages

        assert "{name}" in PackagesMessages.Menu.PACKAGE_DETAILS
        assert "{data}" in PackagesMessages.Menu.PACKAGE_DETAILS
        assert "{price_usd}" in PackagesMessages.Menu.PACKAGE_DETAILS
        assert "{price_stars}" in PackagesMessages.Menu.PACKAGE_DETAILS

    @pytest.mark.asyncio
    async def test_packages_messages_payment_select_method_has_placeholders(self):
        """El mensaje de selección de método de pago tiene placeholders."""
        from src.bot.keyboards.messages_packages import PackagesMessages

        assert "{name}" in PackagesMessages.Payment.SELECT_METHOD
        assert "{data}" in PackagesMessages.Payment.SELECT_METHOD
        assert "{price_stars}" in PackagesMessages.Payment.SELECT_METHOD
        assert "{price_usd}" in PackagesMessages.Payment.SELECT_METHOD

    @pytest.mark.asyncio
    async def test_packages_messages_stars_payment_sent_has_placeholders(self):
        """El mensaje de pago con stars enviado tiene placeholders."""
        from src.bot.keyboards.messages_packages import PackagesMessages

        assert "{stars}" in PackagesMessages.Payment.STARS_PAYMENT_SENT

    @pytest.mark.asyncio
    async def test_packages_messages_stars_success_has_placeholders(self):
        """El mensaje de éxito con stars tiene placeholders."""
        from src.bot.keyboards.messages_packages import PackagesMessages

        assert "{name}" in PackagesMessages.Payment.STARS_SUCCESS
        assert "{data}" in PackagesMessages.Payment.STARS_SUCCESS

    @pytest.mark.asyncio
    async def test_packages_messages_stars_failed_has_placeholders(self):
        """El mensaje de fallo con stars tiene placeholders."""
        from src.bot.keyboards.messages_packages import PackagesMessages

        assert "{reason}" in PackagesMessages.Payment.STARS_FAILED

    @pytest.mark.asyncio
    async def test_packages_messages_crypto_payment_has_placeholders(self):
        """El mensaje de pago crypto tiene placeholders."""
        from src.bot.keyboards.messages_packages import PackagesMessages

        assert "{amount_usd}" in PackagesMessages.Payment.CRYPTO_PAYMENT
        assert "{network}" in PackagesMessages.Payment.CRYPTO_PAYMENT
        assert "{address}" in PackagesMessages.Payment.CRYPTO_PAYMENT
        assert "{package_name}" in PackagesMessages.Payment.CRYPTO_PAYMENT
        assert "{data_gb}" in PackagesMessages.Payment.CRYPTO_PAYMENT

    @pytest.mark.asyncio
    async def test_packages_messages_crypto_pending_has_placeholders(self):
        """El mensaje de pago crypto pendiente tiene placeholders."""
        from src.bot.keyboards.messages_packages import PackagesMessages

        assert "{amount}" in PackagesMessages.Payment.CRYPTO_PENDING

    @pytest.mark.asyncio
    async def test_packages_messages_summary_has_placeholders(self):
        """El mensaje de resumen de datos tiene placeholders."""
        from src.bot.keyboards.messages_packages import PackagesMessages

        assert "{packages}" in PackagesMessages.Summary.DATA_SUMMARY
        assert "{total}" in PackagesMessages.Summary.DATA_SUMMARY
        assert "{used}" in PackagesMessages.Summary.DATA_SUMMARY
        assert "{remaining}" in PackagesMessages.Summary.DATA_SUMMARY
        assert "{percentage}" in PackagesMessages.Summary.DATA_SUMMARY
        assert "{renewal}" in PackagesMessages.Summary.DATA_SUMMARY

    @pytest.mark.asyncio
    async def test_packages_messages_slots_header_has_placeholders(self):
        """El mensaje de cabecera de slots tiene placeholders."""
        from src.bot.keyboards.messages_packages import PackagesMessages

        assert "{used}" in PackagesMessages.Slots.SLOTS_HEADER
        assert "{max}" in PackagesMessages.Slots.SLOTS_HEADER

    @pytest.mark.asyncio
    async def test_packages_messages_slot_item_has_placeholders(self):
        """El mensaje de item de slot tiene placeholders."""
        from src.bot.keyboards.messages_packages import PackagesMessages

        assert "{status}" in PackagesMessages.Slots.SLOT_ITEM
        assert "{name}" in PackagesMessages.Slots.SLOT_ITEM
        assert "{data}" in PackagesMessages.Slots.SLOT_ITEM
        assert "{expires}" in PackagesMessages.Slots.SLOT_ITEM

    @pytest.mark.asyncio
    async def test_packages_messages_max_slots_reached_has_placeholders(self):
        """El mensaje de límite de slots alcanzado tiene placeholders."""
        from src.bot.keyboards.messages_packages import PackagesMessages

        assert "{max}" in PackagesMessages.Slots.MAX_SLOTS_REACHED

    @pytest.mark.asyncio
    async def test_packages_keyboard_main_menu_exists(self):
        """PackagesKeyboard.packages_menu existe."""
        from src.bot.keyboards.packages import PackagesKeyboard

        packages = [
            {"id": "small", "name": "Pequeño", "data_gb": 5, "price_usd": 5.00, "price_stars": 600},
        ]
        keyboard = PackagesKeyboard.packages_menu(packages)

        from telegram import InlineKeyboardMarkup

        assert isinstance(keyboard, InlineKeyboardMarkup)

    @pytest.mark.asyncio
    async def test_packages_keyboard_main_menu_returns_inline_keyboard(self):
        """packages_menu retorna InlineKeyboardMarkup."""
        from telegram import InlineKeyboardMarkup
        from src.bot.keyboards.packages import PackagesKeyboard

        packages = [
            {"id": "small", "name": "Pequeño", "data_gb": 5, "price_usd": 5.00, "price_stars": 600},
            {
                "id": "medium",
                "name": "Mediano",
                "data_gb": 10,
                "price_usd": 10.00,
                "price_stars": 1200,
            },
        ]
        keyboard = PackagesKeyboard.packages_menu(packages)

        assert isinstance(keyboard, InlineKeyboardMarkup)
        assert len(keyboard.inline_keyboard) > 0

    @pytest.mark.asyncio
    async def test_packages_keyboard_payment_method_selection_exists(self):
        """PackagesKeyboard.payment_method_selection existe."""
        from src.bot.keyboards.packages import PackagesKeyboard

        keyboard = PackagesKeyboard.payment_method_selection(package_id="small")

        from telegram import InlineKeyboardMarkup

        assert isinstance(keyboard, InlineKeyboardMarkup)

        buttons = keyboard.inline_keyboard
        assert any("Stars" in btn.text or "⭐" in btn.text for row in buttons for btn in row)
        assert any("Crypto" in btn.text or "🪙" in btn.text for row in buttons for btn in row)

    @pytest.mark.asyncio
    async def test_packages_keyboard_stars_payment_exists(self):
        """El teclado de pago con stars tiene botón correcto."""
        from src.bot.keyboards.packages import PackagesKeyboard

        keyboard = PackagesKeyboard.payment_method_selection(package_id="medium")

        buttons = keyboard.inline_keyboard
        assert any("pay_stars_medium" in btn.callback_data for row in buttons for btn in row)

    @pytest.mark.asyncio
    async def test_packages_keyboard_crypto_payment_exists(self):
        """El teclado de pago con crypto tiene botón correcto."""
        from src.bot.keyboards.packages import PackagesKeyboard

        keyboard = PackagesKeyboard.payment_method_selection(package_id="large")

        buttons = keyboard.inline_keyboard
        assert any("pay_crypto_large" in btn.callback_data for row in buttons for btn in row)

    @pytest.mark.asyncio
    async def test_packages_keyboard_package_selection_exists(self):
        """packages_menu genera botones para cada paquete."""
        from src.bot.keyboards.packages import PackagesKeyboard

        packages = [
            {"id": "small", "name": "Pequeño", "data_gb": 5},
            {"id": "large", "name": "Grande", "data_gb": 25},
        ]
        keyboard = PackagesKeyboard.packages_menu(packages)

        buttons = keyboard.inline_keyboard
        assert any("select_package_small" in btn.callback_data for row in buttons for btn in row)
        assert any("select_package_large" in btn.callback_data for row in buttons for btn in row)

    @pytest.mark.asyncio
    async def test_packages_keyboard_data_summary_exists(self):
        """PackagesKeyboard.data_summary_menu existe."""
        from src.bot.keyboards.packages import PackagesKeyboard

        keyboard = PackagesKeyboard.data_summary_menu()

        from telegram import InlineKeyboardMarkup

        assert isinstance(keyboard, InlineKeyboardMarkup)

        buttons = keyboard.inline_keyboard
        assert any("Comprar" in btn.text or "📦" in btn.text for row in buttons for btn in row)
        assert any("Slots" in btn.text or "🗂️" in btn.text for row in buttons for btn in row)

    @pytest.mark.asyncio
    async def test_packages_keyboard_slots_menu_exists(self):
        """PackagesKeyboard.slots_menu existe."""
        from src.bot.keyboards.packages import PackagesKeyboard

        keyboard = PackagesKeyboard.slots_menu(has_packages=True)

        from telegram import InlineKeyboardMarkup

        assert isinstance(keyboard, InlineKeyboardMarkup)

        buttons = keyboard.inline_keyboard
        assert any("Slot" in btn.text or "➕" in btn.text for row in buttons for btn in row)

    @pytest.mark.asyncio
    async def test_packages_keyboard_back_to_packages_exists(self):
        """PackagesKeyboard.back_to_packages existe."""
        from src.bot.keyboards.packages import PackagesKeyboard

        keyboard = PackagesKeyboard.back_to_packages()

        from telegram import InlineKeyboardMarkup

        assert isinstance(keyboard, InlineKeyboardMarkup)

        buttons = keyboard.inline_keyboard
        assert any("Paquetes" in btn.text or "📦" in btn.text for row in buttons for btn in row)

    @pytest.mark.asyncio
    async def test_packages_keyboard_payment_success_exists(self):
        """PackagesKeyboard.back_to_menu existe."""
        from src.bot.keyboards.packages import PackagesKeyboard

        keyboard = PackagesKeyboard.back_to_menu()

        from telegram import InlineKeyboardMarkup

        assert isinstance(keyboard, InlineKeyboardMarkup)

    @pytest.mark.asyncio
    async def test_packages_keyboard_crypto_payment_status_exists(self):
        """PackagesKeyboard.crypto_payment_status existe."""
        from src.bot.keyboards.packages import PackagesKeyboard

        keyboard = PackagesKeyboard.crypto_payment_status(payment_id="crypto_123")

        from telegram import InlineKeyboardMarkup

        assert isinstance(keyboard, InlineKeyboardMarkup)

        buttons = keyboard.inline_keyboard
        assert any("Verificar" in btn.text or "🔄" in btn.text for row in buttons for btn in row)

    @pytest.mark.asyncio
    async def test_packages_keyboard_buy_slot_confirmation_exists(self):
        """PackagesKeyboard.buy_slot_confirmation existe."""
        from src.bot.keyboards.packages import PackagesKeyboard

        keyboard = PackagesKeyboard.buy_slot_confirmation()

        from telegram import InlineKeyboardMarkup

        assert isinstance(keyboard, InlineKeyboardMarkup)

        buttons = keyboard.inline_keyboard
        assert any("Confirmar" in btn.text or "✅" in btn.text for row in buttons for btn in row)
        assert any("Cancelar" in btn.text or "❌" in btn.text for row in buttons for btn in row)

    @pytest.mark.asyncio
    async def test_show_packages_command_exists(self):
        """show_packages command handler existe."""
        with (
            patch("src.bot.handlers.packages.APIClient"),
            patch("src.bot.handlers.packages.TokenStorage"),
        ):
            from src.bot.handlers.packages import PackagesHandler

            mock_api = AsyncMock()
            mock_storage = AsyncMock()

            handler = PackagesHandler(mock_api, mock_storage)

            assert hasattr(handler, "show_packages")
            assert callable(getattr(handler, "show_packages"))

    @pytest.mark.asyncio
    async def test_select_payment_method_callback_exists(self):
        """select_payment_method callback handler existe."""
        with (
            patch("src.bot.handlers.packages.APIClient"),
            patch("src.bot.handlers.packages.TokenStorage"),
        ):
            from src.bot.handlers.packages import PackagesHandler

            mock_api = AsyncMock()
            mock_storage = AsyncMock()

            handler = PackagesHandler(mock_api, mock_storage)

            assert hasattr(handler, "select_payment_method")
            assert callable(getattr(handler, "select_payment_method"))

    @pytest.mark.asyncio
    async def test_pay_with_stars_flow(self):
        """pay_with_stars inicia el flujo de pago con stars."""
        with (
            patch("src.bot.handlers.packages.APIClient"),
            patch("src.bot.handlers.packages.TokenStorage"),
        ):
            from src.bot.handlers.packages import PackagesHandler

            mock_api = AsyncMock()
            mock_storage = AsyncMock()
            mock_storage.is_authenticated.return_value = True
            mock_storage.get.return_value = {"access_token": "test-token"}

            handler = PackagesHandler(mock_api, mock_storage)

            assert hasattr(handler, "pay_with_stars")
            assert callable(getattr(handler, "pay_with_stars"))

    @pytest.mark.asyncio
    async def test_pay_with_crypto_flow(self):
        """pay_with_crypto inicia el flujo de pago con crypto."""
        with (
            patch("src.bot.handlers.packages.APIClient"),
            patch("src.bot.handlers.packages.TokenStorage"),
        ):
            from src.bot.handlers.packages import PackagesHandler

            mock_api = AsyncMock()
            mock_storage = AsyncMock()
            mock_storage.is_authenticated.return_value = True
            mock_storage.get.return_value = {"access_token": "test-token"}

            handler = PackagesHandler(mock_api, mock_storage)

            assert hasattr(handler, "pay_with_crypto")
            assert callable(getattr(handler, "pay_with_crypto"))

    @pytest.mark.asyncio
    async def test_view_data_summary_exists(self):
        """view_data_summary handler existe."""
        with (
            patch("src.bot.handlers.packages.APIClient"),
            patch("src.bot.handlers.packages.TokenStorage"),
        ):
            from src.bot.handlers.packages import PackagesHandler

            mock_api = AsyncMock()
            mock_storage = AsyncMock()

            handler = PackagesHandler(mock_api, mock_storage)

            assert hasattr(handler, "view_data_summary")
            assert callable(getattr(handler, "view_data_summary"))

    @pytest.mark.asyncio
    async def test_pre_checkout_callback_exists(self):
        """pre_checkout_callback handler existe."""
        with (
            patch("src.bot.handlers.packages.APIClient"),
            patch("src.bot.handlers.packages.TokenStorage"),
        ):
            from src.bot.handlers.packages import PackagesHandler

            mock_api = AsyncMock()
            mock_storage = AsyncMock()

            handler = PackagesHandler(mock_api, mock_storage)

            assert hasattr(handler, "pre_checkout_callback")
            assert callable(getattr(handler, "pre_checkout_callback"))

    @pytest.mark.asyncio
    async def test_successful_payment_handler_exists(self):
        """successful_payment handler existe."""
        with (
            patch("src.bot.handlers.packages.APIClient"),
            patch("src.bot.handlers.packages.TokenStorage"),
        ):
            from src.bot.handlers.packages import PackagesHandler

            mock_api = AsyncMock()
            mock_storage = AsyncMock()

            handler = PackagesHandler(mock_api, mock_storage)

            assert hasattr(handler, "successful_payment")
            assert callable(getattr(handler, "successful_payment"))

    @pytest.mark.asyncio
    async def test_check_crypto_payment_status_exists(self):
        """check_crypto_payment_status handler existe."""
        with (
            patch("src.bot.handlers.packages.APIClient"),
            patch("src.bot.handlers.packages.TokenStorage"),
        ):
            from src.bot.handlers.packages import PackagesHandler

            mock_api = AsyncMock()
            mock_storage = AsyncMock()

            handler = PackagesHandler(mock_api, mock_storage)

            assert hasattr(handler, "check_crypto_payment_status")
            assert callable(getattr(handler, "check_crypto_payment_status"))

    @pytest.mark.asyncio
    async def test_show_slots_menu_exists(self):
        """show_slots_menu handler existe."""
        with (
            patch("src.bot.handlers.packages.APIClient"),
            patch("src.bot.handlers.packages.TokenStorage"),
        ):
            from src.bot.handlers.packages import PackagesHandler

            mock_api = AsyncMock()
            mock_storage = AsyncMock()

            handler = PackagesHandler(mock_api, mock_storage)

            assert hasattr(handler, "show_slots_menu")
            assert callable(getattr(handler, "show_slots_menu"))

    @pytest.mark.asyncio
    async def test_buy_extra_slot_exists(self):
        """buy_extra_slot handler existe."""
        with (
            patch("src.bot.handlers.packages.APIClient"),
            patch("src.bot.handlers.packages.TokenStorage"),
        ):
            from src.bot.handlers.packages import PackagesHandler

            mock_api = AsyncMock()
            mock_storage = AsyncMock()

            handler = PackagesHandler(mock_api, mock_storage)

            assert hasattr(handler, "buy_extra_slot")
            assert callable(getattr(handler, "buy_extra_slot"))

    @pytest.mark.asyncio
    async def test_confirm_buy_slot_exists(self):
        """confirm_buy_slot handler existe."""
        with (
            patch("src.bot.handlers.packages.APIClient"),
            patch("src.bot.handlers.packages.TokenStorage"),
        ):
            from src.bot.handlers.packages import PackagesHandler

            mock_api = AsyncMock()
            mock_storage = AsyncMock()

            handler = PackagesHandler(mock_api, mock_storage)

            assert hasattr(handler, "confirm_buy_slot")
            assert callable(getattr(handler, "confirm_buy_slot"))

    @pytest.mark.asyncio
    async def test_packages_handler_get_auth_headers(self):
        """_get_auth_headers retorna headers con token."""
        with (
            patch("src.bot.handlers.packages.APIClient"),
            patch("src.bot.handlers.packages.TokenStorage"),
        ):
            from src.bot.handlers.packages import PackagesHandler

            mock_api = AsyncMock()
            mock_storage = AsyncMock()
            mock_storage.get.return_value = {"access_token": "test-token-123"}

            handler = PackagesHandler(mock_api, mock_storage)

            headers = await handler._get_auth_headers(telegram_id=123)

            assert "Authorization" in headers
            assert headers["Authorization"] == "Bearer test-token-123"

    @pytest.mark.asyncio
    async def test_packages_handler_get_auth_headers_unauthenticated(self):
        """_get_auth_headers lanza error si no está autenticado."""
        with (
            patch("src.bot.handlers.packages.APIClient"),
            patch("src.bot.handlers.packages.TokenStorage"),
        ):
            from src.bot.handlers.packages import PackagesHandler

            mock_api = AsyncMock()
            mock_storage = AsyncMock()
            mock_storage.get.return_value = None

            handler = PackagesHandler(mock_api, mock_storage)

            with pytest.raises(PermissionError):
                await handler._get_auth_headers(telegram_id=123)

    @pytest.mark.asyncio
    async def test_get_packages_handlers_returns_list(self):
        """get_packages_handlers retorna una lista."""
        with (
            patch("src.bot.handlers.packages.APIClient"),
            patch("src.bot.handlers.packages.TokenStorage"),
        ):
            from src.bot.handlers.packages import get_packages_handlers

            mock_api = AsyncMock()
            mock_storage = AsyncMock()

            handlers = get_packages_handlers(mock_api, mock_storage)

            assert isinstance(handlers, list)
            assert len(handlers) > 0

    @pytest.mark.asyncio
    async def test_get_packages_callback_handlers_returns_list(self):
        """get_packages_callback_handlers retorna una lista."""
        with (
            patch("src.bot.handlers.packages.APIClient"),
            patch("src.bot.handlers.packages.TokenStorage"),
        ):
            from src.bot.handlers.packages import get_packages_callback_handlers

            mock_api = AsyncMock()
            mock_storage = AsyncMock()

            handlers = get_packages_callback_handlers(mock_api, mock_storage)

            assert isinstance(handlers, list)
            assert len(handlers) > 0

    @pytest.mark.asyncio
    async def test_get_packages_payment_handlers_returns_list(self):
        """get_packages_payment_handlers retorna una lista."""
        with (
            patch("src.bot.handlers.packages.APIClient"),
            patch("src.bot.handlers.packages.TokenStorage"),
        ):
            from src.bot.handlers.packages import get_packages_payment_handlers

            mock_api = AsyncMock()
            mock_storage = AsyncMock()

            handlers = get_packages_payment_handlers(mock_api, mock_storage)

            assert isinstance(handlers, list)
            assert len(handlers) > 0

    @pytest.mark.asyncio
    async def test_packages_keyboard_back_to_main_menu_exists(self):
        """PackagesKeyboard.back_to_main_menu existe."""
        from src.bot.keyboards.packages import PackagesKeyboard

        keyboard = PackagesKeyboard.back_to_main_menu()

        from telegram import InlineKeyboardMarkup

        assert isinstance(keyboard, InlineKeyboardMarkup)

        buttons = keyboard.inline_keyboard
        assert any(
            "Menú Principal" in btn.text or "🔙" in btn.text for row in buttons for btn in row
        )

    @pytest.mark.asyncio
    async def test_packages_keyboard_packages_menu_button_exists(self):
        """PackagesKeyboard.packages_menu_button existe."""
        from src.bot.keyboards.packages import PackagesKeyboard

        keyboard = PackagesKeyboard.packages_menu_button()

        from telegram import InlineKeyboardMarkup

        assert isinstance(keyboard, InlineKeyboardMarkup)

        buttons = keyboard.inline_keyboard
        assert any("Paquetes" in btn.text or "📦" in btn.text for row in buttons for btn in row)

    @pytest.mark.asyncio
    async def test_select_package_handler_exists(self):
        """select_package handler existe."""
        with (
            patch("src.bot.handlers.packages.APIClient"),
            patch("src.bot.handlers.packages.TokenStorage"),
        ):
            from src.bot.handlers.packages import PackagesHandler

            mock_api = AsyncMock()
            mock_storage = AsyncMock()

            handler = PackagesHandler(mock_api, mock_storage)

            assert hasattr(handler, "select_package")
            assert callable(getattr(handler, "select_package"))

    @pytest.mark.asyncio
    async def test_back_to_main_menu_handler_exists(self):
        """back_to_main_menu handler existe."""
        with (
            patch("src.bot.handlers.packages.APIClient"),
            patch("src.bot.handlers.packages.TokenStorage"),
        ):
            from src.bot.handlers.packages import PackagesHandler

            mock_api = AsyncMock()
            mock_storage = AsyncMock()

            handler = PackagesHandler(mock_api, mock_storage)

            assert hasattr(handler, "back_to_main_menu")
            assert callable(getattr(handler, "back_to_main_menu"))

    @pytest.mark.asyncio
    async def test_packages_messages_invoice_has_placeholders(self):
        """Los mensajes de invoice tienen placeholders correctos."""
        from src.bot.keyboards.messages_packages import PackagesMessages

        # Verify invoice-related messages exist
        assert hasattr(PackagesMessages.Payment, "STARS_PAYMENT_SENT")
        assert "{stars}" in PackagesMessages.Payment.STARS_PAYMENT_SENT

    @pytest.mark.asyncio
    async def test_packages_keyboard_main_menu_has_view_summary_button(self):
        """packages_menu tiene botón de ver resumen."""
        from src.bot.keyboards.packages import PackagesKeyboard

        packages = [{"id": "small", "name": "Pequeño", "data_gb": 5}]
        keyboard = PackagesKeyboard.packages_menu(packages)

        buttons = keyboard.inline_keyboard
        assert any("Resumen" in btn.text or "📊" in btn.text for row in buttons for btn in row)

    @pytest.mark.asyncio
    async def test_packages_keyboard_main_menu_has_slots_button(self):
        """packages_menu tiene botón de gestionar slots."""
        from src.bot.keyboards.packages import PackagesKeyboard

        packages = [{"id": "small", "name": "Pequeño", "data_gb": 5}]
        keyboard = PackagesKeyboard.packages_menu(packages)

        buttons = keyboard.inline_keyboard
        assert any("Slots" in btn.text or "🗂️" in btn.text for row in buttons for btn in row)

    @pytest.mark.asyncio
    async def test_packages_keyboard_main_menu_has_back_button(self):
        """packages_menu tiene botón de volver."""
        from src.bot.keyboards.packages import PackagesKeyboard

        packages = [{"id": "small", "name": "Pequeño", "data_gb": 5}]
        keyboard = PackagesKeyboard.packages_menu(packages)

        buttons = keyboard.inline_keyboard
        assert any("Volver" in btn.text or "🔙" in btn.text for row in buttons for btn in row)

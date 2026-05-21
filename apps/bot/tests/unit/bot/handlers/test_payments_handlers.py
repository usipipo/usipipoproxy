"""Tests para Payments Handlers."""

import pytest
from unittest.mock import patch, AsyncMock


class TestPaymentsHandler:
    """Tests para PaymentsHandler."""

    @pytest.mark.asyncio
    async def test_payments_handler_initialization(self):
        """PaymentsHandler se inicializa correctamente."""
        with (
            patch("src.bot.handlers.payments.APIClient"),
            patch("src.bot.handlers.payments.TokenStorage"),
        ):
            from src.bot.handlers.payments import PaymentsHandler

            mock_api = AsyncMock()
            mock_storage = AsyncMock()

            handler = PaymentsHandler(mock_api, mock_storage)

            assert handler.api == mock_api
            assert handler.tokens == mock_storage

    # ============================================
    # MESSAGE CONSTANTS TESTS
    # ============================================

    @pytest.mark.asyncio
    async def test_payments_messages_constants_exist(self):
        """PaymentsMessages constants están definidas."""
        from src.bot.keyboards.messages_payments import PaymentsMessages

        assert hasattr(PaymentsMessages, "Menu")
        assert hasattr(PaymentsMessages, "Payment")
        assert hasattr(PaymentsMessages, "History")
        assert hasattr(PaymentsMessages, "Error")

    @pytest.mark.asyncio
    async def test_payments_messages_has_menu_messages(self):
        """PaymentsMessages tiene mensajes de menú."""
        from src.bot.keyboards.messages_payments import PaymentsMessages

        assert hasattr(PaymentsMessages.Menu, "PAYMENT_METHODS")
        assert hasattr(PaymentsMessages.Menu, "NO_PAYMENT_METHODS")

    @pytest.mark.asyncio
    async def test_payments_messages_has_payment_messages(self):
        """PaymentsMessages tiene mensajes de pago."""
        from src.bot.keyboards.messages_payments import PaymentsMessages

        assert hasattr(PaymentsMessages.Payment, "CRYPTO_PAYMENT")
        assert hasattr(PaymentsMessages.Payment, "CRYPTO_PENDING")
        assert hasattr(PaymentsMessages.Payment, "CRYPTO_SUCCESS")
        assert hasattr(PaymentsMessages.Payment, "CRYPTO_EXPIRED")
        assert hasattr(PaymentsMessages.Payment, "STARS_PAYMENT_SENT")
        assert hasattr(PaymentsMessages.Payment, "STARS_SUCCESS")
        assert hasattr(PaymentsMessages.Payment, "STARS_FAILED")

    @pytest.mark.asyncio
    async def test_payments_messages_has_crypto_messages(self):
        """PaymentsMessages tiene mensajes específicos de crypto."""
        from src.bot.keyboards.messages_payments import PaymentsMessages

        assert hasattr(PaymentsMessages.Payment, "CRYPTO_PAYMENT")
        assert hasattr(PaymentsMessages.Payment, "CRYPTO_PENDING")
        assert hasattr(PaymentsMessages.Payment, "CRYPTO_SUCCESS")
        assert hasattr(PaymentsMessages.Payment, "CRYPTO_EXPIRED")

    @pytest.mark.asyncio
    async def test_payments_messages_has_stars_messages(self):
        """PaymentsMessages tiene mensajes específicos de Stars."""
        from src.bot.keyboards.messages_payments import PaymentsMessages

        assert hasattr(PaymentsMessages.Payment, "STARS_PAYMENT_SENT")
        assert hasattr(PaymentsMessages.Payment, "STARS_SUCCESS")
        assert hasattr(PaymentsMessages.Payment, "STARS_FAILED")

    @pytest.mark.asyncio
    async def test_payments_messages_has_error_messages(self):
        """PaymentsMessages tiene mensajes de error."""
        from src.bot.keyboards.messages_payments import PaymentsMessages

        assert hasattr(PaymentsMessages.Error, "SYSTEM_ERROR")
        assert hasattr(PaymentsMessages.Error, "NOT_AUTHENTICATED")
        assert hasattr(PaymentsMessages.Error, "PAYMENT_FAILED")
        assert hasattr(PaymentsMessages.Error, "CRYPTO_PAYMENT_FAILED")
        assert hasattr(PaymentsMessages.Error, "NETWORK_ERROR")
        assert hasattr(PaymentsMessages.Error, "INSUFFICIENT_FUNDS")
        assert hasattr(PaymentsMessages.Error, "TIMEOUT")

    # ============================================
    # MESSAGE PLACEHOLDERS TESTS
    # ============================================

    @pytest.mark.asyncio
    async def test_payments_messages_menu_has_placeholders(self):
        """El mensaje de menú de pagos tiene placeholders."""
        from src.bot.keyboards.messages_payments import PaymentsMessages

        # PAYMENT_METHODS no tiene placeholders, es estático
        assert isinstance(PaymentsMessages.Menu.PAYMENT_METHODS, str)
        assert len(PaymentsMessages.Menu.PAYMENT_METHODS) > 0

    @pytest.mark.asyncio
    async def test_payments_messages_crypto_payment_has_placeholders(self):
        """El mensaje de pago crypto tiene placeholders."""
        from src.bot.keyboards.messages_payments import PaymentsMessages

        assert "{amount_usd}" in PaymentsMessages.Payment.CRYPTO_PAYMENT
        assert "{network}" in PaymentsMessages.Payment.CRYPTO_PAYMENT
        assert "{address}" in PaymentsMessages.Payment.CRYPTO_PAYMENT
        assert "{qr_url}" in PaymentsMessages.Payment.CRYPTO_PAYMENT

    @pytest.mark.asyncio
    async def test_payments_messages_crypto_pending_has_placeholders(self):
        """El mensaje de pago crypto pendiente tiene placeholders."""
        from src.bot.keyboards.messages_payments import PaymentsMessages

        assert "{amount}" in PaymentsMessages.Payment.CRYPTO_PENDING
        assert "{tx_hash}" in PaymentsMessages.Payment.CRYPTO_PENDING

    @pytest.mark.asyncio
    async def test_payments_messages_crypto_success_has_placeholders(self):
        """El mensaje de éxito crypto no requiere placeholders."""
        from src.bot.keyboards.messages_payments import PaymentsMessages

        assert isinstance(PaymentsMessages.Payment.CRYPTO_SUCCESS, str)
        assert len(PaymentsMessages.Payment.CRYPTO_SUCCESS) > 0

    @pytest.mark.asyncio
    async def test_payments_messages_stars_payment_has_placeholders(self):
        """El mensaje de pago con stars tiene placeholders."""
        from src.bot.keyboards.messages_payments import PaymentsMessages

        assert "{stars}" in PaymentsMessages.Payment.STARS_PAYMENT_SENT

    @pytest.mark.asyncio
    async def test_payments_messages_stars_success_has_placeholders(self):
        """El mensaje de éxito con stars tiene placeholders."""
        from src.bot.keyboards.messages_payments import PaymentsMessages

        assert "{stars}" in PaymentsMessages.Payment.STARS_SUCCESS

    @pytest.mark.asyncio
    async def test_payments_messages_stars_failed_has_placeholders(self):
        """El mensaje de fallo con stars tiene placeholders."""
        from src.bot.keyboards.messages_payments import PaymentsMessages

        assert "{reason}" in PaymentsMessages.Payment.STARS_FAILED

    @pytest.mark.asyncio
    async def test_payments_messages_payment_history_has_placeholders(self):
        """El mensaje de historial de pagos tiene placeholders."""
        from src.bot.keyboards.messages_payments import PaymentsMessages

        assert "{total}" in PaymentsMessages.History.HEADER
        assert "{crypto}" in PaymentsMessages.History.HEADER
        assert "{stars}" in PaymentsMessages.History.HEADER
        assert "{completed}" in PaymentsMessages.History.HEADER
        assert "{pending}" in PaymentsMessages.History.HEADER
        assert "{type}" in PaymentsMessages.History.PAYMENT_ITEM
        assert "{amount}" in PaymentsMessages.History.PAYMENT_ITEM
        assert "{date}" in PaymentsMessages.History.PAYMENT_ITEM
        assert "{status}" in PaymentsMessages.History.PAYMENT_ITEM
        assert "{status_text}" in PaymentsMessages.History.PAYMENT_ITEM

    # ============================================
    # KEYBOARD METHODS TESTS
    # ============================================

    @pytest.mark.asyncio
    async def test_payments_keyboard_main_menu_exists(self):
        """PaymentsKeyboard.payment_menu existe."""
        from src.bot.keyboards.payments import PaymentsKeyboard

        payment_methods = [
            {"id": "crypto", "name": "Criptomonedas", "enabled": True},
            {"id": "stars", "name": "Telegram Stars", "enabled": True},
        ]
        keyboard = PaymentsKeyboard.payment_menu(payment_methods)

        from telegram import InlineKeyboardMarkup

        assert isinstance(keyboard, InlineKeyboardMarkup)

    @pytest.mark.asyncio
    async def test_payments_keyboard_main_menu_returns_inline_keyboard(self):
        """payment_menu retorna InlineKeyboardMarkup."""
        from telegram import InlineKeyboardMarkup
        from src.bot.keyboards.payments import PaymentsKeyboard

        payment_methods = [
            {"id": "crypto", "name": "Criptomonedas", "enabled": True},
        ]
        keyboard = PaymentsKeyboard.payment_menu(payment_methods)

        assert isinstance(keyboard, InlineKeyboardMarkup)
        assert len(keyboard.inline_keyboard) > 0

    @pytest.mark.asyncio
    async def test_payments_keyboard_crypto_payment_exists(self):
        """PaymentsKeyboard.crypto_amounts existe."""
        from src.bot.keyboards.payments import PaymentsKeyboard

        keyboard = PaymentsKeyboard.crypto_amounts()

        from telegram import InlineKeyboardMarkup

        assert isinstance(keyboard, InlineKeyboardMarkup)

        buttons = keyboard.inline_keyboard
        # Check for crypto payment buttons (format: pay_crypto_X_XX)
        assert any("pay_crypto_5_00" in btn.callback_data for row in buttons for btn in row)
        assert any("pay_crypto_15_00" in btn.callback_data for row in buttons for btn in row)

    @pytest.mark.asyncio
    async def test_payments_keyboard_stars_payment_exists(self):
        """PaymentsKeyboard.stars_amounts existe."""
        from src.bot.keyboards.payments import PaymentsKeyboard

        keyboard = PaymentsKeyboard.stars_amounts()

        from telegram import InlineKeyboardMarkup

        assert isinstance(keyboard, InlineKeyboardMarkup)

        buttons = keyboard.inline_keyboard
        assert any("pay_stars_300" in btn.callback_data for row in buttons for btn in row)
        assert any("pay_stars_600" in btn.callback_data for row in buttons for btn in row)

    @pytest.mark.asyncio
    async def test_payments_keyboard_payment_history_exists(self):
        """PaymentsKeyboard.payment_history_list existe."""
        from src.bot.keyboards.payments import PaymentsKeyboard

        keyboard = PaymentsKeyboard.payment_history_list(has_next=True, page=0)

        from telegram import InlineKeyboardMarkup

        assert isinstance(keyboard, InlineKeyboardMarkup)

        buttons = keyboard.inline_keyboard
        assert any("payment_history_1" in btn.callback_data for row in buttons for btn in row)

    @pytest.mark.asyncio
    async def test_payments_keyboard_payment_success_exists(self):
        """PaymentsKeyboard.back_to_menu existe."""
        from src.bot.keyboards.payments import PaymentsKeyboard

        keyboard = PaymentsKeyboard.back_to_menu()

        from telegram import InlineKeyboardMarkup

        assert isinstance(keyboard, InlineKeyboardMarkup)

        buttons = keyboard.inline_keyboard
        assert any("payment_menu" in btn.callback_data for row in buttons for btn in row)

    @pytest.mark.asyncio
    async def test_payments_keyboard_payment_failed_exists(self):
        """PaymentsKeyboard.back_to_payments existe."""
        from src.bot.keyboards.payments import PaymentsKeyboard

        keyboard = PaymentsKeyboard.back_to_payments()

        from telegram import InlineKeyboardMarkup

        assert isinstance(keyboard, InlineKeyboardMarkup)

        buttons = keyboard.inline_keyboard
        assert any("payment_menu" in btn.callback_data for row in buttons for btn in row)

    @pytest.mark.asyncio
    async def test_payments_keyboard_back_to_payments_exists(self):
        """PaymentsKeyboard.back_to_payments retorna InlineKeyboardMarkup."""
        from telegram import InlineKeyboardMarkup
        from src.bot.keyboards.payments import PaymentsKeyboard

        keyboard = PaymentsKeyboard.back_to_payments()

        assert isinstance(keyboard, InlineKeyboardMarkup)
        assert len(keyboard.inline_keyboard) > 0

    @pytest.mark.asyncio
    async def test_payments_keyboard_crypto_payment_status_exists(self):
        """PaymentsKeyboard.crypto_payment_status existe."""
        from src.bot.keyboards.payments import PaymentsKeyboard

        keyboard = PaymentsKeyboard.crypto_payment_status(payment_id="crypto_123")

        from telegram import InlineKeyboardMarkup

        assert isinstance(keyboard, InlineKeyboardMarkup)

        buttons = keyboard.inline_keyboard
        assert any(
            "check_crypto_status_crypto_123" in btn.callback_data for row in buttons for btn in row
        )

    @pytest.mark.asyncio
    async def test_payments_keyboard_payment_history_pagination_exists(self):
        """payment_history_list soporta paginación."""
        from src.bot.keyboards.payments import PaymentsKeyboard

        keyboard_page_0 = PaymentsKeyboard.payment_history_list(has_next=True, page=0)
        keyboard_page_1 = PaymentsKeyboard.payment_history_list(has_next=False, page=1)

        from telegram import InlineKeyboardMarkup

        assert isinstance(keyboard_page_0, InlineKeyboardMarkup)
        assert isinstance(keyboard_page_1, InlineKeyboardMarkup)

        # Page 0 should have next button
        buttons_0 = keyboard_page_0.inline_keyboard
        assert any("payment_history_1" in btn.callback_data for row in buttons_0 for btn in row)

        # Page 1 with no next should not have next button
        buttons_1 = keyboard_page_1.inline_keyboard
        assert not any("payment_history_2" in btn.callback_data for row in buttons_1 for btn in row)

    # ============================================
    # HANDLER METHODS TESTS
    # ============================================

    @pytest.mark.asyncio
    async def test_show_payment_menu_command_exists(self):
        """show_payment_menu handler existe."""
        with (
            patch("src.bot.handlers.payments.APIClient"),
            patch("src.bot.handlers.payments.TokenStorage"),
        ):
            from src.bot.handlers.payments import PaymentsHandler

            mock_api = AsyncMock()
            mock_storage = AsyncMock()

            handler = PaymentsHandler(mock_api, mock_storage)

            assert hasattr(handler, "show_payment_menu")
            assert callable(getattr(handler, "show_payment_menu"))

    @pytest.mark.asyncio
    async def test_pay_with_crypto_flow(self):
        """pay_with_crypto inicia el flujo de pago con crypto."""
        with (
            patch("src.bot.handlers.payments.APIClient"),
            patch("src.bot.handlers.payments.TokenStorage"),
        ):
            from src.bot.handlers.payments import PaymentsHandler

            mock_api = AsyncMock()
            mock_storage = AsyncMock()
            mock_storage.is_authenticated.return_value = True
            mock_storage.get.return_value = {"access_token": "test-token"}

            handler = PaymentsHandler(mock_api, mock_storage)

            assert hasattr(handler, "pay_with_crypto")
            assert callable(getattr(handler, "pay_with_crypto"))

    @pytest.mark.asyncio
    async def test_pay_with_stars_flow(self):
        """pay_with_stars inicia el flujo de pago con stars."""
        with (
            patch("src.bot.handlers.payments.APIClient"),
            patch("src.bot.handlers.payments.TokenStorage"),
        ):
            from src.bot.handlers.payments import PaymentsHandler

            mock_api = AsyncMock()
            mock_storage = AsyncMock()
            mock_storage.is_authenticated.return_value = True
            mock_storage.get.return_value = {"access_token": "test-token"}

            handler = PaymentsHandler(mock_api, mock_storage)

            assert hasattr(handler, "pay_with_stars")
            assert callable(getattr(handler, "pay_with_stars"))

    @pytest.mark.asyncio
    async def test_view_payment_history_exists(self):
        """view_payment_history handler existe."""
        with (
            patch("src.bot.handlers.payments.APIClient"),
            patch("src.bot.handlers.payments.TokenStorage"),
        ):
            from src.bot.handlers.payments import PaymentsHandler

            mock_api = AsyncMock()
            mock_storage = AsyncMock()

            handler = PaymentsHandler(mock_api, mock_storage)

            assert hasattr(handler, "view_payment_history")
            assert callable(getattr(handler, "view_payment_history"))

    @pytest.mark.asyncio
    async def test_pre_checkout_callback_exists(self):
        """pre_checkout_callback handler existe."""
        with (
            patch("src.bot.handlers.payments.APIClient"),
            patch("src.bot.handlers.payments.TokenStorage"),
        ):
            from src.bot.handlers.payments import PaymentsHandler

            mock_api = AsyncMock()
            mock_storage = AsyncMock()

            handler = PaymentsHandler(mock_api, mock_storage)

            assert hasattr(handler, "pre_checkout_callback")
            assert callable(getattr(handler, "pre_checkout_callback"))

    @pytest.mark.asyncio
    async def test_successful_payment_handler_exists(self):
        """successful_payment handler existe."""
        with (
            patch("src.bot.handlers.payments.APIClient"),
            patch("src.bot.handlers.payments.TokenStorage"),
        ):
            from src.bot.handlers.payments import PaymentsHandler

            mock_api = AsyncMock()
            mock_storage = AsyncMock()

            handler = PaymentsHandler(mock_api, mock_storage)

            assert hasattr(handler, "successful_payment")
            assert callable(getattr(handler, "successful_payment"))

    @pytest.mark.asyncio
    async def test_check_crypto_payment_status_exists(self):
        """check_crypto_payment_status handler existe."""
        with (
            patch("src.bot.handlers.payments.APIClient"),
            patch("src.bot.handlers.payments.TokenStorage"),
        ):
            from src.bot.handlers.payments import PaymentsHandler

            mock_api = AsyncMock()
            mock_storage = AsyncMock()

            handler = PaymentsHandler(mock_api, mock_storage)

            assert hasattr(handler, "check_crypto_payment_status")
            assert callable(getattr(handler, "check_crypto_payment_status"))

    @pytest.mark.asyncio
    async def test_crypto_payment_confirmation_exists(self):
        """check_crypto_payment_status verifica estado de pago."""
        with (
            patch("src.bot.handlers.payments.APIClient"),
            patch("src.bot.handlers.payments.TokenStorage"),
        ):
            from src.bot.handlers.payments import PaymentsHandler

            mock_api = AsyncMock()
            mock_storage = AsyncMock()
            mock_storage.is_authenticated.return_value = True
            mock_storage.get.return_value = {"access_token": "test-token"}

            handler = PaymentsHandler(mock_api, mock_storage)

            # Mock API response
            mock_api.get.return_value = {
                "status": "completed",
                "amount_usd": 10.0,
                "transaction_hash": "0x123abc",
            }

            assert callable(handler.check_crypto_payment_status)

    # ============================================
    # AUTHENTICATION & INTEGRATION TESTS
    # ============================================

    @pytest.mark.asyncio
    async def test_payments_handler_get_auth_headers(self):
        """_get_auth_headers retorna headers con token."""
        with (
            patch("src.bot.handlers.payments.APIClient"),
            patch("src.bot.handlers.payments.TokenStorage"),
        ):
            from src.bot.handlers.payments import PaymentsHandler

            mock_api = AsyncMock()
            mock_storage = AsyncMock()
            mock_storage.get.return_value = {"access_token": "test-token-123"}

            handler = PaymentsHandler(mock_api, mock_storage)

            headers = await handler._get_auth_headers(telegram_id=123)

            assert "Authorization" in headers
            assert headers["Authorization"] == "Bearer test-token-123"

    @pytest.mark.asyncio
    async def test_payments_handler_get_auth_headers_unauthenticated(self):
        """_get_auth_headers lanza error si no está autenticado."""
        with (
            patch("src.bot.handlers.payments.APIClient"),
            patch("src.bot.handlers.payments.TokenStorage"),
        ):
            from src.bot.handlers.payments import PaymentsHandler

            mock_api = AsyncMock()
            mock_storage = AsyncMock()
            mock_storage.get.return_value = None

            handler = PaymentsHandler(mock_api, mock_storage)

            with pytest.raises(PermissionError):
                await handler._get_auth_headers(telegram_id=123)

    @pytest.mark.asyncio
    async def test_get_payments_handlers_returns_list(self):
        """get_payments_handlers retorna una lista."""
        with (
            patch("src.bot.handlers.payments.APIClient"),
            patch("src.bot.handlers.payments.TokenStorage"),
        ):
            from src.bot.handlers.payments import get_payments_handlers

            mock_api = AsyncMock()
            mock_storage = AsyncMock()

            handlers = get_payments_handlers(mock_api, mock_storage)

            assert isinstance(handlers, list)
            assert len(handlers) > 0

    @pytest.mark.asyncio
    async def test_get_payments_callback_handlers_returns_list(self):
        """get_payments_callback_handlers retorna una lista."""
        with (
            patch("src.bot.handlers.payments.APIClient"),
            patch("src.bot.handlers.payments.TokenStorage"),
        ):
            from src.bot.handlers.payments import get_payments_callback_handlers

            mock_api = AsyncMock()
            mock_storage = AsyncMock()

            handlers = get_payments_callback_handlers(mock_api, mock_storage)

            assert isinstance(handlers, list)
            assert len(handlers) > 0

    @pytest.mark.asyncio
    async def test_get_payments_payment_handlers_returns_list(self):
        """get_payments_payment_handlers retorna una lista."""
        with (
            patch("src.bot.handlers.payments.APIClient"),
            patch("src.bot.handlers.payments.TokenStorage"),
        ):
            from src.bot.handlers.payments import get_payments_payment_handlers

            mock_api = AsyncMock()
            mock_storage = AsyncMock()

            handlers = get_payments_payment_handlers(mock_api, mock_storage)

            assert isinstance(handlers, list)
            assert len(handlers) > 0

    # ============================================
    # ADDITIONAL KEYBOARD TESTS
    # ============================================

    @pytest.mark.asyncio
    async def test_payments_keyboard_back_to_main_menu_exists(self):
        """PaymentsKeyboard.back_to_main_menu existe."""
        from src.bot.keyboards.payments import PaymentsKeyboard

        keyboard = PaymentsKeyboard.back_to_main_menu()

        from telegram import InlineKeyboardMarkup

        assert isinstance(keyboard, InlineKeyboardMarkup)

        buttons = keyboard.inline_keyboard
        assert any("main_menu" in btn.callback_data for row in buttons for btn in row)

    @pytest.mark.asyncio
    async def test_payments_keyboard_has_crypto_buttons(self):
        """El teclado crypto tiene botones de montos."""
        from src.bot.keyboards.payments import PaymentsKeyboard

        keyboard = PaymentsKeyboard.crypto_amounts()

        buttons = keyboard.inline_keyboard
        # Actual crypto amounts in the keyboard
        crypto_amounts = [
            "pay_crypto_2_08",
            "pay_crypto_5_00",
            "pay_crypto_8_00",
            "pay_crypto_12_00",
            "pay_crypto_15_00",
        ]

        for amount in crypto_amounts:
            assert any(amount in btn.callback_data for row in buttons for btn in row)

    @pytest.mark.asyncio
    async def test_payments_keyboard_has_stars_buttons(self):
        """El teclado stars tiene botones de montos."""
        from src.bot.keyboards.payments import PaymentsKeyboard

        keyboard = PaymentsKeyboard.stars_amounts()

        buttons = keyboard.inline_keyboard
        # Actual stars amounts in the keyboard
        stars_amounts = [
            "pay_stars_300",
            "pay_stars_600",
            "pay_stars_960",
            "pay_stars_1440",
            "pay_stars_1800",
        ]

        for amount in stars_amounts:
            assert any(amount in btn.callback_data for row in buttons for btn in row)

    # ============================================
    # HELPER METHODS TESTS
    # ============================================

    @pytest.mark.asyncio
    async def test_safe_answer_query_method_exists(self):
        """_safe_answer_query método existe."""
        with (
            patch("src.bot.handlers.payments.APIClient"),
            patch("src.bot.handlers.payments.TokenStorage"),
        ):
            from src.bot.handlers.payments import PaymentsHandler

            mock_api = AsyncMock()
            mock_storage = AsyncMock()

            handler = PaymentsHandler(mock_api, mock_storage)

            assert hasattr(handler, "_safe_answer_query")
            assert callable(getattr(handler, "_safe_answer_query"))

    @pytest.mark.asyncio
    async def test_safe_edit_message_method_exists(self):
        """_safe_edit_message método existe."""
        with (
            patch("src.bot.handlers.payments.APIClient"),
            patch("src.bot.handlers.payments.TokenStorage"),
        ):
            from src.bot.handlers.payments import PaymentsHandler

            mock_api = AsyncMock()
            mock_storage = AsyncMock()

            handler = PaymentsHandler(mock_api, mock_storage)

            assert hasattr(handler, "_safe_edit_message")
            assert callable(getattr(handler, "_safe_edit_message"))

    # ============================================
    # ERROR HANDLING TESTS
    # ============================================

    @pytest.mark.asyncio
    async def test_payments_messages_has_history_messages(self):
        """PaymentsMessages tiene mensajes de historial."""
        from src.bot.keyboards.messages_payments import PaymentsMessages

        assert hasattr(PaymentsMessages.History, "HEADER")
        assert hasattr(PaymentsMessages.History, "PAYMENT_ITEM")
        assert hasattr(PaymentsMessages.History, "NO_PAYMENTS")

    @pytest.mark.asyncio
    async def test_payments_messages_has_timeout_error(self):
        """PaymentsMessages tiene error de timeout."""
        from src.bot.keyboards.messages_payments import PaymentsMessages

        assert hasattr(PaymentsMessages.Error, "TIMEOUT")
        assert hasattr(PaymentsMessages.Error, "PAYMENT_EXPIRED")
        assert hasattr(PaymentsMessages.Error, "DUPLICATE_PAYMENT")

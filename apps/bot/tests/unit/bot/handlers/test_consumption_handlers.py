"""Tests para Consumption Billing Handlers."""

import pytest
from unittest.mock import patch, AsyncMock


class TestConsumptionHandler:
    """Tests para ConsumptionHandler."""

    @pytest.mark.asyncio
    async def test_consumption_handler_initialization(self):
        """ConsumptionHandler se inicializa correctamente."""
        with (
            patch("src.bot.handlers.consumption.APIClient"),
            patch("src.bot.handlers.consumption.TokenStorage"),
        ):
            from src.bot.handlers.consumption import ConsumptionHandler

            mock_api = AsyncMock()
            mock_storage = AsyncMock()

            handler = ConsumptionHandler(mock_api, mock_storage)

            assert handler.api == mock_api
            assert handler.tokens == mock_storage

    @pytest.mark.asyncio
    async def test_consumption_messages_constants_exist(self):
        """ConsumptionMessages constants están definidas."""
        from src.bot.keyboards.messages_consumption import ConsumptionMessages

        assert hasattr(ConsumptionMessages, "Menu")
        assert hasattr(ConsumptionMessages, "Activation")
        assert hasattr(ConsumptionMessages, "Cancellation")
        assert hasattr(ConsumptionMessages, "Status")
        assert hasattr(ConsumptionMessages, "Invoices")
        assert hasattr(ConsumptionMessages, "Error")
        assert hasattr(ConsumptionMessages, "Invoice")

    @pytest.mark.asyncio
    async def test_consumption_messages_has_menu_messages(self):
        """ConsumptionMessages tiene mensajes de menú."""
        from src.bot.keyboards.messages_consumption import ConsumptionMessages

        assert hasattr(ConsumptionMessages.Menu, "MAIN_MENU")
        assert hasattr(ConsumptionMessages.Menu, "INACTIVE_STATE")
        assert hasattr(ConsumptionMessages.Menu, "ACTIVE_STATE")
        assert hasattr(ConsumptionMessages.Menu, "DEBT_STATE")
        assert hasattr(ConsumptionMessages.Menu, "STATUS_INACTIVE")
        assert hasattr(ConsumptionMessages.Menu, "STATUS_ACTIVE")
        assert hasattr(ConsumptionMessages.Menu, "STATUS_DEBT")

    @pytest.mark.asyncio
    async def test_consumption_messages_has_activation_messages(self):
        """ConsumptionMessages tiene mensajes de activación."""
        from src.bot.keyboards.messages_consumption import ConsumptionMessages

        assert hasattr(ConsumptionMessages.Activation, "TERMS")
        assert hasattr(ConsumptionMessages.Activation, "CONFIRMATION_PROMPT")
        assert hasattr(ConsumptionMessages.Activation, "SUCCESS")
        assert hasattr(ConsumptionMessages.Activation, "FAILED")
        assert hasattr(ConsumptionMessages.Activation, "ALREADY_ACTIVE")
        assert hasattr(ConsumptionMessages.Activation, "CANNOT_ACTIVATE")

    @pytest.mark.asyncio
    async def test_consumption_messages_has_cancellation_messages(self):
        """ConsumptionMessages tiene mensajes de cancelación."""
        from src.bot.keyboards.messages_consumption import ConsumptionMessages

        assert hasattr(ConsumptionMessages.Cancellation, "CONFIRMATION_HEADER")
        assert hasattr(ConsumptionMessages.Cancellation, "SUMMARY_WITH_DEBT")
        assert hasattr(ConsumptionMessages.Cancellation, "SUMMARY_NO_DEBT")
        assert hasattr(ConsumptionMessages.Cancellation, "SUCCESS_WITH_DEBT")
        assert hasattr(ConsumptionMessages.Cancellation, "SUCCESS_NO_DEBT")
        assert hasattr(ConsumptionMessages.Cancellation, "FAILED")
        assert hasattr(ConsumptionMessages.Cancellation, "CANNOT_CANCEL")

    @pytest.mark.asyncio
    async def test_consumption_messages_has_status_messages(self):
        """ConsumptionMessages tiene mensajes de estado."""
        from src.bot.keyboards.messages_consumption import ConsumptionMessages

        assert hasattr(ConsumptionMessages.Status, "ACTIVE")
        assert hasattr(ConsumptionMessages.Status, "INACTIVE")
        assert hasattr(ConsumptionMessages.Status, "CLOSED_CYCLE")

    @pytest.mark.asyncio
    async def test_consumption_messages_has_invoices_messages(self):
        """ConsumptionMessages tiene mensajes de facturas."""
        from src.bot.keyboards.messages_consumption import ConsumptionMessages

        assert hasattr(ConsumptionMessages.Invoices, "HEADER")
        assert hasattr(ConsumptionMessages.Invoices, "INVOICE_ITEM")
        assert hasattr(ConsumptionMessages.Invoices, "NO_INVOICES")

    @pytest.mark.asyncio
    async def test_consumption_messages_has_error_messages(self):
        """ConsumptionMessages tiene mensajes de error."""
        from src.bot.keyboards.messages_consumption import ConsumptionMessages

        assert hasattr(ConsumptionMessages.Error, "GENERIC")
        assert hasattr(ConsumptionMessages.Error, "SYSTEM_ERROR")
        assert hasattr(ConsumptionMessages.Error, "NOT_AUTHENTICATED")
        assert hasattr(ConsumptionMessages.Error, "UNAUTHORIZED")
        assert hasattr(ConsumptionMessages.Error, "INVOICE_GENERATION")
        assert hasattr(ConsumptionMessages.Error, "PAYMENT_PROCESSING")

    @pytest.mark.asyncio
    async def test_consumption_messages_has_invoice_payment_messages(self):
        """ConsumptionMessages tiene mensajes de pago de facturas."""
        from src.bot.keyboards.messages_consumption import ConsumptionMessages

        assert hasattr(ConsumptionMessages.Invoice, "SELECT_PAYMENT_METHOD")
        assert hasattr(ConsumptionMessages.Invoice, "CRYPTO_PAYMENT")
        assert hasattr(ConsumptionMessages.Invoice, "STARS_PAYMENT")
        assert hasattr(ConsumptionMessages.Invoice, "PAYMENT_SUCCESS")
        assert hasattr(ConsumptionMessages.Invoice, "PAYMENT_EXPIRED")
        assert hasattr(ConsumptionMessages.Invoice, "NO_PENDING_DEBT")

    @pytest.mark.asyncio
    async def test_consumption_messages_main_menu_has_placeholders(self):
        """El mensaje del menú principal tiene placeholders."""
        from src.bot.keyboards.messages_consumption import ConsumptionMessages

        assert "{status_text}" in ConsumptionMessages.Menu.MAIN_MENU

    @pytest.mark.asyncio
    async def test_consumption_messages_active_state_has_placeholders(self):
        """El mensaje de estado activo tiene placeholders."""
        from src.bot.keyboards.messages_consumption import ConsumptionMessages

        assert "{gb_consumed}" in ConsumptionMessages.Menu.ACTIVE_STATE
        assert "{cost}" in ConsumptionMessages.Menu.ACTIVE_STATE
        assert "{days_remaining}" in ConsumptionMessages.Menu.ACTIVE_STATE

    @pytest.mark.asyncio
    async def test_consumption_messages_debt_state_has_placeholders(self):
        """El mensaje de estado con deuda tiene placeholders."""
        from src.bot.keyboards.messages_consumption import ConsumptionMessages

        assert "{debt_amount}" in ConsumptionMessages.Menu.DEBT_STATE

    @pytest.mark.asyncio
    async def test_consumption_messages_activation_terms_has_price_placeholder(self):
        """El mensaje de términos de activación tiene placeholders de precio."""
        from src.bot.keyboards.messages_consumption import ConsumptionMessages

        assert (
            "{_CONSUMPTION_PRICE_PER_GB:.2f}" in ConsumptionMessages.Activation.TERMS
            or "USD por GB" in ConsumptionMessages.Activation.TERMS
        )

    @pytest.mark.asyncio
    async def test_consumption_messages_activation_failed_has_placeholder(self):
        """El mensaje de activación fallida tiene placeholder."""
        from src.bot.keyboards.messages_consumption import ConsumptionMessages

        assert "{reason}" in ConsumptionMessages.Activation.FAILED

    @pytest.mark.asyncio
    async def test_consumption_messages_activation_cannot_activate_has_placeholder(self):
        """El mensaje de no poder activar tiene placeholder."""
        from src.bot.keyboards.messages_consumption import ConsumptionMessages

        assert "{reason}" in ConsumptionMessages.Activation.CANNOT_ACTIVATE

    @pytest.mark.asyncio
    async def test_consumption_messages_status_active_has_placeholders(self):
        """El mensaje de estado activo tiene placeholders."""
        from src.bot.keyboards.messages_consumption import ConsumptionMessages

        assert "{days_active}" in ConsumptionMessages.Status.ACTIVE
        assert "{gb_consumed}" in ConsumptionMessages.Status.ACTIVE
        assert "{mb_consumed}" in ConsumptionMessages.Status.ACTIVE
        assert "{cost}" in ConsumptionMessages.Status.ACTIVE
        assert "{days_remaining}" in ConsumptionMessages.Status.ACTIVE

    @pytest.mark.asyncio
    async def test_consumption_messages_cancellation_summary_with_debt_has_placeholders(self):
        """El mensaje de resumen con deuda tiene placeholders."""
        from src.bot.keyboards.messages_consumption import ConsumptionMessages

        assert "{days_active}" in ConsumptionMessages.Cancellation.SUMMARY_WITH_DEBT
        assert "{gb_consumed}" in ConsumptionMessages.Cancellation.SUMMARY_WITH_DEBT
        assert "{cost}" in ConsumptionMessages.Cancellation.SUMMARY_WITH_DEBT

    @pytest.mark.asyncio
    async def test_consumption_messages_cancellation_summary_no_debt_has_placeholders(self):
        """El mensaje de resumen sin deuda tiene placeholders."""
        from src.bot.keyboards.messages_consumption import ConsumptionMessages

        assert "{days_active}" in ConsumptionMessages.Cancellation.SUMMARY_NO_DEBT

    @pytest.mark.asyncio
    async def test_consumption_messages_invoices_header_has_placeholders(self):
        """El mensaje de cabecera de facturas tiene placeholders."""
        from src.bot.keyboards.messages_consumption import ConsumptionMessages

        assert "{total}" in ConsumptionMessages.Invoices.HEADER
        assert "{pending}" in ConsumptionMessages.Invoices.HEADER
        assert "{paid}" in ConsumptionMessages.Invoices.HEADER
        assert "{expired}" in ConsumptionMessages.Invoices.HEADER

    @pytest.mark.asyncio
    async def test_consumption_messages_invoice_item_has_placeholders(self):
        """El mensaje de item de factura tiene placeholders."""
        from src.bot.keyboards.messages_consumption import ConsumptionMessages

        assert "{date}" in ConsumptionMessages.Invoices.INVOICE_ITEM
        assert "{amount}" in ConsumptionMessages.Invoices.INVOICE_ITEM
        assert "{status}" in ConsumptionMessages.Invoices.INVOICE_ITEM
        assert "{status_text}" in ConsumptionMessages.Invoices.INVOICE_ITEM

    @pytest.mark.asyncio
    async def test_consumption_keyboard_main_menu_exists(self):
        """ConsumptionKeyboard.consumption_main_menu existe."""
        from src.bot.keyboards.consumption import ConsumptionKeyboard

        assert hasattr(ConsumptionKeyboard, "consumption_main_menu")
        assert callable(getattr(ConsumptionKeyboard, "consumption_main_menu"))

    @pytest.mark.asyncio
    async def test_consumption_keyboard_main_menu_returns_inline_keyboard(self):
        """consumption_main_menu retorna InlineKeyboardMarkup."""
        from telegram import InlineKeyboardMarkup
        from src.bot.keyboards.consumption import ConsumptionKeyboard

        keyboard = ConsumptionKeyboard.consumption_main_menu(
            is_active=False, has_debt=False, can_activate=True
        )

        assert isinstance(keyboard, InlineKeyboardMarkup)

    @pytest.mark.asyncio
    async def test_consumption_keyboard_main_menu_with_inactive_state(self):
        """consumption_main_menu con estado inactivo muestra activación."""
        from src.bot.keyboards.consumption import ConsumptionKeyboard

        keyboard = ConsumptionKeyboard.consumption_main_menu(
            is_active=False, has_debt=False, can_activate=True
        )

        buttons = keyboard.inline_keyboard
        assert any("Activar" in btn.text or "⚡" in btn.text for row in buttons for btn in row)

    @pytest.mark.asyncio
    async def test_consumption_keyboard_main_menu_with_active_state(self):
        """consumption_main_menu con estado activo muestra ver consumo y cancelar."""
        from src.bot.keyboards.consumption import ConsumptionKeyboard

        keyboard = ConsumptionKeyboard.consumption_main_menu(
            is_active=True, has_debt=False, can_activate=False
        )

        buttons = keyboard.inline_keyboard
        assert any("Consumo" in btn.text or "📊" in btn.text for row in buttons for btn in row)
        assert any("Cancelar" in btn.text or "🚫" in btn.text for row in buttons for btn in row)

    @pytest.mark.asyncio
    async def test_consumption_keyboard_main_menu_with_debt_state(self):
        """consumption_main_menu con deuda muestra generar factura."""
        from src.bot.keyboards.consumption import ConsumptionKeyboard

        keyboard = ConsumptionKeyboard.consumption_main_menu(
            is_active=False, has_debt=True, can_activate=False
        )

        buttons = keyboard.inline_keyboard
        assert any("Factura" in btn.text or "💳" in btn.text for row in buttons for btn in row)

    @pytest.mark.asyncio
    async def test_consumption_keyboard_activation_confirmation_exists(self):
        """ConsumptionKeyboard.activation_confirmation existe."""
        from src.bot.keyboards.consumption import ConsumptionKeyboard

        keyboard = ConsumptionKeyboard.activation_confirmation()

        from telegram import InlineKeyboardMarkup

        assert isinstance(keyboard, InlineKeyboardMarkup)

        buttons = keyboard.inline_keyboard
        assert any("Acepto" in btn.text or "✅" in btn.text for row in buttons for btn in row)
        assert any("Cancelar" in btn.text or "❌" in btn.text for row in buttons for btn in row)

    @pytest.mark.asyncio
    async def test_consumption_keyboard_activation_success_exists(self):
        """ConsumptionKeyboard.activation_success existe."""
        from src.bot.keyboards.consumption import ConsumptionKeyboard

        keyboard = ConsumptionKeyboard.activation_success()

        from telegram import InlineKeyboardMarkup

        assert isinstance(keyboard, InlineKeyboardMarkup)

    @pytest.mark.asyncio
    async def test_consumption_keyboard_cancellation_confirmation_exists(self):
        """ConsumptionKeyboard.cancellation_confirmation existe."""
        from src.bot.keyboards.consumption import ConsumptionKeyboard

        keyboard = ConsumptionKeyboard.cancellation_confirmation(has_debt=False)

        from telegram import InlineKeyboardMarkup

        assert isinstance(keyboard, InlineKeyboardMarkup)

        buttons = keyboard.inline_keyboard
        assert any("Cancelar" in btn.text or "✅" in btn.text for row in buttons for btn in row)
        assert any("Volver" in btn.text or "❌" in btn.text for row in buttons for btn in row)

    @pytest.mark.asyncio
    async def test_consumption_keyboard_cancellation_success_exists(self):
        """ConsumptionKeyboard.cancellation_success existe."""
        from src.bot.keyboards.consumption import ConsumptionKeyboard

        keyboard = ConsumptionKeyboard.cancellation_success()

        from telegram import InlineKeyboardMarkup

        assert isinstance(keyboard, InlineKeyboardMarkup)

    @pytest.mark.asyncio
    async def test_consumption_keyboard_consumption_status_exists(self):
        """ConsumptionKeyboard.consumption_status existe."""
        from src.bot.keyboards.consumption import ConsumptionKeyboard

        keyboard = ConsumptionKeyboard.consumption_status()

        from telegram import InlineKeyboardMarkup

        assert isinstance(keyboard, InlineKeyboardMarkup)

    @pytest.mark.asyncio
    async def test_consumption_keyboard_invoices_list_exists(self):
        """ConsumptionKeyboard.invoices_list existe."""
        from src.bot.keyboards.consumption import ConsumptionKeyboard

        keyboard = ConsumptionKeyboard.invoices_list(has_next=False, page=0)

        from telegram import InlineKeyboardMarkup

        assert isinstance(keyboard, InlineKeyboardMarkup)

    @pytest.mark.asyncio
    async def test_consumption_keyboard_invoices_list_with_pagination(self):
        """invoices_list muestra paginación correctamente."""
        from src.bot.keyboards.consumption import ConsumptionKeyboard

        keyboard = ConsumptionKeyboard.invoices_list(has_next=True, page=1)

        buttons = keyboard.inline_keyboard
        assert any("Anterior" in btn.text or "◀️" in btn.text for row in buttons for btn in row)
        assert any("Siguiente" in btn.text or "▶️" in btn.text for row in buttons for btn in row)

    @pytest.mark.asyncio
    async def test_consumption_keyboard_back_to_consumption_menu_exists(self):
        """ConsumptionKeyboard.back_to_consumption_menu existe."""
        from src.bot.keyboards.consumption import ConsumptionKeyboard

        keyboard = ConsumptionKeyboard.back_to_consumption_menu()

        from telegram import InlineKeyboardMarkup

        assert isinstance(keyboard, InlineKeyboardMarkup)

    @pytest.mark.asyncio
    async def test_consumption_keyboard_back_to_menu_exists(self):
        """ConsumptionKeyboard.back_to_menu existe."""
        from src.bot.keyboards.consumption import ConsumptionKeyboard

        keyboard = ConsumptionKeyboard.back_to_menu()

        from telegram import InlineKeyboardMarkup

        assert isinstance(keyboard, InlineKeyboardMarkup)

    @pytest.mark.asyncio
    async def test_consumption_keyboard_inactive_state_menu_exists(self):
        """ConsumptionKeyboard.inactive_state_menu existe."""
        from src.bot.keyboards.consumption import ConsumptionKeyboard

        keyboard = ConsumptionKeyboard.inactive_state_menu()

        from telegram import InlineKeyboardMarkup

        assert isinstance(keyboard, InlineKeyboardMarkup)

    @pytest.mark.asyncio
    async def test_consumption_keyboard_active_state_menu_exists(self):
        """ConsumptionKeyboard.active_state_menu existe."""
        from src.bot.keyboards.consumption import ConsumptionKeyboard

        keyboard = ConsumptionKeyboard.active_state_menu()

        from telegram import InlineKeyboardMarkup

        assert isinstance(keyboard, InlineKeyboardMarkup)

    @pytest.mark.asyncio
    async def test_consumption_keyboard_debt_state_menu_exists(self):
        """ConsumptionKeyboard.debt_state_menu existe."""
        from src.bot.keyboards.consumption import ConsumptionKeyboard

        keyboard = ConsumptionKeyboard.debt_state_menu()

        from telegram import InlineKeyboardMarkup

        assert isinstance(keyboard, InlineKeyboardMarkup)

    @pytest.mark.asyncio
    async def test_consumption_handler_get_auth_headers(self):
        """_get_auth_headers retorna headers con token."""
        with (
            patch("src.bot.handlers.consumption.APIClient"),
            patch("src.bot.handlers.consumption.TokenStorage"),
        ):
            from src.bot.handlers.consumption import ConsumptionHandler

            mock_api = AsyncMock()
            mock_storage = AsyncMock()
            mock_storage.get.return_value = {"access_token": "test-token-123"}

            handler = ConsumptionHandler(mock_api, mock_storage)

            headers = await handler._get_auth_headers(telegram_id=123)

            assert "Authorization" in headers
            assert headers["Authorization"] == "Bearer test-token-123"

    @pytest.mark.asyncio
    async def test_consumption_handler_get_auth_headers_unauthenticated(self):
        """_get_auth_headers lanza error si no está autenticado."""
        with (
            patch("src.bot.handlers.consumption.APIClient"),
            patch("src.bot.handlers.consumption.TokenStorage"),
        ):
            from src.bot.handlers.consumption import ConsumptionHandler

            mock_api = AsyncMock()
            mock_storage = AsyncMock()
            mock_storage.get.return_value = None

            handler = ConsumptionHandler(mock_api, mock_storage)

            with pytest.raises(PermissionError):
                await handler._get_auth_headers(telegram_id=123)

    @pytest.mark.asyncio
    async def test_get_consumption_handlers_returns_list(self):
        """get_consumption_handlers retorna una lista."""
        with (
            patch("src.bot.handlers.consumption.APIClient"),
            patch("src.bot.handlers.consumption.TokenStorage"),
        ):
            from src.bot.handlers.consumption import get_consumption_handlers

            mock_api = AsyncMock()
            mock_storage = AsyncMock()

            handlers = get_consumption_handlers(mock_api, mock_storage)

            assert isinstance(handlers, list)
            assert len(handlers) > 0

    @pytest.mark.asyncio
    async def test_get_consumption_callback_handlers_returns_list(self):
        """get_consumption_callback_handlers retorna una lista."""
        with (
            patch("src.bot.handlers.consumption.APIClient"),
            patch("src.bot.handlers.consumption.TokenStorage"),
        ):
            from src.bot.handlers.consumption import get_consumption_callback_handlers

            mock_api = AsyncMock()
            mock_storage = AsyncMock()

            handlers = get_consumption_callback_handlers(mock_api, mock_storage)

            assert isinstance(handlers, list)
            assert len(handlers) > 0

    @pytest.mark.asyncio
    async def test_consumption_messages_price_per_gb_constant_exists(self):
        """ConsumptionMessages tiene constante PRICE_PER_GB."""
        from src.bot.keyboards.messages_consumption import ConsumptionMessages

        assert hasattr(ConsumptionMessages, "PRICE_PER_GB")
        assert isinstance(ConsumptionMessages.PRICE_PER_GB, (int, float))
        assert ConsumptionMessages.PRICE_PER_GB > 0

    @pytest.mark.asyncio
    async def test_consumption_keyboard_cancellation_confirmation_with_debt(self):
        """cancellation_confirmation con deuda se genera correctamente."""
        from src.bot.keyboards.consumption import ConsumptionKeyboard

        keyboard = ConsumptionKeyboard.cancellation_confirmation(has_debt=True)

        from telegram import InlineKeyboardMarkup

        assert isinstance(keyboard, InlineKeyboardMarkup)

        buttons = keyboard.inline_keyboard
        assert len(buttons) > 0

    @pytest.mark.asyncio
    async def test_consumption_messages_already_active_has_placeholder(self):
        """El mensaje de ya estar activo tiene placeholders."""
        from src.bot.keyboards.messages_consumption import ConsumptionMessages

        assert hasattr(ConsumptionMessages.Activation, "ALREADY_ACTIVE")
        assert "{days_remaining}" in ConsumptionMessages.Activation.ALREADY_ACTIVE

    @pytest.mark.asyncio
    async def test_consumption_messages_closed_cycle_has_placeholders(self):
        """El mensaje de ciclo cerrado tiene placeholders."""
        from src.bot.keyboards.messages_consumption import ConsumptionMessages

        assert "{gb_consumed}" in ConsumptionMessages.Status.CLOSED_CYCLE
        assert "{cost}" in ConsumptionMessages.Status.CLOSED_CYCLE

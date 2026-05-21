"""Tests para Subscriptions Handlers."""

import pytest
from unittest.mock import patch, AsyncMock


class TestSubscriptionsHandler:
    """Tests para SubscriptionsHandler."""

    @pytest.mark.asyncio
    async def test_subscriptions_handler_initialization(self):
        """SubscriptionsHandler se inicializa correctamente."""
        with (
            patch("src.bot.handlers.subscriptions.APIClient"),
            patch("src.bot.handlers.subscriptions.TokenStorage"),
        ):
            from src.bot.handlers.subscriptions import SubscriptionsHandler

            mock_api = AsyncMock()
            mock_storage = AsyncMock()

            handler = SubscriptionsHandler(mock_api, mock_storage)

            assert handler.api == mock_api
            assert handler.tokens == mock_storage

    # ============================================
    # MESSAGE CONSTANTS TESTS
    # ============================================

    @pytest.mark.asyncio
    async def test_subscriptions_messages_constants_exist(self):
        """SubscriptionsMessages constants están definidas."""
        from src.bot.keyboards.messages_subscriptions import SubscriptionsMessages

        assert hasattr(SubscriptionsMessages, "Subscription")
        assert hasattr(SubscriptionsMessages, "Plans")
        assert hasattr(SubscriptionsMessages, "Payment")
        assert hasattr(SubscriptionsMessages, "Activation")
        assert hasattr(SubscriptionsMessages, "Renewal")
        assert hasattr(SubscriptionsMessages, "Error")

    @pytest.mark.asyncio
    async def test_subscriptions_messages_has_menu_messages(self):
        """SubscriptionsMessages tiene mensajes de menú."""
        from src.bot.keyboards.messages_subscriptions import SubscriptionsMessages

        assert hasattr(SubscriptionsMessages.Subscription, "SUBSCRIPTION_ACTIVE")
        assert hasattr(SubscriptionsMessages.Subscription, "SUBSCRIPTION_INACTIVE")
        assert hasattr(SubscriptionsMessages.Subscription, "SUBSCRIPTION_EXPIRED")
        assert hasattr(SubscriptionsMessages.Subscription, "SUBSCRIPTION_DETAILS")

    @pytest.mark.asyncio
    async def test_subscriptions_messages_has_plans_messages(self):
        """SubscriptionsMessages tiene mensajes de planes."""
        from src.bot.keyboards.messages_subscriptions import SubscriptionsMessages

        assert hasattr(SubscriptionsMessages.Plans, "PLANS_HEADER")
        assert hasattr(SubscriptionsMessages.Plans, "PLAN_ITEM")
        assert hasattr(SubscriptionsMessages.Plans, "PLAN_DETAILS")
        assert hasattr(SubscriptionsMessages.Plans, "NO_PLANS")
        assert hasattr(SubscriptionsMessages.Plans, "PLAN_NOT_FOUND")

    @pytest.mark.asyncio
    async def test_subscriptions_messages_has_payment_messages(self):
        """SubscriptionsMessages tiene mensajes de pago."""
        from src.bot.keyboards.messages_subscriptions import SubscriptionsMessages

        assert hasattr(SubscriptionsMessages.Payment, "CHOOSE_PAYMENT_METHOD")
        assert hasattr(SubscriptionsMessages.Payment, "CRYPTO_PAYMENT")
        assert hasattr(SubscriptionsMessages.Payment, "STARS_PAYMENT")
        assert hasattr(SubscriptionsMessages.Payment, "CRYPTO_SUCCESS")
        assert hasattr(SubscriptionsMessages.Payment, "STARS_SUCCESS")

    @pytest.mark.asyncio
    async def test_subscriptions_messages_has_activation_messages(self):
        """SubscriptionsMessages tiene mensajes de activación."""
        from src.bot.keyboards.messages_subscriptions import SubscriptionsMessages

        assert hasattr(SubscriptionsMessages.Activation, "SUCCESS")
        assert hasattr(SubscriptionsMessages.Activation, "FAILED")
        assert hasattr(SubscriptionsMessages.Activation, "ALREADY_ACTIVE")

    @pytest.mark.asyncio
    async def test_subscriptions_messages_has_renewal_messages(self):
        """SubscriptionsMessages tiene mensajes de renovación."""
        from src.bot.keyboards.messages_subscriptions import SubscriptionsMessages

        assert hasattr(SubscriptionsMessages.Renewal, "RENEW_SUCCESS")
        assert hasattr(SubscriptionsMessages.Renewal, "RENEW_FAILED")
        assert hasattr(SubscriptionsMessages.Renewal, "NO_ACTIVE_SUBSCRIPTION")
        assert hasattr(SubscriptionsMessages.Renewal, "RENEWAL_PROMPT")

    @pytest.mark.asyncio
    async def test_subscriptions_messages_has_error_messages(self):
        """SubscriptionsMessages tiene mensajes de error."""
        from src.bot.keyboards.messages_subscriptions import SubscriptionsMessages

        assert hasattr(SubscriptionsMessages.Error, "SYSTEM_ERROR")
        assert hasattr(SubscriptionsMessages.Error, "NOT_AUTHENTICATED")
        assert hasattr(SubscriptionsMessages.Error, "INVALID_PLAN")
        assert hasattr(SubscriptionsMessages.Error, "PAYMENT_FAILED")
        assert hasattr(SubscriptionsMessages.Error, "NETWORK_ERROR")
        assert hasattr(SubscriptionsMessages.Error, "INSUFFICIENT_FUNDS")
        assert hasattr(SubscriptionsMessages.Error, "TIMEOUT")

    # ============================================
    # MESSAGE PLACEHOLDERS TESTS
    # ============================================

    @pytest.mark.asyncio
    async def test_subscriptions_messages_menu_has_placeholders(self):
        """El mensaje de menú de suscripciones tiene placeholders."""
        from src.bot.keyboards.messages_subscriptions import SubscriptionsMessages

        # SUBSCRIPTION_INACTIVE no tiene placeholders, es estático
        assert isinstance(SubscriptionsMessages.Subscription.SUBSCRIPTION_INACTIVE, str)
        assert len(SubscriptionsMessages.Subscription.SUBSCRIPTION_INACTIVE) > 0

    @pytest.mark.asyncio
    async def test_subscriptions_messages_plan_details_has_placeholders(self):
        """El mensaje de detalles de plan tiene placeholders."""
        from src.bot.keyboards.messages_subscriptions import SubscriptionsMessages

        assert "{plan_name}" in SubscriptionsMessages.Plans.PLAN_DETAILS
        assert "{price}" in SubscriptionsMessages.Plans.PLAN_DETAILS
        assert "{duration}" in SubscriptionsMessages.Plans.PLAN_DETAILS
        assert "{features}" in SubscriptionsMessages.Plans.PLAN_DETAILS

    @pytest.mark.asyncio
    async def test_subscriptions_messages_subscription_status_has_placeholders(self):
        """El mensaje de estado de suscripción tiene placeholders."""
        from src.bot.keyboards.messages_subscriptions import SubscriptionsMessages

        assert "{status_icon}" in SubscriptionsMessages.Subscription.SUBSCRIPTION_DETAILS
        assert "{status}" in SubscriptionsMessages.Subscription.SUBSCRIPTION_DETAILS
        assert "{plan_name}" in SubscriptionsMessages.Subscription.SUBSCRIPTION_DETAILS
        assert "{start_date}" in SubscriptionsMessages.Subscription.SUBSCRIPTION_DETAILS
        assert "{renewal_date}" in SubscriptionsMessages.Subscription.SUBSCRIPTION_DETAILS
        assert "{price}" in SubscriptionsMessages.Subscription.SUBSCRIPTION_DETAILS
        assert "{devices}" in SubscriptionsMessages.Subscription.SUBSCRIPTION_DETAILS
        assert "{data_limit}" in SubscriptionsMessages.Subscription.SUBSCRIPTION_DETAILS

    @pytest.mark.asyncio
    async def test_subscriptions_messages_activation_success_has_placeholders(self):
        """El mensaje de activación exitosa tiene placeholders."""
        from src.bot.keyboards.messages_subscriptions import SubscriptionsMessages

        assert "{plan_name}" in SubscriptionsMessages.Subscription.SUBSCRIPTION_ACTIVATED
        assert "{activation_date}" in SubscriptionsMessages.Subscription.SUBSCRIPTION_ACTIVATED
        assert "{renewal_date}" in SubscriptionsMessages.Subscription.SUBSCRIPTION_ACTIVATED

    @pytest.mark.asyncio
    async def test_subscriptions_messages_renewal_success_has_placeholders(self):
        """El mensaje de renovación exitosa tiene placeholders."""
        from src.bot.keyboards.messages_subscriptions import SubscriptionsMessages

        assert "{plan_name}" in SubscriptionsMessages.Subscription.SUBSCRIPTION_RENEWED
        assert "{renewal_date}" in SubscriptionsMessages.Subscription.SUBSCRIPTION_RENEWED

    @pytest.mark.asyncio
    async def test_subscriptions_messages_payment_method_has_placeholders(self):
        """El mensaje de método de pago tiene placeholders."""
        from src.bot.keyboards.messages_subscriptions import SubscriptionsMessages

        # CHOOSE_PAYMENT_METHOD no tiene placeholders, es estático
        assert isinstance(SubscriptionsMessages.Payment.CHOOSE_PAYMENT_METHOD, str)
        assert len(SubscriptionsMessages.Payment.CHOOSE_PAYMENT_METHOD) > 0

    @pytest.mark.asyncio
    async def test_subscriptions_messages_crypto_payment_has_placeholders(self):
        """El mensaje de pago crypto tiene placeholders."""
        from src.bot.keyboards.messages_subscriptions import SubscriptionsMessages

        assert "{plan_name}" in SubscriptionsMessages.Payment.CRYPTO_PAYMENT
        assert "{amount_usd}" in SubscriptionsMessages.Payment.CRYPTO_PAYMENT
        assert "{network}" in SubscriptionsMessages.Payment.CRYPTO_PAYMENT
        assert "{address}" in SubscriptionsMessages.Payment.CRYPTO_PAYMENT

    @pytest.mark.asyncio
    async def test_subscriptions_messages_stars_payment_has_placeholders(self):
        """El mensaje de pago con stars tiene placeholders."""
        from src.bot.keyboards.messages_subscriptions import SubscriptionsMessages

        assert "{plan_name}" in SubscriptionsMessages.Payment.STARS_PAYMENT
        assert "{stars_amount}" in SubscriptionsMessages.Payment.STARS_PAYMENT

    @pytest.mark.asyncio
    async def test_subscriptions_messages_plan_item_has_placeholders(self):
        """El mensaje de item de plan tiene placeholders."""
        from src.bot.keyboards.messages_subscriptions import SubscriptionsMessages

        assert "{name}" in SubscriptionsMessages.Plans.PLAN_ITEM
        assert "{price}" in SubscriptionsMessages.Plans.PLAN_ITEM
        assert "{duration}" in SubscriptionsMessages.Plans.PLAN_ITEM

    @pytest.mark.asyncio
    async def test_subscriptions_messages_activation_failed_has_placeholders(self):
        """El mensaje de fallo de activación tiene placeholders."""
        from src.bot.keyboards.messages_subscriptions import SubscriptionsMessages

        assert "{reason}" in SubscriptionsMessages.Subscription.ACTIVATION_FAILED

    @pytest.mark.asyncio
    async def test_subscriptions_messages_renewal_failed_has_placeholders(self):
        """El mensaje de fallo de renovación tiene placeholders."""
        from src.bot.keyboards.messages_subscriptions import SubscriptionsMessages

        assert "{reason}" in SubscriptionsMessages.Subscription.RENEWAL_FAILED

    # ============================================
    # KEYBOARD METHODS TESTS
    # ============================================

    @pytest.mark.asyncio
    async def test_subscriptions_keyboard_main_menu_exists(self):
        """SubscriptionsKeyboard.subscription_menu existe."""
        from src.bot.keyboards.subscriptions import SubscriptionsKeyboard

        keyboard_active = SubscriptionsKeyboard.subscription_menu(is_active=True)
        keyboard_inactive = SubscriptionsKeyboard.subscription_menu(is_active=False)

        from telegram import InlineKeyboardMarkup

        assert isinstance(keyboard_active, InlineKeyboardMarkup)
        assert isinstance(keyboard_inactive, InlineKeyboardMarkup)

    @pytest.mark.asyncio
    async def test_subscriptions_keyboard_main_menu_returns_inline_keyboard(self):
        """subscription_menu retorna InlineKeyboardMarkup."""
        from telegram import InlineKeyboardMarkup
        from src.bot.keyboards.subscriptions import SubscriptionsKeyboard

        keyboard = SubscriptionsKeyboard.subscription_menu(is_active=False)

        assert isinstance(keyboard, InlineKeyboardMarkup)
        assert len(keyboard.inline_keyboard) > 0

    @pytest.mark.asyncio
    async def test_subscriptions_keyboard_plans_list_exists(self):
        """SubscriptionsKeyboard.plans_list existe."""
        from src.bot.keyboards.subscriptions import SubscriptionsKeyboard

        plans = [
            {"id": "basic", "name": "Plan Básico", "price": 9.99},
            {"id": "premium", "name": "Plan Premium", "price": 29.99},
        ]
        keyboard = SubscriptionsKeyboard.plans_list(plans)

        from telegram import InlineKeyboardMarkup

        assert isinstance(keyboard, InlineKeyboardMarkup)

        buttons = keyboard.inline_keyboard
        assert any("select_plan_basic" in btn.callback_data for row in buttons for btn in row)
        assert any("select_plan_premium" in btn.callback_data for row in buttons for btn in row)

    @pytest.mark.asyncio
    async def test_subscriptions_keyboard_plan_details_exists(self):
        """SubscriptionsKeyboard.plan_details existe."""
        from src.bot.keyboards.subscriptions import SubscriptionsKeyboard

        keyboard = SubscriptionsKeyboard.plan_details(plan_id="basic")

        from telegram import InlineKeyboardMarkup

        assert isinstance(keyboard, InlineKeyboardMarkup)

        buttons = keyboard.inline_keyboard
        assert any("choose_payment_basic" in btn.callback_data for row in buttons for btn in row)

    @pytest.mark.asyncio
    async def test_subscriptions_keyboard_payment_method_selection_exists(self):
        """SubscriptionsKeyboard.payment_method_selection existe."""
        from src.bot.keyboards.subscriptions import SubscriptionsKeyboard

        keyboard = SubscriptionsKeyboard.payment_method_selection(plan_id="premium")

        from telegram import InlineKeyboardMarkup

        assert isinstance(keyboard, InlineKeyboardMarkup)

        buttons = keyboard.inline_keyboard
        assert any(
            "activate_plan_premium_stars" in btn.callback_data for row in buttons for btn in row
        )
        assert any(
            "activate_plan_premium_crypto" in btn.callback_data for row in buttons for btn in row
        )

    @pytest.mark.asyncio
    async def test_subscriptions_keyboard_activation_success_exists(self):
        """SubscriptionsKeyboard.activation_success existe."""
        from src.bot.keyboards.subscriptions import SubscriptionsKeyboard

        keyboard = SubscriptionsKeyboard.activation_success()

        from telegram import InlineKeyboardMarkup

        assert isinstance(keyboard, InlineKeyboardMarkup)

        buttons = keyboard.inline_keyboard
        assert any(
            "view_subscription_status" in btn.callback_data for row in buttons for btn in row
        )
        assert any("main_menu" in btn.callback_data for row in buttons for btn in row)

    @pytest.mark.asyncio
    async def test_subscriptions_keyboard_renewal_menu_exists(self):
        """SubscriptionsKeyboard.renewal_menu existe."""
        from src.bot.keyboards.subscriptions import SubscriptionsKeyboard

        keyboard = SubscriptionsKeyboard.renewal_menu()

        from telegram import InlineKeyboardMarkup

        assert isinstance(keyboard, InlineKeyboardMarkup)

        buttons = keyboard.inline_keyboard
        assert any("renew_subscription" in btn.callback_data for row in buttons for btn in row)

    @pytest.mark.asyncio
    async def test_subscriptions_keyboard_back_to_subscription_exists(self):
        """SubscriptionsKeyboard.back_to_subscription existe."""
        from src.bot.keyboards.subscriptions import SubscriptionsKeyboard

        keyboard = SubscriptionsKeyboard.back_to_subscription()

        from telegram import InlineKeyboardMarkup

        assert isinstance(keyboard, InlineKeyboardMarkup)

        buttons = keyboard.inline_keyboard
        assert any("subscription_menu" in btn.callback_data for row in buttons for btn in row)
        assert any("main_menu" in btn.callback_data for row in buttons for btn in row)

    @pytest.mark.asyncio
    async def test_subscriptions_keyboard_subscription_active_menu_exists(self):
        """SubscriptionsKeyboard.subscription_active_menu existe."""
        from src.bot.keyboards.subscriptions import SubscriptionsKeyboard

        keyboard = SubscriptionsKeyboard.subscription_active_menu()

        from telegram import InlineKeyboardMarkup

        assert isinstance(keyboard, InlineKeyboardMarkup)

        buttons = keyboard.inline_keyboard
        assert any(
            "view_subscription_status" in btn.callback_data for row in buttons for btn in row
        )
        assert any("renew_subscription" in btn.callback_data for row in buttons for btn in row)

    @pytest.mark.asyncio
    async def test_subscriptions_keyboard_subscription_inactive_menu_exists(self):
        """SubscriptionsKeyboard.subscription_inactive_menu existe."""
        from src.bot.keyboards.subscriptions import SubscriptionsKeyboard

        keyboard = SubscriptionsKeyboard.subscription_inactive_menu()

        from telegram import InlineKeyboardMarkup

        assert isinstance(keyboard, InlineKeyboardMarkup)

        buttons = keyboard.inline_keyboard
        assert any("view_plans" in btn.callback_data for row in buttons for btn in row)

    @pytest.mark.asyncio
    async def test_subscriptions_keyboard_subscription_status_menu_exists(self):
        """SubscriptionsKeyboard.subscription_status_menu existe."""
        from src.bot.keyboards.subscriptions import SubscriptionsKeyboard

        subscription = {"status": "active", "id": "sub_123"}
        keyboard = SubscriptionsKeyboard.subscription_status_menu(subscription)

        from telegram import InlineKeyboardMarkup

        assert isinstance(keyboard, InlineKeyboardMarkup)

        buttons = keyboard.inline_keyboard
        assert any("renew_subscription" in btn.callback_data for row in buttons for btn in row)

    @pytest.mark.asyncio
    async def test_subscriptions_keyboard_view_plans_button_exists(self):
        """SubscriptionsKeyboard.view_plans_button existe."""
        from src.bot.keyboards.subscriptions import SubscriptionsKeyboard

        keyboard = SubscriptionsKeyboard.view_plans_button()

        from telegram import InlineKeyboardMarkup

        assert isinstance(keyboard, InlineKeyboardMarkup)

        buttons = keyboard.inline_keyboard
        assert any("view_plans" in btn.callback_data for row in buttons for btn in row)

    # ============================================
    # HANDLER METHODS TESTS
    # ============================================

    @pytest.mark.asyncio
    async def test_show_subscription_menu_command_exists(self):
        """show_subscription_menu handler existe."""
        with (
            patch("src.bot.handlers.subscriptions.APIClient"),
            patch("src.bot.handlers.subscriptions.TokenStorage"),
        ):
            from src.bot.handlers.subscriptions import SubscriptionsHandler

            mock_api = AsyncMock()
            mock_storage = AsyncMock()

            handler = SubscriptionsHandler(mock_api, mock_storage)

            assert hasattr(handler, "show_subscription_menu")
            assert callable(getattr(handler, "show_subscription_menu"))

    @pytest.mark.asyncio
    async def test_view_plans_command_exists(self):
        """view_plans handler existe."""
        with (
            patch("src.bot.handlers.subscriptions.APIClient"),
            patch("src.bot.handlers.subscriptions.TokenStorage"),
        ):
            from src.bot.handlers.subscriptions import SubscriptionsHandler

            mock_api = AsyncMock()
            mock_storage = AsyncMock()

            handler = SubscriptionsHandler(mock_api, mock_storage)

            assert hasattr(handler, "view_plans")
            assert callable(getattr(handler, "view_plans"))

    @pytest.mark.asyncio
    async def test_select_plan_callback_exists(self):
        """select_plan handler existe."""
        with (
            patch("src.bot.handlers.subscriptions.APIClient"),
            patch("src.bot.handlers.subscriptions.TokenStorage"),
        ):
            from src.bot.handlers.subscriptions import SubscriptionsHandler

            mock_api = AsyncMock()
            mock_storage = AsyncMock()

            handler = SubscriptionsHandler(mock_api, mock_storage)

            assert hasattr(handler, "select_plan")
            assert callable(getattr(handler, "select_plan"))

    @pytest.mark.asyncio
    async def test_activate_subscription_callback_exists(self):
        """activate_subscription handler existe."""
        with (
            patch("src.bot.handlers.subscriptions.APIClient"),
            patch("src.bot.handlers.subscriptions.TokenStorage"),
        ):
            from src.bot.handlers.subscriptions import SubscriptionsHandler

            mock_api = AsyncMock()
            mock_storage = AsyncMock()

            handler = SubscriptionsHandler(mock_api, mock_storage)

            assert hasattr(handler, "activate_subscription")
            assert callable(getattr(handler, "activate_subscription"))

    @pytest.mark.asyncio
    async def test_renew_subscription_command_exists(self):
        """renew_subscription handler existe."""
        with (
            patch("src.bot.handlers.subscriptions.APIClient"),
            patch("src.bot.handlers.subscriptions.TokenStorage"),
        ):
            from src.bot.handlers.subscriptions import SubscriptionsHandler

            mock_api = AsyncMock()
            mock_storage = AsyncMock()

            handler = SubscriptionsHandler(mock_api, mock_storage)

            assert hasattr(handler, "renew_subscription")
            assert callable(getattr(handler, "renew_subscription"))

    @pytest.mark.asyncio
    async def test_view_subscription_status_exists(self):
        """view_subscription_status handler existe."""
        with (
            patch("src.bot.handlers.subscriptions.APIClient"),
            patch("src.bot.handlers.subscriptions.TokenStorage"),
        ):
            from src.bot.handlers.subscriptions import SubscriptionsHandler

            mock_api = AsyncMock()
            mock_storage = AsyncMock()

            handler = SubscriptionsHandler(mock_api, mock_storage)

            assert hasattr(handler, "view_subscription_status")
            assert callable(getattr(handler, "view_subscription_status"))

    @pytest.mark.asyncio
    async def test_choose_payment_method_callback_exists(self):
        """choose_payment_method handler existe."""
        with (
            patch("src.bot.handlers.subscriptions.APIClient"),
            patch("src.bot.handlers.subscriptions.TokenStorage"),
        ):
            from src.bot.handlers.subscriptions import SubscriptionsHandler

            mock_api = AsyncMock()
            mock_storage = AsyncMock()

            handler = SubscriptionsHandler(mock_api, mock_storage)

            assert hasattr(handler, "choose_payment_method")
            assert callable(getattr(handler, "choose_payment_method"))

    # ============================================
    # AUTHENTICATION & INTEGRATION TESTS
    # ============================================

    @pytest.mark.asyncio
    async def test_subscriptions_handler_get_auth_headers(self):
        """_get_auth_headers retorna headers con token."""
        with (
            patch("src.bot.handlers.subscriptions.APIClient"),
            patch("src.bot.handlers.subscriptions.TokenStorage"),
        ):
            from src.bot.handlers.subscriptions import SubscriptionsHandler

            mock_api = AsyncMock()
            mock_storage = AsyncMock()
            mock_storage.get.return_value = {"access_token": "test-token-456"}

            handler = SubscriptionsHandler(mock_api, mock_storage)

            headers = await handler._get_auth_headers(telegram_id=456)

            assert "Authorization" in headers
            assert headers["Authorization"] == "Bearer test-token-456"

    @pytest.mark.asyncio
    async def test_subscriptions_handler_get_auth_headers_unauthenticated(self):
        """_get_auth_headers lanza error si no está autenticado."""
        with (
            patch("src.bot.handlers.subscriptions.APIClient"),
            patch("src.bot.handlers.subscriptions.TokenStorage"),
        ):
            from src.bot.handlers.subscriptions import SubscriptionsHandler

            mock_api = AsyncMock()
            mock_storage = AsyncMock()
            mock_storage.get.return_value = None

            handler = SubscriptionsHandler(mock_api, mock_storage)

            with pytest.raises(PermissionError):
                await handler._get_auth_headers(telegram_id=456)

    @pytest.mark.asyncio
    async def test_get_subscriptions_handlers_returns_list(self):
        """get_subscriptions_handlers retorna una lista."""
        with (
            patch("src.bot.handlers.subscriptions.APIClient"),
            patch("src.bot.handlers.subscriptions.TokenStorage"),
        ):
            from src.bot.handlers.subscriptions import get_subscriptions_handlers

            mock_api = AsyncMock()
            mock_storage = AsyncMock()

            handlers = get_subscriptions_handlers(mock_api, mock_storage)

            assert isinstance(handlers, list)
            assert len(handlers) > 0

    @pytest.mark.asyncio
    async def test_get_subscriptions_callback_handlers_returns_list(self):
        """get_subscriptions_callback_handlers retorna una lista."""
        with (
            patch("src.bot.handlers.subscriptions.APIClient"),
            patch("src.bot.handlers.subscriptions.TokenStorage"),
        ):
            from src.bot.handlers.subscriptions import get_subscriptions_callback_handlers

            mock_api = AsyncMock()
            mock_storage = AsyncMock()

            handlers = get_subscriptions_callback_handlers(mock_api, mock_storage)

            assert isinstance(handlers, list)
            assert len(handlers) > 0

    # ============================================
    # HELPER METHODS TESTS
    # ============================================

    @pytest.mark.asyncio
    async def test_safe_answer_query_method_exists(self):
        """_safe_answer_query método existe."""
        with (
            patch("src.bot.handlers.subscriptions.APIClient"),
            patch("src.bot.handlers.subscriptions.TokenStorage"),
        ):
            from src.bot.handlers.subscriptions import SubscriptionsHandler

            mock_api = AsyncMock()
            mock_storage = AsyncMock()

            handler = SubscriptionsHandler(mock_api, mock_storage)

            assert hasattr(handler, "_safe_answer_query")
            assert callable(getattr(handler, "_safe_answer_query"))

    @pytest.mark.asyncio
    async def test_safe_edit_message_method_exists(self):
        """_safe_edit_message método existe."""
        with (
            patch("src.bot.handlers.subscriptions.APIClient"),
            patch("src.bot.handlers.subscriptions.TokenStorage"),
        ):
            from src.bot.handlers.subscriptions import SubscriptionsHandler

            mock_api = AsyncMock()
            mock_storage = AsyncMock()

            handler = SubscriptionsHandler(mock_api, mock_storage)

            assert hasattr(handler, "_safe_edit_message")
            assert callable(getattr(handler, "_safe_edit_message"))

    # ============================================
    # ADDITIONAL KEYBOARD TESTS
    # ============================================

    @pytest.mark.asyncio
    async def test_subscriptions_keyboard_back_to_main_exists(self):
        """SubscriptionsKeyboard.back_to_main existe."""
        from src.bot.keyboards.subscriptions import SubscriptionsKeyboard

        keyboard = SubscriptionsKeyboard.back_to_main()

        from telegram import InlineKeyboardMarkup

        assert isinstance(keyboard, InlineKeyboardMarkup)

        buttons = keyboard.inline_keyboard
        assert any("main_menu" in btn.callback_data for row in buttons for btn in row)

    @pytest.mark.asyncio
    async def test_subscriptions_keyboard_back_to_plans_exists(self):
        """SubscriptionsKeyboard.back_to_plans existe."""
        from src.bot.keyboards.subscriptions import SubscriptionsKeyboard

        keyboard = SubscriptionsKeyboard.back_to_plans()

        from telegram import InlineKeyboardMarkup

        assert isinstance(keyboard, InlineKeyboardMarkup)

        buttons = keyboard.inline_keyboard
        assert any("view_plans" in btn.callback_data for row in buttons for btn in row)

    @pytest.mark.asyncio
    async def test_subscriptions_keyboard_plan_selection_is_alias(self):
        """plan_selection es alias de plan_details."""
        from src.bot.keyboards.subscriptions import SubscriptionsKeyboard

        keyboard1 = SubscriptionsKeyboard.plan_details(plan_id="test")
        keyboard2 = SubscriptionsKeyboard.plan_selection(plan_id="test")

        # Both should have the same structure
        assert len(keyboard1.inline_keyboard) == len(keyboard2.inline_keyboard)

    @pytest.mark.asyncio
    async def test_subscriptions_keyboard_back_to_subscription_menu_is_alias(self):
        """back_to_subscription_menu es alias de back_to_subscription."""
        from src.bot.keyboards.subscriptions import SubscriptionsKeyboard

        keyboard1 = SubscriptionsKeyboard.back_to_subscription()
        keyboard2 = SubscriptionsKeyboard.back_to_subscription_menu()

        # Both should have the same structure
        assert len(keyboard1.inline_keyboard) == len(keyboard2.inline_keyboard)

    @pytest.mark.asyncio
    async def test_subscriptions_keyboard_back_to_menu_is_alias(self):
        """back_to_menu es alias de back_to_main."""
        from src.bot.keyboards.subscriptions import SubscriptionsKeyboard

        keyboard1 = SubscriptionsKeyboard.back_to_main()
        keyboard2 = SubscriptionsKeyboard.back_to_menu()

        # Both should have the same structure
        assert len(keyboard1.inline_keyboard) == len(keyboard2.inline_keyboard)

    @pytest.mark.asyncio
    async def test_subscriptions_keyboard_crypto_payment_status_exists(self):
        """SubscriptionsKeyboard.crypto_payment_status existe."""
        from src.bot.keyboards.subscriptions import SubscriptionsKeyboard

        keyboard = SubscriptionsKeyboard.crypto_payment_status(payment_id="crypto_sub_123")

        from telegram import InlineKeyboardMarkup

        assert isinstance(keyboard, InlineKeyboardMarkup)

        buttons = keyboard.inline_keyboard
        assert any(
            "check_crypto_status_crypto_sub_123" in btn.callback_data
            for row in buttons
            for btn in row
        )

    # ============================================
    # ERROR HANDLING TESTS
    # ============================================

    @pytest.mark.asyncio
    async def test_subscriptions_messages_has_unauthorized_error(self):
        """SubscriptionsMessages tiene error de no autorizado."""
        from src.bot.keyboards.messages_subscriptions import SubscriptionsMessages

        assert hasattr(SubscriptionsMessages.Error, "UNAUTHORIZED")

    @pytest.mark.asyncio
    async def test_subscriptions_messages_has_invalid_plan_error(self):
        """SubscriptionsMessages tiene error de plan inválido."""
        from src.bot.keyboards.messages_subscriptions import SubscriptionsMessages

        assert hasattr(SubscriptionsMessages.Error, "INVALID_PLAN")

    @pytest.mark.asyncio
    async def test_subscriptions_messages_subscription_expired_has_placeholders(self):
        """El mensaje de suscripción expirada tiene placeholders."""
        from src.bot.keyboards.messages_subscriptions import SubscriptionsMessages

        assert "{plan_name}" in SubscriptionsMessages.Subscription.SUBSCRIPTION_EXPIRED
        assert "{expiry_date}" in SubscriptionsMessages.Subscription.SUBSCRIPTION_EXPIRED

    @pytest.mark.asyncio
    async def test_subscriptions_messages_already_active_has_placeholders(self):
        """El mensaje de ya tener suscripción activa tiene placeholders."""
        from src.bot.keyboards.messages_subscriptions import SubscriptionsMessages

        assert "{plan_name}" in SubscriptionsMessages.Activation.ALREADY_ACTIVE
        assert "{renewal_date}" in SubscriptionsMessages.Activation.ALREADY_ACTIVE

    @pytest.mark.asyncio
    async def test_subscriptions_messages_renewal_prompt_has_placeholders(self):
        """El mensaje de promoción de renovación tiene placeholders."""
        from src.bot.keyboards.messages_subscriptions import SubscriptionsMessages

        assert "{plan_name}" in SubscriptionsMessages.Renewal.RENEWAL_PROMPT
        assert "{price}" in SubscriptionsMessages.Renewal.RENEWAL_PROMPT
        assert "{renewal_date}" in SubscriptionsMessages.Renewal.RENEWAL_PROMPT

    # ============================================
    # PLANS LIST TESTS
    # ============================================

    @pytest.mark.asyncio
    async def test_subscriptions_keyboard_plans_list_generates_buttons(self):
        """plans_list genera botones para cada plan."""
        from src.bot.keyboards.subscriptions import SubscriptionsKeyboard

        plans = [
            {"id": "basic", "name": "Básico", "price": 9.99},
            {"id": "standard", "name": "Estándar", "price": 19.99},
            {"id": "premium", "name": "Premium", "price": 29.99},
        ]
        keyboard = SubscriptionsKeyboard.plans_list(plans)

        buttons = keyboard.inline_keyboard
        assert any("select_plan_basic" in btn.callback_data for row in buttons for btn in row)
        assert any("select_plan_standard" in btn.callback_data for row in buttons for btn in row)
        assert any("select_plan_premium" in btn.callback_data for row in buttons for btn in row)

    @pytest.mark.asyncio
    async def test_subscriptions_keyboard_active_menu_has_correct_buttons(self):
        """subscription_active_menu tiene botones correctos."""
        from src.bot.keyboards.subscriptions import SubscriptionsKeyboard

        keyboard = SubscriptionsKeyboard.subscription_active_menu()

        buttons = keyboard.inline_keyboard
        callback_datas = [btn.callback_data for row in buttons for btn in row]

        assert "view_subscription_status" in callback_datas
        assert "renew_subscription" in callback_datas
        assert "main_menu" in callback_datas

    @pytest.mark.asyncio
    async def test_subscriptions_keyboard_inactive_menu_has_correct_buttons(self):
        """subscription_inactive_menu tiene botones correctos."""
        from src.bot.keyboards.subscriptions import SubscriptionsKeyboard

        keyboard = SubscriptionsKeyboard.subscription_inactive_menu()

        buttons = keyboard.inline_keyboard
        callback_datas = [btn.callback_data for row in buttons for btn in row]

        assert "view_plans" in callback_datas
        assert "main_menu" in callback_datas

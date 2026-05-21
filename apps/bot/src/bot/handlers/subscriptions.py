"""Handlers para gestión de suscripciones y planes (Subscriptions & Plans)."""

import logging
from typing import TYPE_CHECKING, Any

from telegram import Update
from telegram.ext import CallbackQueryHandler, CommandHandler, ContextTypes

from src.bot.keyboards.messages_subscriptions import SubscriptionsMessages
from src.infrastructure.api_client import APIClient
from src.infrastructure.token_storage import TokenStorage

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


class SubscriptionsHandler:
    """Handler para gestión de suscripciones y planes."""

    def __init__(self, api_client: APIClient, token_storage: TokenStorage):
        self.api = api_client
        self.tokens = token_storage
        logger.info("SubscriptionsHandler initialized")

    async def _get_auth_headers(self, telegram_id: int) -> dict[str, str]:
        """Obtiene headers de autenticación para el usuario."""
        tokens = await self.tokens.get(telegram_id)
        if not tokens:
            raise PermissionError("User not authenticated")
        return {"Authorization": f"Bearer {tokens['access_token']}"}

    async def _safe_answer_query(self, query: Any) -> None:
        """Responde a callback query de forma segura."""
        try:
            await query.answer()
        except Exception as e:
            logger.error(f"Error answering query: {e}")

    async def _safe_edit_message(
        self,
        query: Any,
        context: ContextTypes.DEFAULT_TYPE,
        text: str,
        reply_markup: Any = None,
        parse_mode: str = "Markdown",
    ) -> None:
        """Edita mensaje de forma segura."""
        try:
            await query.edit_message_text(
                text=text,
                reply_markup=reply_markup,
                parse_mode=parse_mode,
            )
        except Exception as e:
            logger.error(f"Error editing message: {e}")

    async def show_subscription_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Muestra el menú principal de suscripciones."""
        if update.effective_user is None:
            return

        telegram_id = update.effective_user.id
        logger.info(f"User {telegram_id} viewing subscription menu")

        try:
            # Check authentication
            if not await self.tokens.is_authenticated(telegram_id):
                if update.message:
                    await update.message.reply_text(
                        SubscriptionsMessages.Error.NOT_AUTHENTICATED,
                        parse_mode="Markdown",
                    )
                return

            # Get user subscription status
            headers = await self._get_auth_headers(telegram_id)
            try:
                subscription = await self.api.get("/subscriptions/me", headers=headers)
            except Exception:
                subscription = None

            if subscription and subscription.get("status") == "active":
                # User has active subscription
                plan_name = subscription.get("plan_name", "Plan")
                renewal_date = subscription.get("renewal_date", "N/A")[:10]
                price = subscription.get("price", 0)

                message = SubscriptionsMessages.Subscription.SUBSCRIPTION_ACTIVE.format(
                    plan_name=plan_name,
                    renewal_date=renewal_date,
                    price=f"{price:.2f}",
                )
                keyboard = SubscriptionsKeyboard.subscription_active_menu()
            else:
                # No active subscription
                message = SubscriptionsMessages.Subscription.SUBSCRIPTION_INACTIVE
                keyboard = SubscriptionsKeyboard.subscription_inactive_menu()

            if update.callback_query:
                await self._safe_edit_message(update.callback_query, context, message, keyboard)
            elif update.message:
                await update.message.reply_text(
                    message,
                    reply_markup=keyboard,
                    parse_mode="Markdown",
                )

        except Exception as e:
            logger.error(f"Error showing subscription menu: {e}")
            if update.callback_query:
                await self._safe_edit_message(
                    update.callback_query,
                    context,
                    SubscriptionsMessages.Error.SYSTEM_ERROR,
                    SubscriptionsKeyboard.back_to_menu(),
                )
            elif update.message:
                await update.message.reply_text(
                    SubscriptionsMessages.Error.SYSTEM_ERROR,
                    reply_markup=SubscriptionsKeyboard.back_to_menu(),
                    parse_mode="Markdown",
                )

    async def view_plans(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Muestra los planes disponibles."""
        query = update.callback_query
        if query is None:
            return

        await self._safe_answer_query(query)
        telegram_id = update.effective_user.id if update.effective_user else 0

        logger.info(f"User {telegram_id} viewing available plans")

        try:
            # Check authentication
            if not await self.tokens.is_authenticated(telegram_id):
                await self._safe_edit_message(
                    query,
                    context,
                    SubscriptionsMessages.Error.NOT_AUTHENTICATED,
                    SubscriptionsKeyboard.back_to_menu(),
                )
                return

            # Get available plans from backend
            headers = await self._get_auth_headers(telegram_id)
            try:
                plans_response = await self.api.get("/subscriptions/plans", headers=headers)
                plans = plans_response if isinstance(plans_response, list) else []
            except Exception as e:
                logger.error(f"Error fetching plans: {e}")
                # Fallback to default plans if endpoint fails (legacy pricing: 1 USDT = 120 Stars)
                plans = [
                    {
                        "id": "one_month",
                        "name": "1 Month",
                        "price": 2.99,
                        "duration_days": 30,
                        "features": ["1 dispositivo", "Velocidad estándar", "Soporte básico"],
                    },
                    {
                        "id": "three_months",
                        "name": "3 Months",
                        "price": 7.49,
                        "duration_days": 90,
                        "features": ["1 dispositivo", "Velocidad estándar", "Soporte básico"],
                    },
                    {
                        "id": "six_months",
                        "name": "6 Months",
                        "price": 13.99,
                        "duration_days": 180,
                        "features": ["1 dispositivo", "Velocidad estándar", "Soporte básico"],
                    },
                    {
                        "id": "twelve_months",
                        "name": "12 Months",
                        "price": 24.99,
                        "duration_days": 365,
                        "features": ["1 dispositivo", "Velocidad estándar", "Soporte básico"],
                    },
                ]

            if not plans:
                message = SubscriptionsMessages.Plans.NO_PLANS
                keyboard = SubscriptionsKeyboard.back_to_subscription_menu()
            else:
                message = SubscriptionsMessages.Plans.PLANS_HEADER
                keyboard = SubscriptionsKeyboard.plans_list(plans)

            await self._safe_edit_message(query, context, message, keyboard)

        except Exception as e:
            logger.error(f"Error viewing plans: {e}")
            await self._safe_edit_message(
                query,
                context,
                SubscriptionsMessages.Error.SYSTEM_ERROR,
                SubscriptionsKeyboard.back_to_menu(),
            )

    async def select_plan(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Muestra detalles de un plan seleccionado."""
        query = update.callback_query
        if query is None or query.data is None:
            return

        await self._safe_answer_query(query)

        # Extract plan_id from callback_data
        parts = query.data.split("_")
        plan_id = parts[-1] if len(parts) > 1 else ""
        telegram_id = update.effective_user.id if update.effective_user else 0

        logger.info(f"User {telegram_id} selecting plan: {plan_id}")

        try:
            # Check authentication
            if not await self.tokens.is_authenticated(telegram_id):
                await self._safe_edit_message(
                    query,
                    context,
                    SubscriptionsMessages.Error.NOT_AUTHENTICATED,
                    SubscriptionsKeyboard.back_to_menu(),
                )
                return

            # Get plan details
            headers = await self._get_auth_headers(telegram_id)
            try:
                plans_response = await self.api.get("/subscriptions/plans", headers=headers)
                plans: list = plans_response if isinstance(plans_response, list) else []
                plan = next((p for p in plans if p.get("id") == plan_id), None)
            except Exception:
                # Fallback to default plans (legacy pricing: 1 USDT = 120 Stars)
                default_plans = {
                    "one_month": {
                        "id": "one_month",
                        "name": "1 Month",
                        "price": 2.99,
                        "duration_days": 30,
                        "features": ["1 dispositivo", "Velocidad estándar", "Soporte básico"],
                    },
                    "three_months": {
                        "id": "three_months",
                        "name": "3 Months",
                        "price": 7.49,
                        "duration_days": 90,
                        "features": ["1 dispositivo", "Velocidad estándar", "Soporte básico"],
                    },
                    "six_months": {
                        "id": "six_months",
                        "name": "6 Months",
                        "price": 13.99,
                        "duration_days": 180,
                        "features": ["1 dispositivo", "Velocidad estándar", "Soporte básico"],
                    },
                    "twelve_months": {
                        "id": "twelve_months",
                        "name": "12 Months",
                        "price": 24.99,
                        "duration_days": 365,
                        "features": ["1 dispositivo", "Velocidad estándar", "Soporte básico"],
                    },
                }
                plan = default_plans.get(plan_id)

            if not plan:
                message = SubscriptionsMessages.Plans.PLAN_NOT_FOUND
                keyboard = SubscriptionsKeyboard.back_to_plans()
            else:
                plan_name = plan.get("name", "Plan")
                price = f"{plan.get('price', 0):.2f}"
                duration = plan.get("duration_days", 30)
                features = plan.get("features", [])

                features_list = "\n".join([f"  ✓ {f}" for f in features])

                message = SubscriptionsMessages.Plans.PLAN_DETAILS.format(
                    plan_name=plan_name,
                    price=price,
                    duration=duration,
                    features=features_list,
                )
                keyboard = SubscriptionsKeyboard.plan_selection(plan_id)

            await self._safe_edit_message(query, context, message, keyboard)

        except Exception as e:
            logger.error(f"Error selecting plan: {e}")
            await self._safe_edit_message(
                query,
                context,
                SubscriptionsMessages.Error.SYSTEM_ERROR,
                SubscriptionsKeyboard.back_to_menu(),
            )

    async def activate_subscription(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Activa una suscripción para el usuario."""
        query = update.callback_query
        if query is None or query.data is None:
            return

        await self._safe_answer_query(query)

        # Extract plan_id and payment_method from callback_data
        # Format: activate_plan_{plan_id}_{payment_method}
        parts = query.data.split("_")
        if len(parts) < 3:
            logger.error(f"Invalid callback data: {query.data}")
            return

        plan_id = parts[2] if len(parts) > 2 else ""
        payment_method = parts[3] if len(parts) > 3 else "crypto"
        telegram_id = update.effective_user.id if update.effective_user else 0

        logger.info(
            f"User {telegram_id} activating subscription: plan={plan_id}, payment={payment_method}"
        )

        try:
            # Check authentication
            if not await self.tokens.is_authenticated(telegram_id):
                await self._safe_edit_message(
                    query,
                    context,
                    SubscriptionsMessages.Error.NOT_AUTHENTICATED,
                    SubscriptionsKeyboard.back_to_menu(),
                )
                return

            # Activate subscription via backend
            headers = await self._get_auth_headers(telegram_id)
            try:
                activation_response = await self.api.post(
                    "/subscriptions/activate",
                    headers=headers,
                    data={
                        "plan_id": plan_id,
                        "payment_method": payment_method,
                        "telegram_id": telegram_id,
                    },
                )
                success = activation_response.get("success", False)
                subscription_id = activation_response.get("subscription_id")
                plan_name = activation_response.get("plan_name", "Plan")
                activation_date = activation_response.get("activation_date", "N/A")[:10]
                renewal_date = activation_response.get("renewal_date", "N/A")[:10]
                error_message = activation_response.get("error_message")

            except Exception as e:
                logger.error(f"Error activating subscription: {e}")
                success = False
                error_message = str(e)

            if success:
                message = SubscriptionsMessages.Subscription.SUBSCRIPTION_ACTIVATED.format(
                    plan_name=plan_name,
                    activation_date=activation_date,
                    renewal_date=renewal_date,
                )
                keyboard = SubscriptionsKeyboard.back_to_menu()
                logger.info(
                    f"User {telegram_id} successfully activated subscription: {subscription_id}"
                )
            else:
                message = SubscriptionsMessages.Subscription.ACTIVATION_FAILED.format(
                    reason=error_message or "Error desconocido",
                )
                keyboard = SubscriptionsKeyboard.back_to_plans()
                logger.warning(
                    f"User {telegram_id} failed to activate subscription: {error_message}"
                )

            await self._safe_edit_message(query, context, message, keyboard)

        except Exception as e:
            logger.error(f"Error in activate_subscription: {e}")
            await self._safe_edit_message(
                query,
                context,
                SubscriptionsMessages.Error.SYSTEM_ERROR,
                SubscriptionsKeyboard.back_to_menu(),
            )

    async def renew_subscription(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Renueva la suscripción actual del usuario."""
        query = update.callback_query
        if query is None or query.data is None:
            return

        await self._safe_answer_query(query)
        telegram_id = update.effective_user.id if update.effective_user else 0

        logger.info(f"User {telegram_id} renewing subscription")

        try:
            # Check authentication
            if not await self.tokens.is_authenticated(telegram_id):
                await self._safe_edit_message(
                    query,
                    context,
                    SubscriptionsMessages.Error.NOT_AUTHENTICATED,
                    SubscriptionsKeyboard.back_to_menu(),
                )
                return

            # Get current subscription
            headers = await self._get_auth_headers(telegram_id)
            try:
                subscription = await self.api.get("/subscriptions/me", headers=headers)
            except Exception:
                subscription = None

            if not subscription or subscription.get("status") != "active":
                message = SubscriptionsMessages.Subscription.NO_ACTIVE_SUBSCRIPTION
                keyboard = SubscriptionsKeyboard.view_plans_button()
                await self._safe_edit_message(query, context, message, keyboard)
                return

            # Renew subscription via backend
            try:
                renewal_response = await self.api.post(
                    "/subscriptions/renew",
                    headers=headers,
                    data={
                        "subscription_id": subscription.get("id"),
                        "telegram_id": telegram_id,
                    },
                )
                success = renewal_response.get("success", False)
                renewal_date = renewal_response.get("renewal_date", "N/A")[:10]
                plan_name = renewal_response.get("plan_name", "Plan")
                error_message = renewal_response.get("error_message")

            except Exception as e:
                logger.error(f"Error renewing subscription: {e}")
                success = False
                error_message = str(e)

            if success:
                message = SubscriptionsMessages.Subscription.SUBSCRIPTION_RENEWED.format(
                    plan_name=plan_name,
                    renewal_date=renewal_date,
                )
                keyboard = SubscriptionsKeyboard.back_to_menu()
                logger.info(f"User {telegram_id} successfully renewed subscription")
            else:
                message = SubscriptionsMessages.Subscription.RENEWAL_FAILED.format(
                    reason=error_message or "Error desconocido",
                )
                keyboard = SubscriptionsKeyboard.back_to_subscription_menu()
                logger.warning(f"User {telegram_id} failed to renew subscription: {error_message}")

            await self._safe_edit_message(query, context, message, keyboard)

        except Exception as e:
            logger.error(f"Error in renew_subscription: {e}")
            await self._safe_edit_message(
                query,
                context,
                SubscriptionsMessages.Error.SYSTEM_ERROR,
                SubscriptionsKeyboard.back_to_menu(),
            )

    async def view_subscription_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Muestra el estado detallado de la suscripción del usuario."""
        query = update.callback_query
        if query is None:
            return

        await self._safe_answer_query(query)
        telegram_id = update.effective_user.id if update.effective_user else 0

        logger.info(f"User {telegram_id} viewing subscription status")

        try:
            # Check authentication
            if not await self.tokens.is_authenticated(telegram_id):
                await self._safe_edit_message(
                    query,
                    context,
                    SubscriptionsMessages.Error.NOT_AUTHENTICATED,
                    SubscriptionsKeyboard.back_to_menu(),
                )
                return

            # Get subscription from backend
            headers = await self._get_auth_headers(telegram_id)
            try:
                subscription = await self.api.get("/subscriptions/me", headers=headers)
            except Exception:
                subscription = None

            if not subscription:
                message = SubscriptionsMessages.Subscription.SUBSCRIPTION_INACTIVE
                keyboard = SubscriptionsKeyboard.view_plans_button()
            else:
                status = subscription.get("status", "inactive")
                plan_name = subscription.get("plan_name", "Plan")
                start_date = subscription.get("start_date", "N/A")[:10]
                renewal_date = subscription.get("renewal_date", "N/A")[:10]
                price = f"{subscription.get('price', 0):.2f}"
                devices = subscription.get("devices", 0)
                data_limit = subscription.get("data_limit", "Ilimitado")

                status_icon = "✅" if status == "active" else "⏳" if status == "pending" else "❌"

                message = SubscriptionsMessages.Subscription.SUBSCRIPTION_DETAILS.format(
                    status_icon=status_icon,
                    status=status.upper(),
                    plan_name=plan_name,
                    start_date=start_date,
                    renewal_date=renewal_date,
                    price=price,
                    devices=devices,
                    data_limit=data_limit,
                )
                keyboard = SubscriptionsKeyboard.subscription_status_menu(subscription)

            await self._safe_edit_message(query, context, message, keyboard)

        except Exception as e:
            logger.error(f"Error viewing subscription status: {e}")
            await self._safe_edit_message(
                query,
                context,
                SubscriptionsMessages.Error.SYSTEM_ERROR,
                SubscriptionsKeyboard.back_to_menu(),
            )

    async def choose_payment_method(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Muestra opciones de método de pago para activar suscripción."""
        query = update.callback_query
        if query is None or query.data is None:
            return

        await self._safe_answer_query(query)

        # Extract plan_id from callback_data
        parts = query.data.split("_")
        plan_id = parts[-1] if len(parts) > 1 else ""
        telegram_id = update.effective_user.id if update.effective_user else 0

        logger.info(f"User {telegram_id} choosing payment method for plan: {plan_id}")

        try:
            message = SubscriptionsMessages.Payment.CHOOSE_PAYMENT_METHOD
            keyboard = SubscriptionsKeyboard.payment_method_selection(plan_id)

            await self._safe_edit_message(query, context, message, keyboard)

        except Exception as e:
            logger.error(f"Error choosing payment method: {e}")
            await self._safe_edit_message(
                query,
                context,
                SubscriptionsMessages.Error.SYSTEM_ERROR,
                SubscriptionsKeyboard.back_to_menu(),
            )


# Need to import keyboard at module level for helper functions
from src.bot.keyboards.subscriptions import SubscriptionsKeyboard  # noqa: E402


def get_subscriptions_handlers(
    api_client: APIClient, token_storage: TokenStorage
) -> list[CommandHandler]:
    """Retorna los handlers de comandos para suscripciones."""
    handler = SubscriptionsHandler(api_client, token_storage)

    return [
        CommandHandler("suscripcion", handler.show_subscription_menu),
        CommandHandler("subscription", handler.show_subscription_menu),
        CommandHandler("planes", handler.view_plans),
        CommandHandler("plans", handler.view_plans),
        CommandHandler("renovar", handler.renew_subscription),
        CommandHandler("renew", handler.renew_subscription),
    ]


def get_subscriptions_callback_handlers(
    api_client: APIClient, token_storage: TokenStorage
) -> list[CallbackQueryHandler]:
    """Retorna los handlers de callbacks para suscripciones."""
    handler = SubscriptionsHandler(api_client, token_storage)

    return [
        CallbackQueryHandler(handler.show_subscription_menu, pattern="^subscription_menu$"),
        CallbackQueryHandler(handler.view_plans, pattern="^view_plans$"),
        CallbackQueryHandler(handler.select_plan, pattern="^select_plan_"),
        CallbackQueryHandler(handler.activate_subscription, pattern="^activate_plan_"),
        CallbackQueryHandler(handler.renew_subscription, pattern="^renew_subscription$"),
        CallbackQueryHandler(
            handler.view_subscription_status, pattern="^view_subscription_status$"
        ),
        CallbackQueryHandler(handler.choose_payment_method, pattern="^choose_payment_"),
    ]

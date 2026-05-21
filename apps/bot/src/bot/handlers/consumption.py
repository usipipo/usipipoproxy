"""Handlers para gestión de facturación por consumo."""

import logging
from typing import TYPE_CHECKING, Any

from telegram import Update
from telegram.ext import CallbackQueryHandler, CommandHandler, ContextTypes

from src.bot.keyboards.consumption import ConsumptionKeyboard
from src.bot.keyboards.messages_consumption import ConsumptionMessages
from src.infrastructure.api_client import APIClient
from src.infrastructure.token_storage import TokenStorage

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


class ConsumptionHandler:
    """Handler para gestión de facturación por consumo."""

    def __init__(self, api_client: APIClient, token_storage: TokenStorage):
        self.api = api_client
        self.tokens = token_storage
        logger.info("ConsumptionHandler initialized")

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

    async def show_consumption_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Muestra el menú principal de consumo."""
        if update.effective_user is None:
            return

        telegram_id = update.effective_user.id
        logger.info(f"User {telegram_id} viewing consumption menu")

        try:
            # Check authentication
            if not await self.tokens.is_authenticated(telegram_id):
                if update.message:
                    await update.message.reply_text(
                        ConsumptionMessages.Error.NOT_AUTHENTICATED,
                        parse_mode="Markdown",
                    )
                return

            # Get consumption status
            headers = await self._get_auth_headers(telegram_id)
            try:
                response = await self.api.get("/consumption/status", headers=headers)

                is_active = response.get("is_active", False)
                has_debt = response.get("has_debt", False)
                gb_consumed = response.get("gb_consumed", 0)
                total_cost_usd = response.get("total_cost_usd", 0)
                days_remaining = response.get("days_remaining", 0)

            except Exception:
                # Endpoint may not be implemented yet
                is_active = False
                has_debt = False
                gb_consumed = 0
                total_cost_usd = 0
                days_remaining = 0

            # Determine state and show appropriate menu
            if has_debt:
                message = ConsumptionMessages.Menu.DEBT_STATE.format(
                    debt_amount=f"{total_cost_usd:.2f}",
                )
                keyboard = ConsumptionKeyboard.debt_state_menu()
            elif is_active:
                message = ConsumptionMessages.Menu.ACTIVE_STATE.format(
                    gb_consumed=f"{gb_consumed:.2f}",
                    cost=f"{total_cost_usd:.2f}",
                    days_remaining=days_remaining,
                )
                keyboard = ConsumptionKeyboard.active_state_menu()
            else:
                message = ConsumptionMessages.Menu.INACTIVE_STATE
                keyboard = ConsumptionKeyboard.inactive_state_menu()

            if update.callback_query:
                await self._safe_edit_message(update.callback_query, context, message, keyboard)
            elif update.message:
                await update.message.reply_text(
                    message,
                    reply_markup=keyboard,
                    parse_mode="Markdown",
                )

        except Exception as e:
            logger.error(f"Error showing consumption menu: {e}")
            if update.callback_query:
                await self._safe_edit_message(
                    update.callback_query,
                    context,
                    ConsumptionMessages.Error.SYSTEM_ERROR,
                    ConsumptionKeyboard.back_to_menu(),
                )
            elif update.message:
                await update.message.reply_text(
                    ConsumptionMessages.Error.SYSTEM_ERROR,
                    reply_markup=ConsumptionKeyboard.back_to_menu(),
                    parse_mode="Markdown",
                )

    async def start_activation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Inicia el flujo de activación del modo consumo."""
        query = update.callback_query
        if query is None:
            return

        await self._safe_answer_query(query)
        telegram_id = update.effective_user.id if update.effective_user else 0

        logger.info(f"User {telegram_id} starting consumption activation")

        try:
            # Check if can activate
            headers = await self._get_auth_headers(telegram_id)
            try:
                response = await self.api.get("/consumption/status/can_activate", headers=headers)
                can_activate = response.get("can_activate", False)
                error_message = response.get("error_message")
            except Exception:
                # Assume can activate if endpoint not available
                can_activate = True
                error_message = None

            if not can_activate:
                message = ConsumptionMessages.Activation.CANNOT_ACTIVATE.format(
                    reason=error_message or "razón desconocida"
                )
                keyboard = ConsumptionKeyboard.back_to_menu()
            else:
                message = ConsumptionMessages.Activation.TERMS
                keyboard = ConsumptionKeyboard.activation_confirmation()

                # Store state for next step
                if context.user_data is not None:
                    context.user_data["activating_consumption"] = True

            await self._safe_edit_message(query, context, message, keyboard)

        except Exception as e:
            logger.error(f"Error starting activation: {e}")
            await self._safe_edit_message(
                query,
                context,
                ConsumptionMessages.Error.SYSTEM_ERROR,
                ConsumptionKeyboard.back_to_menu(),
            )

    async def confirm_activation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Confirma y ejecuta la activación del modo consumo."""
        query = update.callback_query
        if query is None:
            return

        await self._safe_answer_query(query)
        telegram_id = update.effective_user.id if update.effective_user else 0

        logger.info(f"User {telegram_id} confirming consumption activation")

        try:
            # Clear state
            if context.user_data is not None and "activating_consumption" in context.user_data:
                del context.user_data["activating_consumption"]

            # Activate consumption
            headers = await self._get_auth_headers(telegram_id)
            response = await self.api.post(
                "/consumption/activate",
                headers=headers,
                data={},
            )

            success = response.get("success", False)

            if success:
                message = ConsumptionMessages.Activation.SUCCESS
                keyboard = ConsumptionKeyboard.active_state_menu()
                logger.info(f"User {telegram_id} successfully activated consumption mode")
            else:
                error_msg = response.get("error_message", "Error desconocido")
                message = ConsumptionMessages.Activation.FAILED.format(reason=error_msg)
                keyboard = ConsumptionKeyboard.back_to_menu()
                logger.warning(f"User {telegram_id} failed to activate consumption: {error_msg}")

            await self._safe_edit_message(query, context, message, keyboard)

        except Exception as e:
            logger.error(f"Error confirming activation: {e}")
            await self._safe_edit_message(
                query,
                context,
                ConsumptionMessages.Error.SYSTEM_ERROR,
                ConsumptionKeyboard.back_to_menu(),
            )

    async def view_consumption_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Muestra el estado actual del consumo."""
        query = update.callback_query
        if query is None:
            return

        await self._safe_answer_query(query)
        telegram_id = update.effective_user.id if update.effective_user else 0

        logger.info(f"User {telegram_id} viewing consumption status")

        try:
            headers = await self._get_auth_headers(telegram_id)
            try:
                response = await self.api.get("/consumption/status", headers=headers)

                is_active = response.get("is_active", False)
                mb_consumed = response.get("mb_consumed", 0)
                gb_consumed = response.get("gb_consumed", 0)
                total_cost_usd = response.get("total_cost_usd", 0)
                days_active = response.get("days_active", 0)
                days_remaining = response.get("days_remaining", 0)

            except Exception:
                # Endpoint may not be implemented yet
                is_active = False
                gb_consumed = 0
                total_cost_usd = 0
                days_active = 0
                days_remaining = 0

            if not is_active:
                message = ConsumptionMessages.Status.INACTIVE
                keyboard = ConsumptionKeyboard.inactive_state_menu()
            else:
                message = ConsumptionMessages.Status.ACTIVE.format(
                    gb_consumed=f"{gb_consumed:.2f}",
                    mb_consumed=f"{mb_consumed:.2f}",
                    cost=f"{total_cost_usd:.2f}",
                    days_active=days_active,
                    days_remaining=days_remaining,
                )
                keyboard = ConsumptionKeyboard.active_state_menu()

            await self._safe_edit_message(query, context, message, keyboard)

        except Exception as e:
            logger.error(f"Error viewing consumption status: {e}")
            await self._safe_edit_message(
                query,
                context,
                ConsumptionMessages.Error.SYSTEM_ERROR,
                ConsumptionKeyboard.back_to_menu(),
            )

    async def start_cancellation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Inicia el flujo de cancelación del modo consumo."""
        query = update.callback_query
        if query is None:
            return

        await self._safe_answer_query(query)
        telegram_id = update.effective_user.id if update.effective_user else 0

        logger.info(f"User {telegram_id} starting consumption cancellation")

        try:
            # Check if can cancel and get summary
            headers = await self._get_auth_headers(telegram_id)
            try:
                response = await self.api.get("/consumption/status/can_cancel", headers=headers)
                can_cancel = response.get("can_cancel", False)
                error_message = response.get("error_message")

                # Get summary data
                gb_consumed = response.get("gb_consumed", 0)
                total_cost_usd = response.get("total_cost_usd", 0)
                days_active = response.get("days_active", 0)

            except Exception:
                # Assume can cancel if endpoint not available
                can_cancel = True
                error_message = None
                gb_consumed = 0
                total_cost_usd = 0
                days_active = 0

            if not can_cancel:
                message = ConsumptionMessages.Cancellation.CANNOT_CANCEL.format(
                    reason=error_message or "razón desconocida"
                )
                keyboard = ConsumptionKeyboard.back_to_menu()
            else:
                # Show cancellation summary
                if total_cost_usd > 0:
                    message = ConsumptionMessages.Cancellation.SUMMARY_WITH_DEBT.format(
                        gb_consumed=f"{gb_consumed:.2f}",
                        cost=f"{total_cost_usd:.2f}",
                        days_active=days_active,
                    )
                else:
                    message = ConsumptionMessages.Cancellation.SUMMARY_NO_DEBT.format(
                        days_active=days_active,
                    )
                keyboard = ConsumptionKeyboard.cancellation_confirmation()

                # Store state for next step
                if context.user_data is not None:
                    context.user_data["cancelling_consumption"] = True

            await self._safe_edit_message(query, context, message, keyboard)

        except Exception as e:
            logger.error(f"Error starting cancellation: {e}")
            await self._safe_edit_message(
                query,
                context,
                ConsumptionMessages.Error.SYSTEM_ERROR,
                ConsumptionKeyboard.back_to_menu(),
            )

    async def confirm_cancellation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Confirma y ejecuta la cancelación del modo consumo."""
        query = update.callback_query
        if query is None:
            return

        await self._safe_answer_query(query)
        telegram_id = update.effective_user.id if update.effective_user else 0

        logger.warning(f"User {telegram_id} confirming consumption cancellation")

        try:
            # Clear state
            if context.user_data is not None and "cancelling_consumption" in context.user_data:
                del context.user_data["cancelling_consumption"]

            # Cancel consumption
            headers = await self._get_auth_headers(telegram_id)
            response = await self.api.post(
                "/consumption/cancel",
                headers=headers,
                data={},
            )

            success = response.get("success", False)
            had_debt = response.get("had_debt", False)
            total_cost_usd = response.get("total_cost_usd", 0)

            if success:
                if had_debt:
                    message = ConsumptionMessages.Cancellation.SUCCESS_WITH_DEBT.format(
                        cost=f"{total_cost_usd:.2f}",
                    )
                else:
                    message = ConsumptionMessages.Cancellation.SUCCESS_NO_DEBT
                keyboard = ConsumptionKeyboard.inactive_state_menu()
                logger.info(f"User {telegram_id} successfully cancelled consumption mode")
            else:
                error_msg = response.get("error_message", "Error desconocido")
                message = ConsumptionMessages.Cancellation.FAILED.format(reason=error_msg)
                keyboard = ConsumptionKeyboard.back_to_menu()
                logger.warning(f"User {telegram_id} failed to cancel consumption: {error_msg}")

            await self._safe_edit_message(query, context, message, keyboard)

        except Exception as e:
            logger.error(f"Error confirming cancellation: {e}")
            await self._safe_edit_message(
                query,
                context,
                ConsumptionMessages.Error.SYSTEM_ERROR,
                ConsumptionKeyboard.back_to_menu(),
            )

    async def view_invoices(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Muestra el listado de facturas del usuario."""
        query = update.callback_query
        if query is None:
            return

        await self._safe_answer_query(query)
        telegram_id = update.effective_user.id if update.effective_user else 0

        logger.info(f"User {telegram_id} viewing invoices")

        try:
            headers = await self._get_auth_headers(telegram_id)

            # Extract page from callback data if present
            page = 0
            if query.data and "_" in query.data:
                try:
                    page = int(query.data.split("_")[-1])
                except ValueError:
                    page = 0

            # Get invoices from backend
            try:
                response = await self.api.get(
                    f"/consumption/invoices/user/me?page={page}&limit=10", headers=headers
                )
                invoices = response.get("invoices", [])
                total = response.get("total", 0)
                pending_count = response.get("pending_count", 0)
                paid_count = response.get("paid_count", 0)
                expired_count = response.get("expired_count", 0)
                has_more = response.get("has_more", False)
            except Exception:
                # Endpoint may not be implemented yet
                invoices = []
                total = 0
                pending_count = 0
                paid_count = 0
                expired_count = 0
                has_more = False

            if not invoices:
                message = ConsumptionMessages.Invoices.NO_INVOICES
                keyboard = ConsumptionKeyboard.back_to_menu()
            else:
                message = ConsumptionMessages.Invoices.HEADER.format(
                    total=total,
                    pending=pending_count,
                    paid=paid_count,
                    expired=expired_count,
                )

                for invoice in invoices:
                    status_icon = (
                        "⏳"
                        if invoice.get("status") == "pending"
                        else "✅"
                        if invoice.get("status") == "paid"
                        else "❌"
                    )

                    message += ConsumptionMessages.Invoices.INVOICE_ITEM.format(
                        date=invoice.get("created_at", "N/A")[:10],
                        amount=f"{invoice.get('amount_usd', 0):.2f}",
                        status=status_icon,
                        status_text=invoice.get("status", "unknown").upper(),
                    )

                keyboard = ConsumptionKeyboard.invoices_list(has_next=has_more, page=page)

            await self._safe_edit_message(query, context, message, keyboard)

        except Exception as e:
            logger.error(f"Error viewing invoices: {e}")
            await self._safe_edit_message(
                query,
                context,
                ConsumptionMessages.Error.SYSTEM_ERROR,
                ConsumptionKeyboard.back_to_menu(),
            )

    async def back_to_main_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Vuelve al menú principal."""
        query = update.callback_query
        if query is None:
            return

        await self._safe_answer_query(query)

        from src.bot.keyboards.main_menu import MainMenuKeyboard
        from src.bot.keyboards.main import BasicMessages

        # Show main menu with buttons
        message = BasicMessages.BACK_TO_MAIN
        keyboard = MainMenuKeyboard.main_menu()

        await self._safe_edit_message(query, context, message, keyboard, parse_mode="Markdown")


def get_consumption_handlers(api_client: APIClient, token_storage: TokenStorage):
    """Retorna los handlers de consumo."""
    handler = ConsumptionHandler(api_client, token_storage)

    return [
        CommandHandler("consumo", handler.show_consumption_menu),
        CommandHandler("activar", handler.start_activation),
        CommandHandler("cancelar", handler.start_cancellation),
        CommandHandler("factura", handler.view_invoices),
    ]


def get_consumption_callback_handlers(api_client: APIClient, token_storage: TokenStorage):
    """Retorna los handlers de callbacks para consumo."""
    handler = ConsumptionHandler(api_client, token_storage)

    return [
        CallbackQueryHandler(handler.show_consumption_menu, pattern="^consumption_menu$"),
        CallbackQueryHandler(handler.start_activation, pattern="^consumption_activate$"),
        CallbackQueryHandler(handler.confirm_activation, pattern="^consumption_confirm_activate$"),
        CallbackQueryHandler(handler.view_consumption_status, pattern="^consumption_status$"),
        CallbackQueryHandler(handler.start_cancellation, pattern="^consumption_cancel$"),
        CallbackQueryHandler(handler.confirm_cancellation, pattern="^consumption_confirm_cancel$"),
        CallbackQueryHandler(handler.view_invoices, pattern="^consumption_invoices"),
        CallbackQueryHandler(handler.back_to_main_menu, pattern="^consumption_back_to_main$"),
    ]

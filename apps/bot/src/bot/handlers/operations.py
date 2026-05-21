"""Handlers para operaciones del usuario."""

import logging
from typing import Any

from telegram import Update
from telegram.ext import CallbackQueryHandler, CommandHandler, ContextTypes

from src.bot.keyboards.messages_operations import OperationsMessages
from src.bot.keyboards.messages_referrals import ReferralsMessages
from src.bot.keyboards.operations import OperationsKeyboard
from src.bot.keyboards.referrals import ReferralsKeyboard
from src.infrastructure.api_client import APIClient
from src.infrastructure.token_storage import TokenStorage

logger = logging.getLogger(__name__)


class OperationsHandler:
    """Handler para operaciones del usuario."""

    def __init__(self, api_client: APIClient, token_storage: TokenStorage):
        self.api = api_client
        self.tokens = token_storage
        logger.info("⚙️ OperationsHandler initialized")

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

    async def operations_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Muestra el menú de operaciones."""
        if update.effective_user is None:
            return

        telegram_id = update.effective_user.id
        logger.info(f"⚙️ User {telegram_id} opened operations menu")

        try:
            # Check authentication
            if not await self.tokens.is_authenticated(telegram_id):
                if update.message:
                    await update.message.reply_text(
                        OperationsMessages.Error.INVALID_OPTION,
                        parse_mode="Markdown",
                    )
                return

            # Get user referral stats (for credits)
            credits = 0
            try:
                headers = await self._get_auth_headers(telegram_id)
                response = await self.api.get("/referrals/me", headers=headers)
                credits = response.get("referral_credits", 0)
            except Exception:
                # Referrals endpoint may not be implemented yet
                credits = 0

            # Show menu
            if credits > 0:
                message = OperationsMessages.Menu.MAIN_WITH_CREDITS.format(credits=credits)
            else:
                message = OperationsMessages.Menu.MAIN

            keyboard = OperationsKeyboard.operations_menu(credits=credits)

            if update.callback_query:
                await self._safe_edit_message(update.callback_query, context, message, keyboard)
            elif update.message:
                await update.message.reply_text(
                    message, reply_markup=keyboard, parse_mode="Markdown"
                )

        except Exception as e:
            logger.error(f"Error en operations_menu: {e}")
            if update.callback_query:
                await self._safe_edit_message(
                    update.callback_query,
                    context,
                    OperationsMessages.Error.SYSTEM_ERROR,
                    OperationsKeyboard.back_to_operations(),
                )
            elif update.message:
                await update.message.reply_text(
                    OperationsMessages.Error.SYSTEM_ERROR,
                    reply_markup=OperationsKeyboard.back_to_operations(),
                    parse_mode="Markdown",
                )

    async def show_credits(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Muestra el menú de créditos."""
        query = update.callback_query
        if query is None or update.effective_user is None:
            return

        await self._safe_answer_query(query)
        telegram_id = update.effective_user.id

        logger.info(f"🎁 User {telegram_id} viewing credits")

        try:
            # Get credits from referrals endpoint
            credits = 0
            try:
                headers = await self._get_auth_headers(telegram_id)
                response = await self.api.get("/referrals/me", headers=headers)
                credits = response.get("referral_credits", 0)
            except Exception:
                credits = 0

            message = OperationsMessages.Credits.DISPLAY.format(credits=credits)
            keyboard = OperationsKeyboard.credits_menu(credits=credits)

            await self._safe_edit_message(query, context, message, keyboard)

        except Exception as e:
            logger.error(f"Error en show_credits: {e}")
            await self._safe_edit_message(
                query,
                context,
                OperationsMessages.Error.SYSTEM_ERROR,
                OperationsKeyboard.back_to_operations(),
            )

    async def show_shop(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Muestra la tienda."""
        query = update.callback_query
        if query is None:
            return

        await self._safe_answer_query(query)

        logger.info("🛒 User viewing shop")

        try:
            message = OperationsMessages.Shop.WELCOME
            keyboard = OperationsKeyboard.shop_menu()

            await self._safe_edit_message(query, context, message, keyboard)

        except Exception as e:
            logger.error(f"Error en show_shop: {e}")
            await self._safe_edit_message(
                query,
                context,
                OperationsMessages.Error.SYSTEM_ERROR,
                OperationsKeyboard.back_to_operations(),
            )

    async def show_transactions_history(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Muestra el historial de transacciones."""
        query = update.callback_query
        if query is None or update.effective_user is None:
            return

        await self._safe_answer_query(query)
        telegram_id = update.effective_user.id

        logger.info(f"📜 User {telegram_id} viewing transactions history")

        try:
            # Get transactions from backend
            transactions = []
            page = 0
            has_more = False

            try:
                headers = await self._get_auth_headers(telegram_id)
                # Extract page from callback data if present
                if query.data and "_" in query.data:
                    try:
                        page = int(query.data.split("_")[-1])
                    except ValueError:
                        page = 0

                response = await self.api.get(
                    f"/transactions?limit=10&offset={page * 10}", headers=headers
                )
                transactions = response.get("transactions", [])
                has_more = response.get("has_more", False)
            except Exception:
                # Transactions endpoint may not be implemented yet
                transactions = []

            if not transactions:
                message = OperationsMessages.Transactions.NO_TRANSACTIONS
                keyboard = OperationsKeyboard.back_to_operations()
            else:
                message = OperationsMessages.Transactions.HISTORY_HEADER.format(page=page + 1)
                for tx in transactions:
                    message += OperationsMessages.Transactions.TRANSACTION_ITEM.format(
                        date=tx.get("created_at", "N/A")[:10],
                        type=tx.get("type", "N/A"),
                        amount=tx.get("amount", 0),
                        description=tx.get("description", "N/A"),
                    )
                keyboard = OperationsKeyboard.transactions_history_menu(
                    has_more=has_more, page=page
                )

            await self._safe_edit_message(query, context, message, keyboard)

        except Exception as e:
            logger.error(f"Error en show_transactions_history: {e}")
            await self._safe_edit_message(
                query,
                context,
                OperationsMessages.Error.SYSTEM_ERROR,
                OperationsKeyboard.back_to_operations(),
            )

    async def show_referrals(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Muestra el menú de referidos."""
        query = update.callback_query
        if query is None or update.effective_user is None:
            return

        await self._safe_answer_query(query)
        telegram_id = update.effective_user.id

        logger.info(f"👥 User {telegram_id} viewing referrals")

        try:
            # Get referral stats from backend
            invited = 0
            credits = 0
            referral_code = str(telegram_id)

            try:
                headers = await self._get_auth_headers(telegram_id)
                response = await self.api.get("/referrals/me", headers=headers)
                invited = response.get("total_referrals", 0)
                credits = response.get("referral_credits", 0)
                referral_code = response.get("referral_code", referral_code)
            except Exception:
                # Referrals endpoint may not be implemented yet
                pass

            # Build referral link
            link = f"https://t.me/usipipobot?start={referral_code}"

            # Use unified template and keyboard (same as /referidos command)
            message = ReferralsMessages.Menu.REFERRAL_STATS.format(
                referral_code=referral_code,
                total_referrals=invited,
                referral_credits=credits,
                referral_link=link,
            )
            keyboard = ReferralsKeyboard.menu(link)

            await self._safe_edit_message(query, context, message, keyboard, parse_mode="Markdown")

        except Exception as e:
            logger.error(f"Error en show_referrals: {e}")
            await self._safe_edit_message(
                query,
                context,
                OperationsMessages.Error.SYSTEM_ERROR,
                OperationsKeyboard.back_to_operations(),
            )

    async def back_to_operations(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Vuelve al menú de operaciones."""
        await self.operations_menu(update, context)

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


def get_operations_handlers(api_client: APIClient, token_storage: TokenStorage):
    """Retorna los handlers de operaciones."""
    handler = OperationsHandler(api_client, token_storage)

    return [
        CommandHandler("operaciones", handler.operations_menu),
    ]


def get_operations_callback_handlers(api_client: APIClient, token_storage: TokenStorage):
    """Retorna los handlers de callbacks para operaciones."""
    handler = OperationsHandler(api_client, token_storage)

    return [
        CallbackQueryHandler(handler.operations_menu, pattern="^operations_menu$"),
        CallbackQueryHandler(handler.show_credits, pattern="^credits_menu$"),
        CallbackQueryHandler(handler.show_shop, pattern="^shop_menu$"),
        CallbackQueryHandler(handler.show_transactions_history, pattern="^transactions_"),
        CallbackQueryHandler(handler.show_referrals, pattern="^referral_menu$"),
        CallbackQueryHandler(handler.back_to_operations, pattern="^back_to_operations$"),
        CallbackQueryHandler(handler.back_to_main_menu, pattern="^main_menu$"),
    ]

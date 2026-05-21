"""Handlers for Referral system."""

import logging
from typing import Any

from telegram import Update
from telegram.ext import CallbackQueryHandler, CommandHandler, ContextTypes, ConversationHandler

from src.bot.keyboards.messages_referrals import ReferralsMessages
from src.bot.keyboards.referrals import ReferralsKeyboard
from src.infrastructure.api_client import APIClient
from src.infrastructure.token_storage import TokenStorage

logger = logging.getLogger(__name__)


class ReferralsHandler:
    """Handler for referral system."""

    def __init__(self, api_client: APIClient, token_storage: TokenStorage):
        self.api = api_client
        self.tokens = token_storage
        logger.info("🎯 ReferralsHandler initialized")

    async def _get_auth_headers(self, telegram_id: int) -> dict[str, str]:
        """Get authentication headers for user."""
        tokens = await self.tokens.get(telegram_id)
        if not tokens:
            raise PermissionError("User not authenticated")
        return {"Authorization": f"Bearer {tokens['access_token']}"}

    async def _safe_answer_query(self, query: Any) -> None:
        """Answer callback query safely."""
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
        """Edit message safely."""
        try:
            await query.edit_message_text(
                text=text,
                reply_markup=reply_markup,
                parse_mode=parse_mode,
            )
        except Exception as e:
            logger.error(f"Error editing message: {e}")
            # Fallback: send new message
            await query.message.reply_text(
                text=text,
                reply_markup=reply_markup,
                parse_mode=parse_mode,
            )

    async def show_referrals(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show referral stats and menu."""
        if update.effective_user is None:
            return

        telegram_id = update.effective_user.id
        logger.info(f"🎯 User {telegram_id} viewing referrals")

        try:
            # Check authentication
            if not await self.tokens.is_authenticated(telegram_id):
                if update.message:
                    await update.message.reply_text(
                        ReferralsMessages.Error.NOT_AUTHENTICATED,
                        parse_mode="Markdown",
                    )
                return

            # Get referral stats
            headers = await self._get_auth_headers(telegram_id)
            response = await self.api.get(
                "/referrals/me",
                headers=headers,
            )

            # Build referral link
            referral_code = response["referral_code"]
            referral_link = f"https://t.me/usipipobot?start={referral_code}"

            # Format message (template uses inline link syntax for safe URL handling)
            message = ReferralsMessages.Menu.REFERRAL_STATS.format(
                referral_code=referral_code,
                total_referrals=response["total_referrals"],
                referral_credits=response["referral_credits"],
                referral_link=referral_link,
            )

            # Send with keyboard
            if update.message:
                await update.message.reply_text(
                    text=message,
                    reply_markup=ReferralsKeyboard.menu(referral_link),
                    parse_mode="Markdown",
                )

        except Exception as e:
            logger.error(f"Error showing referrals: {e}")
            if update.message:
                await update.message.reply_text(
                    ReferralsMessages.Error.SYSTEM_ERROR,
                    parse_mode="Markdown",
                )

    async def get_referral_link(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Get user's referral link."""
        if update.effective_user is None:
            return

        telegram_id = update.effective_user.id
        logger.info(f"🎯 User {telegram_id} getting referral link")

        try:
            # Check authentication
            if not await self.tokens.is_authenticated(telegram_id):
                if update.message:
                    await update.message.reply_text(
                        ReferralsMessages.Error.NOT_AUTHENTICATED,
                        parse_mode="Markdown",
                    )
                return

            # Get referral stats
            headers = await self._get_auth_headers(telegram_id)
            response = await self.api.get(
                "/referrals/me",
                headers=headers,
            )

            # Build referral link
            referral_code = response["referral_code"]
            referral_link = f"https://t.me/usipipobot?start={referral_code}"

            # Format message (template uses inline link syntax for safe URL handling)
            message = ReferralsMessages.Menu.INVITE_LINK.format(
                referral_link=referral_link,
            )

            # Send message
            if update.message:
                await update.message.reply_text(
                    text=message,
                    parse_mode="Markdown",
                )

        except Exception as e:
            logger.error(f"Error getting referral link: {e}")
            if update.message:
                await update.message.reply_text(
                    ReferralsMessages.Error.SYSTEM_ERROR,
                    parse_mode="Markdown",
                )

    async def redeem_credits(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show redeem credits confirmation keyboard."""
        if update.effective_user is None or update.callback_query is None:
            return

        telegram_id = update.effective_user.id
        query = update.callback_query
        logger.info(f"🎯 User {telegram_id} opening redeem credits")

        try:
            # Check authentication
            if not await self.tokens.is_authenticated(telegram_id):
                await self._safe_answer_query(query)
                await query.edit_message_text(
                    text=ReferralsMessages.Error.NOT_AUTHENTICATED,
                    parse_mode="Markdown",
                )
                return

            # Get current credits
            headers = await self._get_auth_headers(telegram_id)
            response = await self.api.get("/referrals/me", headers=headers)
            credits = response.get("referral_credits", 0)

            if credits <= 0:
                await self._safe_answer_query(query)
                await query.edit_message_text(
                    text=ReferralsMessages.Error.INSUFFICIENT_CREDITS,
                    parse_mode="Markdown",
                )
                return

            message = f"💰 *Canjear Créditos*\n\nTienes `{credits}` créditos disponibles.\n\n10 créditos = 1 GB de datos\n\n¿Cuántos créditos deseas canjear?"

            await self._safe_answer_query(query)
            await self._safe_edit_message(
                query=query,
                context=context,
                text=message,
                reply_markup=ReferralsKeyboard.redeem_confirmation(credits),
            )

        except Exception as e:
            logger.error(f"Error opening redeem credits: {e}")
            await self._safe_answer_query(query)
            await query.edit_message_text(
                text=ReferralsMessages.Error.SYSTEM_ERROR,
                parse_mode="Markdown",
            )

    async def cancel_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle cancel callback."""
        if update.effective_user is None or update.callback_query is None:
            return

        query = update.callback_query
        await self._safe_answer_query(query)
        await self.show_referrals(update, context)

    async def redeem_credits_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle redeem credits callback."""
        if update.effective_user is None or update.callback_query is None:
            return

        telegram_id = update.effective_user.id
        query = update.callback_query
        logger.info(f"🎯 User {telegram_id} redeeming credits")

        try:
            # Check authentication
            if not await self.tokens.is_authenticated(telegram_id):
                await self._safe_answer_query(query)
                await query.edit_message_text(
                    text=ReferralsMessages.Error.NOT_AUTHENTICATED,
                    parse_mode="Markdown",
                )
                return

            # Parse credits from callback_data
            # Format: "referral_redeem_confirm:10"
            if not query.data:
                return ConversationHandler.END
            credits = int(query.data.split(":")[1])

            # Redeem credits
            headers = await self._get_auth_headers(telegram_id)
            response = await self.api.post(
                "/referrals/redeem",
                data={"credits": credits},
                headers=headers,
            )

            # Calculate GB added (10 credits = 1 GB)
            gb_added = response.get("gb_added", credits // 10)
            remaining = response.get("data", {}).get("remaining_credits", 0)

            # Format success message
            message = ReferralsMessages.Menu.REDEEM_CONFIRMATION.format(
                credits=credits,
                gb=gb_added,
                remaining_credits=remaining,
            )

            await self._safe_edit_message(
                query=query,
                context=context,
                text=message,
                reply_markup=ReferralsKeyboard.back_to_menu(),
            )

        except ValueError as e:
            logger.error(f"Invalid credits value: {e}")
            await self._safe_answer_query(query)
            await query.edit_message_text(
                text=ReferralsMessages.Error.INVALID_CODE,
                parse_mode="Markdown",
            )
        except Exception as e:
            logger.error(f"Error redeeming credits: {e}")
            await self._safe_answer_query(query)
            await query.edit_message_text(
                text=ReferralsMessages.Error.SYSTEM_ERROR,
                parse_mode="Markdown",
            )

    async def apply_code_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle apply referral code callback."""
        if update.effective_user is None or update.callback_query is None:
            return

        telegram_id = update.effective_user.id
        query = update.callback_query
        logger.info(f"🎯 User {telegram_id} applying referral code")

        try:
            # Check authentication
            if not await self.tokens.is_authenticated(telegram_id):
                await self._safe_answer_query(query)
                await query.edit_message_text(
                    text=ReferralsMessages.Error.NOT_AUTHENTICATED,
                    parse_mode="Markdown",
                )
                return

            # Prompt user to enter code (simplified: direct apply for now)
            # In full implementation: ConversationHandler for user input
            await self._safe_answer_query(query)
            await query.edit_message_text(
                text="📝 Envía tu código de referido como mensaje de texto:",
                reply_markup=ReferralsKeyboard.back_to_menu(),
                parse_mode="Markdown",
            )

        except Exception as e:
            logger.error(f"Error applying code: {e}")
            await self._safe_answer_query(query)
            await query.edit_message_text(
                text=ReferralsMessages.Error.SYSTEM_ERROR,
                parse_mode="Markdown",
            )


def get_referrals_handlers(api_client: APIClient, token_storage: TokenStorage):
    """Get all referrals command handlers."""
    handler = ReferralsHandler(api_client, token_storage)

    return [
        CommandHandler("referidos", handler.show_referrals),
        CommandHandler("invitar", handler.get_referral_link),
    ]


def get_referrals_callback_handlers(api_client: APIClient, token_storage: TokenStorage):
    """Get all referrals callback handlers."""
    handler = ReferralsHandler(api_client, token_storage)

    return [
        CallbackQueryHandler(
            handler.redeem_credits,
            pattern=r"^referral_redeem$",
        ),
        CallbackQueryHandler(
            handler.redeem_credits_callback,
            pattern=r"^referral_redeem_confirm:\d+$",
        ),
        CallbackQueryHandler(
            handler.cancel_callback,
            pattern=r"^referral_cancel$",
        ),
        CallbackQueryHandler(
            handler.apply_code_callback,
            pattern=r"^referral_apply$",
        ),
        CallbackQueryHandler(
            handler.show_referrals,
            pattern=r"^referral_back$",
        ),
    ]

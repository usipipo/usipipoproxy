"""Handler para perfil de usuario."""

import logging
from typing import TYPE_CHECKING, Any

from telegram import Update
from telegram.ext import CallbackQueryHandler, ContextTypes

from src.bot.keyboards.messages_user_profile import UserProfileMessages
from src.bot.keyboards.user_profile import UserProfileKeyboard

if TYPE_CHECKING:
    from src.infrastructure.api_client import APIClient
    from src.infrastructure.token_storage import TokenStorage

logger = logging.getLogger(__name__)


class UserProfileHandler:
    """Handler para mostrar perfil de usuario."""

    def __init__(self, api_client: "APIClient", token_storage: "TokenStorage"):
        self.api = api_client
        self.tokens = token_storage

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

    async def show_user_profile(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Muestra el perfil del usuario con información detallada.

        Args:
            update: Update de Telegram
            context: Contexto del bot
        """
        query = update.callback_query
        if query is None:
            logger.warning("show_user_profile called without callback_query")
            return

        await self._safe_answer_query(query)

        if update.effective_user is None:
            return

        telegram_id = update.effective_user.id
        logger.info(f"User {telegram_id} viewing profile")

        try:
            # Check authentication
            if not await self.tokens.is_authenticated(telegram_id):
                await self._safe_edit_message(
                    query,
                    context,
                    UserProfileMessages.Error.NOT_AUTHENTICATED,
                    UserProfileKeyboard.profile_menu(),
                )
                return

            # Get user profile from backend
            headers = await self._get_auth_headers(telegram_id)

            # Get user data
            user_response = await self.api.get("/users/me", headers=headers)

            # Get VPN keys count (optional, don't fail if not available)
            try:
                vpn_keys = await self.api.get("/vpn/keys", headers=headers)
                vpn_keys_count = len(vpn_keys) if isinstance(vpn_keys, list) else 0
            except Exception:
                vpn_keys_count = 0

            # Build profile message
            message = UserProfileMessages.Profile.HEADER

            # Personal info
            message += UserProfileMessages.format_personal_info(
                username=user_response.get("username"),
                first_name=user_response.get("first_name"),
                last_name=user_response.get("last_name"),
                telegram_id=telegram_id,
            )

            # Balance info
            message += UserProfileMessages.format_balance_info(
                balance_gb=user_response.get("balance_gb", 0),
                total_purchased_gb=user_response.get("total_purchased_gb", 0),
                vpn_keys_count=vpn_keys_count,
            )

            # Referral info
            message += UserProfileMessages.format_referral_info(
                referral_code=user_response.get("referral_code", "N/A"),
                referrals_count=user_response.get("total_referrals", 0),
                referral_credits=user_response.get("referral_credits", 0),
            )

            # Loyalty info
            message += UserProfileMessages.format_loyalty_info(
                loyalty_bonus_percent=user_response.get("loyalty_bonus_percent", 0),
                purchase_count=user_response.get("purchase_count", 0),
                welcome_bonus_used=user_response.get("welcome_bonus_used", False),
            )

            # Account info
            from datetime import datetime

            created_at = datetime.fromisoformat(user_response.get("created_at", "2024-01-01"))
            updated_at = datetime.fromisoformat(user_response.get("updated_at", "2024-01-01"))
            message += UserProfileMessages.format_account_info(created_at, updated_at)

            # Add tip
            message += "\n" + UserProfileMessages.Profile.TIP

            await self._safe_edit_message(
                query,
                context,
                message,
                UserProfileKeyboard.profile_menu(),
            )

        except PermissionError:
            logger.warning(f"Unauthenticated user {telegram_id} tried to view profile")
            await self._safe_edit_message(
                query,
                context,
                UserProfileMessages.Error.NOT_AUTHENTICATED,
                UserProfileKeyboard.profile_menu(),
            )
        except Exception as e:
            logger.error(f"Error showing user profile: {e}")
            await self._safe_edit_message(
                query,
                context,
                UserProfileMessages.Error.API_ERROR,
                UserProfileKeyboard.profile_menu(),
            )


def get_user_profile_handlers(api_client: "APIClient", token_storage: "TokenStorage"):
    """Retorna los handlers para perfil de usuario."""
    handler = UserProfileHandler(api_client, token_storage)

    return [
        CallbackQueryHandler(handler.show_user_profile, pattern="^show_usage$"),
    ]

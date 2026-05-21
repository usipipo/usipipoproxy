"""Inline keyboards for Referrals feature."""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


class ReferralsKeyboard:
    """Inline keyboards for referral system."""

    @staticmethod
    def menu(referral_link: str | None = None) -> InlineKeyboardMarkup:
        """Main referrals menu keyboard with optional share button."""
        keyboard = []

        # Add share button as first row if referral link is provided
        if referral_link:
            keyboard.append(
                [
                    InlineKeyboardButton("📤 Compartir Enlace", switch_inline_query=referral_link),
                ]
            )

        # Add existing buttons
        keyboard.extend(
            [
                [
                    InlineKeyboardButton("💰 Canjear Créditos", callback_data="referral_redeem"),
                ],
                [
                    InlineKeyboardButton("📝 Aplicar Código", callback_data="referral_apply"),
                ],
            ]
        )

        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def redeem_confirmation(credits: int) -> InlineKeyboardMarkup:
        """Confirmation keyboard for redeeming credits."""
        keyboard = [
            [
                InlineKeyboardButton(
                    "✅ Confirmar", callback_data=f"referral_redeem_confirm:{credits}"
                ),
            ],
            [
                InlineKeyboardButton("❌ Cancelar", callback_data="referral_cancel"),
            ],
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def apply_code() -> InlineKeyboardMarkup:
        """Keyboard for applying referral code."""
        keyboard = [
            [
                InlineKeyboardButton("🔙 Volver", callback_data="referral_back"),
            ],
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def back_to_menu() -> InlineKeyboardMarkup:
        """Back to menu keyboard."""
        keyboard = [
            [
                InlineKeyboardButton("🔙 Volver al Menú", callback_data="referral_back"),
            ],
        ]
        return InlineKeyboardMarkup(keyboard)

"""Teclado para perfil de usuario."""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


class UserProfileKeyboard:
    """Teclado para mostrar perfil de usuario."""

    @staticmethod
    def profile_menu() -> InlineKeyboardMarkup:
        """
        Retorna teclado para el menú de perfil.

        Returns:
            InlineKeyboardMarkup: Teclado con botón para volver al menú principal
        """
        keyboard = [
            [InlineKeyboardButton("🔙 Volver al Menú Principal", callback_data="main_menu")],
        ]
        return InlineKeyboardMarkup(keyboard)

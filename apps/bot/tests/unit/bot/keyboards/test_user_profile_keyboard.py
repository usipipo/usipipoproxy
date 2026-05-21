"""Tests for UserProfileKeyboard."""

from telegram import InlineKeyboardMarkup
from src.bot.keyboards.user_profile import UserProfileKeyboard


class TestUserProfileKeyboard:
    """Tests for user profile keyboard."""

    def test_profile_menu_structure(self):
        """Test that profile menu has correct structure."""
        keyboard = UserProfileKeyboard.profile_menu()

        assert isinstance(keyboard, InlineKeyboardMarkup)
        assert len(keyboard.inline_keyboard) == 1
        assert len(keyboard.inline_keyboard[0]) == 1

        button = keyboard.inline_keyboard[0][0]
        assert button.text == "🔙 Volver al Menú Principal"
        assert button.callback_data == "main_menu"

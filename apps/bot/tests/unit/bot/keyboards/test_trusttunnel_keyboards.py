"""Tests para TrustTunnel keyboards."""
from telegram import InlineKeyboardMarkup


class TestTrustTunnelKeyboards:
    """Tests para TrustTunnelKeyboard."""

    def test_key_actions_exists(self):
        """key_actions retorna InlineKeyboardMarkup."""
        from src.bot.keyboards.trusttunnel import TrustTunnelKeyboard

        keyboard = TrustTunnelKeyboard.key_actions(key_id="test-uuid", is_active=True)
        assert isinstance(keyboard, InlineKeyboardMarkup)

    def test_key_actions_has_download_button(self):
        """key_actions incluye botón de descarga de config."""
        from src.bot.keyboards.trusttunnel import TrustTunnelKeyboard

        keyboard = TrustTunnelKeyboard.key_actions(key_id="test-uuid", is_active=True)
        buttons = keyboard.inline_keyboard
        assert any("Descargar" in btn.text or "📥" in btn.text for row in buttons for btn in row)

    def test_key_actions_has_delete_button(self):
        """key_actions incluye botón de eliminar."""
        from src.bot.keyboards.trusttunnel import TrustTunnelKeyboard

        keyboard = TrustTunnelKeyboard.key_actions(key_id="test-uuid", is_active=True)
        buttons = keyboard.inline_keyboard
        assert any("Eliminar" in btn.text or "🗑️" in btn.text for row in buttons for btn in row)

    def test_key_actions_inactive_has_reactivate(self):
        """key_actions para clave inactiva incluye reactivar."""
        from src.bot.keyboards.trusttunnel import TrustTunnelKeyboard

        keyboard = TrustTunnelKeyboard.key_actions(key_id="test-uuid", is_active=False)
        buttons = keyboard.inline_keyboard
        assert any("Reactivar" in btn.text or "✅" in btn.text for row in buttons for btn in row)

    def test_confirm_delete_exists(self):
        """confirm_delete retorna InlineKeyboardMarkup."""
        from src.bot.keyboards.trusttunnel import TrustTunnelKeyboard

        keyboard = TrustTunnelKeyboard.confirm_delete(key_id="test-uuid")
        assert isinstance(keyboard, InlineKeyboardMarkup)

    def test_back_to_list_exists(self):
        """back_to_list retorna InlineKeyboardMarkup."""
        from src.bot.keyboards.trusttunnel import TrustTunnelKeyboard

        keyboard = TrustTunnelKeyboard.back_to_list()
        assert isinstance(keyboard, InlineKeyboardMarkup)

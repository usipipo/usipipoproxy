"""Teclados para gestión de TrustTunnel VPN."""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


class TrustTunnelKeyboard:
    """Teclados para gestión de TrustTunnel VPN."""

    @staticmethod
    def key_actions(key_id: str, is_active: bool) -> InlineKeyboardMarkup:
        """
        Teclado de acciones para una clave TrustTunnel.

        Args:
            key_id: ID de la clave
            is_active: Si la clave está activa

        Returns:
            InlineKeyboardMarkup: Teclado de acciones
        """
        keyboard = []

        # Download config and copy deeplink row
        keyboard.append(
            [
                InlineKeyboardButton(
                    "📥 Descargar .toml",
                    callback_data=f"vpn_download_tt_{key_id}",
                ),
                InlineKeyboardButton(
                    "📋 Copiar Deeplink",
                    callback_data=f"vpn_copy_deeplink_{key_id}",
                ),
            ]
        )

        # Management row
        management_row = []
        if not is_active:
            management_row.append(
                InlineKeyboardButton("✅ Reactivar", callback_data=f"vpn_reactivate_{key_id}")
            )
        management_row.append(
            InlineKeyboardButton("✏️ Renombrar", callback_data=f"vpn_rename_{key_id}")
        )
        keyboard.append(management_row)

        # Delete
        keyboard.append(
            [InlineKeyboardButton("🗑️ Eliminar Clave", callback_data=f"vpn_delete_{key_id}")]
        )

        # Navigation
        keyboard.append(
            [InlineKeyboardButton("🔙 Volver a la lista", callback_data="vpn_keys_menu")]
        )

        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def confirm_delete(key_id: str) -> InlineKeyboardMarkup:
        """Teclado de confirmación para eliminar clave."""
        keyboard = [
            [
                InlineKeyboardButton(
                    "✅ Sí, Eliminar", callback_data=f"vpn_confirm_delete_{key_id}"
                ),
                InlineKeyboardButton("❌ Cancelar", callback_data="vpn_cancel_delete"),
            ]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def back_to_list() -> InlineKeyboardMarkup:
        """Volver a la lista de claves."""
        keyboard = [[InlineKeyboardButton("🔙 Volver a la lista", callback_data="vpn_keys_menu")]]
        return InlineKeyboardMarkup(keyboard)

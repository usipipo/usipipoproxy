"""Teclado del menú principal para navegación del bot uSipipo."""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


class MainMenuKeyboard:
    """Teclado del menú principal con botones inline."""

    @staticmethod
    def main_menu() -> InlineKeyboardMarkup:
        """
        Retorna teclado principal con botones de navegación.

        Returns:
            InlineKeyboardMarkup: Teclado con botones VPN, Operaciones, Datos, Soporte
        """
        keyboard = [
            # Fila 1: Claves VPN
            [
                InlineKeyboardButton("🔑 Mis Claves VPN", callback_data="vpn_keys_menu"),
                InlineKeyboardButton("➕ Nueva Clave", callback_data="vpn_create_key"),
            ],
            # Fila 2: Operaciones y Datos
            [
                InlineKeyboardButton("⚙️ Operaciones", callback_data="operations_menu"),
                InlineKeyboardButton("💾 Mis Datos", callback_data="show_usage"),
            ],
            # Fila 3: Soporte Técnico
            [
                InlineKeyboardButton("💬 Soporte Técnico", url="https://t.me/uSipipoSupport_Bot"),
            ],
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def main_menu_with_admin(admin_id: int, current_user_id: int) -> InlineKeyboardMarkup:
        """
        Retorna teclado principal con botón de admin si corresponde.

        Args:
            admin_id: ID del administrador principal
            current_user_id: ID del usuario actual

        Returns:
            InlineKeyboardMarkup: Teclado con o sin botón de admin
        """
        if str(current_user_id) == str(admin_id):
            keyboard = [
                # Fila 0: Admin (solo para admin)
                [InlineKeyboardButton("🔧 Admin", callback_data="admin_panel")],
                # Fila 1: Claves VPN
                [
                    InlineKeyboardButton("🔑 Mis Claves VPN", callback_data="vpn_keys_menu"),
                    InlineKeyboardButton("➕ Nueva Clave", callback_data="vpn_create_key"),
                ],
                # Fila 2: Operaciones y Datos
                [
                    InlineKeyboardButton("⚙️ Operaciones", callback_data="operations_menu"),
                    InlineKeyboardButton("💾 Mis Datos", callback_data="show_usage"),
                ],
                # Fila 3: Soporte Técnico
                [
                    InlineKeyboardButton(
                        "💬 Soporte Técnico", url="https://t.me/uSipipoSupport_Bot"
                    ),
                ],
            ]
            return InlineKeyboardMarkup(keyboard)

        return MainMenuKeyboard.main_menu()

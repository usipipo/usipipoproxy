"""Teclados para operaciones del usuario."""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


class OperationsKeyboard:
    """Teclados para operaciones del usuario."""

    @staticmethod
    def operations_menu(credits: int = 0) -> InlineKeyboardMarkup:
        """
        Teclado del menú de operaciones.

        Args:
            credits: Créditos de referidos disponibles

        Returns:
            InlineKeyboardMarkup: Teclado de operaciones
        """
        keyboard = [
            # Sección de Beneficios y Referidos
            [
                InlineKeyboardButton(f"🎁 Créditos ({credits})", callback_data="credits_menu"),
                InlineKeyboardButton("👥 Referidos", callback_data="referral_menu"),
            ],
            # Sección de Compras e Historial
            [
                InlineKeyboardButton("🛒 Shop", callback_data="shop_menu"),
                InlineKeyboardButton("📜 Historial", callback_data="transactions_history"),
            ],
            # Volver
            [InlineKeyboardButton("🔙 Volver", callback_data="main_menu")],
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def credits_menu(credits: int) -> InlineKeyboardMarkup:
        """
        Teclado para menú de créditos.

        Args:
            credits: Créditos disponibles

        Returns:
            InlineKeyboardMarkup: Teclado de créditos
        """
        keyboard = [
            [
                InlineKeyboardButton("✨ Canjear por GB", callback_data="credits_redeem_data"),
                InlineKeyboardButton("🔑 Canjear por Slot", callback_data="credits_redeem_slot"),
            ],
            [InlineKeyboardButton("🔙 Volver", callback_data="operations_menu")],
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def shop_menu() -> InlineKeyboardMarkup:
        """
        Teclado para tienda.

        Returns:
            InlineKeyboardMarkup: Teclado de tienda
        """
        keyboard = [
            [
                InlineKeyboardButton("📦 Paquetes de GB", callback_data="buy_gb_menu"),
            ],
            [
                InlineKeyboardButton("🔑 Slots Adicionales", callback_data="buy_slots_menu"),
            ],
            [
                InlineKeyboardButton("💎 Suscripciones", callback_data="subscriptions"),
            ],
            [
                InlineKeyboardButton("✨ Extras con Créditos", callback_data="credits_menu"),
            ],
            [InlineKeyboardButton("🔙 Volver", callback_data="operations_menu")],
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def transactions_history_menu(has_more: bool = False, page: int = 0) -> InlineKeyboardMarkup:
        """
        Teclado para historial de transacciones.

        Args:
            has_more: Si hay más páginas
            page: Página actual

        Returns:
            InlineKeyboardMarkup: Teclado de historial
        """
        keyboard = []

        # Botones de paginación si hay más páginas
        if page > 0 or has_more:
            nav_buttons = []
            if page > 0:
                prev_callback = f"transactions_page_{page - 1}"
                nav_buttons.append(InlineKeyboardButton("◀️ Anterior", callback_data=prev_callback))
            if has_more:
                next_callback = f"transactions_page_{page + 1}"
                nav_buttons.append(InlineKeyboardButton("Siguiente ▶️", callback_data=next_callback))
            keyboard.append(nav_buttons)

        keyboard.append(
            [InlineKeyboardButton("🔙 Volver a Operaciones", callback_data="operations_menu")]
        )
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def back_to_operations() -> InlineKeyboardMarkup:
        """
        Teclado para volver a operaciones.

        Returns:
            InlineKeyboardMarkup: Teclado de retorno
        """
        keyboard = [
            [InlineKeyboardButton("🔙 Volver a Operaciones", callback_data="operations_menu")]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def back_to_main_menu() -> InlineKeyboardMarkup:
        """
        Teclado para volver al menú principal.

        Returns:
            InlineKeyboardMarkup: Teclado de retorno principal
        """
        keyboard = [
            [InlineKeyboardButton("🔙 Volver al Menú Principal", callback_data="main_menu")]
        ]
        return InlineKeyboardMarkup(keyboard)

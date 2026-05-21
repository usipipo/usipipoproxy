"""Teclados para facturación por consumo."""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


class ConsumptionKeyboard:
    """Teclados para el sistema de facturación por consumo."""

    @staticmethod
    def consumption_main_menu(
        is_active: bool = False,
        has_debt: bool = False,
        can_activate: bool = False,
    ) -> InlineKeyboardMarkup:
        """
        Menú principal de tarifa por consumo.

        Args:
            is_active: Si el usuario tiene un ciclo activo
            has_debt: Si el usuario tiene deuda pendiente
            can_activate: Si el usuario puede activar el modo consumo

        Returns:
            InlineKeyboardMarkup: Teclado del menú principal
        """
        keyboard = []

        if has_debt:
            # Usuario con deuda - mostrar botón de generar factura
            keyboard.append(
                [
                    InlineKeyboardButton(
                        "💳 Generar Factura",
                        callback_data="consumption_generate_invoice",
                    )
                ]
            )
        elif is_active:
            # Usuario con ciclo activo - ver consumo y opción de cancelar
            keyboard.append(
                [InlineKeyboardButton("📊 Ver Mi Consumo", callback_data="consumption_status")]
            )
            keyboard.append(
                [
                    InlineKeyboardButton(
                        "🚫 Cancelar Modo Consumo",
                        callback_data="consumption_cancel",
                    )
                ]
            )
        elif can_activate:
            # Usuario puede activar
            keyboard.append(
                [
                    InlineKeyboardButton(
                        "⚡ Activar Modo Consumo",
                        callback_data="consumption_activate",
                    )
                ]
            )

        # Información siempre disponible
        keyboard.append(
            [InlineKeyboardButton("ℹ️ ¿Qué es el Modo Consumo?", callback_data="consumption_info")]
        )

        keyboard.append([InlineKeyboardButton("🔙 Volver al Menú", callback_data="main_menu")])

        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def activation_confirmation() -> InlineKeyboardMarkup:
        """
        Teclado de confirmación para activar modo consumo.

        Returns:
            InlineKeyboardMarkup: Teclado de confirmación
        """
        keyboard = [
            [
                InlineKeyboardButton(
                    "✅ Acepto los Términos",
                    callback_data="consumption_confirm_activate",
                )
            ],
            [InlineKeyboardButton("❌ Cancelar", callback_data="consumption_menu")],
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def activation_success() -> InlineKeyboardMarkup:
        """
        Teclado para después de activación exitosa.

        Returns:
            InlineKeyboardMarkup: Teclado de éxito
        """
        keyboard = [
            [InlineKeyboardButton("📊 Ver Mi Consumo", callback_data="consumption_status")],
            [InlineKeyboardButton("🔙 Volver al Menú", callback_data="main_menu")],
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def cancellation_confirmation(has_debt: bool = False) -> InlineKeyboardMarkup:
        """
        Teclado de confirmación para cancelar modo consumo.

        Args:
            has_debt: Si hay deuda pendiente

        Returns:
            InlineKeyboardMarkup: Teclado de confirmación
        """
        keyboard = [
            [
                InlineKeyboardButton(
                    "✅ Sí, Cancelar",
                    callback_data="consumption_confirm_cancel",
                ),
                InlineKeyboardButton("❌ No, Volver", callback_data="consumption_menu"),
            ],
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def cancellation_success() -> InlineKeyboardMarkup:
        """
        Teclado para después de cancelación exitosa.

        Returns:
            InlineKeyboardMarkup: Teclado de éxito
        """
        keyboard = [
            [
                InlineKeyboardButton(
                    "💳 Generar Factura", callback_data="consumption_generate_invoice"
                )
            ],
            [InlineKeyboardButton("🔙 Volver al Menú", callback_data="main_menu")],
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def consumption_status() -> InlineKeyboardMarkup:
        """
        Teclado para ver estado de consumo.

        Returns:
            InlineKeyboardMarkup: Teclado de estado
        """
        keyboard = [
            [InlineKeyboardButton("📊 Ver Consumo Detallado", callback_data="consumption_status")],
            [InlineKeyboardButton("🔙 Volver", callback_data="consumption_menu")],
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def invoices_list(has_next: bool = False, page: int = 0) -> InlineKeyboardMarkup:
        """
        Teclado para lista de facturas con paginación.

        Args:
            has_next: Si hay más páginas
            page: Página actual

        Returns:
            InlineKeyboardMarkup: Teclado de facturas
        """
        keyboard = []

        # Botones de paginación si hay más páginas
        if page > 0 or has_next:
            nav_buttons = []
            if page > 0:
                prev_callback = f"consumption_invoices_{page - 1}"
                nav_buttons.append(InlineKeyboardButton("◀️ Anterior", callback_data=prev_callback))
            if has_next:
                next_callback = f"consumption_invoices_{page + 1}"
                nav_buttons.append(InlineKeyboardButton("Siguiente ▶️", callback_data=next_callback))
            keyboard.append(nav_buttons)

        keyboard.append(
            [InlineKeyboardButton("🔙 Volver al Menú", callback_data="consumption_menu")]
        )
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def back_to_consumption_menu() -> InlineKeyboardMarkup:
        """
        Teclado para volver al menú de consumo.

        Returns:
            InlineKeyboardMarkup: Teclado de retorno
        """
        keyboard = [
            [InlineKeyboardButton("📊 Menú Consumo", callback_data="consumption_menu")],
            [InlineKeyboardButton("🔙 Menú Principal", callback_data="main_menu")],
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def back_to_menu() -> InlineKeyboardMarkup:
        """
        Teclado para volver al menú principal.

        Returns:
            InlineKeyboardMarkup: Teclado de retorno
        """
        keyboard = [
            [InlineKeyboardButton("🔙 Volver al Menú Principal", callback_data="main_menu")]
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def inactive_state_menu() -> InlineKeyboardMarkup:
        """
        Teclado para estado inactivo.

        Returns:
            InlineKeyboardMarkup: Teclado inactivo
        """
        keyboard = [
            [
                InlineKeyboardButton(
                    "⚡ Activar Modo Consumo",
                    callback_data="consumption_activate",
                )
            ],
            [InlineKeyboardButton("ℹ️ ¿Qué es el Modo Consumo?", callback_data="consumption_info")],
            [InlineKeyboardButton("🔙 Volver al Menú", callback_data="main_menu")],
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def active_state_menu() -> InlineKeyboardMarkup:
        """
        Teclado para estado activo.

        Returns:
            InlineKeyboardMarkup: Teclado activo
        """
        keyboard = [
            [InlineKeyboardButton("📊 Ver Mi Consumo", callback_data="consumption_status")],
            [
                InlineKeyboardButton(
                    "🚫 Cancelar Modo Consumo",
                    callback_data="consumption_cancel",
                )
            ],
            [InlineKeyboardButton("🔙 Volver al Menú", callback_data="main_menu")],
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def debt_state_menu() -> InlineKeyboardMarkup:
        """
        Teclado para estado con deuda.

        Returns:
            InlineKeyboardMarkup: Teclado con deuda
        """
        keyboard = [
            [
                InlineKeyboardButton(
                    "💳 Generar Factura",
                    callback_data="consumption_generate_invoice",
                )
            ],
            [InlineKeyboardButton("📊 Ver Facturas", callback_data="consumption_invoices")],
            [InlineKeyboardButton("🔙 Volver al Menú", callback_data="main_menu")],
        ]
        return InlineKeyboardMarkup(keyboard)

"""Teclados para gestión de paquetes de datos (Data Packages)."""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


class PackagesKeyboard:
    """Teclados para gestión de paquetes de datos."""

    @staticmethod
    def packages_menu(packages: list) -> InlineKeyboardMarkup:
        """
        Teclado del menú principal de paquetes.

        Args:
            packages: Lista de paquetes disponibles

        Returns:
            InlineKeyboardMarkup: Teclado del menú de paquetes
        """
        keyboard = []

        # Create buttons for each package
        for pkg in packages:
            package_id = pkg.get("id", "unknown")
            package_name = pkg.get("name", "Unknown")
            data_gb = pkg.get("data_gb", 0)
            keyboard.append(
                [
                    InlineKeyboardButton(
                        f"📦 {package_name} ({data_gb} GB)",
                        callback_data=f"select_package_{package_id}",
                    )
                ]
            )

        # Additional options
        keyboard.append(
            [
                InlineKeyboardButton("📊 Ver Resumen de Datos", callback_data="view_data_summary"),
            ]
        )
        keyboard.append(
            [
                InlineKeyboardButton("🗂️ Gestionar Slots", callback_data="buy_slots_menu"),
            ]
        )
        keyboard.append(
            [
                InlineKeyboardButton("🔙 Volver al Menú Principal", callback_data="main_menu"),
            ]
        )

        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def payment_method_selection(package_id: str) -> InlineKeyboardMarkup:
        """
        Teclado para seleccionar método de pago.

        Args:
            package_id: ID del paquete seleccionado

        Returns:
            InlineKeyboardMarkup: Teclado de selección de pago
        """
        keyboard = [
            [
                InlineKeyboardButton(
                    "⭐ Pagar con Telegram Stars",
                    callback_data=f"pay_stars_{package_id}",
                ),
            ],
            [
                InlineKeyboardButton(
                    "🪙 Pagar con Crypto (USDT)",
                    callback_data=f"pay_crypto_{package_id}",
                ),
            ],
            [
                InlineKeyboardButton("🔙 Volver", callback_data="buy_gb_menu"),
            ],
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def back_to_menu() -> InlineKeyboardMarkup:
        """
        Teclado para volver al menú de paquetes.

        Returns:
            InlineKeyboardMarkup: Teclado de retorno
        """
        keyboard = [[InlineKeyboardButton("🔙 Volver", callback_data="buy_gb_menu")]]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def back_to_packages() -> InlineKeyboardMarkup:
        """
        Teclado para volver a la lista de paquetes.

        Returns:
            InlineKeyboardMarkup: Teclado de retorno
        """
        keyboard = [[InlineKeyboardButton("📦 Ver Paquetes", callback_data="buy_gb_menu")]]
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

    @staticmethod
    def crypto_payment_status(payment_id: str) -> InlineKeyboardMarkup:
        """
        Teclado para verificar estado de pago crypto.

        Args:
            payment_id: ID del pago

        Returns:
            InlineKeyboardMarkup: Teclado de verificación
        """
        keyboard = [
            [
                InlineKeyboardButton(
                    "🔄 Verificar Estado",
                    callback_data=f"check_crypto_status_{payment_id}",
                ),
            ],
            [
                InlineKeyboardButton("🔙 Volver a Paquetes", callback_data="buy_gb_menu"),
            ],
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def data_summary_menu() -> InlineKeyboardMarkup:
        """
        Teclado del menú de resumen de datos.

        Returns:
            InlineKeyboardMarkup: Teclado de resumen
        """
        keyboard = [
            [
                InlineKeyboardButton("📦 Comprar Más Datos", callback_data="buy_gb_menu"),
            ],
            [
                InlineKeyboardButton("🗂️ Gestionar Slots", callback_data="buy_slots_menu"),
            ],
            [
                InlineKeyboardButton("🔙 Volver", callback_data="main_menu"),
            ],
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def packages_menu_button() -> InlineKeyboardMarkup:
        """
        Botón simple para ir al menú de paquetes.

        Returns:
            InlineKeyboardMarkup: Teclado con botón
        """
        keyboard = [
            [InlineKeyboardButton("📦 Ver Paquetes Disponibles", callback_data="buy_gb_menu")],
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def slots_menu(has_packages: bool = True) -> InlineKeyboardMarkup:
        """
        Teclado del menú de slots.

        Args:
            has_packages: Si hay paquetes disponibles para comprar

        Returns:
            InlineKeyboardMarkup: Teclado de slots
        """
        keyboard = []

        if has_packages:
            keyboard.append(
                [
                    InlineKeyboardButton("➕ Comprar Slot Extra", callback_data="buy_extra_slot"),
                ]
            )

        keyboard.append(
            [
                InlineKeyboardButton("📊 Ver Resumen", callback_data="view_data_summary"),
            ]
        )
        keyboard.append(
            [
                InlineKeyboardButton("🔙 Volver", callback_data="buy_gb_menu"),
            ]
        )

        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def buy_slot_confirmation() -> InlineKeyboardMarkup:
        """
        Teclado de confirmación para compra de slot.

        Returns:
            InlineKeyboardMarkup: Teclado de confirmación
        """
        keyboard = [
            [
                InlineKeyboardButton("✅ Confirmar Compra", callback_data="confirm_buy_slot"),
                InlineKeyboardButton("❌ Cancelar", callback_data="buy_slots_menu"),
            ],
        ]
        return InlineKeyboardMarkup(keyboard)

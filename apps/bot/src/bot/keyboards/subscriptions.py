"""Teclados para gestión de suscripciones y planes (Subscriptions & Plans)."""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


class SubscriptionsKeyboard:
    """Teclados para gestión de suscripciones y planes."""

    @staticmethod
    def subscription_menu(is_active: bool) -> InlineKeyboardMarkup:
        """
        Teclado del menú principal de suscripciones.

        Args:
            is_active: Si el usuario tiene una suscripción activa

        Returns:
            InlineKeyboardMarkup: Teclado del menú de suscripciones
        """
        keyboard = []

        if is_active:
            # User has active subscription - show renewal and status options
            keyboard.append(
                [
                    InlineKeyboardButton(
                        "📊 Ver Estado de Suscripción",
                        callback_data="view_subscription_status",
                    )
                ]
            )
            keyboard.append(
                [
                    InlineKeyboardButton(
                        "🔄 Renovar Suscripción",
                        callback_data="renew_subscription",
                    )
                ]
            )
        else:
            # No active subscription - show view plans option
            keyboard.append(
                [
                    InlineKeyboardButton(
                        "📦 Ver Planes Disponibles",
                        callback_data="view_plans",
                    )
                ]
            )

        keyboard.append(
            [InlineKeyboardButton("🔙 Volver al Menú Principal", callback_data="main_menu")]
        )

        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def subscription_active_menu() -> InlineKeyboardMarkup:
        """
        Teclado para suscripción activa.

        Returns:
            InlineKeyboardMarkup: Teclado para suscripción activa
        """
        keyboard = [
            [
                InlineKeyboardButton(
                    "📊 Ver Estado Detallado",
                    callback_data="view_subscription_status",
                )
            ],
            [
                InlineKeyboardButton(
                    "🔄 Renovar Suscripción",
                    callback_data="renew_subscription",
                )
            ],
            [InlineKeyboardButton("🔙 Volver al Menú Principal", callback_data="main_menu")],
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def subscription_inactive_menu() -> InlineKeyboardMarkup:
        """
        Teclado para suscripción inactiva.

        Returns:
            InlineKeyboardMarkup: Teclado para suscripción inactiva
        """
        keyboard = [
            [
                InlineKeyboardButton(
                    "📦 Ver Planes Disponibles",
                    callback_data="view_plans",
                )
            ],
            [InlineKeyboardButton("🔙 Volver al Menú Principal", callback_data="main_menu")],
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def subscription_status_menu(subscription: dict) -> InlineKeyboardMarkup:
        """
        Teclado para estado de suscripción.

        Args:
            subscription: Diccionario con datos de la suscripción

        Returns:
            InlineKeyboardMarkup: Teclado de estado
        """
        keyboard = []

        # Show renewal button if subscription is active
        if subscription.get("status") == "active":
            keyboard.append(
                [
                    InlineKeyboardButton(
                        "🔄 Renovar Ahora",
                        callback_data="renew_subscription",
                    )
                ]
            )

        keyboard.append(
            [
                InlineKeyboardButton("📦 Ver Otros Planes", callback_data="view_plans"),
            ]
        )
        keyboard.append(
            [
                InlineKeyboardButton("🔙 Volver", callback_data="subscription_menu"),
            ]
        )

        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def plans_list(plans: list) -> InlineKeyboardMarkup:
        """
        Teclado con lista de planes disponibles.

        Args:
            plans: Lista de planes disponibles

        Returns:
            InlineKeyboardMarkup: Teclado de planes
        """
        keyboard = []

        # Create buttons for each plan
        for plan in plans:
            plan_id = plan.get("id", "unknown")
            plan_name = plan.get("name", "Unknown Plan")
            price = plan.get("price", 0)
            keyboard.append(
                [
                    InlineKeyboardButton(
                        f"📦 {plan_name} - ${price:.2f}",
                        callback_data=f"select_plan_{plan_id}",
                    )
                ]
            )

        # Back button
        keyboard.append([InlineKeyboardButton("🔙 Volver", callback_data="subscription_menu")])

        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def plan_details(plan_id: str) -> InlineKeyboardMarkup:
        """
        Teclado para detalles de un plan específico.

        Args:
            plan_id: ID del plan seleccionado

        Returns:
            InlineKeyboardMarkup: Teclado de detalles
        """
        keyboard = [
            [
                InlineKeyboardButton(
                    "⚡ Seleccionar Plan",
                    callback_data=f"choose_payment_{plan_id}",
                )
            ],
            [
                InlineKeyboardButton("📦 Ver Otros Planes", callback_data="view_plans"),
            ],
            [
                InlineKeyboardButton("🔙 Volver", callback_data="subscription_menu"),
            ],
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def plan_selection(plan_id: str) -> InlineKeyboardMarkup:
        """
        Teclado para selección de plan (alias para plan_details).

        Args:
            plan_id: ID del plan seleccionado

        Returns:
            InlineKeyboardMarkup: Teclado de selección
        """
        return SubscriptionsKeyboard.plan_details(plan_id)

    @staticmethod
    def payment_method_selection(plan_id: str) -> InlineKeyboardMarkup:
        """
        Teclado para seleccionar método de pago.

        Args:
            plan_id: ID del paquete seleccionado

        Returns:
            InlineKeyboardMarkup: Teclado de selección de pago
        """
        keyboard = [
            [
                InlineKeyboardButton(
                    "⭐ Pagar con Telegram Stars",
                    callback_data=f"activate_plan_{plan_id}_stars",
                ),
            ],
            [
                InlineKeyboardButton(
                    "🪙 Pagar con Crypto (USDT)",
                    callback_data=f"activate_plan_{plan_id}_crypto",
                ),
            ],
            [
                InlineKeyboardButton("🔙 Volver", callback_data="view_plans"),
            ],
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
            [
                InlineKeyboardButton(
                    "📊 Ver Mi Suscripción",
                    callback_data="view_subscription_status",
                )
            ],
            [InlineKeyboardButton("🔙 Volver al Menú Principal", callback_data="main_menu")],
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def renewal_menu() -> InlineKeyboardMarkup:
        """
        Teclado para menú de renovación.

        Returns:
            InlineKeyboardMarkup: Teclado de renovación
        """
        keyboard = [
            [
                InlineKeyboardButton(
                    "🔄 Confirmar Renovación",
                    callback_data="renew_subscription",
                )
            ],
            [
                InlineKeyboardButton("📦 Ver Otros Planes", callback_data="view_plans"),
            ],
            [
                InlineKeyboardButton("🔙 Volver", callback_data="subscription_menu"),
            ],
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def back_to_subscription() -> InlineKeyboardMarkup:
        """
        Teclado para volver al menú de suscripciones.

        Returns:
            InlineKeyboardMarkup: Teclado de retorno
        """
        keyboard = [
            [InlineKeyboardButton("📊 Suscripción", callback_data="subscription_menu")],
            [InlineKeyboardButton("🔙 Menú Principal", callback_data="main_menu")],
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def back_to_subscription_menu() -> InlineKeyboardMarkup:
        """
        Teclado para volver al menú de suscripciones (alias).

        Returns:
            InlineKeyboardMarkup: Teclado de retorno
        """
        return SubscriptionsKeyboard.back_to_subscription()

    @staticmethod
    def back_to_main() -> InlineKeyboardMarkup:
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
    def back_to_menu() -> InlineKeyboardMarkup:
        """
        Teclado para volver al menú principal (alias).

        Returns:
            InlineKeyboardMarkup: Teclado de retorno
        """
        return SubscriptionsKeyboard.back_to_main()

    @staticmethod
    def back_to_plans() -> InlineKeyboardMarkup:
        """
        Teclado para volver a la lista de planes.

        Returns:
            InlineKeyboardMarkup: Teclado de retorno a planes
        """
        keyboard = [
            [InlineKeyboardButton("📦 Ver Planes", callback_data="view_plans")],
            [InlineKeyboardButton("🔙 Volver", callback_data="subscription_menu")],
        ]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def view_plans_button() -> InlineKeyboardMarkup:
        """
        Botón simple para ver planes.

        Returns:
            InlineKeyboardMarkup: Teclado con botón
        """
        keyboard = [
            [InlineKeyboardButton("📦 Ver Planes Disponibles", callback_data="view_plans")],
            [InlineKeyboardButton("🔙 Volver al Menú", callback_data="main_menu")],
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
                InlineKeyboardButton(
                    "🔙 Volver a Suscripciones", callback_data="subscription_menu"
                ),
            ],
        ]
        return InlineKeyboardMarkup(keyboard)

"""Teclados para gestión de claves VPN."""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


class KeysKeyboard:
    """Teclados para gestión de claves VPN."""

    @staticmethod
    def main_menu(
        total_keys: int, outline_count: int, wireguard_count: int, trusttunnel_count: int = 0
    ) -> InlineKeyboardMarkup:
        """
        Teclado del menú principal de gestión de claves.

        Args:
            total_keys: Total de claves del usuario
            outline_count: Cantidad de claves Outline
            wireguard_count: Cantidad de claves WireGuard
            trusttunnel_count: Cantidad de claves TrustTunnel

        Returns:
            InlineKeyboardMarkup: Teclado del menú principal
        """
        keyboard = []

        if total_keys == 0:
            keyboard.append(
                [InlineKeyboardButton("➕ Crear Nueva Clave", callback_data="vpn_create_key")]
            )
            keyboard.append(
                [InlineKeyboardButton("🔙 Volver al Menú Principal", callback_data="main_menu")]
            )
            return InlineKeyboardMarkup(keyboard)

        # Fila de tipos de claves
        keys_row = []
        if outline_count > 0:
            keys_row.append(
                InlineKeyboardButton(
                    f"🌐 Outline ({outline_count})",
                    callback_data="vpn_keys_outline",
                )
            )

        if wireguard_count > 0:
            keys_row.append(
                InlineKeyboardButton(
                    f"🔒 WireGuard ({wireguard_count})",
                    callback_data="vpn_keys_wireguard",
                )
            )

        if trusttunnel_count > 0:
            keys_row.append(
                InlineKeyboardButton(
                    f"🛡️ TrustTunnel ({trusttunnel_count})",
                    callback_data="vpn_keys_trusttunnel",
                )
            )

        if keys_row:
            keyboard.append(keys_row)

        keyboard.extend(
            [
                [
                    InlineKeyboardButton("➕ Crear Nueva", callback_data="vpn_create_key"),
                ],
                [
                    InlineKeyboardButton("📊 Estadísticas", callback_data="vpn_key_stats"),
                ],
                [InlineKeyboardButton("🔙 Volver al Menú Principal", callback_data="main_menu")],
            ]
        )

        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def keys_list(keys: list, key_type: str) -> InlineKeyboardMarkup:
        """
        Genera teclado dinámico para lista de claves.

        Args:
            keys: Lista de claves VPN
            key_type: Tipo de clave (outline, wireguard)

        Returns:
            InlineKeyboardMarkup: Teclado de lista de claves
        """
        keyboard = []

        for key in keys:
            status_emoji = "🟢" if key.get("status", "active") == "active" else "🔴"
            button_text = f"{status_emoji} {key.get('name', 'Unknown')}"
            callback_data = f"vpn_key_details_{key['id']}"
            keyboard.append([InlineKeyboardButton(button_text, callback_data=callback_data)])

        keyboard.append([InlineKeyboardButton("➕ Crear Nueva", callback_data="vpn_create_key")])
        keyboard.append([InlineKeyboardButton("🔙 Volver", callback_data="vpn_keys_menu")])

        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def key_actions(key_id: str, is_active: bool, key_type: str) -> InlineKeyboardMarkup:
        """
        Teclado de acciones para una clave específica.

        Args:
            key_id: ID de la clave
            is_active: Si la clave está activa
            key_type: Tipo de clave (wireguard, outline)

        Returns:
            InlineKeyboardMarkup: Teclado de acciones
        """
        keyboard = []

        # 1. Acción principal (Descarga/Enlace) - Prominente
        if key_type.lower() == "wireguard":
            keyboard.append(
                [
                    InlineKeyboardButton(
                        "📥 Descargar Configuración .conf",
                        callback_data=f"vpn_download_wg_{key_id}",
                    )
                ]
            )
        elif key_type.lower() == "outline":
            keyboard.append(
                [
                    InlineKeyboardButton(
                        "🔗 Obtener Clave de Acceso",
                        callback_data=f"vpn_get_link_{key_id}",
                    )
                ]
            )

        # 2. Acciones de Gestión (Estado y Nombre)
        management_row = []
        if not is_active:
            management_row.append(
                InlineKeyboardButton("✅ Reactivar", callback_data=f"vpn_reactivate_{key_id}")
            )

        management_row.append(
            InlineKeyboardButton("✏️ Renombrar", callback_data=f"vpn_rename_{key_id}")
        )
        keyboard.append(management_row)

        # 3. Eliminar clave
        keyboard.append(
            [InlineKeyboardButton("🗑️ Eliminar Clave", callback_data=f"vpn_delete_{key_id}")]
        )

        # 4. Navegación
        keyboard.append(
            [InlineKeyboardButton("🔙 Volver a la lista", callback_data="vpn_keys_menu")]
        )

        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def confirm_delete(key_id: str) -> InlineKeyboardMarkup:
        """
        Teclado de confirmación para eliminar clave.

        Args:
            key_id: ID de la clave

        Returns:
            InlineKeyboardMarkup: Teclado de confirmación
        """
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
    def cancel_rename() -> InlineKeyboardMarkup:
        """
        Teclado para cancelar el renombrado.

        Returns:
            InlineKeyboardMarkup: Teclado de cancelación
        """
        keyboard = [[InlineKeyboardButton("❌ Cancelar", callback_data="vpn_cancel_rename")]]
        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def back_to_menu() -> InlineKeyboardMarkup:
        """
        Teclado para volver al menú de claves.

        Returns:
            InlineKeyboardMarkup: Teclado de retorno
        """
        keyboard = [[InlineKeyboardButton("🔙 Volver", callback_data="vpn_keys_menu")]]
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
    def protocol_selection() -> InlineKeyboardMarkup:
        """
        Teclado para selección de protocolo VPN.

        Returns:
            InlineKeyboardMarkup: Teclado con botones Outline, WireGuard y TrustTunnel
        """
        keyboard = [
            [
                InlineKeyboardButton("🌐 Outline", callback_data="vpn_create_outline"),
                InlineKeyboardButton("🔒 WireGuard", callback_data="vpn_create_wireguard"),
            ],
            [
                InlineKeyboardButton("🛡️ TrustTunnel", callback_data="vpn_create_trusttunnel"),
            ],
            [InlineKeyboardButton("🔙 Cancelar", callback_data="vpn_keys_menu")],
        ]
        return InlineKeyboardMarkup(keyboard)

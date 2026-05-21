"""Mensajes para operaciones del usuario."""


class OperationsMessages:
    """Mensajes para operaciones del usuario."""

    # ============================================
    # MAIN MENU
    # ============================================

    class Menu:
        """Mensajes del menú de operaciones."""

        MAIN = (
            "⚙️ *Operaciones*\n\n"
            "Gestiona tus beneficios y compras:\n\n"
            "🎁 Beneficios de referidos\n"
            "🛒 Tienda de paquetes\n"
            "📜 Historial de transacciones"
        )

        MAIN_WITH_CREDITS = (
            "⚙️ *Operaciones*\n\n"
            "🎁 *Créditos disponibles:* {credits}\n\n"
            "Gestiona tus beneficios y compras:\n\n"
            "🎁 Canjea créditos por GB o slots\n"
            "🛒 Tienda de paquetes\n"
            "📜 Historial de transacciones"
        )

    # ============================================
    # CREDITS
    # ============================================

    class Credits:
        """Mensajes de créditos."""

        DISPLAY = (
            "🎁 *Tus Créditos*\n\n"
            "💰 Saldo: *{credits} créditos*\n\n"
            "✨ Canjea tus créditos por:\n"
            "• 📦 Paquetes de datos (GB)\n"
            "• 🔑 Slots adicionales de VPN\n\n"
            "⚡ *Elige una opción:*"
        )

        REDEEM_DATA = (
            "📦 *Canjear por Datos*\n\n"
            "10 créditos = 1 GB adicional\n\n"
            "Tienes {credits} créditos disponibles.\n"
            "¿Cuántos GB deseas obtener?"
        )

        REDEEM_SLOT = (
            "🔑 *Canjear por Slot*\n\n"
            "50 créditos = 1 slot adicional\n\n"
            "Tienes {credits} créditos disponibles.\n"
            "¿Deseas canjear por un slot?"
        )

        REDEEM_SUCCESS = (
            "✅ *Canje exitoso*\n\n"
            "Has canjeado {credits} créditos por {item}.\n\n"
            "🎉 ¡Disfruta tu beneficio!"
        )

        INSUFFICIENT_CREDITS = (
            "❌ *Créditos insuficientes*\n\n"
            "Necesitas {required} créditos para este canje.\n"
            "Tienes {available} créditos.\n\n"
            "💡 Sigue invitando amigos para ganar más créditos!"
        )

    # ============================================
    # SHOP
    # ============================================

    class Shop:
        """Mensajes de la tienda."""

        WELCOME = (
            "🛒 *Tienda uSipipo*\n\n"
            "Elige qué deseas adquirir:\n\n"
            "📦 Paquetes de datos\n"
            "🔑 Slots adicionales\n"
            "💎 Suscripciones\n"
            "✨ Extras con créditos"
        )

        ITEMS_LIST = "📦 *Paquetes Disponibles*\n\n{items}\n\n⚡ Selecciona un paquete para comprar"

    # ============================================
    # TRANSACTIONS HISTORY
    # ============================================

    class Transactions:
        """Mensajes de historial de transacciones."""

        HISTORY_HEADER = "📜 *Historial de Transacciones*\n\nPágina {page}\n\n"

        NO_TRANSACTIONS = (
            "📜 *Sin transacciones*\n\n"
            "Aún no has realizado ninguna transacción.\n\n"
            "💡 ¡Comienza comprando tu primer paquete!"
        )

        TRANSACTION_ITEM = "🔹 {date} - {type}\n   💰 {amount} créditos\n   📦 {description}\n"

    # ============================================
    # REFERRALS
    # ============================================

    class Referrals:
        """Mensajes de referidos."""

        MENU = (
            "👥 *Programa de Referidos*\n\n"
            "🎁 *Beneficios:*\n"
            "• 1 crédito por cada amigo invitado\n"
            "• 5 créditos si tu amigo compra un paquete\n\n"
            "🔗 *Tu enlace de referido:*\n"
            "`{link}`\n\n"
            "📊 *Estadísticas:*\n"
            "• Amigos invitados: {invited}\n"
            "• Créditos ganados: {credits}"
        )

    # ============================================
    # ERRORS
    # ============================================

    class Error:
        """Mensajes de error."""

        SYSTEM_ERROR = (
            "🚨 *Error del sistema*\n\n💥 Fallo temporal\n\n🔄 Intenta de nuevo en un momento 📡"
        )

        OPERATION_FAILED = "❌ *Operación fallida*\n\n💥 No se pudo completar\n\n📟 {error}"

        INVALID_OPTION = "⛔ *Opción inválida*\n\n🚫 No disponible en este momento"

    # ============================================
    # SUCCESS
    # ============================================

    class Success:
        """Mensajes de éxito."""

        OPERATION_COMPLETED = "✅ *Listo*\n\n⚡ Operación completada 🎯"

        CHANGES_SAVED = "💾 *Guardado*\n\n✨ Cambios actualizados"

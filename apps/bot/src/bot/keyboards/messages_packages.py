"""Mensajes para gestión de paquetes de datos (Data Packages)."""


class PackagesMessages:
    """Mensajes para gestión de paquetes de datos."""

    # ============================================
    # MAIN MENU
    # ============================================

    class Menu:
        """Mensajes del menú."""

        PACKAGES_LIST = (
            "📦 *Paquetes de Datos Disponibles*\n\n"
            "Elige el paquete que mejor se adapte a tus necesidades:\n\n"
        )

        PACKAGE_ITEM = (
            "🔹 *{name}* - {data} GB\n   💰 ${price_usd} USD\n   ⭐ {price_stars} Stars\n\n"
        )

        PACKAGE_DETAILS = (
            "📦 *Paquete {name}*\n\n"
            "📊 Datos: {data} GB\n"
            "💰 Precio:\n"
            "   • ${price_usd} USD\n"
            "   • ⭐ {price_stars} Stars\n\n"
            "⚡ *Selecciona tu método de pago:*"
        )

        NO_PACKAGES = (
            "📭 *Sin paquetes disponibles*\n\n"
            "No hay paquetes disponibles en este momento.\n\n"
            "💡 Intenta más tarde."
        )

        INVALID_PACKAGE = "❌ *Paquete inválido*\n\nEl paquete seleccionado no existe."

    # ============================================
    # PAYMENT MESSAGES
    # ============================================

    class Payment:
        """Mensajes de pago."""

        SELECT_METHOD = (
            "💳 *Método de Pago*\n\n"
            "Paquete: {name} ({data} GB)\n\n"
            "Elige cómo deseas pagar:\n\n"
            "⭐ *Telegram Stars* - Pago rápido y seguro\n"
            "   Total: {price_stars} Stars\n\n"
            "🪙 *Crypto (USDT)* - Usando red TRC20\n"
            "   Total: ${price_usd} USD\n\n"
            "⚡ *Selecciona una opción:*"
        )

        STARS_PAYMENT_SENT = (
            "⭐ *Pago con Telegram Stars*\n\n"
            "Se ha enviado la factura de {stars} Stars.\n\n"
            "💡 Revisa tu chat de Telegram para completar el pago."
        )

        STARS_SUCCESS = (
            "✅ *¡Pago Exitoso!*\n\n"
            "🎉 Tu paquete {name} de {data} GB ha sido activado.\n\n"
            "🚀 ¡Disfruta de tu conexión VPN!"
        )

        STARS_FAILED = (
            "❌ *Pago Fallido*\n\n"
            "No se pudo activar tu paquete.\n\n"
            "📟 Motivo: {reason}\n\n"
            "💡 Por favor, contacta a soporte o intenta nuevamente."
        )

        CRYPTO_PAYMENT = (
            "🪙 *Pago con Criptomonedas*\n\n"
            "📦 Paquete: {package_name} ({data_gb} GB)\n"
            "💰 Monto: ${amount_usd} USDT\n"
            "🌐 Red: {network}\n\n"
            "📬 *Dirección de pago:*\n"
            "`{address}`\n\n"
            "⚠️ *Instrucciones:*\n"
            "1. Envía exactamente ${amount_usd} USDT a la dirección anterior\n"
            "2. Usa la red {network} (TRC20)\n"
            "3. El pago se confirmará automáticamente\n"
            "4. Tu paquete se activará tras la confirmación\n\n"
            "⏱️ Tiempo estimado: 5-30 minutos"
        )

        CRYPTO_PENDING = (
            "⏳ *Pago Pendiente*\n\n"
            "Esperando confirmación de tu pago de ${amount} USDT.\n\n"
            "🔄 Presiona 'Verificar Estado' para comprobar."
        )

        CRYPTO_SUCCESS = (
            "✅ *¡Pago Confirmado!*\n\n"
            "🎉 Tu paquete ha sido activado exitosamente.\n\n"
            "🚀 ¡Disfruta de tu conexión VPN!"
        )

        CRYPTO_EXPIRED = (
            "⏰ *Pago Expirado*\n\n"
            "El tiempo límite para el pago ha vencido.\n\n"
            "💡 Por favor, intenta nuevamente con un nuevo paquete."
        )

        CRYPTO_PAYMENT_FAILED = (
            "❌ *Error en Pago Crypto*\n\n"
            "No se pudo generar la dirección de pago.\n\n"
            "💡 Por favor, intenta nuevamente o contacta a soporte."
        )

    # ============================================
    # DATA SUMMARY
    # ============================================

    class Summary:
        """Mensajes de resumen de datos."""

        DATA_SUMMARY = (
            "📊 *Resumen de Datos*\n\n"
            "📦 Paquetes activos: {packages}\n\n"
            "📊 Uso de datos:\n"
            "   Total: {total} GB\n"
            "   Usado: {used} GB\n"
            "   Restante: {remaining} GB\n\n"
            "📈 Consumo: {percentage}%\n\n"
            "📅 Próxima renovación: {renewal}\n\n"
            "⚡ *Opciones:*"
        )

        NO_ACTIVE_PACKAGES = (
            "📭 *Sin Paquetes Activos*\n\n"
            "No tienes paquetes de datos activos en este momento.\n\n"
            "💡 Compra tu primer paquete para comenzar."
        )

    # ============================================
    # SLOTS MANAGEMENT
    # ============================================

    class Slots:
        """Mensajes de gestión de slots."""

        SLOTS_HEADER = (
            "🗂️ *Tus Slots de Datos*\n\nSlots usados: {used}/{max}\n\n📦 *Paquetes activos:*\n\n"
        )

        SLOT_ITEM = "{status} *{name}*\n   📊 {data} GB\n   📅 Expira: {expires}\n\n"

        NO_SLOTS = (
            "📭 *Sin Slots Activos*\n\n"
            "No tienes paquetes de datos activos.\n\n"
            "💡 Compra tu primer paquete para comenzar."
        )

        BUY_SLOT_PROMPT = (
            "➕ *Comprar Slot Extra*\n\n"
            "¿Deseas comprar un slot de datos adicional?\n\n"
            "💡 Un slot te permite tener múltiples paquetes activos simultáneamente."
        )

        SLOT_PURCHASED = (
            "✅ *Slot Comprado*\n\n"
            "Tu slot extra ha sido añadido exitosamente.\n\n"
            "🚀 Ahora puedes activar un paquete adicional."
        )

        SLOT_PURCHASE_FAILED = (
            "❌ *Error en Compra*\n\n"
            "No se pudo completar la compra del slot.\n\n"
            "💡 Por favor, intenta nuevamente o contacta a soporte."
        )

        MAX_SLOTS_REACHED = (
            "⚠️ *Límite Alcanzado*\n\n"
            "Has alcanzado el máximo de {max} slots permitidos.\n\n"
            "💡 Contacta a soporte si necesitas más slots."
        )

    # ============================================
    # ERRORS
    # ============================================

    class Error:
        """Mensajes de error."""

        SYSTEM_ERROR = (
            "🚨 *Error del Sistema*\n\n"
            "💥 Ocurrió un error temporal.\n\n"
            "🔄 Intenta nuevamente en un momento."
        )

        NOT_AUTHENTICATED = (
            "🚫 *Acceso Denegado*\n\n"
            "🔒 No has iniciado sesión.\n\n"
            "💡 Usa /start para autenticarte primero."
        )

        INVALID_PACKAGE = (
            "❌ *Paquete Inválido*\n\n"
            "El paquete seleccionado no existe o no está disponible.\n\n"
            "💡 Por favor, elige otro paquete."
        )

        PAYMENT_FAILED = (
            "❌ *Pago Fallido*\n\n"
            "No se pudo procesar tu pago.\n\n"
            "💡 Verifica tu saldo e intenta nuevamente."
        )

        CRYPTO_PAYMENT_FAILED = (
            "❌ *Error en Pago Crypto*\n\n"
            "No se pudo generar la dirección de pago.\n\n"
            "💡 Intenta nuevamente o contacta a soporte."
        )

        NETWORK_ERROR = (
            "📡 *Error de Conexión*\n\n"
            "No se pudo conectar con el servidor.\n\n"
            "🔄 Intenta nuevamente en unos segundos."
        )

        INSUFFICIENT_FUNDS = (
            "⚠️ *Saldo Insuficiente*\n\n"
            "No tienes suficiente saldo para completar esta compra.\n\n"
            "💡 Recarga tu saldo e intenta nuevamente."
        )

        TIMEOUT = (
            "⏰ *Tiempo Agotado*\n\n"
            "La operación ha excedido el tiempo límite.\n\n"
            "🔄 Por favor, intenta nuevamente."
        )

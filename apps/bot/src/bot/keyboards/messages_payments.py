"""Mensajes para gestión de pagos y suscripciones (Payments & Subscriptions)."""


class PaymentMenu:
    """Mensajes del menú de pagos."""

    MAIN_MENU = """
💳 **Menú de Pagos**

Selecciona el monto que deseas pagar:

**Paquetes de Datos (Data Packages):**
• Básico (10 GB) - 250 Stars ⭐ | $2.08 USDT 💰
• Estándar (30 GB) - 600 Stars ⭐ | $5.00 USDT 💰
• Avanzado (60 GB) - 960 Stars ⭐ | $8.00 USDT 💰
• Premium (120 GB) - 1440 Stars ⭐ | $12.00 USDT 💰
• Ilimitado (200 GB) - 1800 Stars ⭐ | $15.00 USDT 💰

**Slots (Claves Extra):**
• +1 Clave - 300 Stars ⭐ | $2.50 USDT 💰
• +3 Claves - 700 Stars ⭐ | $5.83 USDT 💰
• +5 Claves - 1000 Stars ⭐ | $8.33 USDT 💰

_Pagos procesados vía TronDealer (TRC20) y Telegram Stars_
"""


class PaymentsMessages:
    """Mensajes para gestión de pagos y suscripciones."""

    # ============================================
    # MAIN MENU
    # ============================================

    class Menu:
        """Mensajes del menú."""

        PAYMENT_METHODS = (
            "💳 *Métodos de Pago*\n\n"
            "Elige cómo deseas realizar tu pago:\n\n"
            "🪙 *Criptomonedas (USDT)*\n"
            "   • Red TRC20 (Tron)\n"
            "   • Confirmación en 5-30 min\n"
            "   • Ideal para montos grandes\n\n"
            "⭐ *Telegram Stars*\n"
            "   • Pago instantáneo\n"
            "   • Sin salir de Telegram\n"
            "   • Ideal para montos pequeños\n\n"
            "⚡ *Selecciona una opción:*"
        )

        NO_PAYMENT_METHODS = (
            "📭 *Sin métodos de pago disponibles*\n\n"
            "No hay métodos de pago disponibles en este momento.\n\n"
            "💡 Intenta más tarde."
        )

    # ============================================
    # PAYMENT MESSAGES
    # ============================================

    class Payment:
        """Mensajes de pago."""

        CRYPTO_PAYMENT = (
            "🪙 *Pago con Criptomonedas*\n\n"
            "💰 Monto: ${amount_usd} USDT\n"
            "🌐 Red: {network}\n\n"
            "📬 *Dirección de pago:*\n"
            "`{address}`\n\n"
            "⚠️ *Instrucciones:*\n"
            "1. Envía exactamente ${amount_usd} USDT a la dirección anterior\n"
            "2. Usa la red {network} (TRC20)\n"
            "3. El pago se confirmará automáticamente\n"
            "4. Tu saldo se acreditará tras la confirmación\n\n"
            "⏱️ Tiempo estimado: 5-30 minutos\n\n"
            "📱 *O escanea el código QR:*\n{qr_url}"
        )

        CRYPTO_PENDING = (
            "⏳ *Pago Pendiente*\n\n"
            "Esperando confirmación de tu pago de ${amount} USDT.\n\n"
            "🔗 TX Hash: `{tx_hash}`\n\n"
            "🔄 Presiona 'Verificar Estado' para comprobar."
        )

        CRYPTO_SUCCESS = (
            "✅ *¡Pago Confirmado!*\n\n"
            "🎉 Tu pago ha sido confirmado exitosamente.\n\n"
            "💰 Tu saldo ha sido acreditado.\n"
            "🚀 ¡Gracias por tu compra!"
        )

        CRYPTO_EXPIRED = (
            "⏰ *Pago Expirado*\n\n"
            "El tiempo límite para el pago ha vencido.\n\n"
            "💡 Por favor, intenta nuevamente con un nuevo pago."
        )

        STARS_PAYMENT_SENT = (
            "⭐ *Pago con Telegram Stars*\n\n"
            "Se ha enviado la factura de {stars} Stars.\n\n"
            "💡 Revisa tu chat de Telegram para completar el pago."
        )

        STARS_SUCCESS = (
            "✅ *¡Pago Exitoso!*\n\n"
            "🎉 Tu pago de {stars} Stars ha sido procesado.\n\n"
            "💰 Tu saldo ha sido acreditado.\n"
            "🚀 ¡Gracias por tu compra!"
        )

        STARS_FAILED = (
            "❌ *Pago Fallido*\n\n"
            "No se pudo procesar tu pago.\n\n"
            "📟 Motivo: {reason}\n\n"
            "💡 Por favor, contacta a soporte o intenta nuevamente."
        )

    # ============================================
    # PAYMENT HISTORY
    # ============================================

    class History:
        """Mensajes de historial de pagos."""

        HEADER = (
            "📜 *Historial de Pagos*\n\n"
            "📊 Resumen:\n"
            "   Total: {total}\n"
            "   🪙 Crypto: {crypto}\n"
            "   ⭐ Stars: {stars}\n"
            "   ✅ Completados: {completed}\n"
            "   ⏳ Pendientes: {pending}\n\n"
            "📋 *Pagos recientes:*\n\n"
        )

        PAYMENT_ITEM = "{status} *{type}* - {amount}\n   📅 {date}\n   Estado: {status_text}\n\n"

        NO_PAYMENTS = (
            "📭 *Sin Pagos*\n\n"
            "No tienes pagos registrados en este momento.\n\n"
            "💡 Realiza tu primer pago para comenzar."
        )

    # ============================================
    # SUBSCRIPTIONS
    # ============================================

    class Subscriptions:
        """Mensajes de suscripciones."""

        SUBSCRIPTION_ACTIVE = (
            "✅ *Suscripción Activa*\n\n"
            "📦 Plan: {plan_name}\n"
            "📅 Renovación: {renewal_date}\n"
            "💰 Precio: ${price}/mes\n\n"
            "⚙️ *Opciones:*\n"
        )

        SUBSCRIPTION_INACTIVE = (
            "📭 *Sin Suscripción Activa*\n\n"
            "No tienes una suscripción activa en este momento.\n\n"
            "💡 Suscríbete para beneficios exclusivos."
        )

        SUBSCRIPTION_CANCELLED = (
            "✅ *Suscripción Cancelada*\n\n"
            "Tu suscripción ha sido cancelada exitosamente.\n\n"
            "📅 Tendrás acceso hasta: {expiry_date}\n\n"
            "💡 Gracias por haber sido parte de uSipipo."
        )

        SUBSCRIPTION_RENEWED = (
            "🔄 *Suscripción Renovada*\n\n"
            "Tu suscripción ha sido renovada exitosamente.\n\n"
            "📅 Próxima renovación: {renewal_date}\n\n"
            "🚀 ¡Gracias por continuar con nosotros!"
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

        INVALID_AMOUNT = (
            "❌ *Monto Inválido*\n\n"
            "El monto seleccionado no es válido.\n\n"
            "💡 Por favor, elige un monto válido."
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

        PAYMENT_EXPIRED = (
            "⏰ *Pago Expirado*\n\n"
            "El tiempo límite para completar el pago ha vencido.\n\n"
            "💡 Por favor, inicia un nuevo pago."
        )

        DUPLICATE_PAYMENT = (
            "⚠️ *Pago Duplicado*\n\n"
            "Ya existe un pago pendiente con el mismo monto.\n\n"
            "💡 Espera a que se complete o cancela el pago anterior."
        )

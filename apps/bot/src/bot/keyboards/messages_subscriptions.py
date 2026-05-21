"""Mensajes para gestión de suscripciones y planes (Subscriptions & Plans)."""


class SubscriptionsMessages:
    """Mensajes para gestión de suscripciones y planes."""

    # ============================================
    # SUBSCRIPTION STATUS
    # ============================================

    class Subscription:
        """Mensajes de estado de suscripción."""

        SUBSCRIPTION_ACTIVE = (
            "✅ *Suscripción Activa*\n\n"
            "📦 Plan: {plan_name}\n"
            "💰 Precio: ${price} USD\n"
            "📅 Próxima renovación: {renewal_date}\n\n"
            "🎉 Tu suscripción está activa y disfrutas de todos los beneficios.\n\n"
            "⚡ *Opciones:*"
        )

        SUBSCRIPTION_INACTIVE = (
            "📭 *Sin Suscripción Activa*\n\n"
            "No tienes una suscripción activa en este momento.\n\n"
            "💡 Suscríbete para disfrutar de beneficios exclusivos:\n"
            "  ✓ Acceso prioritario\n"
            "  ✓ Soporte 24/7\n"
            "  ✓ Características premium\n\n"
            "⚡ *Elige una opción:*"
        )

        SUBSCRIPTION_EXPIRED = (
            "⏰ *Suscripción Expirada*\n\n"
            "Tu suscripción ha expirado.\n\n"
            "📦 Plan anterior: {plan_name}\n"
            "📅 Expiró el: {expiry_date}\n\n"
            "💡 Renueva tu suscripción para continuar disfrutando de los beneficios.\n\n"
            "⚡ *Opciones:*"
        )

        SUBSCRIPTION_DETAILS = (
            "{status_icon} *Detalles de Suscripción*\n\n"
            "📊 Estado: {status}\n"
            "📦 Plan: {plan_name}\n"
            "💰 Precio: ${price} USD\n"
            "📅 Inicio: {start_date}\n"
            "🔄 Renovación: {renewal_date}\n"
            "📱 Dispositivos: {devices}\n"
            "📊 Límite de datos: {data_limit}\n\n"
            "⚡ *Opciones:*"
        )

        SUBSCRIPTION_ACTIVATED = (
            "✅ *¡Suscripción Activada!*\n\n"
            "🎉 Tu suscripción ha sido activada exitosamente.\n\n"
            "📦 Plan: {plan_name}\n"
            "📅 Activación: {activation_date}\n"
            "🔄 Próxima renovación: {renewal_date}\n\n"
            "🚀 ¡Disfruta de todos los beneficios!"
        )

        SUBSCRIPTION_RENEWED = (
            "✅ *¡Suscripción Renovada!*\n\n"
            "🎉 Tu suscripción ha sido renovada exitosamente.\n\n"
            "📦 Plan: {plan_name}\n"
            "🔄 Nueva renovación: {renewal_date}\n\n"
            "🚀 ¡Gracias por continuar con nosotros!"
        )

        ACTIVATION_FAILED = (
            "❌ *Error al Activar Suscripción*\n\n"
            "No se pudo activar tu suscripción.\n\n"
            "📟 Motivo: {reason}\n\n"
            "💡 Por favor, intenta nuevamente o contacta a soporte."
        )

        RENEWAL_FAILED = (
            "❌ *Error al Renovar Suscripción*\n\n"
            "No se pudo renovar tu suscripción.\n\n"
            "📟 Motivo: {reason}\n\n"
            "💡 Por favor, intenta nuevamente o contacta a soporte."
        )

        NO_ACTIVE_SUBSCRIPTION = (
            "⚠️ *Sin Suscripción Activa*\n\n"
            "No tienes una suscripción activa para renovar.\n\n"
            "💡 Explora nuestros planes disponibles y suscríbete."
        )

    # ============================================
    # PLANS
    # ============================================

    class Plans:
        """Mensajes de planes disponibles."""

        PLANS_HEADER = (
            "📦 *Planes Disponibles*\n\nElige el plan que mejor se adapte a tus necesidades:\n\n"
        )

        PLAN_ITEM = "🔹 *{name}*\n   💰 ${price} USD/mes\n   📅 Duración: {duration} días\n\n"

        PLAN_DETAILS = (
            "📦 *{plan_name}*\n\n"
            "💰 Precio: ${price} USD/mes\n"
            "📅 Duración: {duration} días\n\n"
            "✨ *Características:*\n"
            "{features}\n\n"
            "⚡ *Selecciona una opción:*"
        )

        NO_PLANS = (
            "📭 *Sin Planes Disponibles*\n\n"
            "No hay planes disponibles en este momento.\n\n"
            "💡 Intenta más tarde."
        )

        PLAN_NOT_FOUND = (
            "❌ *Plan No Encontrado*\n\n"
            "El plan seleccionado no existe o no está disponible.\n\n"
            "💡 Por favor, elige otro plan."
        )

    # ============================================
    # PAYMENT
    # ============================================

    class Payment:
        """Mensajes de pago."""

        CHOOSE_PAYMENT_METHOD = (
            "💳 *Método de Pago*\n\n"
            "Selecciona cómo deseas pagar tu suscripción:\n\n"
            "⭐ *Telegram Stars* - Pago rápido y seguro\n"
            "   • Procesamiento instantáneo\n"
            "   • Sin configuración adicional\n\n"
            "🪙 *Crypto (USDT)* - Usando red TRC20\n"
            "   • Pagos anónimos\n"
            "   • Sin comisiones adicionales\n\n"
            "⚡ *Elige una opción:*"
        )

        CRYPTO_PAYMENT = (
            "🪙 *Pago con Criptomonedas*\n\n"
            "📦 Plan: {plan_name}\n"
            "💰 Monto: ${amount_usd} USDT\n"
            "🌐 Red: {network}\n\n"
            "📬 *Dirección de pago:*\n"
            "`{address}`\n\n"
            "⚠️ *Instrucciones:*\n"
            "1. Envía exactamente ${amount_usd} USDT a la dirección anterior\n"
            "2. Usa la red {network} (TRC20)\n"
            "3. El pago se confirmará automáticamente\n"
            "4. Tu suscripción se activará tras la confirmación\n\n"
            "⏱️ Tiempo estimado: 5-30 minutos"
        )

        CRYPTO_PENDING = (
            "⏳ *Pago Pendiente*\n\n"
            "Esperando confirmación de tu pago de ${amount} USDT.\n\n"
            "🔄 Presiona 'Verificar Estado' para comprobar."
        )

        CRYPTO_SUCCESS = (
            "✅ *¡Pago Confirmado!*\n\n"
            "🎉 Tu suscripción ha sido activada exitosamente.\n\n"
            "🚀 ¡Disfruta de todos los beneficios!"
        )

        CRYPTO_EXPIRED = (
            "⏰ *Pago Expirado*\n\n"
            "El tiempo límite para el pago ha vencido.\n\n"
            "💡 Por favor, intenta nuevamente con un nuevo plan."
        )

        CRYPTO_PAYMENT_FAILED = (
            "❌ *Error en Pago Crypto*\n\n"
            "No se pudo generar la dirección de pago.\n\n"
            "💡 Por favor, intenta nuevamente o contacta a soporte."
        )

        STARS_PAYMENT = (
            "⭐ *Pago con Telegram Stars*\n\n"
            "📦 Plan: {plan_name}\n"
            "💰 Monto: {stars_amount} Stars\n\n"
            "⚡ *Instrucciones:*\n"
            "1. Presiona el botón de pago\n"
            "2. Confirma el pago en la factura de Telegram\n"
            "3. Tu suscripción se activará automáticamente\n\n"
            "💡 Es rápido, seguro y sin configuración adicional."
        )

        STARS_SUCCESS = (
            "✅ *¡Pago Exitoso!*\n\n"
            "🎉 Tu suscripción ha sido activada.\n\n"
            "📦 Plan: {plan_name}\n"
            "⭐ Stars utilizadas: {stars_amount}\n\n"
            "🚀 ¡Disfruta de todos los beneficios!"
        )

        STARS_FAILED = (
            "❌ *Pago Fallido*\n\n"
            "No se pudo procesar tu pago con Stars.\n\n"
            "📟 Motivo: {reason}\n\n"
            "💡 Por favor, contacta a soporte o intenta nuevamente."
        )

    # ============================================
    # ACTIVATION
    # ============================================

    class Activation:
        """Mensajes de activación de suscripción."""

        SUCCESS = (
            "✅ *¡Activación Exitosa!*\n\n"
            "🎉 Tu suscripción ha sido activada correctamente.\n\n"
            "📦 Plan: {plan_name}\n"
            "📅 Fecha de activación: {activation_date}\n"
            "🔄 Próxima renovación: {renewal_date}\n\n"
            "🚀 ¡Disfruta de todos los beneficios!"
        )

        FAILED = (
            "❌ *Activación Fallida*\n\n"
            "No se pudo activar tu suscripción.\n\n"
            "📟 Motivo: {reason}\n\n"
            "💡 Por favor, intenta nuevamente o contacta a soporte."
        )

        ALREADY_ACTIVE = (
            "ℹ️ *Ya Tienes Suscripción Activa*\n\n"
            "Actualmente tienes una suscripción activa.\n\n"
            "📦 Plan: {plan_name}\n"
            "🔄 Renovación: {renewal_date}\n\n"
            "💡 Si deseas cambiar de plan, contacta a soporte."
        )

    # ============================================
    # RENEWAL
    # ============================================

    class Renewal:
        """Mensajes de renovación de suscripción."""

        RENEW_SUCCESS = (
            "✅ *¡Renovación Exitosa!*\n\n"
            "🎉 Tu suscripción ha sido renovada correctamente.\n\n"
            "📦 Plan: {plan_name}\n"
            "🔄 Nueva fecha de renovación: {renewal_date}\n\n"
            "🚀 ¡Gracias por continuar con nosotros!"
        )

        RENEW_FAILED = (
            "❌ *Renovación Fallida*\n\n"
            "No se pudo renovar tu suscripción.\n\n"
            "📟 Motivo: {reason}\n\n"
            "💡 Por favor, verifica tu método de pago e intenta nuevamente."
        )

        NO_ACTIVE_SUBSCRIPTION = (
            "⚠️ *No Hay Suscripción para Renovar*\n\n"
            "No tienes una suscripción activa para renovar.\n\n"
            "💡 Explora nuestros planes disponibles y suscríbete."
        )

        RENEWAL_PROMPT = (
            "🔄 *Renovar Suscripción*\n\n"
            "Tu suscripción se renovará automáticamente.\n\n"
            "📦 Plan: {plan_name}\n"
            "💰 Monto: ${price} USD\n"
            "📅 Próxima renovación: {renewal_date}\n\n"
            "⚡ *¿Deseas renovar ahora?*"
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

        INVALID_PLAN = (
            "❌ *Plan Inválido*\n\n"
            "El plan seleccionado no existe o no está disponible.\n\n"
            "💡 Por favor, elige otro plan."
        )

        PAYMENT_FAILED = (
            "❌ *Pago Fallido*\n\n"
            "No se pudo procesar tu pago.\n\n"
            "💡 Verifica tu saldo e intenta nuevamente."
        )

        NOT_AUTHENTICATED = (
            "🔒 *No Autenticado*\n\n"
            "Debes iniciar sesión para acceder a esta función.\n\n"
            "💡 Usa /start para autenticarte."
        )

        UNAUTHORIZED = "🚫 *Acceso Denegado*\n\nNo tienes permisos para realizar esta acción."

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
